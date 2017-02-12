# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk
from tkinter import ttk
from pythonic_tkinter.preconfigured_widgets import *
from collections import defaultdict
from miscellaneous.network_functions import mac_comparer
from heapq import heappop, heappush
from . import area
from . import AS_management

class AutonomousSystem(object):
    
    class_type = 'AS'
    has_area = False

    def __init__(
                 self, 
                 scenario,
                 name, 
                 id,
                 links = set(), 
                 nodes = set(), 
                 imp = False
                 ):
                     
        self.cs = scenario
        self.ntw = self.cs.ntw
        self.name = name
        self.id = id
        self.links = links
        self.nodes = nodes

        # pAS as in 'pool AS': same as pool network
        self.pAS = {'link': self.links, 'node': self.nodes}
        
        # unselect everything
        scenario.unhighlight_all()
        
    def __repr__(self):
        return self.name
        
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name
        
    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __hash__(self):
        return hash(self.name)
        
    def add_to_AS(self, *objects):
        for obj in objects:
            # add objects in the AS corresponding pool
            self.pAS[obj.class_type].add(obj)
            if not self in obj.AS:
                obj.AS[self] = set()
        
    def remove_from_AS(self, *objects):
        for obj in objects:
            # we remove the object from its pool in the AS
            self.pAS[obj.class_type].discard(obj)
            # we pop the AS from the dict of object AS, and retrieve the list
            # of area it belongs to in this AS
            obj.AS.pop(self)
            
    def delete_AS(self):
        for obj in self.nodes | self.links:
            obj.AS.pop(self)
            self.pAS[obj.class_type].discard(obj)
        self.management.destroy()
        self.ntw.pnAS.pop(self.name)
            
class ASWithArea(AutonomousSystem):
    
    has_area = True
    
    def __init__(self, *args):
        super().__init__(*args)
        
        # areas is a dict associating a name to an area
        self.areas = {}
        
    def area_factory(self, name, id=0, links=set(), nodes=set()):
        if name not in self.areas:
            self.areas[name] = area.Area(name, id, self, links, nodes)
        return self.areas[name]
        
    def add_to_area(self, area='Backbone', *objects):
        area.add_to_area(*objects)         
                
    def remove_from_area(self, *objects):
        for obj in objects:
            # for each area, we delete the object from the corresponding pool
            for area in set(obj.AS[self]):
                area.remove_from_area(obj)
        
    def delete_area(self, area):
        # we remove the area of the AS areas dictionary
        area = self.areas.pop(area.name)
        for obj_type in ('node', 'link'):
            for obj in area.pa[obj_type]:
                # we remove the area to the list of area in the AS 
                # dictionary, for all objects of the area
                obj.AS[area.AS].remove(area)
                
    def delete_AS(self):
        for area in tuple(self.areas.values()):
            self.delete_area(area)
        super(ASWithArea, self).delete_AS()
            
class Ethernet_AS(AutonomousSystem):
    
    layer = 'Ethernet'
    
    def __init__(self, *args):
        super().__init__(*args)
        
    def add_to_AS(self, *objects):
        super(Ethernet_AS, self).add_to_AS(*objects)
        
class VLAN_AS(ASWithArea, Ethernet_AS):
    
    AS_type = 'VLAN'
    
    def __init__(self, *args):
        super().__init__(*args)
        is_imported = args[-1]
        
        # management window of the AS 
        self.management = AS_management.VLAN_Management(self, is_imported)
                
        if not is_imported:
            self.area_factory(
                              'Default VLAN', 
                              id = 1, 
                              links = self.links, 
                              nodes = self.nodes
                              )
                              
            # set the default per-AS properties of all AS objects
            self.add_to_AS(*(self.nodes | self.links))

        # update the AS management panel by filling all boxes
        self.management.refresh_display()
            
class STP_AS(Ethernet_AS):
    
    AS_type = 'STP'
    
    def __init__(self, *args):
        super().__init__(*args)
        is_imported = args[-1]
        
        # root of the AS
        self.root = None
        self.SPT_links = set()
        
        # management window of the AS 
        self.management = AS_management.STP_Management(self, is_imported)
                
        if not is_imported:
            # set the default per-AS properties of all AS objects
            self.add_to_AS(*(self.nodes | self.links))
            
        # trigger the root switch election. The root is the swith with the
        # highest priority, or in case of tie, the highest MAC address
        self.root_election()
        # update the AS management panel by filling all boxes
        self.management.refresh_display()
                    
    def add_to_AS(self, *objects):
        super(Ethernet_AS, self).add_to_AS(*objects)
        
        for obj in objects:
            # A RSTP AS has no area, each object's area set is initialized 
            # to None as it should never be needed
            obj.AS[self] = None
            if obj.type == 'plink':
                obj.interfaceS(self.name, 'cost', 1)
                obj.interfaceD(self.name, 'cost', 1)
                obj.interfaceS(self.name, 'priority', 32768)
                obj.interfaceD(self.name, 'priority', 32768)
                
            if obj.subtype == 'switch':
                obj.AS_properties[self.name].update({'priority': 32768})
                
    def root_election(self):
        for node in self.nodes:
            if not self.root:
                self.root = node
                continue
            root_priority = self.root.AS_properties[self.name]['priority']
            node_priority = node.AS_properties[self.name]['priority'] 
            # if the current node has a higher priority, it becomes root
            if node_priority < root_priority:
                self.root = node
            # if the priority is the same
            if node_priority == root_priority:
                # and the current node has a higher MAC address, it becomes root
                if mac_comparer(self.root.base_macaddress, node.base_macaddress):
                    self.root = node
        print(self.root)
        
    def build_SPT(self):
        # clear the current spanning tree physical links
        self.SPT_links.clear()
        visited = set()
        # allowed nodes and links
        allowed_nodes = self.pAS['node']
        allowed_links =  self.pAS['link'] - self.ntw.fdtks
        # we keep track of all already visited subnetworks so that we 
        # don't add them more than once to the mapping dict.
        heap = [(0, self.root, [])]
        
        while heap:
            dist, node, path_link = heappop(heap)
            if node not in visited:
                if path_link:
                    self.SPT_links.add(path_link[-1])
                visited.add(node)
                for neighbor, l2vc in self.ntw.gftr(node, 'l2link', 'l2vc'):
                    adj_link = l2vc('link', node)
                    remote_link = l2vc('link', neighbor)
                    if adj_link in path_link:
                        continue
                    # excluded and allowed nodes
                    if neighbor not in allowed_nodes:
                        continue
                    # excluded and allowed physical links
                    if adj_link not in allowed_links: 
                        continue
                    ex_int_cost = adj_link('cost', node, AS=self.name)
                    heappush(heap, (dist + ex_int_cost, 
                                        neighbor, path_link + [adj_link]))
    
class IP_AS(AutonomousSystem):
    
    layer = 'IP'
    
    def __init__(self, *args):
        super().__init__(*args)
        
    def add_to_AS(self, *objects):
        super(IP_AS, self).add_to_AS(*objects)
        
        for obj in objects:            
            if obj.subtype == 'router':
                obj.AS_properties[self.name].update({
                                                    'LB_paths': 4,
                                                    'router_id': None
                                                    })
                                                    
    def build_RFT(self):
        allowed_nodes = self.nodes
        allowed_links =  self.links - self.ntw.fdtks
        for node in self.nodes:
            self.RFT_builder(node, allowed_nodes, allowed_links)
                
class RIP_AS(IP_AS):
    
    AS_type = 'RIP'
    
    def __init__(self, *args):
        super().__init__(*args)
        is_imported = args[-1]
        
        # management window of the AS 
        self.management = AS_management.RIP_Management(self, is_imported)
        
        # the metric used to compute the shortest path. By default, it is 
        # a hop count for a RIP AS, and bandwidth-dependent for ISIS or OSPF.
        # if the metric is bandwidth, it is calculated based on the interface
        # of the physical link, and a user-defined reference bandwidth.
        self.metric = 'hop count'
        
        if not is_imported:
            # set the default per-AS properties of all AS objects
            self.add_to_AS(*(self.nodes | self.links))
            
        # update the AS management panel by filling all boxes
        self.management.refresh_display()
            
    def add_to_AS(self, *objects):
        super(RIP_AS, self).add_to_AS(*objects)       
        
        for obj in objects:
            # A RIP AS has no area, each object's area set is initialized 
            # to None as it should never be needed
            obj.AS[self] = None
            if obj.type == 'plink':
                obj.interfaceS(self.name, 'cost', 1)
                obj.interfaceD(self.name, 'cost', 1)   
        
    def RFT_builder(self, source, allowed_nodes, allowed_links):
        K = source.AS_properties[self.name]['LB_paths']
        visited = set()
        # we keep track of all already visited subnetworks so that we 
        # don't add them more than once to the mapping dict.
        visited_subnetworks = set()
        heap = [(0, source, [], None)]
        # cost of the shortesth path to a subnetwork
        SP_cost = {}
        
        while heap:
            dist, node, l3_path, ex_int = heappop(heap)  
            if (node, ex_int) not in visited:
                visited.add((node, ex_int))
                for neighbor, l3vc in self.ntw.gftr(node, 'l3link', 'l3vc'):
                    adj_link = l3vc('link', node)
                    remote_link = l3vc('link', neighbor)
                    if l3vc in l3_path:
                        continue
                    # excluded and allowed nodes
                    if neighbor not in allowed_nodes:
                        continue
                    # excluded and allowed physical links
                    if adj_link not in allowed_links: 
                        continue
                    if node == source:
                        ex_ip = remote_link('ipaddress', neighbor)
                        ex_int = adj_link('interface', source)
                        source.rt[adj_link.sntw] = {('C', ex_ip, ex_int,
                                            dist, neighbor, adj_link)}
                        SP_cost[adj_link.sntw] = 0
                    ex_int_cost = adj_link('cost', node, AS=self.name)
                    heappush(heap, (dist + ex_int_cost, 
                            neighbor, l3_path + [l3vc], ex_int))
                    
            if l3_path:
                curr_l3, ex_l3 = l3_path[-1], l3_path[0]
                ex_tk = ex_l3('link', source)
                nh = ex_l3.destination if ex_l3.source == source else ex_l3.source
                ex_ip = ex_l3('link', nh)('ipaddress', nh)
                link = curr_l3('link', node)
                ex_int = ex_tk('interface', source)
                if link.sntw not in source.rt:
                    SP_cost[link.sntw] = dist
                    source.rt[link.sntw] = {('R', ex_ip, ex_int, 
                                                dist, nh, ex_tk)}
                else:
                    if (dist == SP_cost[link.sntw] 
                        and K > len(source.rt[link.sntw])):
                        source.rt[link.sntw].add(('R', ex_ip, ex_int, 
                                                dist, nh, ex_tk))
        
class ISIS_AS(ASWithArea, IP_AS):
    
    AS_type = 'ISIS'
    
    def __init__(self, *args):
        super().__init__(*args)
        is_imported = args[-1]
        self.ref_bw = 10000 # (kbps)
        
        # management window of the AS 
        self.management = AS_management.ISIS_Management(self, is_imported)
        
        # contains all L1/L2 nodes
        self.border_routers = set()
        
        if not is_imported:
            self.area_factory(
                              'Backbone', 
                              id = 2, 
                              links = self.links, 
                              nodes = self.nodes
                              )
                              
            # set the default per-AS properties of all AS objects
            self.add_to_AS(*(self.nodes | self.links))
            self.add_to_area(self.areas['Backbone'], *(self.nodes | self.links))
        
        # update the AS management panel by filling all boxes
        self.management.refresh_display()
        
    def add_to_AS(self, *objects):
        super(ISIS_AS, self).add_to_AS(*objects)       
        
        for obj in objects:
            if obj.type == 'plink':
                cost = self.ref_bw / obj.bw
                obj.interfaceS(self.name, 'cost', cost)
                obj.interfaceD(self.name, 'cost', cost)  
                
    def update_AS_topology(self):
        
        self.border_routers.clear()
        # reset all area physical links
        self.areas['Backbone'].pa['link'].clear()
        for link in self.pAS['link']:
            link.AS[self].clear()
        
        for node in self.pAS['node']:
            
            # In IS-IS, a router has only one area
            node_area ,= node.AS[self]
            
            for neighbor, adj_link in self.cs.ntw.graph[node.id]['plink']:
                
                # A multi-area IS-IS AS is defined by the status of its nodes.
                # we automatically update the link area status, by considering 
                # that a link belongs to an area as soon as both of its ends do.
                # A link between two L1/L2 routers that belong to different
                # areas will be considered as being part of the backbone.

                # we check that the neighbor belongs to the AS
                if self in neighbor.AS:
                    # we retrieve the neighbor's area
                    neighbor_area ,= neighbor.AS[self]
                    # if they are the same, we add the link to the area
                    if node_area == neighbor_area:
                        node_area.add_to_area(adj_link)
                    # if not, it is at the edge of two areas
                    # a router is considered L1/L2 if it has at least
                    # one neighbor which is in a different area.
                    else:
                        # we consider that the link belongs to the backbone,
                        # for interfaces to have IP addresses.
                        self.areas['Backbone'].add_to_area(adj_link)
                        self.border_routers.add(node)   

    def RFT_builder(self, source, allowed_nodes, allowed_links):

        K = source.AS_properties[self.name]['LB_paths']
        visited = set()
        # we keep track of all already visited subnetworks so that we 
        # don't add them more than once to the mapping dict.
        visited_subnetworks = set()
        heap = [(0, source, [], None)]

        # cost of the shortesth path to a subnetwork
        SP_cost = {}
                
        # if source is an L1 there will be a default route to
        # 0.0.0.0 heading to the closest L1/L2 node.
        src_area ,= source.AS[self]
        
        # we keep a boolean telling us if source is L1 so that we know we
        # must add the i*L1 default route when we first meet a L1/L2 node
        # and all other routes are i L1 as rtype (route type).
        isL1 = source not in self.border_routers and src_area.name != 'Backbone'
        
        while heap:
            dist, node, l3_path, ex_int = heappop(heap)  
            if (node, ex_int) not in visited:
                visited.add((node, ex_int))
                for neighbor, l3vc in self.ntw.gftr(node, 'l3link', 'l3vc'):
                    adj_link = l3vc('link', node)
                    remote_link = l3vc('link', neighbor)
                    if l3vc in l3_path:
                        continue
                    # excluded and allowed nodes
                    if neighbor not in allowed_nodes:
                        continue
                    # excluded and allowed physical links
                    if adj_link not in allowed_links: 
                        continue
                    if node == source:
                        ex_ip = remote_link('ipaddress', neighbor)
                        ex_int = adj_link('interface', source)
                        source.rt[adj_link.sntw] = {('C', ex_ip, ex_int,
                                            dist, neighbor, adj_link)}
                        SP_cost[adj_link.sntw] = 0
                    ex_int_cost = adj_link('cost', node, AS=self.name)
                    heappush(heap, (dist + ex_int_cost, 
                                neighbor, l3_path + [l3vc], ex_int))
                    
            if l3_path:
                curr_l3, ex_l3 = l3_path[-1], l3_path[0]
                ex_tk = ex_l3('link', source)
                nh = ex_l3.destination if ex_l3.source == source else ex_l3.source
                ex_ip = ex_l3('link', nh)('ipaddress', nh)
                link = curr_l3('link', node)
                ex_int = ex_tk('interface', source)
                link_int_cost = link('cost', node, AS=self.name)
                if isL1:
                    if (node in self.border_routers 
                                        and '0.0.0.0' not in source.rt):
                        if source.name == 'router4':
                            print(node, self.border_routers, link, link.sntw)
                        source.rt['0.0.0.0'] = {('i*L1', ex_ip, ex_int,
                                                    dist, nh, ex_tk)}
                    else:
                        if (('i L1', link.sntw) not in visited_subnetworks 
                                        and link.AS[self] & ex_tk.AS[self]):
                            visited_subnetworks.add(('i L1', link.sntw))
                            source.rt[link.sntw] = {('i L1', ex_ip, ex_int,
                                    dist + link_int_cost, nh, ex_tk)}
                else:
                    linkAS ,= link.AS[self]
                    exit_area ,= ex_tk.AS[self]
                    rtype = 'i L1' if (link.AS[self] & ex_tk.AS[self] and 
                                    linkAS.name != 'Backbone') else 'i L2'
                    # we favor intra-area routes by excluding a 
                    # route if the area of the exit physical link is not
                    # the one of the subnetwork
                    if (not ex_tk.AS[self] & link.AS[self] 
                                    and linkAS.name == 'Backbone'):
                        continue
                    # if the source is an L1/L2 node and the destination
                    # is an L1 area different from its own, we force it
                    # to use the backbone by forbidding it to use the
                    # exit interface in the source area
                    if (rtype == 'i L2' and source in self.border_routers and 
                                exit_area.name != 'Backbone'):
                        continue
                    if (('i L1', link.sntw) not in visited_subnetworks 
                        and ('i L2', link.sntw) not in visited_subnetworks):
                        visited_subnetworks.add((rtype, link.sntw))
                        source.rt[link.sntw] = {(rtype, ex_ip, ex_int,
                                dist + link_int_cost, nh, ex_tk)}
                    # TODO
                    # IS-IS uses per-address unequal cost load balancing 
                    # a user-defined variance defined as a percentage of the
                    # primary path cost defines which paths can be used
                    # (up to 9).
                
class OSPF_AS(ASWithArea, IP_AS):
    
    AS_type = 'OSPF'
    
    def __init__(self, *args):
        super().__init__(*args)
        is_imported = args[-1]
        self.metric = 'bandwidth'
        self.ref_bw = 10**8

        # management window of the AS
        self.management = AS_management.OSPF_Management(self, is_imported)
        
        # contains all ABRs
        self.border_routers = set()
        
        # node used to exit the domain (ASBR for OSPF)
        self.exit_point = None
        
        if not is_imported:
            self.area_factory(
                              'Backbone', 
                              id = 0, 
                              links = self.links, 
                              nodes = self.nodes
                              )
                              
            # set the default per-AS properties of all AS objects
            self.add_to_AS(*(self.nodes | self.links))
            self.add_to_area(self.areas['Backbone'], *(self.nodes | self.links))
            
        # update the AS management panel by filling all boxes
        self.management.refresh_display()
        
    def add_to_AS(self, *objects):
        super(OSPF_AS, self).add_to_AS(*objects)     
        
        for obj in objects:            
            if obj.type == 'plink':
                cost = self.ref_bw / obj.bw
                obj.interfaceS(self.name, 'cost', cost)
                obj.interfaceD(self.name, 'cost', cost) 
                
    def update_AS_topology(self):
        
        self.border_routers.clear()
        # reset all area nodes
        self.areas['Backbone'].pa['node'].clear()
        
        for node in self.pAS['node']:
                
            # in OSPF, a router is considered ABR if it has attached
            # links that are in different area. Since we just updated 
            # the router's areas, all we need to check is that it has
            # at least 2 distinct areas.
            # an ABR is automatically part of the backbone area.
            if len(node.AS[self]) > 1:
                self.border_routers.add(node)
                self.areas['Backbone'].add_to_area(node)
            
            for neighbor, adj_link in self.cs.ntw.graph[node.id]['plink']:

                # a multi-area OSPF AS is defined by the area of its link.
                # we automatically update the node area status, by considering that a 
                # node belongs to an area as soon as one of its adjacent link does.
                for area in adj_link.AS[self]:
                    area.add_to_area(node)  
            
    def RFT_builder(self, source, allowed_nodes, allowed_links):
        K = source.AS_properties[self.name]['LB_paths']
        visited = set()
        # we keep track of all already visited subnetworks so that we 
        # don't add them more than once to the mapping dict.
        visited_subnetworks = set()
        heap = [(0, source, [], None)]
        # source area: we make sure that if the node is connected to an area,
        # the path we find to any subnetwork in that area is an intra-area path.
        src_areas = source.AS[self]
        # cost of the shortesth path to a subnetwork
        SP_cost = {}
        
        while heap:
            dist, node, l3_path, ex_int = heappop(heap)
            if (node, ex_int) not in visited:
                visited.add((node, ex_int))
                for neighbor, l3vc in self.ntw.gftr(node, 'l3link', 'l3vc'):
                    adj_link = l3vc('link', node)
                    remote_link = l3vc('link', neighbor)
                    if l3vc in l3_path:
                        continue
                    # excluded and allowed nodes
                    if neighbor not in allowed_nodes:
                        continue
                    # excluded and allowed physical links
                    if adj_link not in allowed_links: 
                        continue
                    if node == source:
                        ex_ip = remote_link('ipaddress', neighbor)
                        ex_int = adj_link('interface', source)
                        source.rt[adj_link.sntw] = {('C', ex_ip, ex_int,
                                            dist, neighbor, adj_link)}
                        SP_cost[adj_link.sntw] = 0
                    ex_int_cost = adj_link('cost', node, AS=self.name)
                    heappush(heap, (dist + ex_int_cost, 
                                    neighbor, l3_path + [l3vc], ex_int))
                    
            if l3_path:
                curr_l3, ex_l3 = l3_path[-1], l3_path[0]
                ex_tk = ex_l3('link', source)
                nh = ex_l3.destination if ex_l3.source == source else ex_l3.source
                ex_ip = ex_l3('link', nh)('ipaddress', nh)
                link = curr_l3('link', node)
                ex_int = ex_tk('interface', source)
                # we check if the physical link has any common area with the
                # exit physical link: if it does not, it is an inter-area route.
                rtype = 'O' if (link.AS[self] & ex_tk.AS[self]) else 'O IA'
                if link.sntw not in source.rt:
                    SP_cost[link.sntw] = dist
                    source.rt[link.sntw] = {(rtype, ex_ip, ex_int, 
                                                dist, nh, ex_tk)}
                else:
                    for route in source.rt[link.sntw]:
                        break
                    if route[0] == 'O' and rtype == 'IA':
                        continue
                    elif route[0] == 'O IA' and rtype == 'O':
                        SP_cost[link.sntw] = dist
                        source.rt[link.sntw] = {(rtype, ex_ip, ex_int, 
                                                dist, nh, ex_tk)}
                    else:
                        if (dist == SP_cost[link.sntw]
                            and K > len(source.rt[link.sntw])):
                            source.rt[link.sntw].add((
                                                    rtype, ex_ip, ex_int, 
                                                        dist, nh, ex_tk
                                                        ))
                if (rtype, link.sntw) not in visited_subnetworks:
                    if ('O', link.sntw) in visited_subnetworks:
                        continue
                    else:
                        visited_subnetworks.add((rtype, link.sntw))
                        source.rt[link.sntw] = {(rtype, ex_ip, ex_int, 
                                                        dist, nh, ex_tk)}
                                                        
class BGP_AS(ASWithArea, IP_AS):
    
    AS_type = 'BGP'
    
    def __init__(self, *args):
        super().__init__(*args)
        is_imported = args[-1]

        # management window of the AS
        self.management = AS_management.BGP_Management(self, is_imported)
        
        if not is_imported:
            # set the default per-AS properties of all AS objects
            self.add_to_AS(*(self.nodes | self.links)),
            
        # update the AS management panel by filling all boxes
        self.management.refresh_display()
        
    def add_to_AS(self, *objects):
        super(BGP_AS, self).add_to_AS(*objects)       
        
        for obj in objects:
            if obj.subtype == 'router':
                obj.AS_properties[self.name].update({
                                                    'local_pref': 100,
                                                    })
                
    def update_AS_topology(self):                
        # update all BGP peering type based on the source and destination AS
        for node in self.nodes:
            for neighbor, peering in self.ntw.gftr(node, 'l3link', 'BGP peering'):
                # add the peering as an AS link
                self.add_to_AS(peering)
                # set the peering type
                if set(node.AS[self]) & set(neighbor.AS[self]):
                    peering.bgp_type = 'iBGP'
                else:
                    peering.bgp_type = 'eBGP'
            
    def RFT_builder(self, source, allowed_nodes, allowed_links):
        source.bgpt.clear()
        visited = {source}
        heap = []
        # bgp table
        bgpt = defaultdict(set)
        
        # populate the BGP table with the routes sourced by the source node,
        # with a default weight of 32768
        for ip, routes in source.rt.items():
            for route in routes:
                _, nh, *_ = route
                source.bgpt[ip] |= {(0, nh, source, ())}
        
        # we fill the heap
        for src_nb, bgp_pr in self.ntw.gftr(source, 'l3link', 'BGP peering'):
            first_AS = [source.bgp_AS, src_nb.bgp_AS]
            # Cisco weight is 0 by default
            if bgp_pr('weight', source):
                weight = 1 / bgp_pr('weight', source)
            else: 
                weight = float('inf')
            heappush(heap, (
                            weight, # weight 
                            2, # length of the AS_PATH vector
                            bgp_pr('ip', src_nb), # next-hop IP address
                            src_nb, # current node
                            [], # path as a list of BGP peering connections
                            first_AS # path as a list of AS
                            ))
        
        while heap:
            weight, length, nh, node, route_path, AS_path = heappop(heap)
            if node not in visited:
                for ip, routes in node.rt.items():
                    real_weight = 0 if weight == float('inf') else 1 / weight
                    source.bgpt[ip] |= {(real_weight, nh, node, tuple(AS_path))}
                visited.add(node)
                for bgp_nb, bgp_pr in self.ntw.gftr(node, 'l3link', 'BGP peering'):
                    # excluded and allowed nodes
                    if bgp_nb in visited:
                        continue
                    # we append a new AS if we use an external BGP peering
                    new_AS = [bgp_nb.bgp_AS]*(bgp_pr.bgp_type == 'eBGP')
                    heappush(heap, (
                                    weight, 
                                    length + (bgp_pr.bgp_type == 'eBGP'), 
                                    nh, 
                                    bgp_nb,
                                    route_path + [bgp_pr], 
                                    AS_path + new_AS
                                    ))
        
class AreaOperation(CustomTopLevel):
    
    # Add objects to an area, or remove objects from an area
    
    def __init__(self, scenario, mode, obj, AS=set()):
        super().__init__()
        
        title = 'Add to area' if mode == 'add' else 'Remove from area'
        
        # main label frame
        lf_area_operation = Labelframe(self)
        lf_area_operation.text = title
        lf_area_operation.grid(0, 0)
        
        self.title(title)

        values = tuple(map(str, AS))
        
        # List of existing AS
        self.AS_list = Combobox(self, width=15)
        self.AS_list['values'] = values
        self.AS_list.current(0)
        self.AS_list.bind('<<ComboboxSelected>>', lambda e: self.update_value(scenario))
        
        self.area_list = Combobox(self, width=15)
        self.update_value(scenario)
        self.area_list.current(0)

        button_area_operation = Button(self)
        button_area_operation.text = 'OK'
        button_area_operation.command = lambda: self.area_operation(scenario, mode, *obj)
        
        self.AS_list.grid(0, 0, in_=lf_area_operation)
        self.area_list.grid(1, 0, in_=lf_area_operation)
        button_area_operation.grid(2, 0, in_=lf_area_operation)
        
    def update_value(self, scenario):
        selected_AS = scenario.ntw.AS_factory(name=self.AS_list.get())
        self.area_list['values'] = tuple(map(str, selected_AS.areas))
        
    def area_operation(self, scenario, mode, *objects):
        selected_AS = scenario.ntw.AS_factory(name=self.AS_list.get())
        selected_area = self.area_list.get()

        if mode == 'add':
            selected_AS.management.add_to_area(selected_area, *objects)
        else:
            selected_AS.management.remove_from_area(selected_area, *objects)
            
        self.destroy()
        
class ASOperation(CustomTopLevel):
    
    # Add objects to an AS, or remove objects from an AS
    
    def __init__(self, scenario, mode, obj, AS=set()):
        super().__init__()
        
        title = {
        'add': 'Add to AS',
        'remove': 'Remove from AS',
        'manage': 'Manage AS'
        }[mode]
        
        # main label frame
        lf_AS_operation = Labelframe(self)
        lf_AS_operation.text = title
        lf_AS_operation.grid(0, 0)
        
        self.title(title)
        
        if mode == 'add':
            # All AS are proposed 
            values = tuple(map(str, scenario.ntw.pnAS))
        else:
            # Only the common AS among all selected objects
            values = tuple(map(str, AS))
        
        # List of existing AS
        self.AS_list = Combobox(self, width=15)
        self.AS_list['values'] = values
        self.AS_list.current(0)

        button_AS_operation = Button(self)
        button_AS_operation.text = 'OK'
        button_AS_operation.command = lambda: self.as_operation(scenario, mode, *obj)
        
        self.AS_list.grid(0, 0, 1, 2, in_=lf_AS_operation)
        button_AS_operation.grid(1, 0, 1, 2, in_=lf_AS_operation)
        
    def as_operation(self, scenario, mode, *objects):
        selected_AS = scenario.ntw.AS_factory(name=self.AS_list.get())

        if mode == 'add':
            selected_AS.management.add_to_AS(*objects)
        elif mode == 'remove':
            selected_AS.management.remove_from_AS(*objects)
        else:
            selected_AS.management.deiconify()
            
        self.destroy()
        
class ASCreation(CustomTopLevel):
    def __init__(self, scenario, nodes, links):
        super().__init__()
        self.title('Create AS')
        
        # main label frame
        lf_create_AS = Labelframe(self)
        lf_create_AS.text = 'Create AS'
        lf_create_AS.grid(0, 0)
        
        # List of AS type
        self.AS_type_list = Combobox(self, width=10)
        self.AS_type_list['values'] = ('RIP', 'ISIS', 'OSPF', 'RSTP', 'BGP', 'STP', 'VLAN')
        self.AS_type_list.current(0)

        # retrieve and save node data
        button_create_AS = Button(self)
        button_create_AS.text = 'Create AS'
        button_create_AS.command = lambda: self.create_AS(scenario, nodes, links)
                        
        # Label for the name/type of the AS
        label_name = Label(self)
        label_name.text = 'Name'
        
        label_type = Label(self)
        label_type.text = 'Type'
        
        label_id = Label(self)
        label_id.text = 'ID'
        
        # Entry box for the name of the AS
        self.entry_name  = Entry(self, width=13)
        self.entry_id  = Entry(self, width=13)
        
        label_name.grid(0, 0, in_=lf_create_AS)
        label_id.grid(1, 0, in_=lf_create_AS)
        self.entry_name.grid(0, 1, in_=lf_create_AS)
        self.entry_id.grid(1, 1, in_=lf_create_AS)
        label_type.grid(2, 0, in_=lf_create_AS)
        self.AS_type_list.grid(2, 1, in_=lf_create_AS)
        button_create_AS.grid(3, 0, 1, 2, in_=lf_create_AS)

    def create_AS(self, scenario, nodes, links):
        # automatic initialization of the AS id in case it is empty
        id = int(self.entry_id.get()) if self.entry_id.get() else len(scenario.ntw.pnAS) + 1
        
        new_AS = scenario.ntw.AS_factory(
                                         self.AS_type_list.get(), 
                                         self.entry_name.get(), 
                                         id,
                                         links, 
                                         nodes
                                         )
        self.destroy()
            