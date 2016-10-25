# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import objects
from autonomous_system import AS
from objects import objects
import random
import warnings
import tkinter as tk
from miscellaneous.network_functions import compute_network, ip_incrementer, tomask
from math import cos, sin, asin, radians, sqrt, ceil, log
from collections import defaultdict, deque, OrderedDict
from heapq import heappop, heappush, nsmallest
from operator import getitem, itemgetter
from itertools import combinations
from miscellaneous.union_find import UnionFind
try:
    import numpy as np
    from cvxopt import matrix, glpk, solvers
except ImportError:
    warnings.warn('Package missing: linear programming functions will fail')

class Network(object):
    
    # Ordered to keep the order when using the keys 
    node_class = OrderedDict([
    ('router', objects.Router),
    ('oxc', objects.OXC),
    ('host', objects.Host),
    ('antenna', objects.Antenna),
    ('regenerator', objects.Regenerator),
    ('splitter', objects.Splitter),
    ('switch', objects.Switch),
    ('cloud', objects.Cloud)
    ])
    
    VC_class = OrderedDict([
    ('l2vc', objects.L2VC),
    ('l3vc', objects.L3VC)
    ])
    
    trunk_class = OrderedDict([
    ('ethernet', objects.Ethernet),
    ('wdm', objects.WDMFiber)
    ])
    
    route_class = OrderedDict([
    ('static route', objects.StaticRoute),
    ('BGP peering', objects.BGPPeering),
    ('OSPF virtual link', objects.VirtualLink),
    ('Label Switched Path', objects.LSP)
    ])
    
    traffic_class = OrderedDict([
    ('routed traffic', objects.RoutedTraffic),
    ('static traffic', objects.StaticTraffic)
    ])
    
    link_class = {}
    for dclass in (trunk_class, route_class, traffic_class, VC_class):
        link_class.update(dclass)
    
    node_subtype = tuple(node_class.keys())
    link_type = ('trunk', 'route', 'traffic', 'l2vc', 'l3vc')
    link_subtype = tuple(link_class.keys())
    all_subtypes = node_subtype + link_subtype
    
    def __init__(self, scenario):
        # pn for 'pool network'
        self.pn = {'trunk': {}, 'node': {}, 'route': {}, 'traffic': {}, 'l2vc':{}, 'l3vc':{}}
        self.pnAS = {}
        self.cs = scenario
        self.graph = defaultdict(lambda: defaultdict(set))
        self.cpt_link = self.cpt_node = self.cpt_AS = 1
        # useful for tests and listbox when we want to retrieve an object
        # based on its name. The only object that needs changing when a object
        # is renamed by the user.
        self.name_to_id = {}
        
        # dicts used for IP networks 
        # - associates a subnetwork to a set of IP addresses while the 
        # second one associate each IP to its subnet mask
        self.sntw_to_ip = defaultdict(set)
        # - associates an IP to its mask
        self.ip_to_mask = {}
        # - associates an IP to a node. when a default / static route is 
        # defined, only the next-hop ip is specified: we need to translate it 
        # into a next-hop node to properly fill the routing table.
        self.ip_to_node = {}
        # - finds all layer-n segments networks, i.e all layer-n-capable 
        # interfaces that communicate via a layer-(n-1) device
        self.ma_segments = defaultdict(set)
        # - associates a trunk to its L3 neighbors, different from 
        # the 'graph neighbor' which, in case of a multi-access network,
        # is a L2 device like a switch or a bridge.
        self.trunk_to_neighbor = defaultdict(set)
        
        # osi layer to devices
        self.osi_layers = {
        3: ('router', 'host', 'cloud'),
        2: ('switch', 'oxc'),
        1: ('regenerator', 'splitter', 'antenna')
        }
        
        # set of all trunks in failure: this parameter is used for
        # link dimensioning and failure simulation
        self.fdtks = set()
        
    # function filtering pn to retrieve all objects of given subtypes
    def ftr(self, type, *sts):
        keep = lambda r: r.subtype in sts
        return filter(keep, self.pn[type].values())
        
    # function filtering graph to retrieve all links of given subtypes
    # attached to the source node. 
    # if ud (undirected) is set to True, we retrieve all links of the 
    # corresponding subtypes, else we check that 'src' is the source
    def gftr(self, src, type, *sts, ud=True):
        keep = lambda r: r[1].subtype in sts and (ud or r[1].source == src)
        return filter(keep, self.graph[src][type])
        
    # function that retrieves all IP addresses attached to a node, including
    # it's loopback IP.
    def attached_ips(self, src):
        for _, trunk in self.graph[src]['trunk']:
            yield trunk('ipaddress', src)
        yield src.ipaddress
        
    # function that retrieves all next-hop IP addresses attached to a node, 
    # including the loopback addresses of its neighbors
    def nh_ips(self, src):
        for nb, trunk in self.graph[src]['trunk']:
            yield trunk('ipaddress', nb)
            yield nb.ipaddress
          
    # 'lf' is the link factory. Creates or retrieves any type of link
    def lf(
           self, 
           *param, 
           subtype = 'ethernet', 
           id = None,
           name = None, 
           s = None, 
           d = None
           ):
        link_type = self.cs.ms.st_to_type[subtype]
        print(name, id)
        # creation link in the s-d direction if no link at all yet
        if not id:
            print(name)
            if name in self.name_to_id:
                return self.pn[link_type][self.name_to_id[name]]
            if not name:
                name = link_type + str(self.cpt_link)
            print("test", name)
            id = self.cpt_link
            self.cpt_link += 1
            new_link = self.link_class[subtype](id, name, s, d, *param)
            self.name_to_id[name] = id
            self.pn[link_type][id] = new_link
            self.graph[s.id][link_type].add((d, new_link))
            self.graph[d.id][link_type].add((s, new_link))
        return self.pn[link_type][id]
        
    # 'nf' is the node factory. Creates or retrieves any type of nodes
    def nf(self, *p, node_type='router', name=None, id=None):
        if name in self.name_to_id:
            return self.pn['node'][self.name_to_id[name]]
        if not id:
            id = self.cpt_node
            if not name:
                name = 'node' + str(self.cpt_node)
            self.pn['node'][id] = self.node_class[node_type](self.cpt_node, name, *p)
            self.name_to_id[name] = id
            self.cpt_node += 1
        return self.pn['node'][id]
        
    def AS_factory(
                   self, 
                   name = None, 
                   _type = 'RIP',
                   id = 0,
                   trunks = set(), 
                   nodes = set(), 
                   edges = set(), 
                   routes = set(),
                   imp = False
                   ):
        if not name:
            name = 'AS' + str(self.cpt_AS)
        if name not in self.pnAS:
            # creation of the AS
            self.pnAS[name] = AS.AutonomousSystem(
                                                  self.cs, 
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
        
    # 'of' is the object factory: returns a link or a node from its name
    def of(self, name, _type):
        if _type == 'node':
            return self.nf(name=name)
        else:
            return self.lf(name=name)
            
    def erase_network(self):
        self.graph.clear()
        for dict_of_objects in self.pn.values():
            dict_of_objects.clear()
            
    def remove_node(self, node):
        self.pn['node'].pop(self.name_to_id.pop(node.name))
        # retrieve adj links to delete them 
        dict_of_adj_links = self.graph.pop(node.id, {})
        for type_link, adj_obj in dict_of_adj_links.items():
            for neighbor, adj_link in adj_obj:
                yield adj_link

    def remove_link(self, link):
        self.graph[link.source.id][link.type].discard((link.destination, link))
        self.graph[link.destination.id][link.type].discard((link.source, link))
        self.pn[link.type].pop(self.name_to_id.pop(link.name))
        
    def find_edge_nodes(self, AS):
        AS.pAS['edge'].clear()
        for node in AS.pAS['node']:
            if any(
                   n not in AS.pAS['node'] 
                   for n, _ in self.graph[node.id]['trunk']
                   ):
                AS.pAS['edge'].add(node)
                yield node
            
    def is_connected(self, nodeA, nodeB, link_type):
        return any(n == nodeA for n, _ in self.graph[nodeB.id][link_type])
        
    # given a node, retrieves nodes attached with a link which subtype 
    # is in sts
    def neighbors(self, node, *sts):
        for subtype in sts:
            for neighbor, _ in self.graph[node.id][subtype]:
                yield neighbor
        
    def number_of_links_between(self, nodeA, nodeB):
        return sum(
                   n == nodeB 
                   for _type in self.link_type 
                   for n, _ in self.graph[nodeA.id][_type]
                   )
        
    def links_between(self, nodeA, nodeB, _type='all'):
        if _type == 'all':
            for link_type in self.link_type:
                for neighbor, trunk in self.graph[nodeA.id][link_type]:
                    if neighbor == nodeB:
                        yield trunk
        else:
            for neighbor, trunk in self.graph[nodeA.id][_type]:
                if neighbor == nodeB:
                    yield trunk
                    
    def update_AS_topology(self):
        # update all BGP AS property of nodes in a BGP AS
        for AS in filter(lambda a: a.type == 'BGP', self.pnAS.values()):
            for node in AS.pAS['node']:
                node.bgp_AS = AS.name
                
        # update all BGP peering type based on the source and destination AS
        for bgp_pr in self.ftr('route', 'BGP peering'):
            same_AS = bgp_pr.source.bgp_AS == bgp_pr.destination.bgp_AS
            bgp_pr.bgp_type = 'iBGP' if same_AS else 'eBGP'
        
        for AS in self.pnAS.values():
            # for all OSPF and IS-IS AS, fill the ABR/L1L2 sets
            # update trunk area based on nodes area (ISIS) and vice-versa (OSPF)
            AS.management.update_AS_topology()
            
    def segment_finder(self, layer):
        # we associate a set of trunks to each layer-n segment.
        # at this point, there isn't any IP allocated yet: we cannot assign
        # IP addresses until we know the network layer-3 segment topology.
        # this topology will be stored in the network_to_trunk set.
        # we keep the set of all trunks we've already visited 
        visited_trunks = set()
        # we loop through all the layer-3-networks boundaries: routers.
        for router in self.ftr('node', *self.osi_layers[layer]):
            # we start by looking at all attached trunks, and when we find one
            # that hasn't been visited yet, we don't stop until we've discovered
            # all network's trunks (i.e until we've reached all boundaries 
            # of that networks: routers or host).
            for neighbor, trunk in self.graph[router.id]['trunk']:
                if trunk in visited_trunks:
                    continue
                visited_trunks.add(trunk)
                # we update the set of trunks of the network as we discover them
                current_network = {(trunk, router)}
                if any(neighbor.subtype in self.osi_layers[l] for l in range(1, layer)):
                    # we add the neighbor of the router in the stack: we'll fill 
                    # the stack with nodes as we discover them, provided that 
                    # these nodes are not boundaries, i.e not router or host
                    stack_network = [neighbor]
                    visited_nodes = {router}
                    while stack_network:
                        curr_node = stack_network.pop()
                        for node, adj_trunk in self.graph[curr_node.id]['trunk']:
                            if node in visited_nodes:
                                continue
                            visited_trunks.add(adj_trunk)
                            visited_nodes.add(node)
                            if any(node.subtype in self.osi_layers[l] for l in range(1, layer)):
                                stack_network.append(node)
                            else:
                                current_network.add((adj_trunk, node))
                else:
                    current_network.add((trunk, neighbor))
                self.ma_segments[layer].add(frozenset(current_network))
        
    def multi_access_network(self):
        # in order to create the routing table of an IP domain that 
        # contains multi-access networks, we need for each trunk to 
        # associate the list of neighbors, i.e the IP-capable devices
        # that are connected to the graph neighbor, a L2 device (switch, ...)
        for ma_network in self.ma_segments[3]:
            for source_trunk, node in ma_network:
                for destination_trunk, neighbor in ma_network - {(source_trunk, node)}:
                    #self.trunk_to_neighbor[trunk].add(neighbor)
                    if not self.is_connected(node, neighbor, 'l3vc'):
                        l3vc = self.lf(s=node, d=neighbor, subtype='l3vc')
                        l3vc("link", node, source_trunk)
                        l3vc("link", neighbor, destination_trunk)
                        self.cs.create_link(l3vc)
        for ma_network in self.ma_segments[2]:
            for source_trunk, node in ma_network:
                for destination_trunk, neighbor in ma_network - {(source_trunk, node)}:
                    if not self.is_connected(node, neighbor, 'l2vc'):
                        l2vc = self.lf(s=node, d=neighbor, subtype='l2vc')
                        l2vc("link", node, source_trunk)
                        l2vc("link", neighbor, destination_trunk)
                        self.cs.create_link(l2vc)
    
    def ip_allocation(self):
        # we will perform the IP addressing of all subnetworks with VLSM
        # we first sort all subnetworks in increasing order of size, then
        # compute which subnet is needed
        sntws = sorted(list(self.ma_segments[3]), key=len)
        sntw_ip = '10.0.0.0'
        while sntws:
            # we retrieve the biggest subnetwork not yet treated
            sntw = sntws.pop()
            # both network and broadcast addresses are excluded:
            # we add 2 to the size of the subnetwork
            size = ceil(log(len(sntw) + 2, 2))
            subnet, mask = '/{}'.format(32 - size), tomask(32 - size)
            for idx, (trunk, node) in enumerate(sntw, 1):
                trunk.sntw = sntw_ip + subnet
                trunk('subnetmask', node, mask)
                curr_ip = ip_incrementer(sntw_ip, idx)
                trunk('ipaddress', node, curr_ip)
                self.sntw_to_ip[sntw_ip + subnet].add(curr_ip)
                self.ip_to_mask[curr_ip] = mask
                self.ip_to_node[curr_ip] = node
            sntw_ip = ip_incrementer(sntw_ip, 2**size)
            
        # allocate loopback address using the 192.168.0.0/16 private 
        # address space
        for idx, router in enumerate(self.ftr('node', 'router'), 1):
            router.ipaddress = '192.168.{}.{}'.format(idx // 255, idx % 255)
                                                      

    def interface_allocation(self):
        for node in self.pn['node'].values():
            for idx, (_, adj_trunk) in enumerate(self.graph[node.id]['trunk']):
                adj_trunk('interface', node, 'Ethernet0/{}'.format(idx))
                
    # WC trunk dimensioning: this computes the maximum traffic the trunk may 
    # have to carry considering all possible trunk failure. 
    # NetDim fails all trunks of the network one by one, and evaluates 
    # the impact in terms of bandwidth for each trunk. 
    # The highest value is kept in memory, as well as the trunk which failure 
    # induces this value.
    def trunk_dimensioning(self):
        # we need to remove all failures before dimensioning the trunks:
        # the set of failed trunk will be redefined, but we also need the
        # icons to be cleaned from the canvas
        self.cs.remove_failures()
        
        # we consider each trunk in the network to be failed, one by one
        for failed_trunk in self.pn['trunk'].values():
            self.fdtks = {failed_trunk}
            # the trunk being failed, we will recreate all routing tables
            # then use the path finding procedure to map the traffic flows
            self.rt_creation()
            self.path_finder()
            for trunk in self.pn['trunk'].values():
                for dir in ('SD', 'DS'):
                    curr_traffic = getattr(trunk, 'traffic' + dir)
                    if curr_traffic > getattr(trunk, 'wctraffic' + dir):
                        setattr(trunk, 'wctraffic' + dir, curr_traffic)
                        setattr(trunk, 'wcfailure', str(failed_trunk))
                        
        self.fdtks.clear()
        
    def rt_creation(self):
        # we compute the routing table of all routers
        for router in self.ftr('node', 'router', 'host'):
            router.rt = {}
            for AS in router.AS:
                self.RFT_builder(router, AS)
            self.static_RFT_builder(router)
                
    def reset_traffic(self):
        # reset the traffic for all trunks
        for trunk in self.pn['trunk'].values():
            trunk.trafficSD = trunk.trafficDS = 0.
                
    def path_finder(self):
        self.reset_traffic()
        for traffic in self.pn['traffic'].values():
            src, dest = traffic.source, traffic.destination
            if all(node.subtype == 'router' for node in (src, dest)):
                self.RFT_path_finder(traffic)
            else:
                _, traffic.path = self.A_star(src, dest)
            if not traffic.path:
                print('no path found for {}'.format(traffic))
                
    def calculate_all(self):
        self.ma_segments.clear()
        self.update_AS_topology()
        self.segment_finder(3)
        self.segment_finder(2)
        self.ip_allocation()
        self.multi_access_network()
        self.interface_allocation()
        self.rt_creation()
        self.BGPT_builder()
        self.path_finder()
        self.cs.refresh_all_labels()
        
    def route(self):
        # create the routing tables and route all traffic flows
        self.rt_creation()
        self.path_finder()
            
    def bfs(self, source):
        visited = set()
        layer = {source}
        while layer:
            temp = layer
            layer = set()
            for node in temp:
                if node not in visited:
                    visited.add(node)
                    for neighbor, _ in self.graph[node.id]['trunk']:
                        layer.add(neighbor)
                        yield neighbor
                    
    def connected_components(self):
        visited = set()
        for node in self.pn['node'].values():
            if node not in visited:
                new_comp = set(self.bfs(node))
                visited.update(new_comp)
                yield new_comp
                
    ## Shortest path(s) algorithms
    
    ## 1) Dijkstra algorithm
        
    def dijkstra(
                 self, 
                 source, 
                 target,
                 allowed_trunks = None, 
                 allowed_nodes = None
                 ):
        
        if allowed_trunks is None:
            allowed_trunks = set(self.pn['trunk'].values())
        if allowed_nodes is None:
            allowed_nodes = set(self.pn['node'].values())
        
        prec_node = {i: None for i in allowed_nodes}
        prec_trunk = {i: None for i in allowed_nodes}
        visited = set()
        dist = {i: float('inf') for i in allowed_nodes}
        dist[source] = 0
        heap = [(0, source)]
        while heap:
            dist_node, node = heappop(heap) 
            if node not in visited:
                visited.add(node)
                for neighbor, adj_trunk in self.graph[node.id]['trunk']:
                    # we ignore what's not allowed (not in the AS or in failure)
                    if neighbor not in allowed_nodes:
                        continue
                    if adj_trunk not in allowed_trunks:
                        continue
                    dist_neighbor = dist_node + adj_trunk('cost', node)
                    if dist_neighbor < dist[neighbor]:
                        dist[neighbor] = dist_neighbor
                        prec_node[neighbor] = node
                        prec_trunk[neighbor] = adj_trunk
                        heappush(heap, (dist_neighbor, neighbor))
                        
        # traceback the path from target to source
        curr, path_trunk = target, [prec_trunk[target]]
        while curr != source:
            curr = prec_node[curr]
            path_trunk.append(prec_trunk[curr])
                        
        # we return:
        # - the dist dictionnary, that contains the distance from the source
        # to any other node in the tree 
        # - the shortest path from source to target
        # - all edges that belong to the Shortest Path Tree
        # we need all three variables for Suurbale algorithm below
        return dist, path_trunk[:-1][::-1], filter(None, prec_trunk.values())
        
    ## 2) A* algorithm for CSPF modelization
            
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
            path_constraints = []
        if allowed_trunks is None:
            allowed_trunks = set(self.pn['trunk'].values())
        if allowed_nodes is None:
            allowed_nodes = set(self.pn['node'].values())
            
        pc = [target] + path_constraints[::-1]
        visited = set()
        heap = [(0, source, [source], [], pc)]
        while heap:
            dist, node, nodes, trunks, pc = heappop(heap)
            if node not in visited:
                visited.add(node)
                if node == pc[-1]:
                    visited.clear()
                    heap.clear()
                    pc.pop()
                    if not pc:
                        return nodes, trunks
                for neighbor, adj_trunk in self.graph[node.id]['trunk']:
                    # excluded and allowed nodes
                    if neighbor not in allowed_nodes-excluded_nodes: 
                        continue
                    # excluded and allowed trunks
                    if adj_trunk not in allowed_trunks-excluded_trunks: 
                        continue
                    heappush(heap, (
                                    dist + adj_trunk('cost', node), 
                                    neighbor,
                                    nodes + [neighbor], 
                                    trunks + [adj_trunk], 
                                    pc
                                    )
                            )
        return [], []

    ## 3) Bellman-Ford algorithm
        
    def bellman_ford(
                     self, 
                     source, 
                     target, 
                     cycle = False,
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
            allowed_trunks = set(self.pn['trunk'].values())
        if allowed_nodes is None:
            allowed_nodes = set(self.pn['node'].values())

        n = len(allowed_nodes)
        prec_node = {i: None for i in allowed_nodes}
        prec_trunk = {i: None for i in allowed_nodes}
        dist = {i: float('inf') for i in allowed_nodes}
        dist[source] = 0
        
        for i in range(n+2):
            negative_cycle = False
            for node in allowed_nodes:
                for neighbor, adj_trunk in self.graph[node.id]['trunk']:
                    sd = (node == adj_trunk.source)*'SD' or 'DS'
                    # excluded and allowed nodes
                    if neighbor not in allowed_nodes-excluded_nodes: 
                        continue
                    # excluded and allowed trunks
                    if adj_trunk not in allowed_trunks-excluded_trunks: 
                        continue
                    dist_neighbor = dist[node] + getattr(adj_trunk, 'cost' + sd)
                    if dist_neighbor < dist[neighbor]:
                        dist[neighbor] = dist_neighbor
                        prec_node[neighbor] = node
                        prec_trunk[neighbor] = adj_trunk
                        negative_cycle = True
                        
        # traceback the path from target to source
        if dist[target] != float('inf') and not cycle:
            curr, path_node, path_trunk = target, [target], [prec_trunk[target]]
            while curr != source:
                curr = prec_node[curr]
                path_trunk.append(prec_trunk[curr])
                path_node.append(curr)
            return path_node[::-1], path_trunk[:-1][::-1]
        # if we want a cycle, and one exists, we find it
        if cycle and negative_cycle:
                curr, path_node, path_trunk = target, [target], [prec_trunk[target]]
                # return the cycle itself (for the cycle cancelling algorithm) 
                # starting from the target, we go through the predecessors 
                # we find any cycle (we don't necessarily have to come back to
                # the target).
                while curr not in path_node:
                    curr = prec_node[curr]
                    path_trunk.append(prec_trunk[curr])
                    path_node.append(curr)
                return path_node[::-1], path_trunk[:-1][::-1]
        # if we didn't find a path, and were not looking for a cycle, 
        # we return empty lists
        return [], []
            
    ## 4) Floyd-Warshall algorithm
            
    def floyd_warshall(self):
        nodes = list(self.pn['node'].values())
        n = len(nodes)
        W = [[0]*n for _ in range(n)]
        
        for id1, n1 in enumerate(nodes):
            for id2, n2 in enumerate(nodes):
                if id1 != id2:
                    for neighbor, trunk in self.graph[n1.id]['trunk']:
                        if neighbor == n2:
                            W[id1][id2] = trunk.costSD
                            break
                    else:
                        W[id1][id2] = float('inf')
                        
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
        
    ## 5) DFS (all loop-free paths)
        
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
                for neighbor, adj_trunk in self.graph[node.id]['trunk']:
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
        
    ## Model 2:
    
    ## 0) Ping / traceroute
    
    def ping(self, source, dest_sntw):
        node = source
        while True:
            if any(tk.sntw == dest_sntw for _, tk in self.graph[node.id]['trunk']):
                break
            if dest_sntw in node.rt:
                routes = node.rt[dest_sntw]
            # if we wannot find the destination address in the routing table, 
            # and there is a default route, we use it.
            elif '0.0.0.0' in node.rt:
                routes = node.rt['0.0.0.0']
            else:
                warnings.warn('Packet discarded by {}:'.format(node))
                break
            for route in routes:
                yield route
                *_, node, _ = route
                break
    
    ## 1) RFT-based routing and dimensioning
    
    def RFT_path_finder(self, traffic):
        source, destination = traffic.source, traffic.destination
        # the two lines below run faster than making the set an iterable
        for _, trunk in self.graph[destination.id]['trunk']:
            break
        dest_int = trunk.sntw
        heap = [(source, traffic.throughput)]
        path_node, path_trunk = {source}, set()
        while heap:
            curr_router, share = heap.pop()
            if curr_router == destination:
                continue
            if dest_int in curr_router.rt:
                routes = curr_router.rt[dest_int]
            # if we wannot find the destination address in the routing table, 
            # and there is a default route, we use it.
            elif '0.0.0.0' in curr_router.rt:
                routes = curr_router.rt['0.0.0.0']
            else:
                warnings.warn('Path not found for {}'.format(traffic))
                break
            # we count the number of trunks in failure
            failed_trunks = sum(r[-1] in self.fdtks for r in routes)
            # and remove them from share so that they are ignored for 
            # trunk dimensioning
            share /= len(routes) - failed_trunks
            for route in routes:
                *_, router, trunk = route
                path_node.add(router)
                path_trunk.add(trunk)
                sd = (curr_router == trunk.source)*'SD' or 'DS'
                trunk.__dict__['traffic' + sd] += share
                heap.append((router, share))
             
        traffic.path = path_trunk

        return path_node, path_trunk
        
    ## 2) Add connected interfaces to the RFT
    # TODO and default / static route too
    
    def static_RFT_builder(self, source):
        
        if source.default_route:
            try:
                nh_node = self.ip_to_node[source.default_route]
                source.rt['0.0.0.0'] = {('S*', source.default_route, 
                                                    None, 0, nh_node, None)}
            except KeyError:
                pass
            

        for _, sr in self.gftr(source, 'route', 'static route', False):
            # if the static route next-hop ip is not properly configured, 
            # we ignore it.
            try:
                nh_node = self.ip_to_node[sr.nh_ip]
            except KeyError:
                continue
            source.rt[sr.dst_sntw] = {('S', sr.nh_ip, None, 0, nh_node, None)}
                                                                
                    
        for neighbor, adj_trunk in self.graph[source.id]['trunk']:
            if adj_trunk in self.fdtks:
                continue
            ex_ip = adj_trunk('ipaddress', neighbor)
            ex_int = adj_trunk('interface', source)
            # we compute the subnetwork of the attached
            # interface: it is a directly connected interface
            source.rt[adj_trunk.sntw] = {('C', ex_ip, ex_int, 
                                                    0, neighbor, adj_trunk)}
                                            
    ## 3) RFT builder
                                                
    def RFT_builder(
               self, 
               source, 
               AS
               ):
    
        K = source.LB_paths
        visited = set()
        allowed_nodes = AS.pAS['node']
        allowed_trunks =  AS.pAS['trunk'] - self.fdtks
        # we keep track of all already visited subnetworks so that we 
        # don't add them more than once to the mapping dict.
        visited_subnetworks = set()
        heap = [(0, source, [], None)]
        # source area: we make sure that if the node is connected to an area,
        # the path we find to any subnetwork in that area is an intra-area path.
        src_areas = source.AS[AS]
        # cost of the shortesth path to a subnetwork
        SP_cost = {}
                
        if AS.type == 'ISIS':
            # if source is an L1 there will be a default route to
            # 0.0.0.0 heading to the closest L1/L2 node.
            src_area ,= source.AS[AS]
            
            # we keep a boolean telling us if source is L1 so that we know we
            # must add the i*L1 default route when we first meet a L1/L2 node
            # and all other routes are i L1 as rtype (route type).
            isL1 = source not in AS.border_routers and src_area.name != 'Backbone'
        
        while heap:
            dist, node, path_trunk, ex_int = heappop(heap)  
            if (node, ex_int) not in visited:
                visited.add((node, ex_int))
                for neighbor, l3vc in self.graph[node.id]['l3vc']:
                    adj_trunk = l3vc("link", node)
                    remote_trunk = l3vc("link", neighbor)
                    if adj_trunk in path_trunk:
                        continue
                    # excluded and allowed nodes
                    if neighbor not in allowed_nodes:
                        continue
                    # excluded and allowed trunks
                    if adj_trunk not in allowed_trunks: 
                        continue
                    if node == source:
                        ex_ip = remote_trunk('ipaddress', neighbor)
                        print(node, remote_trunk, neighbor, ex_ip)
                        ex_int = adj_trunk('interface', source)
                        source.rt[adj_trunk.sntw] = {('C', ex_ip, ex_int, 
                                            dist, neighbor, adj_trunk)}
                        SP_cost[adj_trunk.sntw] = 0
                    heappush(heap, (dist + adj_trunk('cost', node), 
                            neighbor, path_trunk + [adj_trunk], ex_int))
                    
            if path_trunk:
                trunk = path_trunk[-1]
                ex_tk = path_trunk[0]
                nh = ex_tk.destination if ex_tk.source == source else ex_tk.source
                if AS.type == 'RIP':
                    if trunk.sntw not in source.rt:
                        SP_cost[trunk.sntw] = dist
                        source.rt[trunk.sntw] = {('R', ex_ip, ex_int, 
                                                    dist, nh, ex_tk)}
                    else:
                        if (dist == SP_cost[trunk.sntw] 
                            and K > len(source.rt[trunk.sntw])):
                            source.rt[trunk.sntw].add(('R', ex_ip, ex_int, 
                                                    dist, nh, ex_tk))
                elif AS.type == 'OSPF':
                    # we check if the trunk has any common area with the
                    # exit trunk: if it does not, it is an inter-area route.
                    rtype = 'O' if (trunk.AS[AS] & ex_tk.AS[AS]) else 'O IA'
                    if trunk.sntw not in source.rt:
                        SP_cost[trunk.sntw] = dist
                        source.rt[trunk.sntw] = {(rtype, ex_ip, ex_int, 
                                                    dist, nh, ex_tk)}
                    else:
                        for route in source.rt[trunk.sntw]:
                            break
                        if route[0] == 'O' and rtype == 'IA':
                            continue
                        elif route[0] == 'O IA' and rtype == 'O':
                            SP_cost[trunk.sntw] = dist
                            source.rt[trunk.sntw] = {(rtype, ex_ip, ex_int, 
                                                    dist, nh, ex_tk)}
                        else:
                            if (dist == SP_cost[trunk.sntw]
                                and K > len(source.rt[trunk.sntw])):
                                source.rt[trunk.sntw].add((
                                                        rtype, ex_ip, ex_int, 
                                                         dist, nh, ex_tk
                                                         ))
                    if (rtype, trunk.sntw) not in visited_subnetworks:
                        if ('O', trunk.sntw) in visited_subnetworks:
                            continue
                        else:
                            visited_subnetworks.add((rtype, trunk.sntw))
                            source.rt[trunk.sntw] = {(rtype, ex_ip, ex_int, 
                                                            dist, nh, ex_tk)}
                elif AS.type == 'ISIS':
                    if isL1:
                        if (node in AS.border_routers 
                                            and '0.0.0.0' not in source.rt):
                            source.rt['0.0.0.0'] = {('i*L1', ex_ip, ex_int,
                                                        dist, nh, ex_tk)}
                        else:
                            if (('i L1', trunk.sntw) not in visited_subnetworks 
                                            and trunk.AS[AS] & ex_tk.AS[AS]):
                                visited_subnetworks.add(('i L1', trunk.sntw))
                                source.rt[trunk.sntw] = {('i L1', ex_ip, ex_int,
                                        dist + trunk('cost', node), nh, ex_tk)}
                    else:
                        trunkAS ,= trunk.AS[AS]
                        exit_area ,= ex_tk.AS[AS]
                        rtype = 'i L1' if (trunk.AS[AS] & ex_tk.AS[AS] and 
                                        trunkAS.name != 'Backbone') else 'i L2'
                        # we favor intra-area routes by excluding a 
                        # route if the area of the exit trunk is not
                        # the one of the subnetwork
                        if (not ex_tk.AS[AS] & trunk.AS[AS] 
                                        and trunkAS.name == 'Backbone'):
                            continue
                        # if the source is an L1/L2 node and the destination
                        # is an L1 area different from its own, we force it
                        # to use the backbone by forbidding it to use the
                        # exit interface in the source area
                        if (rtype == 'i L2' and source in AS.border_routers and 
                                    exit_area.name != 'Backbone'):
                            continue
                        if (('i L1', trunk.sntw) not in visited_subnetworks 
                            and ('i L2', trunk.sntw) not in visited_subnetworks):
                            visited_subnetworks.add((rtype, trunk.sntw))
                            source.rt[trunk.sntw] = {(rtype, ex_ip, ex_int,
                                    dist + trunk('cost', node), nh, ex_tk)}
                    # TODO
                    # IS-IS uses per-address unequal cost load balancing 
                    # a user-defined variance defined as a percentage of the
                    # primary path cost defines which paths can be used
                    # (up to 9).
                    
    def BGPT_builder(self):
        for source in self.ftr('node', 'router'):
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
                    source.bgpt[ip] |= {(32768, nh, source, ())}
            
            # we fill the heap so that 
            for src_nb, bgp_pr in self.gftr(source, 'route', 'BGP peering'):
                first_AS = [source.bgp_AS, src_nb.bgp_AS]
                if bgp_pr('weight', source):
                    weight = 1 / bgp_pr('weight', source)
                else: 
                    weight = float('inf')
                print(source, src_nb,bgp_pr, bgp_pr('ip', src_nb))
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
                        real_weight = 0 if weight == float('inf') else 1/weight
                        source.bgpt[ip] |= {(real_weight, nh, node, tuple(AS_path))}
                    visited.add(node)
                    for bgp_nb, bgp_pr in self.gftr(node, 'route', 'BGP peering'):
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
        
    ## Link-disjoint / link-and-node-disjoint shortest pair algorithms
    
    ## 1) A* link-disjoint pair search
    
    def A_star_shortest_pair(self, source, target, a_n=None, a_t=None):
        # To find the shortest pair from the source to the target, we look
        # for the shortest path going from the source to the source, with 
        # the target as a 'path constraint'.
        # Each path is stored with sets of allowed nodes and trunks that will 
        # contains what belongs to the first path, once we've reached the target.
        
        # if a_n is None:
        #     a_n = AS.pAS['node']
        # if a_t is None:
        #     a_t = AS.pAS['trunk']
        
        if a_t is None:
            a_t = set(self.pn['trunk'].values())
        if a_n is None:
            a_n = set(self.pn['node'].values())

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
                for neighbor, adj_trunk in self.graph[node.id]['trunk']:
                    sd = (node == adj_trunk.source)*'SD' or 'DS'
                    # we ignore what's not allowed (not in the AS or in failure
                    # or in the path we've used to reach the target)
                    if neighbor not in a_n or adj_trunk not in a_t-e_o:
                        continue
                    cost = getattr(adj_trunk, 'cost' + sd)
                    heappush(heap, (dist + cost, neighbor, 
                                                path_trunk + [adj_trunk], e_o))
        return [], []
        
    ## 2) Bhandari algorithm for link-disjoint shortest pair
        
    def bhandari(self, source, target, a_n=None, a_t=None):
    # - we find the shortest path from source to target using A* algorithm
    # - we replace bidirectionnal trunks of the shortest path with unidirectional 
    # trunks with a negative cost
    # - we run Bellman-Ford algorithm to find the new 
    # shortest path from source to target
    # - we remove all overlapping trunks
        
        if a_t is None:
            a_t = set(self.pn['trunk'].values())
        if a_n is None:
            a_n = set(self.pn['node'].values())
            
        # we store the cost value in the flow parameters, since bhandari 
        # algorithm relies on graph transformation, and the costs of the edges
        # will be modified.
        # at the end, we will revert the cost to their original value
        for trunk in a_t:
            trunk.flowSD = trunk.costSD
            trunk.flowDS = trunk.costDS
            
        _, first_path = self.A_star(
                              source, 
                              target, 
                              allowed_trunks = a_t, 
                              allowed_nodes = a_n
                              ) 
                   
        # we set the cost of the shortest path trunks to float('inf'), which 
        # is equivalent to just removing them. In the reverse direction, 
        # we set the cost to -1.
        current_node = source
        for trunk in first_path:
            dir = 'SD' * (current_node == trunk.source) or 'DS'
            reverse_dir = 'SD' if dir == 'DS' else 'DS'
            setattr(trunk, 'cost' + dir, float('inf'))
            setattr(trunk, 'cost' + reverse_dir, -1)
            current_node = trunk.destination if dir == 'SD' else trunk.source
            
        _, second_path = self.bellman_ford(
                                           source, 
                                           target, 
                                           allowed_trunks = a_t, 
                                           allowed_nodes = a_n
                                           )
        
        for trunk in a_t:
            trunk.costSD = trunk.flowSD
            trunk.costDS = trunk.flowDS

        return set(first_path) ^ set(second_path)
        
    def suurbale(self, source, target, a_n=None, a_t=None):
    # - we find the shortest path tree from the source using dijkstra algorithm
    # - we change the cost of all edges (a,b) such that
    # c(a, b) = c(a, b) - d(s, b) + d(s, a) (all tree edge will have a 
    # resulting cost of 0 with that formula, since c(a, b) = d(s, a) - d(s, b)
    # - we run A* algorithm to find the new 
    # shortest path from source to target
    # - we remove all overlapping trunks
        
        if a_t is None:
            a_t = set(self.pn['trunk'].values())
        if a_n is None:
            a_n = set(self.pn['node'].values())
            
        # we store the cost value in the flow parameters, since bhandari 
        # algorithm relies on graph transformation, and the costs of the edges
        # will be modified.
        # at the end, we will revert the cost to their original value
        for trunk in a_t:
            trunk.flowSD = trunk.costSD
            trunk.flowDS = trunk.costDS
            
        dist, first_path, tree = self.dijkstra(
                              source, 
                              target, 
                              allowed_trunks = a_t, 
                              allowed_nodes = a_n
                              ) 
                              
        # we change the trunks cost with the formula described above
        for trunk in tree:
            # new_c(a, b) = c(a, b) - D(b) + D(a) where D(x) is the 
            # distance from the source to x.
            src, dest = trunk.source, trunk.destination
            trunk.costSD += dist[src] - dist[dest]
            trunk.costDS += dist[dest] - dist[src]
            
        # we exclude the edge of the shortest path (infinite cost)
        current_node = source
        for trunk in first_path:
            dir = 'SD' * (current_node == trunk.source) or 'DS'
            setattr(trunk, 'cost' + dir, float('inf'))
            current_node = trunk.destination if dir == 'SD' else trunk.source
            
        _, second_path = self.A_star(
                              source, 
                              target, 
                              allowed_trunks = a_t, 
                              allowed_nodes = a_n
                              )
                              
        return set(first_path) ^ set(second_path)

        
    ## Flow algorithms
    
    def reset_flow(self):
        for trunk in self.pn['trunk'].values():
            trunk.flowSD = trunk.flowDS = 0
    
    ## 1) Ford-Fulkerson algorithm
        
    def augment_ff(self, val, curr_node, target, visit):
        visit[curr_node] = True
        if curr_node == target:
            return val
        for neighbor, adj_trunk in self.graph[curr_node.id]['trunk']:
            direction = curr_node == adj_trunk.source
            sd, ds = direction*'SD' or 'DS', direction*'DS' or 'SD'
            cap = getattr(adj_trunk, 'capacity' + sd)
            current_flow = getattr(adj_trunk, 'flow' + sd)
            if cap > current_flow and not visit[neighbor]:
                residual_capacity = min(val, cap - current_flow)
                global_flow = self.augment_ff(
                                              residual_capacity, 
                                              neighbor, 
                                              target, 
                                              visit
                                              )
                if global_flow > 0:
                    adj_trunk.__dict__['flow' + sd] += global_flow
                    adj_trunk.__dict__['flow' + ds] -= global_flow
                    return global_flow
        return False
        
    def ford_fulkerson(self, s, d):
        self.reset_flow()
        while self.augment_ff(float('inf'), s, d, {n:0 for n in self.pn["node"].values()}):
            pass
        # flow leaving from the source 
        return sum(
                  getattr(adj, 'flow' + (s==adj.source)*'SD' or 'DS') 
                  for _, adj in self.graph[s.id]['trunk']
                  )
        
    ## 2) Edmonds-Karp algorithm
        
    def augment_ek(self, source, destination):
        res_cap = {n:0 for n in self.pn["node"].values()}
        augmenting_path = {n: None for n in self.pn["node"].values()}
        Q = deque()
        Q.append(source)
        augmenting_path[source] = source
        res_cap[source] = float('inf')
        while Q:
            curr_node = Q.popleft()
            for neighbor, adj_trunk in self.graph[curr_node.id]['trunk']:
                direction = curr_node == adj_trunk.source
                sd, ds = direction*'SD' or 'DS', direction*'DS' or 'SD'
                cap = getattr(adj_trunk, 'capacity' + sd)
                flow = getattr(adj_trunk, 'flow' + sd)
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
                (_, trunk) ,= filter(find_trunk, self.graph[curr_node.id]['trunk'])
                # define sd and ds depending on how the trunk is defined
                direction = curr_node == trunk.source
                sd, ds = direction*'SD' or 'DS', direction*'DS' or 'SD'
                trunk.__dict__['flow' + ds] += global_flow
                trunk.__dict__['flow' + sd] -= global_flow
                curr_node = prec_node 
        return sum(
                   getattr(adj, 'flow' + ((source==adj.source)*'SD' or 'DS')) 
                   for _, adj in self.graph[source.id]['trunk']
                  )
                  
    ## 2) Dinic algorithm
    
    def augment_di(self, level, flow, curr_node, dest, limit):
        if limit <= 0:
            return 0
        if curr_node == dest:
            return limit
        val = 0
        for neighbor, adj_trunk in self.graph[curr_node.id]['trunk']:
            direction = curr_node == adj_trunk.source
            sd, ds = direction*'SD' or 'DS', direction*'DS' or 'SD'
            cap = getattr(adj_trunk, 'capacity' + sd)
            flow = getattr(adj_trunk, 'flow' + sd)
            residual = cap - flow
            if level[neighbor] == level[curr_node] + 1 and residual > 0:
                z = min(limit, residual)
                aug = self.augment_di(level, flow, neighbor, dest, z)
                adj_trunk.__dict__['flow' + sd] += aug
                adj_trunk.__dict__['flow' + ds] -= aug
                val += aug
                limit -= aug
        if not val:
            level[curr_node] = None
        return val
        
    def dinic(self, source, destination):
        self.reset_flow()
        Q = deque()
        total = 0
        while True:
            Q.appendleft(source)
            level = {node: None for node in self.pn['node'].values()}
            level[source] = 0
            while Q:
                curr_node = Q.pop()
                for neighbor, adj_trunk in self.graph[curr_node.id]['trunk']:
                    direction = curr_node == adj_trunk.source
                    sd = direction*'SD' or 'DS'
                    cap = getattr(adj_trunk, 'capacity' + sd)
                    flow = getattr(adj_trunk, 'flow' + sd)
                    if level[neighbor] is None and cap > flow:
                        level[neighbor] = level[curr_node] + 1
                        Q.appendleft(neighbor)
                        
            if level[destination] is None:
                return flow, total
            limit = sum(
                        getattr(adj_trunk, 'capacity' + 
                        ((source == adj_trunk.source)*'SD' or 'DS'))
                        for _, adj_trunk in self.graph[source.id]['trunk']
                        )
            total += self.augment_di(level, flow, source, destination, limit)
        
    ## Minimum spanning tree algorithms 
    
    ## 1) Kruskal algorithm
        
    def kruskal(self, allowed_nodes):
        uf = UnionFind(allowed_nodes)
        edges = []
        for node in allowed_nodes:
            for neighbor, adj_trunk in self.graph[node.id]['trunk']:
                if neighbor in allowed_nodes:
                    edges.append((adj_trunk.costSD, adj_trunk, node, neighbor))
        for w, t, u, v in sorted(edges, key=itemgetter(0)):
            if uf.union(u, v):
                yield t
                
    ## Linear programming algorithms
    
    ## 1) Shortest path
    
    def LP_SP_formulation(self, s, t):

        # Solves the MILP: minimize c'*x
        #         subject to G*x + s = h
        #                     A*x = b
        #                     s >= 0
        #                     xi integer, forall i in I

        
        self.reset_flow()
        
        new_graph = {node: {} for node in self.pn['node'].values()}
        for node in self.pn['node'].values():
            for neighbor, trunk in self.graph[node.id]['trunk']:
                sd = (node == trunk.source)*'SD' or 'DS'
                new_graph[node][neighbor] = getattr(trunk, 'cost' + sd)

        n = 2*len(self.pn['trunk'])
        
        c = []
        for node in new_graph:
            for neighbor, cost in new_graph[node].items():
                # the float conversion is ESSENTIAL !
                # I first forgot it, then spent hours trying to understand 
                # what was wrong. If 'c' is not made of float, no explicit 
                # error is raised, but the result is sort of random !
                c.append(float(cost))
                
        # for the condition 0 < x_ij < 1
        h = np.concatenate([np.ones(n), np.zeros(n)])
        id = np.eye(n, n)
        G = np.concatenate((id, -1*id), axis=0).tolist()  
        
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
        for trunk in self.pn['trunk'].values():
            src, dest = trunk.source, trunk.destination
            trunk.flowSD = new_graph[src][dest]
            trunk.flowDS = new_graph[dest][src]
            
        # traceback the shortest path with the flow
        curr_node, path_trunk = s, []
        while curr_node != t:
            for neighbor, adj_trunk in self.graph[curr_node.id]['trunk']:
                # if the flow leaving the current node is 1, we move
                # forward and replace the current node with its neighbor
                if adj_trunk('flow', curr_node) == 1:
                    path_trunk.append(adj_trunk)
                    curr_node = neighbor
                    
        return path_trunk
    
    ## 2) Single-source single-destination maximum flow
               
    def LP_MF_formulation(self, s, t):

        # Solves the MILP: minimize c'*x
        #         subject to G*x + s = h
        #                     A*x = b
        #                     s >= 0
        #                     xi integer, forall i in I

        
        new_graph = {node: {} for node in self.pn['node'].values()}
        for node in self.pn['node'].values():
            for neighbor, trunk in self.graph[node.id]['trunk']:
                sd = (node == trunk.source)*'SD' or 'DS'
                new_graph[node][neighbor] = getattr(trunk, 'capacity' + sd)

        n = 2*len(self.pn['trunk'])
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
                
        b = np.zeros(v - 2)
        h = np.concatenate([h, np.zeros(n)])
        x = np.eye(n, n)
        G = np.concatenate((x, -1*x), axis=0).tolist()   
             
        A, G, b, c, h = map(matrix, (A, G, b, c, h))
        solsta, x = glpk.ilp(-c, G.T, h, A.T, b)

        # update the resulting flow for each node
        cpt = 0
        for node in new_graph:
            for neighbor in new_graph[node]:
                new_graph[node][neighbor] = x[cpt]
                cpt += 1
                
        # update the network trunks with the new flow value
        for trunk in self.pn['trunk'].values():
            src, dest = trunk.source, trunk.destination
            trunk.flowSD = new_graph[src][dest]
            trunk.flowDS = new_graph[dest][src]

        return sum(
                   getattr(adj, 'flow' + ((s==adj.source)*'SD' or 'DS')) 
                   for _, adj in self.graph[s.id]['trunk']
                   )
                   
    ## 3) Single-source single-destination minimum-cost flow
               
    def LP_MCF_formulation(self, s, t, flow):

        # Solves the MILP: minimize c'*x
        #         subject to G*x + s = h
        #                     A*x = b
        #                     s >= 0
        #                     xi integer, forall i in I

        
        new_graph = {node: {} for node in self.pn['node'].values()}
        for node in self.pn['node'].values():
            for neighbor, trunk in self.graph[node.id]['trunk']:
                new_graph[node][neighbor] = (trunk('capacity', node),
                                             trunk('cost', node))

        n = 2*len(self.pn['trunk'])
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
                
        h = np.concatenate([h, np.zeros(n)])
        x = np.eye(n, n)
        G = np.concatenate((x, -1*x), axis=0).tolist() 
               
        A, G, b, c, h = map(matrix, (A, G, b, c, h))
        solsta, x = glpk.ilp(c, G.T, h, A.T, b)

        # update the resulting flow for each node
        cpt = 0
        for node in new_graph:
            for neighbor in new_graph[node]:
                new_graph[node][neighbor] = x[cpt]
                cpt += 1
                
        # update the network trunks with the new flow value
        for trunk in self.pn['trunk'].values():
            src, dest = trunk.source, trunk.destination
            trunk.flowSD = new_graph[src][dest]
            trunk.flowDS = new_graph[dest][src]

        return sum(
                   getattr(adj, 'flow' + ((s==adj.source)*'SD' or 'DS')) 
                   for _, adj in self.graph[s.id]['trunk']
                   )
                   
    ## 4) K Link-disjoint shortest pair 
    
    def LP_LDSP_formulation(self, s, t, K):

        # Solves the MILP: minimize c'*x
        #         subject to G*x + s = h
        #                     A*x = b
        #                     s >= 0
        #                     xi integer, forall i in I

        
        self.reset_flow()
        
        all_graph = []
        for i in range(K):
            graph_K = {node: {} for node in self.pn['node'].values()}
            for node in graph_K:
                for neighbor, trunk in self.graph[node.id]['trunk']:
                    sd = (node == trunk.source)*'SD' or 'DS'
                    graph_K[node][neighbor] = getattr(trunk, 'cost' + sd)
            all_graph.append(graph_K)

        n = 2*len(self.pn['trunk'])
        
        c = []
        for graph_K in all_graph:
            for node in graph_K:
                for neighbor, cost in graph_K[node].items():
                    c.append(float(cost))
                
        # for the condition 0 < x_ij < 1
        h = np.concatenate([np.ones(K * n), np.zeros(K * n), np.ones(K * (K - 1) * n)])
        
        G2 = []
        for i in range(K):
            for j in range(K):
                if i != j:
                    for nodeA in all_graph[j]:
                        for neighborA in all_graph[j][nodeA]:
                            row = []
                            for k in range(K):
                                for nodeB in all_graph[k]:
                                    for neighborB in all_graph[k][nodeB]:
                                        row.append(float(k in (i, j) and 
                                                    nodeA == nodeB and
                                                    neighborA == neighborB
                                                   ))
                            G2.append(row)
                            
        id = np.eye(K * n, K * n)
        G = np.concatenate((id, -1*id, G2), axis=0).tolist()
        
        # flow conservation: Ax = b
        
        A, b = [], []
        for i in range(K):
            for node_r in self.pn['node'].values():
                if node_r != t:
                    row = []
                    b.append(float(node_r == s))
                    for j in range(K):
                        for node in all_graph[j]:
                            for neighbor in all_graph[j][node]:
                                row.append(
                                            -1. if neighbor == node_r and i == j 
                                    else     1. if node == node_r and i == j
                                    else     0.
                                        )
                    A.append(row)
        
        A, G, b, c, h = map(matrix, (A, G, b, c, h))
        
        binvar = set(range(n))
        solsta, x = glpk.ilp(c, G.T, h, A.T, b, B=binvar)
        print(x)
        
        # update the resulting flow for each node
        cpt = 0
        for graph_K in all_graph:
            for node in graph_K:
                for neighbor in graph_K[node]:
                    graph_K[node][neighbor] = x[cpt]
                    cpt += 1

        # update the network trunks with the new flow value
        for trunk in self.pn['trunk'].values():
            src, dest = trunk.source, trunk.destination
            trunk.flowSD = max(graph_K[src][dest] for graph_K in all_graph)
            trunk.flowDS = max(graph_K[dest][src] for graph_K in all_graph)
            
        return sum(x)
        
    ## IP network cost optimization: Weight Setting Problem
    
    
    
    # compute the network congestion ratio of an autonomous system
    # it is defined as max( link bw / link capacity for all links):
    # it is the maximum utilization ratio among all AS links.
    # we also use this function to retrieve the argmax, that is, 
    # the trunk with the highlight bandwidth / capacity ratio.
    def ncr_computation(self, AS_links):
        # ct_id is the index of the congested trunk bandwidth in AS_links
        # cd indicates which is the congested direction: SD or DS
        ncr, ct_id, cd = 0, None, None
        for idx, trunk in enumerate(AS_links):
            for direction in ('SD', 'DS'):
                tf, cap = 'traffic' + direction, 'capacity' + direction 
                curr_ncr = getattr(trunk, tf) / getattr(trunk, cap)
                if curr_ncr > ncr:
                    ncr = curr_ncr
                    ct_id = idx
                    cd = direction
        return ncr, ct_id, cd
        
    # 2) Tabu search heuristic
                   
    def WSP_TS(self, AS):
        
        self.update_AS_topology()
        self.ip_allocation()
        self.interface_allocation()
        
        AS_links = list(AS.pAS['trunk'])
        
        # a cost assignment solution is a vector of 2*n value where n is
        # the number of trunks in the AS, because each trunk has two costs:
        # one per direction (SD and DS).
        n = 2*len(AS_links)
        
        iteration_nb = 50
        
        # the tabu list is an empty: it will contain all the solutions, so that
        # we don't evaluate a solution more than once (we don't go 'backward')
        tabu_list = []
        
        # the current optimal solution found
        best_solution = None
        
        # for each solution, we compute the 'network congestion ratio':
        # best_ncr is the best network congestion ratio that has been found
        # so far, i.e the network congestion ratio of the best solution. 
        best_ncr = float('inf')
        
        # we store the cost value in the flow parameters, since we'll change
        # the links' costs to evaluate each solution
        # at the end, we will revert the cost to their original value
        for trunk in AS.pAS['trunk']:
            trunk.flowSD = trunk.costSD
            trunk.flowDS = trunk.costDS
            
        generation_size = 10
        best_candidates = []
        
        for i in range(generation_size):
            print(i)
            curr_solution = [random.randint(1, n) for _ in range(n)]
                
            # we assign the costs to the trunks
            for id, cost in enumerate(curr_solution):
                setattr(AS_links[id//2], 'cost' + ('DS'*(id%2) or 'SD'), cost)
                
            # create the routing tables with the newly allocated costs,
            # route all traffic flows and find the network congestion ratio
            self.rt_creation()
            self.path_finder()
            
            curr_ncr, *_ = self.ncr_computation(AS_links)
            best_candidates.append((curr_ncr, curr_solution)) 
                    
        best_candidates = nsmallest(5, best_candidates)
                    
        for i, (_, curr_solution) in enumerate(best_candidates):
            print(i)
            
            if curr_solution in tabu_list:
                continue
                
            # we create an cost assignment and add it to the tabu list
            tabu_list.append(curr_solution)
            
            # we assign the costs to the trunks
            for id, cost in enumerate(curr_solution):
                setattr(AS_links[id//2], 'cost' + ('DS'*(id%2) or 'SD'), cost)
            
            self.route()
            
            # if we have to look for the most congested trunk more than 
            # C_max times, and still can't have a network congestion 
            # ratio lower than best_ncr, we stop
            C_max, C = 10, 0
            local_best_ncr = float('inf')
            
            while True:
                self.route()
                    
                curr_ncr, ct_id, cd = self.ncr_computation(AS_links)

                # update the best solution found if the network congestion ratio
                # is the lowest one found so far
                if curr_ncr < local_best_ncr:
                    print(curr_ncr)
                    C = 0
                    local_best_ncr = curr_ncr
                    if curr_ncr < best_ncr:
                        best_ncr = curr_ncr
                        best_solution = curr_solution[:]
                else:
                    C += 1
                    if C == C_max:
                        print(best_ncr)
                        break
                    
                # we store the bandwidth of the trunk with the highest
                # congestion (in the congested direction)
                initial_bw = getattr(AS_links[ct_id], 'traffic' + cd)
                    
                # we'll increase the cost of the congested trunk, until
                # at least one traffic is rerouted (in such a way that it will
                # no longer use the congested trunk)
                for k in range(5):
                    #print(k)
                    AS_links[ct_id].__dict__['cost' + cd] += n // 5
                    # we update the solution being evaluated and append
                    # it to the tabu list
                    curr_solution[ct_id*2 + (cd == 'DS')] += n // 5
                    
                    tabu_list.append(curr_solution)
                    
                    self.route()
                    
                    new_bw = getattr(AS_links[ct_id], 'traffic' + cd)
                    
                    if new_bw != initial_bw:
                        break
                else:
                    C = C_max - 1
                

        for id, cost in enumerate(best_solution):
            setattr(AS_links[id//2], 'cost' + ('DS'*(id%2) or 'SD'), cost)
        self.route()
        ncr, ct_id, cd = self.ncr_computation(AS_links)
        print(ncr)
        
    ## Optical networks: routing and wavelength assignment
    
    def RWA_graph_transformation(self, name=None):
        
        # we compute the path of all traffic trunks
        self.path_finder()
        graph_sco = self.cs.ms.add_scenario(name)
        
        # in the new graph, each node corresponds to a traffic path
        # we create one node per traffic trunk in the new scenario            
        visited = set()
        # tl stands for traffic trunk
        for tlA in self.pn['traffic'].values():
            for tlB in self.pn['traffic'].values():
                if tlB not in visited and tlA != tlB:
                    if set(tlA.path) & set(tlB.path):
                        nA, nB = tlA.name, tlB.name
                        name = '{} - {}'.format(nA, nB)
                        graph_sco.ntw.lf(
                                         s = graph_sco.ntw.nf(
                                                              name = nA,
                                                              node_type = 'oxc'
                                                              ),
                                         d = graph_sco.ntw.nf(
                                                              name = nB,
                                                              node_type = 'oxc'
                                                              ),
                                         name = name
                                         )
            visited.add(tlA)
                            
        graph_sco.draw_all(False)
        return graph_sco
        
    def largest_degree_first(self):
        # we color the transformed graph by allocating colors to largest
        # degree nodes:
        # 1) we select the largest degree uncolored oxc
        # 2) we look at the adjacent vertices and select the minimum indexed
        # color not yet used by adjacent vertices
        # 3) when everything is colored, we stop
        
        # we will use a dictionary that binds oxc to the color it uses.
        oxc_color = dict.fromkeys(self.ftr('node', 'oxc'), None)
        # and a list that contains all vertices that we have yet to color
        uncolored_nodes = list(oxc_color)
        # we will use a function that returns the degree of a node to sort
        # the list in ascending order
        uncolored_nodes.sort(key = lambda node: len(self.graph[node.id]['trunk']))
        # and pop nodes one by one
        while uncolored_nodes:
            largest_degree = uncolored_nodes.pop()
            # we compute the set of colors used by adjacent vertices
            colors = set(oxc_color[neighbor] for neighbor, _ in
                                    self.graph[largest_degree.id]['trunk'])
            # we find the minimum indexed color which is available
            min_index = [i in colors for i in range(len(colors) + 1)].index(0)
            # and assign it to the current oxc
            oxc_color[largest_degree] = min_index
            
        number_lambda = max(oxc_color.values()) + 1
        print(number_lambda)
        return number_lambda
        
    def LP_RWA_formulation(self, K=10):

        # Solves the MILP: minimize c'*x
        #         subject to G*x + s = h
        #                     A*x = b
        #                     s >= 0
        #                     xi integer, forall i in I

        # we note x_v_wl the variable that defines whether wl is used for 
        # the path v (x_v_wl = 1) or not (x_v_wl = 0)
        # we construct the vector of variable the following way:
        # x = [x_1_0, x_2_0, ..., x_V_0, x_1_1, ... x_V-1_K-1, x_V_K-1]
        # that is, [(x_v_0) for v in V, ..., (x_v_K) for wl in K]
        
        # V is the total number of path (i.e the total number of trunks
        # in the transformed graph)
        V, T = len(self.pn['node']), len(self.pn['trunk'])
        
        # for the objective function, which must minimize the sum of y_wl, 
        # that is, the number of wavelength used
        c = np.concatenate([np.zeros(V * K), np.ones(K)])
        
        # for a given path v, we must have sum(x_v_wl for wl in K) = 1
        # which ensures that each optical path uses only one wavelength
        # for each path v, we must create a vector with all x_v_wl set to 1
        # for the path v, and the rest of it set to 0.
        A = []
        for path in range(V):
            row = [float(K * path <= i < K * (path + 1)) for i in range(V * K)] 
            row += [0.] * K
            A.append(row)
            
        b = np.ones(V)
        
        G2 = []
        for i in range(K):
            for trunk in self.pn['trunk'].values():
                p_src, p_dest = trunk.source, trunk.destination
                # we want to ensure that paths that have at least one trunk in 
                # common are not assigned the same wavelength.
                # this means that x_v_src_i + x_v_dest_i <= y_i
                row = []
                # vector of x_v_wl: we set x_v_src_i and x_v_dest_i to 1
                for path in self.pn['node'].values():
                    for j in range(K):
                        row.append(float(
                                         (path == p_src or path == p_dest)
                                                        and
                                                       i == j
                                         )
                                   )
                # we continue filling the vector with the y_wl
                # we want to have x_v_src_i + x_v_dest_i - y_i <= 0
                # hence the 'minus' sign instead of float
                for j in range(K):
                    row.append(-float(i == j))
                G2.append(row)
        # G2 size should be K * T (rows) x K * (V + 1) (columns)

        # finally, we want to ensure that wavelength are used in 
        # ascending order, meaning that y_wl >= y_(wl + 1) for wl 
        # in [0, K-1]. We can rewrite it y_(wl + 1) - y_wl <= 0
        G3 = []
        for i in range(1, K):
            row_wl = [float(
                            (i == wl)
                                or 
                            -(i == wl + 1)
                            )
                        for wl in range(K)
                      ]
            final_row = np.concatenate([np.zeros(V * K), row_wl])
            G3.append(final_row)
        # G3 size should be K - 1 (rows) x K * (V + 1) (columns)

        h = np.concatenate([
                            # x_v_src_i + x_v_dest_i - y_i <= 0
                            np.zeros(K * T),
                            # y_(wl + 1) - y_wl <= 0
                            np.zeros(K - 1)
                            ])

        G = np.concatenate((G2, G3), axis=0).tolist()
        A, G, b, c, h = map(matrix, (A, G, b, c, h))
    
        binvar = set(range(K * (V + 1)))
        solsta, x = glpk.ilp(c, G.T, h, A.T, b, B=binvar)
        
        warnings.warn(str(int(sum(x[-K:]))))
        return int(sum(x[-K:]))
        
    ## Distance functions
    
    def distance(self, p, q): 
        return sqrt(p*p + q*q)
        
    def haversine_distance(self, s, d):
        ''' Earth distance between two nodes '''
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
    # - cf is the Coulomb factor (repulsive force factor)
    # - sf is the speed factor
    
    def coulomb_force(self, dx, dy, dist, cf):
        c = dist and cf/dist**3
        return (-c*dx, -c*dy)
        
    def hooke_force(self, dx, dy, dist, L0, k):
        const = dist and k*(dist - L0)/dist
        return (const*dx, const*dy)
            
    def spring_layout(self, nodes, cf, k, sf, L0, v_nodes=set()):
        nodes = set(nodes)
        for nodeA in nodes:
            Fx = Fy = 0
            for nodeB in nodes | v_nodes | set(self.neighbors(nodeA, 'trunk')):
                if nodeA != nodeB:
                    dx, dy = nodeB.x - nodeA.x, nodeB.y - nodeA.y
                    dist = self.distance(dx, dy)
                    F_hooke = (0,)*2
                    if self.is_connected(nodeA, nodeB, 'trunk'):
                        F_hooke = self.hooke_force(dx, dy, dist, L0, k)
                    F_coulomb = self.coulomb_force(dx, dy, dist, cf)
                    Fx += F_hooke[0] + F_coulomb[0] * nodeB.virtual_factor
                    Fy += F_hooke[1] + F_coulomb[1] * nodeB.virtual_factor
            nodeA.vx = 0.5 * nodeA.vx + 0.2 * Fx
            nodeA.vy = 0.5 * nodeA.vy + 0.2 * Fy
    
        for node in nodes:
            node.x += round(node.vx * sf)
            node.y += round(node.vy * sf)
            
    ## 2) Fruchterman-Reingold algorithms
    
    def fa(self, d, k):
        return (d**2)/k
    
    def fr(self, d, k):
        return -(k**2)/d
        
    def fruchterman_reingold_layout(self, nodes, opd, limit):
        t = 1
        if not opd:
            opd = sqrt(1200*700/len(self.pn['trunk']))
        opd /= 3
        for nA in nodes:
            nA.vx, nA.vy = 0, 0
            for nB in nodes:
                if nA != nB:
                    deltax = nA.x - nB.x
                    deltay = nA.y - nB.y
                    dist = self.distance(deltax, deltay)
                    if dist:
                        nA.vx += deltax * opd**2 / dist**2
                        nA.vy += deltay * opd**2 / dist**2   
                    
        for l in self.pn['trunk'].values():
            deltax = l.source.x - l.destination.x
            deltay = l.source.y - l.destination.y
            dist = self.distance(deltax, deltay)
            if dist:
                l.source.vx -= dist * deltax / opd
                l.source.vy -= dist * deltay / opd
                l.destination.vx += dist * deltax / opd
                l.destination.vy += dist * deltay / opd
            
        for n in nodes:
            d = self.distance(n.vx, n.vy)
            n.x += n.vx / sqrt(d)
            n.y += n.vy / sqrt(d)
            if limit:
                n.x = min(800, max(0, n.x))
                n.y = min(800, max(0, n.y))
            
        t *= 0.95
        
    ## 3) BFS-clusterization spring-based algorithm
    
    def bfs_cluster(self, source, visited, stop=30):
        node_number = 0
        cluster = set()
        frontier = {source}
        while frontier and node_number < stop:
            temp = frontier
            frontier = set()
            for node in temp:
                for neighbor, _ in self.graph[node.id]['trunk']:
                    if node not in visited:
                        frontier.add(neighbor)
                        node_number += 1
                cluster.add(node)
        return frontier, cluster
        
    def create_virtual_nodes(self, cluster, nb):
        n = len(cluster)
        mean_value = lambda axe: sum(getattr(node, axe) for node in cluster)
        x_mean, y_mean = mean_value('x')/n , mean_value('y')/n
        virtual_node = self.nf(name = 'vn' + str(nb), node_type = 'cloud')
        virtual_node.x, virtual_node.y = x_mean, y_mean
        virtual_node.virtual_factor = n
        return virtual_node
    
    def bfs_spring(self, nodes, cf, k, sf, L0, size=40, iterations=10):
        nodes = set(nodes)
        source = random.choice(list(nodes))
        # all nodes one step ahead of the already drawn area
        overall_frontier = {source}
        # all nodes which location has already been set
        seen = set(self.pn['node'].values()) - nodes
        # virtuals nodes are the centers of previously clusterized area:
        # they are not connected to any another node, but are equivalent to a
        # coulomb forces of all cluster nodes
        virtual_nodes = set()
        # number of cluster
        nb_cluster = 0
        # total number of nodes
        n = len(self.pn['node'])
        while overall_frontier:
            new_source = overall_frontier.pop()
            new_frontier, new_cluster = self.bfs_cluster(new_source, seen, size)
            nb_cluster += 1
            overall_frontier |= new_frontier
            seen |= new_cluster
            overall_frontier -= seen
            i = 0
            for i in range(iterations):
                self.spring_layout(new_cluster, cf, k, sf, L0, virtual_nodes)
            virtual_nodes.add(self.create_virtual_nodes(new_cluster, nb_cluster))
        for node in virtual_nodes:
            self.name_to_id.pop(node.name)
            self.pn['node'].pop(node.id)

        
    ## Graph generation functions
                
    ## 1) Tree generation
                
    def tree(self, n, subtype):
        for i in range(2**n-1):
            n1, n2, n3 = str(i), str(2*i+1), str(2*i+2)
            self.lf(
                    s = self.nf(name = n1, node_type = subtype), 
                    d = self.nf(name = n2, node_type = subtype)
                    )
            self.lf(
                    s = self.nf(name = n1, node_type = subtype), 
                    d = self.nf(name = n3, node_type = subtype)
                    )
            
    ## 2) Star generation
            
    def star(self, n, subtype):
        nb_node = len(self.pn['node'])
        for i in range(n):
            n1, n2 = str(nb_node), str(nb_node+1+i)
            self.lf(
                    s = self.nf(name = n1, node_type = subtype), 
                    d = self.nf(name = n2, node_type = subtype)
                    )
            
    ## 3) Full-meshed network generation
            
    def full_mesh(self, n, subtype):
        nb_node = len(self.pn['node'])
        for i in range(n):
            for j in range(i):
                n1, n2 = str(nb_node+j), str(nb_node+i)
                self.lf(
                        s = self.nf(name = n1, node_type = subtype), 
                        d = self.nf(name = n2, node_type = subtype)
                        )
                
    ## 4) Ring generation
                
    def ring(self, n, subtype):
        nb_node = len(self.pn['node'])
        for i in range(n):
            n1, n2 = str(nb_node+i), str(nb_node+(1+i)%n)
            self.lf(
                    s = self.nf(name = n1, node_type = subtype), 
                    d = self.nf(name = n2, node_type = subtype)
                    )
                    
    ## 5) Square tiling generation
            
    def square_tiling(self, n, subtype):
        for i in range(n**2):
            n1, n2, n3 = str(i), str(i-1), str(i+n)
            if i-1 > -1 and i%n:
                self.lf(
                        s = self.nf(name = n1, node_type = subtype), 
                        d = self.nf(name = n2, node_type = subtype)
                        )
            if i+n < n**2:
                self.lf(
                        s = self.nf(name = n1, node_type = subtype), 
                        d = self.nf(name = n3, node_type = subtype)
                        )
        print(len(self.pn['node']), len(self.pn['trunk']))
                    
    ## 6) Hypercube generation
            
    def hypercube(self, n, subtype):
        # we create a n-dim hypercube by connecting two (n-1)-dim hypercubes
        i = 0
        graph_nodes = [self.nf(name=str(0), node_type=subtype)]
        graph_trunks = []
        while i < n+1:
            for k in range(len(graph_nodes)):
                # creation of the nodes of the second hypercube
                graph_nodes.append(
                                   self.nf(
                                           name = str(k+2**i), 
                                           node_type = subtype
                                           )
                                   )
            for trunk in graph_trunks[:]:
                # connection of the two hypercubes
                source, destination = trunk.source, trunk.destination
                n1 = str(int(source.name) + 2**i)
                n2 = str(int(destination.name) + 2**i)
                graph_trunks.append(
                                   self.lf(
                                           s = self.nf(name = n1), 
                                           d = self.nf(name = n2)
                                           )
                                   )
            for k in range(len(graph_nodes)//2):
                # creation of the trunks of the second hypercube
                graph_trunks.append(
                                   self.lf(
                                           s = graph_nodes[k], 
                                           d = graph_nodes[k+2**i]
                                           )
                                   )
            i += 1
                    
    ## 7) Generalized Kneser graph
    
    def kneser(self, n, k, subtype):
        # we keep track of what set we've seen to avoid having
        # duplicated edges in the graph, with the 'already_done' set
        already_done = set()
        for setA in map(set, combinations(range(1, n), k)):
            already_done.add(frozenset(setA))
            for setB in map(set, combinations(range(1, n), k)):
                if setB not in already_done and not setA & setB:
                    self.lf(
                            s = self.nf(name = str(setA), node_type = subtype), 
                            d = self.nf(name = str(setB), node_type = subtype)
                            )
                            
    ## 8) Generalized Petersen graph
    
    def petersen(self, n, k, subtype):
        # the petersen graph is made of the vertices (u_i) and (v_i) for 
        # i in [0, n-1] and the edges (u_i, u_i+1), (u_i, v_i) and (v_i, v_i+k).
        # to build it, we consider that v_i = u_(i+n).
        for i in range(n):
            # (u_i, u_i+1) edges
            self.lf(
                    s = self.nf(name = str(i), node_type = subtype), 
                    d = self.nf(name = str((i + 1)%n), node_type = subtype)
                    )
            # (u_i, v_i) edges
            self.lf(
                    s = self.nf(name = str(i), node_type = subtype), 
                    d = self.nf(name = str(i + n), node_type = subtype)
                    )
            # (v_i, v_i+k) edges
            self.lf(
                    s = self.nf(name = str(i + n), node_type = subtype), 
                    d = self.nf(name = str((i + n + k)%n + n), node_type = subtype)
                    )
                    
    ## Multiple object creation
    
    def multiple_nodes(self, n, subtype):
        nb_nodes = len(self.pn['node'])
        for k in range(n):
            yield self.nf(name = str(k + nb_nodes), node_type = subtype)
            
    def multiple_links(self, source_nodes, destination_node):
        # create a link between the destination node and all source nodes
        for src_node in source_nodes:
            # in the multiple link window, the source nodes are not excluded,
            # so we check that both nodes are different before creating the link
            if src_node != destination_node:
                self.lf(s=src_node, d=destination_node)
            