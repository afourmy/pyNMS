# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import miscellaneous
import objects
import AS
import random
import numpy
from math import cos, sin, asin, radians, sqrt
from cvxopt import matrix, glpk
from collections import defaultdict, deque
from heapq import heappop, heappush
from operator import getitem, itemgetter

class Network(object):
    
    node_class = {
    "router": objects.Router,
    "oxc": objects.OXC,
    "host": objects.Host,
    "antenna": objects.Antenna,
    "regenerator": objects.Regenerator,
    "splitter": objects.Splitter,
    "switch": objects.Switch,
    "cloud": objects.Cloud
    }
    
    link_class = {
    "trunk": {
    "ethernet": objects.Ethernet,
    "wdm": objects.WDMFiber
    },
    "route": objects.Route,
    "traffic": objects.Traffic
    }
    
    link_type = tuple(link_class.keys())
    node_type = tuple(node_class.keys())
    all_type = link_type + node_type
    
    def __init__(self, scenario):
        # pn for "pool network"
        self.pn = {"trunk": {}, "node": {}, "route": {}, "traffic": {}}
        self.pnAS = {}
        self.scenario = scenario
        self.graph = defaultdict(lambda: defaultdict(set))
        self.cpt_link = self.cpt_node = self.cpt_AS = 1
        
        # this parameter is used for failure simulation, to display the 
        # recovery path of a route considering the failed trunk
        self.failed_trunk = None
          
    # "lf" is the link factory. Creates or retrieves any type of link
    def lf(
           self, 
           *param, 
           protocol = "ethernet", 
           interface = "10GE", 
           link_type = "trunk", 
           name = None, 
           s = None, 
           d = None
           ):
        if not name:
            name = link_type + str(self.cpt_link)
        # creation link in the s-d direction if no link at all yet
        if not name in self.pn[link_type]:
            if link_type == "trunk":
                new_link = self.link_class[link_type][protocol](interface, name, 
                                                                s, d, *param)
            else:
                new_link = self.link_class[link_type](name, s, d, *param)
            self.cpt_link += 1
            self.pn[link_type][name] = new_link
            self.graph[s][link_type].add((d, new_link))
            self.graph[d][link_type].add((s, new_link))
        return self.pn[link_type][name]
        
    # "nf" is the node factory. Creates or retrieves any type of nodes
    def nf(self, *p, node_type="router", name=None):
        if not name:
            name = "node" + str(self.cpt_node)
        if name not in self.pn["node"]:
            self.pn["node"][name] = self.node_class[node_type](name, *p)
            self.cpt_node += 1
        return self.pn["node"][name]
        
    def AS_factory(
                   self, 
                   name = None, 
                   _type = "RIP",
                   id = 0,
                   trunks = set(), 
                   nodes = set(), 
                   edges = set(), 
                   routes = set(),
                   imp = False
                   ):
        if not name:
            name = "AS" + str(self.cpt_AS)
        if name not in self.pnAS:
            # creation of the AS
            self.pnAS[name] = AS.AutonomousSystem(
                                                  self.scenario, 
                                                  _type, 
                                                  name, 
                                                  id,
                                                  trunks, 
                                                  nodes, 
                                                  edges,
                                                  routes, 
                                                  imp
                                                  )
            # increase the AS counter by one
            self.cpt_AS += 1
        return self.pnAS[name]
        
    # "of" is the object factory: returns a link or a node from its name
    def of(self, name, _type):
        if _type == "node":
            return self.nf(name=name)
        else:
            return self.lf(name=name)
            
    def erase_network(self):
        self.graph.clear()
        for dict_of_objects in self.pn.values():
            dict_of_objects.clear()
            
    def remove_node(self, node):
        self.pn["node"].pop(node.name)
        # retrieve adj links to delete them 
        dict_of_adj_links = self.graph.pop(node, {})
        for type_link, adj_obj in dict_of_adj_links.items():
            for neighbor, adj_link in adj_obj:
                self.graph[neighbor][type_link].discard((node, adj_link))
                yield self.pn[type_link].pop(adj_link.name, None)
            
    def remove_link(self, link):
        self.graph[link.source][link.network_type].discard((link.destination, link))
        self.graph[link.destination][link.network_type].discard((link.source, link))
        self.pn[link.network_type].pop(link.name, None)
        
    def find_edge_nodes(self, AS):
        AS.pAS["edge"].clear()
        for node in AS.pAS["node"]:
            if any(
                   n not in AS.pAS["node"] 
                   for n, _ in self.graph[node]["trunk"]
                   ):
                AS.pAS["edge"].add(node)
                yield node
            
    def is_connected(self, nodeA, nodeB, link_type):
        return any(n == nodeA for n, _ in self.graph[nodeB][link_type])
        
    def number_of_links_between(self, nodeA, nodeB):
        return sum(
                   n == nodeB 
                   for _type in self.link_type 
                   for n, _ in self.graph[nodeA][_type]
                   )
        
    def links_between(self, nodeA, nodeB, _type="all"):
        if _type == "all":
            for link_type in self.link_type:
                for neighbor, trunk in self.graph[nodeA][link_type]:
                    if neighbor == nodeB:
                        yield trunk
        else:
            for neighbor, trunk in self.graph[nodeA][_type]:
                if neighbor == nodeB:
                    yield trunk
            
    def calculate_all(self):
        # reset the traffic for all trunks
        for trunk in self.pn["trunk"].values():
            trunk.trafficSD = trunk.trafficDS = 0.
            trunk.wctrafficSD = trunk.wctrafficDS = 0.
            
        # remove all link in failure, so that when we call "link dimensioning",
        # which in turns calls "failure traffic", the traffic is computed in
        # normal mode, without considering any existing failure
        self.scenario.remove_failures()
        
        for AS in self.pnAS.values():
            # for all OSPF and IS-IS AS, fill the ABR/L1L2 sets
            # update link area based on nodes area (ISIS) and vice-versa (OSPF)
            AS.management.update_AS_topology()
            # create all AS routes
            AS.management.create_routes()
        # we reset the traffic for all routes and for routes that do not 
        # belong to an AS, we find a path based on the route constraints (~CSPF) 
        for route in self.pn["route"].values():
            route.traffic = 0.
            if not route.AS:
                route_param = (
                               route.source, 
                               route.destination, 
                               route.excluded_trunks,
                               route.excluded_nodes, 
                               route.path_constraints
                               )
                _, route_path = self.A_star(*route_param)
                route.path = route_path

        # for traffic link, we use a BGP-like routing to restraint the routing
        # path to routes when crossing an AS
        for traffic_link in self.pn["traffic"].values():
            _, traffic_link.path = self.traffic_routing(traffic_link)
            if not traffic_link.path:
                print("no path found for {}".format(traffic_link))
            # compute the traffic going over the routes and trunks. 
            # trunks are bidirectionnal while routes and traffic link aren't.
            # Starting from the source of the traffic link, we keep in memory
            # the previous node, which indicates us the direction of the traffic
            prec_node = traffic_link.source
            for link in traffic_link.path:
                sd = (link.source == prec_node)*"SD" or "DS"
                # if the link is a trunk, we add the traffic throughput in
                # the appropriate direction, if it is a route, there is only one
                # direction given that routes are unidirectional.
                # the trunks on which the route is mapped will be dimensioned
                # in the AS dimensioning step that follows
                if link.network_type == "trunk":
                    link.__dict__["traffic" + sd] += traffic_link.throughput
                else:
                    link.__dict__["traffic"] += traffic_link.throughput
                # update of the previous node
                prec_node = link.source if sd == "DS" else link.destination
                
        for AS in self.pnAS.values():
            # we dimension the trunks of all AS routes 
            AS.management.link_dimensioning()
        self.ip_allocation()
        self.interface_allocation()
        self.scenario.refresh_all_labels()
        
    def ip_allocation(self):
        # we use 10.0.0.0/8 to allocate IP addresses for all interfaces in
        # an AS. we use the format 10.x.y.z where
        # - x defines the autonomous system
        # - y defines the area in that autonomous
        # - z defines the network device in that area
        address = "10.0.0."
        # we use a /30 subnet mask for all trunks
        mask = "255.255.255.252"
        for id_AS, AS in enumerate(self.pnAS.values()):
            for id_area, area in enumerate(AS.areas.values()):
                address = "10.{AS}.{area}.".format(AS=id_AS, area=id_area)
                cpt_ip = 1
                for id_trunk, trunk in enumerate(area.pa["trunk"]):
                    trunk.subnetmaskS = trunk.subnetmaskD = mask
                    trunk.ipaddressS = address + str(cpt_ip)
                    trunk.ipaddressD = address + str(cpt_ip + 1)
                    # with /30, there are two unused IP address for each subnetwork
                    # we could use /31 but this isn't a common practice
                    cpt_ip += 4
        
        # we use 192.168.0.0/16 to allocate loopback addresses to all routers
        ftr_router = lambda r: r.subtype == "router"
        for id, router in enumerate(filter(ftr_router, self.pn["node"].values()), 1):
            router.ipaddress = "192.168." + str(id // 255) + "." + str(id % 255)
            
        # finally, we use 172.16.0.0/16 for all trunks that do not belong
        # to an AS
        no_AS = lambda t: not t.AS
        cpt_ip, address = 1, "172.16.0."
        for trunk in filter(no_AS, self.pn["trunk"].values()):
            trunk.subnetmaskS = trunk.subnetmaskD = mask
            trunk.ipaddressS = address + str(cpt_ip)
            trunk.ipaddressD = address + str(cpt_ip + 1)
            cpt_ip += 4
                

    def interface_allocation(self):
        for node in self.graph:
            index_interface = 0
            for _, adj_trunk in self.graph[node]["trunk"]:
                direction = "S"*(adj_trunk.source == node) or "D"
                interface = "Ethernet0/{}".format(index_interface)
                setattr(adj_trunk, "interface" + direction, interface)
                index_interface += 1
            
    def bfs(self, source):
        visited = set()
        layer = {source}
        while layer:
            temp = layer
            layer = set()
            for node in temp:
                if node not in visited:
                    visited.add(node)
                    for neighbor, _ in self.graph[node]["trunk"]:
                        layer.add(neighbor)
                        yield neighbor
                    
    def connected_components(self):
        visited = set()
        for node in self.graph:
            if node not in visited:
                new_comp = set(self.bfs(node))
                visited.update(new_comp)
                yield new_comp
                
    ## Shortest path(s) algorithms
        
    ## 1) A* algorithm for CSPF modelization
            
    def A_star(
               self, 
               source, 
               target, 
               excluded_trunks = None, 
               excluded_nodes = None, 
               path_constraints = None, 
               allowed_trunks = None, 
               allowed_nodes = None
               ):
                
        # initialize parameters
        if excluded_nodes is None:
            excluded_nodes = set()
        if excluded_trunks is None:
            excluded_trunks = set()
        if path_constraints is None:
            path_constraints = list()
        if allowed_trunks is None:
            allowed_trunks = set(self.pn["trunk"].values())
        if allowed_nodes is None:
            allowed_nodes = set(self.pn["node"].values())
            
        pc = [target] + path_constraints[::-1]
        visited = set()
        heap = [(0, source, [], pc)]
        while heap:
            dist, node, path, pc = heappop(heap)  
            if node not in visited:
                visited.add(node)
                if node == pc[-1]:
                    visited.clear()
                    heap.clear()
                    pc.pop()
                    if not pc:
                        return [], path
                for neighbor, adj_trunk in self.graph[node]["trunk"]:
                    sd = (node == adj_trunk.source)*"SD" or "DS"
                    # excluded and allowed nodes
                    if neighbor not in allowed_nodes-excluded_nodes: 
                        continue
                    # excluded and allowed trunks
                    if adj_trunk not in allowed_trunks-excluded_trunks: 
                        continue
                    cost = getattr(adj_trunk, "cost" + sd)
                    heappush(heap, (dist + cost, neighbor, path + [adj_trunk], pc))
        return [], []
        
    ## 2) RIP routing algorithm
    
    def RIP_routing(self, source, target, RIP_AS, a_n=None, a_t=None):
        
        if a_n is None:
            a_n = RIP_AS.pAS["node"]
        if a_t is None:
            a_t = RIP_AS.pAS["trunk"]
                    
        return self.A_star(
                             source, 
                             target, 
                             allowed_nodes = a_n,
                             allowed_trunks = a_t
                             )
        
    ## 2) IS-IS routing algorithm 
        
    def ISIS_routing(self, source, target, ISIS_AS, a_n=None, a_t=None):
        
        if a_n is None:
            a_n = ISIS_AS.pAS["node"]
        if a_t is None:
            a_t = ISIS_AS.pAS["trunk"]
        
        source_area, target_area = None, None
        backbone = ISIS_AS.areas["Backbone"]
        source_area ,= source.AS[ISIS_AS]
        target_area ,= target.AS[ISIS_AS]
        
        # step indicates what we have to do:
        # if step is False, it means we are in the source area, heading 
        # for the backbone. The traffic will be routed to the closest L1/L2
        # router of the source area.
        # if step is True, it means we are in the backbone or the target area, 
        # heading to the destination edge via the shortest path.
        step = source_area in (backbone, target_area)
        
        # when heading for the destination, we are allowed to use only nodes
        # that belong to the backbone or to the destination area
        allowed = backbone.pa["node"] | target_area.pa["node"]
        
        visited = set()
        heap = [(0, source, [])]
        while heap:
            dist, node, path = heappop(heap)  
            if node not in visited:
                visited.add(node)
                if node == target:
                    return [], path
                if not step and node in ISIS_AS.border_routers:
                    step = True
                    heap.clear()
                for neighbor, adj_trunk in self.graph[node]["trunk"]:
                    sd = (node == adj_trunk.source)*"SD" or "DS"
                    # we ignore what's not allowed (not in the AS or in failure)
                    if neighbor not in a_n or adj_trunk not in a_t:
                        continue
                    # if step is False, we use only L1 or L1/L2 nodes that 
                    # belong to the source area
                    if not step and neighbor not in source_area.pa["node"]: 
                        continue
                    # else, we use only backbone nodes (L1/L2 or L2) or nodes
                    # that belong to the destination area
                    if step and neighbor not in allowed: 
                        continue
                    cost = getattr(adj_trunk, "cost" + sd)
                    heappush(heap, (dist + cost, neighbor, path + [adj_trunk]))
        return [], []
            
    ## OSPF routing algorithm
    
    def OSPF_routing(self, source, target, OSPF_AS, a_n=None, a_t=None):
        
        if a_n is None:
            a_n = OSPF_AS.pAS["node"]
        if a_t is None:
            a_t = OSPF_AS.pAS["trunk"]
        
        source_area = target_area = None
        backbone = OSPF_AS.areas["Backbone"]
        
        # if source has more than one area, it is a L1/L2 node
        # which means it is in the backbone
        if len(source.AS[OSPF_AS]) > 1:
            source_area = backbone
        # else, it has only one area, which we retrieve
        else:
            source_area ,= source.AS[OSPF_AS]
            
        # same for target
        if len(target.AS[OSPF_AS]) > 1:
            target_area = backbone
        else:
            target_area ,= target.AS[OSPF_AS]
            
        # step indicates in which area we are, which tells us which links 
        # can/cannot be used. 
        # If step is 0, we are in the source area, heading to the backbone. 
        # If step is 1, we are in the backbone, heading to the destination area.
        # If step is 2, we are in the destination area, heading to the exit edge.
        # Because of OSPF intra-area priority, we cannot use links that belong
        # to the source area once we've reached the backbone, and we cannot 
        # use links from the backbone once we've reached the destination
        # area.
        step = 2*(source_area == target_area) or source_area == backbone

        visited = set()
        heap = [(0, source, [], step)]
        while heap:
            dist, node, path, step = heappop(heap)
            if (node, step) not in visited:
                visited.add((node, step))
                if node == target:
                    return [], path
                # in case an ABR is connected to both the source and the target 
                # area, step will be incremented straigth from 0 to 2 since the
                # ABR also belongs to the backbone.
                # that's why we need to break the condition into 2 conditions
                if not step and backbone in node.AS[OSPF_AS]:
                    step += 1
                if step == 1 and target_area in node.AS[OSPF_AS]:
                    step += 1
                for neighbor, adj_trunk in self.graph[node]["trunk"]:
                    sd = (node == adj_trunk.source)*"SD" or "DS"
                    # we ignore what's not allowed (not in the AS or in failure)
                    if neighbor not in a_n or adj_trunk not in a_t:
                        continue
                    # if step is 0, we can only use links of the source area
                    if not step and adj_trunk not in source_area.pa["trunk"]: 
                        continue
                    # else if step is 1, we can only use links of the backbone
                    if step == 1 and adj_trunk not in backbone.pa["trunk"]: 
                        continue
                    # else if step is 2, we can only use links of the target area
                    if step == 2 and adj_trunk not in target_area.pa["trunk"]: 
                        continue
                    # here, it is very important not to reuse an existing 
                    # variable like dist or path (for instance by appending
                    # adj_trunk to path before pushing it to the binary heap)
                    # as it would mess the whole thing up.
                    cost = getattr(adj_trunk, "cost" + sd)
                    heappush(heap, (dist + cost, neighbor, path + [adj_trunk], step))
        return [], []
        
    def protection_routing(self, normal_path, algorithm, failed_link):
        pass
            
    ## 3) Traffic routing algorithm
    
    def traffic_routing(self, traffic_link):
        
        source, target = traffic_link.source, traffic_link.destination
        visited = set()
        heap = [(0, source, [])]
        # we count how many AS we cross in case of ECMP AS path, to keep the 
        # shortest in terms of AS
        while heap:
            dist, node, path = heappop(heap)  
            if node not in visited:
                visited.add(node)
                if node == target:
                    return [], path
                adj_links = self.graph[node]["trunk"] | self.graph[node]["route"]
                for neighbor, adj_link in adj_links:
                    sd = (node == adj_link.source)*"SD" or "DS"
                    # if the link is a trunk and belongs to an AS,  
                    # we ignore it because we use only AS's routes
                    if adj_link.type == "trunk" and adj_link.AS: 
                        continue
                    # if the link is a route, we make sure the current node is 
                    # the source of the route, because routes are unidirectionnal
                    if adj_link.type == "route" and adj_link.source != node: 
                        continue
                    # if the link is a route, it is unidirectional and the
                    # property is simply cost, but if it is a trunk, there are
                    # one cost per direction and we retrieve the right one
                    cost = "cost"*(adj_link.type == "route") or "cost" + sd 
                    dist += getattr(adj_link, cost)
                    heappush(heap, (dist, neighbor, path + [adj_link]))
            
    ## 4) Bellman-Ford algorithm
        
    def bellman_ford(
                     self, 
                     source, 
                     target, 
                     excluded_trunks = None, 
                     excluded_nodes = None, 
                     allowed_trunks = None, 
                     allowed_nodes = None
                     ):
        
        # initialize parameters
        if excluded_nodes is None:
            excluded_nodes = set()
        if excluded_trunks is None:
            excluded_trunks = set()
        if allowed_trunks is None:
            allowed_trunks = set(self.pn["trunk"].values())
        if allowed_nodes is None:
            allowed_nodes = set(self.pn["node"].values())

        n = len(allowed_nodes)
        prec_node = {i: None for i in allowed_nodes}
        prec_link = {i: None for i in allowed_nodes}
        dist = {i: float("inf") for i in allowed_nodes}
        dist[source] = 0
        
        for i in range(n+2):
            negative_cycle = False
            for node in allowed_nodes:
                for neighbor, adj_trunk in self.graph[node]["trunk"]:
                    sd = (node == adj_trunk.source)*"SD" or "DS"
                    # excluded and allowed nodes
                    if neighbor not in allowed_nodes-excluded_nodes: 
                        continue
                    # excluded and allowed trunks
                    if adj_trunk not in allowed_trunks-excluded_trunks: 
                        continue
                    dist_neighbor = dist[node] + getattr(adj_trunk, "cost" + sd)
                    if dist_neighbor < dist[neighbor]:
                        dist[neighbor] = dist_neighbor
                        prec_node[neighbor] = node
                        prec_link[neighbor] = adj_trunk
                        negative_cycle = True
                        
        # traceback the path from target to source
        if dist[target] != float("inf"):
            curr, path_node, path_link = target, [target], [prec_link[target]]
            while curr != source:
                curr = prec_node[curr]
                path_link.append(prec_link[curr])
                path_node.append(curr)
            return path_node[::-1], path_link[:-1][::-1]
        else:
            return [], []
            
    ## 5) Floyd-Warshall algorithm
            
    def floyd_warshall(self):
        nodes = list(self.pn["node"].values())
        n = len(nodes)
        W = [[0]*n for _ in range(n)]
        
        for id1, n1 in enumerate(nodes):
            for id2, n2 in enumerate(nodes):
                if id1 != id2:
                    for neighbor, trunk in self.graph[n1]["trunk"]:
                        if neighbor == n2:
                            W[id1][id2] = trunk.costSD
                            break
                    else:
                        W[id1][id2] = float("inf")
                        
        for k in range(n):
            for u in range(n):
                for v in range(n):
                    W[u][v] = min(W[u][v], W[u][k] + W[k][v])
                    
        if any(W[v][v] < 0 for v in range(n)):
            return False
        else:
            all_length = defaultdict(dict)
            for id1, n1 in enumerate(nodes):
                for id2, n2 in enumerate(nodes):
                    all_length[n1][n2] = W[id1][id2]
                    
        return all_length  
        
    ## 6) DFS (all loop-free paths)
        
    def all_paths(self, source, target=None):
        # generates all loop-free paths from source to optional target
        path = [source]
        seen = {source}
        def find_all_paths():
            dead_end = True
            node = path[-1]
            if node == target:
                yield list(path)
            else:
                for neighbor, adj_trunk in self.graph[node]["trunk"]:
                    if neighbor not in seen:
                        dead_end = False
                        seen.add(neighbor)
                        path.append(neighbor)
                        yield from find_all_paths()
                        path.pop()
                        seen.remove(neighbor)
            if not target and dead_end:
                yield list(path)
        yield from find_all_paths()
        
    ## Link-disjoint / link-and-node-disjoint shortest pair algorithms
    
    ## 1) A* link-disjoint pair search
    
    def A_star_shortest_pair(self, source, target, a_n=None, a_t=None):
        # To find the shortest pair from the source to the target, we look
        # for the shortest path going from the source to the source, with 
        # the target as a "path constraint".
        # Each path is stored with sets of allowed nodes and trunks that will 
        # contains what belongs to the first path, once we've reached the target.
        
        # if a_n is None:
        #     a_n = AS.pAS["node"]
        # if a_t is None:
        #     a_t = AS.pAS["trunk"]
        
        if a_t is None:
            a_t = set(self.pn["trunk"].values())
        if a_n is None:
            a_n = set(self.pn["node"].values())

        visited = set()
        # in the heap, we store e_o, the list of excluded objects, which is
        # empty until we reach the target.
        heap = [(0, source, [], set())]
        while heap:
            dist, node, path_trunk, e_o = heappop(heap)  
            if (node, tuple(path_trunk)) not in visited:
                visited.add((node, tuple(path_trunk)))
                if node == target:
                    e_o = set(path_trunk)
                if node == source and e_o:
                    return [], path_trunk
                for neighbor, adj_trunk in self.graph[node]["trunk"]:
                    sd = (node == adj_trunk.source)*"SD" or "DS"
                    # we ignore what's not allowed (not in the AS or in failure
                    # or in the path we've used to reach the target)
                    if neighbor not in a_n or adj_trunk not in a_t-e_o:
                        continue
                    cost = getattr(adj_trunk, "cost" + sd)
                    heappush(heap, (dist + cost, neighbor, path_trunk + [adj_trunk], e_o))
        return [], []
        
    ## Flow algorithms
    
    def reset_flow(self):
        for link in self.pn["trunk"].values():
            link.flowSD = link.flowDS = 0
    
    ## 1) Ford-Fulkerson algorithm
        
    def augment_ff(self, val, curr_node, target, visit):
        visit[curr_node] = True
        if curr_node == target:
            return val
        for neighbor, adj_link in self.graph[curr_node]["trunk"]:
            direction = curr_node == adj_link.source
            sd, ds = direction*"SD" or "DS", direction*"DS" or "SD"
            cap = getattr(adj_link, "capacity" + sd)
            current_flow = getattr(adj_link, "flow" + sd)
            if cap > current_flow and not visit[neighbor]:
                residual_capacity = min(val, cap - current_flow)
                global_flow = self.augment_ff(
                                              residual_capacity, 
                                              neighbor, 
                                              target, 
                                              visit
                                              )
                if global_flow > 0:
                    adj_link.__dict__["flow" + sd] += global_flow
                    adj_link.__dict__["flow" + ds] -= global_flow
                    return global_flow
        return False
        
    def ford_fulkerson(self, s, d):
        self.reset_flow()
        while self.augment_ff(float("inf"), s, d, {n:0 for n in self.graph}):
            pass
        # flow leaving from the source 
        return sum(
                  getattr(adj, "flow" + (s==adj.source)*"SD" or "DS") 
                  for _, adj in self.graph[s]["trunk"]
                  )
        
    ## 2) Edmonds-Karp algorithm
        
    def augment_ek(self, source, destination):
        res_cap = {n:0 for n in self.graph}
        augmenting_path = {n: None for n in self.graph}
        Q = deque()
        Q.append(source)
        augmenting_path[source] = source
        res_cap[source] = float("inf")
        while Q:
            curr_node = Q.popleft()
            for neighbor, adj_link in self.graph[curr_node]["trunk"]:
                direction = curr_node == adj_link.source
                sd, ds = direction*"SD" or "DS", direction*"DS" or "SD"
                cap = getattr(adj_link, "capacity" + sd)
                flow = getattr(adj_link, "flow" + sd)
                residual = cap - flow
                if residual and augmenting_path[neighbor] is None:
                    augmenting_path[neighbor] = curr_node
                    res_cap[neighbor] = min(res_cap[curr_node], residual)
                    if neighbor == destination:
                        break
                    else:
                        Q.append(neighbor)
        return augmenting_path, res_cap[destination]
        
    def edmonds_karp(self, source, destination):
        self.reset_flow()
        while True:
            augmenting_path, global_flow = self.augment_ek(source, destination)
            if not global_flow:
                break
            curr_node = destination
            while curr_node != source:
                # find the trunk between the two nodes
                prec_node = augmenting_path[curr_node]
                find_trunk = lambda p: getitem(p, 0) == prec_node
                (_, trunk) ,= filter(find_trunk, self.graph[curr_node]["trunk"])
                # define sd and ds depending on how the link is defined
                direction = curr_node == trunk.source
                sd, ds = direction*"SD" or "DS", direction*"DS" or "SD"
                trunk.__dict__["flow" + ds] += global_flow
                trunk.__dict__["flow" + sd] -= global_flow
                curr_node = prec_node 
        return sum(
                   getattr(adj, "flow" + ((source==adj.source)*"SD" or "DS")) 
                   for _, adj in self.graph[source]["trunk"]
                  )
        
    ## Minimum spanning tree algorithms 
    
    ## 1) Kruskal algorithm
        
    def kruskal(self, allowed_nodes):
        uf = miscellaneous.UnionFind(allowed_nodes)
        edges = []
        for node in allowed_nodes:
            for neighbor, adj_trunk in self.graph[node]["trunk"]:
                if neighbor in allowed_nodes:
                    edges.append((adj_trunk.costSD, adj_trunk, node, neighbor))
        for w, t, u, v in sorted(edges, key=itemgetter(0)):
            if uf.union(u, v):
                yield t
                
    ## Linear programming algorithms
    
    ## 1) Shortest path
    
    def LP_SP_formulation(self, s, t):
        """
        Solves the MILP: minimize c'*x
                subject to G*x + s = h
                            A*x = b
                            s >= 0
                            xi integer, forall i in I
        """
        
        self.reset_flow()
        
        new_graph = {node: {} for node in self.graph}
        for node in self.graph:
            for neighbor, trunk in self.graph[node]["trunk"]:
                sd = (node == trunk.source)*"SD" or "DS"
                new_graph[node][neighbor] = getattr(trunk, "cost" + sd)

        n = 2*len(self.pn["trunk"])
        v = len(new_graph)
        c = []

        for node in new_graph:
            for neighbor, cost in new_graph[node].items():
                # the float conversion is ESSENTIAL !
                # I first forgot it, then spent hours trying to understand 
                # what was wrong. If "c" is not made of float, no explicit 
                # error is raised, but the result is sort of random !
                c.append(float(cost))
                
        # for the condition 0 < x_ij < 1
        h = numpy.concatenate([numpy.ones(n), numpy.zeros(n)])
        id = numpy.eye(n, n)
        G = numpy.concatenate((id, -1*id), axis=0).tolist()  
        
        # flow conservation: Ax = b
        A, b = [], []
        for node_r in new_graph:
            if node_r != t:
                b.append(float(node_r == s))
                row = []
                for node in new_graph:
                    for neighbor in new_graph[node]:
                        row.append(
                                   -1. if neighbor == node_r 
                              else  1. if node == node_r 
                              else  0.
                                   )
                A.append(row)
        
        A, G, b, c, h = map(matrix, (A, G, b, c, h))
        solsta, x = glpk.ilp(c, G.T, h, A.T, b)
        
        # update the resulting flow for each node
        cpt = 0
        for node in new_graph:
            for neighbor in new_graph[node]:
                new_graph[node][neighbor] = x[cpt]
                cpt += 1
                
        # update the network trunks with the new flow value
        for trunk in self.pn["trunk"].values():
            src, dest = trunk.source, trunk.destination
            trunk.flowSD = new_graph[src][dest]
            trunk.flowDS = new_graph[dest][src]
            
        return sum(x)
    
    ## 2) Single-source single-destination maximum flow
               
    def LP_MF_formulation(self, s, t):
        """
        Solves the MILP: minimize c'*x
                subject to G*x + s = h
                            A*x = b
                            s >= 0
                            xi integer, forall i in I
        """
        
        new_graph = {node: {} for node in self.graph}
        for node in self.graph:
            for neighbor, trunk in self.graph[node]["trunk"]:
                sd = (node == trunk.source)*"SD" or "DS"
                new_graph[node][neighbor] = getattr(trunk, "capacity" + sd)

        n = 2*len(self.pn["trunk"])
        v = len(new_graph)

        c, h = [], []
        for node in new_graph:
            for neighbor, capacity in new_graph[node].items():
                c.append(float(node == s))
                h.append(float(capacity))
                
        # flow conservation: Ax = b
        A = []
        for node_r in new_graph:
            if node_r not in (s, t):
                row = []
                for node in new_graph:
                    for neighbor in new_graph[node]:
                        row.append(
                                   1. if neighbor == node_r 
                             else -1. if node == node_r 
                              else 0.
                                   )
                A.append(row)
                
        b, h, x = [0.]*(v-2), h+[0.]*n, numpy.eye(n, n)
        G = numpy.concatenate((x, -1*x), axis=0).tolist()        
        A, G, b, c, h = map(matrix, (A, G, b, c, h))
        solsta, x = glpk.ilp(-c, G.T, h, A.T, b)

        # update the resulting flow for each node
        cpt = 0
        for node in new_graph:
            for neighbor in new_graph[node]:
                new_graph[node][neighbor] = x[cpt]
                cpt += 1
                
        # update the network trunks with the new flow value
        for trunk in self.pn["trunk"].values():
            src, dest = trunk.source, trunk.destination
            trunk.flowSD = new_graph[src][dest]
            trunk.flowDS = new_graph[dest][src]

        return sum(
                   getattr(adj, "flow" + ((s==adj.source)*"SD" or "DS")) 
                   for _, adj in self.graph[s]["trunk"]
                   )
                   
    ## 3) Single-source single-destination minimum-cost flow
               
    def LP_MCF_formulation(self, s, t, flow):
        """
        Solves the MILP: minimize c'*x
                subject to G*x + s = h
                            A*x = b
                            s >= 0
                            xi integer, forall i in I
        """
        
        new_graph = {node: {} for node in self.graph}
        for node in self.graph:
            for neighbor, trunk in self.graph[node]["trunk"]:
                sd = (node == trunk.source)*"SD" or "DS"
                new_graph[node][neighbor] = (getattr(trunk, "capacity" + sd),
                                             getattr(trunk, "cost" + sd))

        n = 2*len(self.pn["trunk"])
        v = len(new_graph)

        c, h = [], []
        for node in new_graph:
            for neighbor, (capacity, cost) in new_graph[node].items():
                c.append(float(cost))
                h.append(float(capacity))
                
        # flow conservation: Ax = b
        A, b = [], []
        for node_r in new_graph:
            if node_r != t:
                b.append(flow * float(node_r == s))
                row = []
                for node in new_graph:
                    for neighbor in new_graph[node]:
                        row.append(
                                   -1. if neighbor == node_r 
                              else  1. if node == node_r 
                              else  0.
                                   )
                A.append(row)
                
        h, x = h+[0.]*n, numpy.eye(n, n)
        G = numpy.concatenate((x, -1*x), axis=0).tolist()        
        A, G, b, c, h = map(matrix, (A, G, b, c, h))
        solsta, x = glpk.ilp(c, G.T, h, A.T, b)

        # update the resulting flow for each node
        cpt = 0
        for node in new_graph:
            for neighbor in new_graph[node]:
                new_graph[node][neighbor] = x[cpt]
                cpt += 1
                
        # update the network trunks with the new flow value
        for trunk in self.pn["trunk"].values():
            src, dest = trunk.source, trunk.destination
            trunk.flowSD = new_graph[src][dest]
            trunk.flowDS = new_graph[dest][src]

        return sum(
                   getattr(adj, "flow" + ((s==adj.source)*"SD" or "DS")) 
                   for _, adj in self.graph[s]["trunk"]
                   )
            
    ## Distance functions
    
    def distance(self, p, q): 
        return sqrt(p*p + q*q)
        
    def haversine_distance(self, s, d):
        """ Earth distance between two nodes """
        coord = (s.longitude, s.latitude, d.longitude, d.latitude)
        # decimal degrees to radians conversion
        lon_s, lat_s, lon_d, lat_d = map(radians, coord)
    
        delta_lon = lon_d - lon_s 
        delta_lat = lat_d - lat_s 
        a = sin(delta_lat/2)**2 + cos(lat_s)*cos(lat_d)*sin(delta_lon/2)**2
        c = 2*asin(sqrt(a)) 
        # radius of earth (km)
        r = 6371 
        return c*r
 
    ## Force-directed layout algorithms
    
    ## 1) Eades algorithm 
    
    # We use the following constants:
    # - k is the spring constant (stiffness of the spring)
    # - L0 is the equilibrium length
    
    def coulomb_force(self, dx, dy, dist, beta):
        c = dist and beta/dist**3
        return (-c*dx, -c*dy)
        
    def hooke_force(self, dx, dy, dist, L0, k):
        const = k*(dist - L0)/dist
        return (const*dx, const*dy)
            
    def spring_layout(self, nodes, alpha, beta, k, eta, delta, L0):
        for nodeA in nodes:
            Fx = Fy = 0
            for nodeB in nodes:
                if nodeA != nodeB:
                    dx, dy = nodeB.x - nodeA.x, nodeB.y - nodeA.y
                    dist = self.distance(dx, dy)
                    F_hooke = (0,)*2
                    if self.is_connected(nodeA, nodeB, "trunk"):
                        F_hooke = self.hooke_force(dx, dy, dist, L0, k) 
                    F_coulomb = self.coulomb_force(dx, dy, dist, beta)
                    Fx += F_hooke[0] + F_coulomb[0]
                    Fy += F_hooke[1] + F_coulomb[1]
            nodeA.vx = (nodeA.vx + alpha * Fx) * eta
            nodeA.vy = (nodeA.vy + alpha * Fy) * eta
    
        for node in nodes:
            node.x += round(node.vx*delta)
            node.y += round(node.vy*delta)
            
    ## 2) Fruchterman-Reingold algorithms
    
    def fa(self, d, k):
        return (d**2)/k
    
    def fr(self, d, k):
        return -(k**2)/d
        
    def fruchterman_reingold_layout(self, nodes, opd, limit):
        t = 1
        if not opd:
            opd = sqrt(1200*700/len(self.pn["trunk"]))
        opd /= 3
        for nA in nodes:
            nA.vx, nA.vy = 0, 0
            for nB in nodes:
                if nA != nB:
                    deltax = nA.x - nB.x
                    deltay = nA.y - nB.y
                    dist = self.distance(deltax, deltay)
                    if dist:
                        nA.vx += deltax*(opd**2)/dist**2
                        nA.vy += deltay*(opd**2)/dist**2                        
                    
        for l in self.pn["trunk"].values():
            deltax = l.source.x - l.destination.x
            deltay = l.source.y - l.destination.y
            dist = self.distance(deltax, deltay)
            if dist:
                l.source.vx -= dist*deltax/opd
                l.source.vy -= dist*deltay/opd
                l.destination.vx += dist*deltax/opd
                l.destination.vy += dist*deltay/opd
            
        for n in nodes:
            d = self.distance(n.vx, n.vy)
            n.x += (n.vx)/(sqrt(d))
            n.y += (n.vy)/(sqrt(d))
            if limit:
                n.x = min(800, max(0, n.x))
                n.y = min(800, max(0, n.y))
            
        t *= 0.90
        
    ## Graph generation functions
    
    ## 1) Hypercube generation
            
    def generate_hypercube(self, n, _type):
        # we create a n-dim hypercube by connecting two (n-1)-dim hypercubes
        i = 0
        graph_nodes = [self.nf(name=str(0), node_type=_type)]
        graph_links = []
        while i < n+1:
            for k in range(len(graph_nodes)):
                # creation of the nodes of the second hypercube
                graph_nodes.append(self.nf(name=str(k+2**i), node_type=_type))
            for trunk in graph_links[:]:
                # connection of the two hypercubes
                source, destination = trunk.source, trunk.destination
                n1, n2 = str(int(source.name)+2**i), str(int(destination.name)+2**i)
                graph_links.append(self.lf(s=self.nf(n1), d=self.nf(n2)))
            for k in range(len(graph_nodes)//2):
                # creation of the links of the second hypercube
                graph_links.append(self.lf(s=graph_nodes[k], d=graph_nodes[k+2**i]))
            i += 1
            
    ## 2) Square tiling generation
            
    def generate_square_tiling(self, n, subtype):
        for i in range(n**2):
            n1, n2, n3 = str(i), str(i-1), str(i+n)
            if i-1 > -1 and i%n:
                self.lf(
                        s=self.nf(name=n1, node_type=subtype), 
                        d=self.nf(name=n2, node_type=subtype)
                        )
            if i+n < n**2:
                self.lf(
                        s=self.nf(name=n1, node_type=subtype), 
                        d=self.nf(name=n3, node_type=subtype)
                        )
                
    ## 3) Tree generation
                
    def generate_tree(self, n, subtype):
        for i in range(2**n-1):
            n1, n2, n3 = str(i), str(2*i+1), str(2*i+2)
            self.lf(
                    s=self.nf(name=n1, node_type=subtype), 
                    d=self.nf(name=n2, node_type=subtype)
                    )
            self.lf(
                    s=self.nf(name=n1, node_type=subtype), 
                    d=self.nf(name=n3, node_type=subtype)
                    )
            
    ## 4) Star generation
            
    def generate_star(self, n, subtype):
        nb_node = len(self.pn["node"])
        for i in range(n):
            n1, n2 = str(nb_node), str(nb_node+1+i)
            self.lf(
                    s=self.nf(name=n1, node_type=subtype), 
                    d=self.nf(name=n2, node_type=subtype)
                    )
            
    ## 5) Full-meshed network generation
            
    def generate_full_mesh(self, n, subtype):
        nb_node = len(self.pn["node"])
        for i in range(n):
            for j in range(i):
                n1, n2 = str(nb_node+j), str(nb_node+i)
                self.lf(
                        s=self.nf(name=n1, node_type=subtype), 
                        d=self.nf(name=n2, node_type=subtype)
                        )
                
    ## 6) Ring generation
                
    def generate_ring(self, n, subtype):
        nb_node = len(self.pn["node"])
        for i in range(n):
            n1, n2 = str(nb_node+i), str(nb_node+(1+i)%n)
            self.lf(
                    s=self.nf(name=n1, node_type=subtype), 
                    d=self.nf(name=n2, node_type=subtype)
                    )
            
            