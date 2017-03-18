# NetDim
# Copyright (C) 2017 Antoine Fourmy (contact@netdim.fr)
# Released under the GNU General Public License GPLv3

from objects.objects import *
from collections import defaultdict
from math import sqrt

class BaseNetwork(object):
    
    def __init__(self, scenario):
        self.nodes = {}
        self.plinks = {}
        self.l2links = {}
        self.l3links = {}
        self.traffics = {}
        
        # pn for 'pool network'
        self.pn = {
                   'node': self.nodes, 
                   'plink': self.plinks, 
                   'l2link': self.l2links, 
                   'l3link': self.l3links,
                   'traffic': self.traffics, 
                   }
        self.cs = scenario
        self.graph = defaultdict(lambda: defaultdict(set))
        self.cpt_link = self.cpt_node = self.cpt_AS = 1
        # useful for tests and listbox when we want to retrieve an object
        # based on its name. The only object that needs changing when a object
        # is renamed by the user.
        self.name_to_id = {}
        
        # set of all objects in failure: this parameter is used for
        # link dimensioning and failure simulation
        self.failed_obj = set()
        
        # property -> type associations 
        self.prop_to_type = {
        'capacitySD': int, 
        'capacityDS': int,
        'costSD': float, 
        'costDS': float, 
        'cost': float,
        'destination': self.convert_node, 
        'distance': float, 
        'flowSD': float,
        'flowDS': float,
        'interface': str,
        'interfaceS': str,
        'interfaceD': str,
        'ipaddress': str,
        'lambda_capacity': int,
        'latitude': float,
        'LB_paths': int,
        'longitude': float, 
        'logical_x': float,
        'logical_y': float,
        'macaddress': str,
        'name': str,
        'node': self.convert_node, 
        'protocol': str,
        'sntw': str,
        'source': self.convert_node,
        'subnetmask': str,
        'throughput': float,
        'traffic': float,
        'trafficSD': float,
        'trafficDS': float,
        'wctrafficSD': float,
        'wctrafficDS': float,
        'wcfailure': str,
        'x': float, 
        'y': float, 
        'link': self.convert_link, 
        'linkS': self.convert_link, 
        'linkD': self.convert_link, 
        'nh_tk': str,
        'nh_ip': str,
        'bgp_AS': str,
        'weightS': int,
        'weightD': int,
        'dst_sntw': str,
        'ad': int,
        'subtype': str,
        'bgp_type': str,
        'lsp_type': str,
        'path_constraints': self.convert_node_list, 
        'excluded_nodes': self.convert_node_set,
        'excluded_plinks': self.convert_link_set, 
        'path': self.convert_link_list, 
        'subnets': str, 
        'sites': str,
        'role': str,
        'priority': int,
        'router_id': str,
        'base_macaddress': str,
        'LB_paths': int,
        'role': str,
        'priority': int,
        'router_id': str
        }
        
    # function filtering pn to retrieve all objects of given subtypes
    def ftr(self, type, *sts):
        keep = lambda r: r.subtype in sts
        if type == 'interface':
            return filter(keep, self.pn[type])
        else:
            return filter(keep, self.pn[type].values())
        
    # function filtering graph to retrieve all links of given subtypes
    # attached to the source node. 
    # if ud (undirected) is set to True, we retrieve all links of the 
    # corresponding subtypes, else we check that 'src' is the source
    def gftr(self, src, type, *sts, ud=True):
        keep = lambda r: r[1].subtype in sts and (ud or r[1].source == src)
        return filter(keep, self.graph[src.id][type])
          
    # 'lf' is the link factory. Creates or retrieves any type of link
    def lf(self, subtype='ethernet', id=None, name=None, **kwargs):
        link_type = subtype_to_type[subtype]
        # creation link in the s-d direction if no link at all yet
        if not id:
            if name in self.name_to_id:
                return self.pn[link_type][self.name_to_id[name]]
            s, d = kwargs['source'], kwargs['destination']
            id = self.cpt_link
            if not name:
                name = subtype + str(len(list(self.ftr(link_type, subtype))))
            kwargs.update({'id': id, 'name': name})
            new_link = link_class[subtype](**kwargs)
            self.name_to_id[name] = id
            self.pn[link_type][id] = new_link
            self.graph[s.id][link_type].add((d, new_link))
            self.graph[d.id][link_type].add((s, new_link))
            if subtype in ('ethernet', 'wdm'):
                self.interfaces |= {new_link.interfaceS, new_link.interfaceD}
            self.cpt_link += 1
        return self.pn[link_type][id]
        
    # 'nf' is the node factory. Creates or retrieves any type of nodes
    def nf(self, node_type='router', id=None, **kwargs):
        if not id:
            if 'name' not in kwargs:
                name = node_type + str(len(list(self.ftr('node', node_type))))
                kwargs['name'] = name
            else:
                if kwargs['name'] in self.name_to_id:
                    return self.nodes[self.name_to_id[kwargs['name']]]
            id = self.cpt_node
            kwargs['id'] = id
            self.nodes[id] = node_class[node_type](**kwargs)
            self.name_to_id[kwargs['name']] = id
            self.cpt_node += 1
        return self.nodes[id]
        
    # 'of' is the object factory: returns a link or a node from its name
    def of(self, name, _type):
        if _type == 'node':
            return self.nf(name=name)
        else:
            return self.lf(name=name)
            
    ## Conversion methods and property -> type mapping
    
    # methods used to convert a string to an object 
    
    # convert a node name to a node
    def convert_node(self, node_name):
        return self.nf(name=node_name)
    
    # convert a link name to a node
    def convert_link(self, link_name, subtype='ethernet'):
        return self.lf(name=link_name, subtype=subtype)
    
    # convert a string representing a set of nodes, to an actual set of nodes
    def convert_node_set(self, node_set):
        return set(map(self.convert_node, eval(node_set)))
    
    # convert a string representing a list of nodes, to an actual list of nodes
    def convert_node_list(self, node_list):
        return list(map(self.convert_node, eval(node_list)))
    
    # convert a string representing a set of links, to an actual set of links
    def convert_link_set(self, link_set, subtype='ethernet'):
        convert = lambda link: self.convert_link(link, subtype)
        return set(map(convert, eval(link_set)))
    
    # convert a string representing a list of links, to an actual list of links
    def convert_link_list(self, link_list, subtype='ethernet'):
        convert = lambda link: self.convert_link(link, subtype)
        return list(map(convert, eval(link_list)))
            
    def erase_network(self):
        self.graph.clear()
        for dict_of_objects in self.pn.values():
            dict_of_objects.clear()
            
    def remove_node(self, node):
        self.nodes.pop(self.name_to_id.pop(node.name))
        # retrieve adj links to delete them 
        dict_of_adj_links = self.graph.pop(node.id, {})
        for type_link, adj_obj in dict_of_adj_links.items():
            for neighbor, adj_link in adj_obj:
                yield adj_link

    def remove_link(self, link):
        # if it is a physical link, remove the link's interfaces from the model
        if link.type == 'plink':
            self.interfaces -= {link.interfaceS, link.interfaceD}
        # remove the link itself from the model
        self.graph[link.source.id][link.type].discard((link.destination, link))
        self.graph[link.destination.id][link.type].discard((link.source, link))
        self.pn[link.type].pop(self.name_to_id.pop(link.name))
            
    def is_connected(self, nodeA, nodeB, link_type, subtype=None):
        if not subtype:
            return any(n == nodeA for n, _ in self.graph[nodeB.id][link_type])
        else:
            return any(n == nodeA for n, _ in self.gftr(nodeB, link_type, subtype))
        
    # given a node, retrieves nodes attached with a link which subtype 
    # is in sts
    def neighbors(self, node, *subtypes):
        for subtype in subtypes:
            for neighbor, _ in self.graph[node.id][subtype]:
                yield neighbor
                
    # given a node, retrieves all attached links    
    def attached_links(self, node):
        for link_type in self.link_type:
            for _, link in self.graph[node.id][link_type]:
                yield link
        
    def number_of_links_between(self, nodeA, nodeB):
        return sum(
                   n == nodeB 
                   for _type in self.link_type 
                   for n, _ in self.graph[nodeA.id][_type]
                   )
        
    def links_between(self, nodeA, nodeB, _type='all'):
        if _type == 'all':
            for type in link_type:
                for neighbor, link in self.graph[nodeA.id][type]:
                    if neighbor == nodeB:
                        yield link
        else:
            for neighbor, link in self.graph[nodeA.id][_type]:
                if neighbor == nodeB:
                    yield link
                                                
    ## Graph functions
    
    def bfs(self, source):
        visited = set()
        layer = {source}
        while layer:
            temp = layer
            layer = set()
            for node in temp:
                if node not in visited:
                    visited.add(node)
                    for neighbor, _ in self.graph[node.id]['plink']:
                        layer.add(neighbor)
                        yield neighbor
    
    def connected_components(self):
        visited = set()
        for node in self.nodes.values():
            if node not in visited:
                new_comp = set(self.bfs(node))
                visited.update(new_comp)
                yield new_comp
        
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
            for nodeB in nodes | v_nodes | set(self.neighbors(nodeA, 'plink')):
                if nodeA != nodeB:
                    dx, dy = nodeB.x - nodeA.x, nodeB.y - nodeA.y
                    dist = self.distance(dx, dy)
                    F_hooke = (0,)*2
                    if self.is_connected(nodeA, nodeB, 'plink'):
                        F_hooke = self.hooke_force(dx, dy, dist, L0, k)
                    F_coulomb = self.coulomb_force(dx, dy, dist, cf)
                    Fx += F_hooke[0] + F_coulomb[0] * nodeB.virtual_factor
                    Fy += F_hooke[1] + F_coulomb[1] * nodeB.virtual_factor
            nodeA.vx = max(-100, min(100, 0.5 * nodeA.vx + 0.2 * Fx))
            nodeA.vy = max(-100, min(100, 0.5 * nodeA.vy + 0.2 * Fy))
    
        for node in nodes:
            node.x += round(node.vx * sf)
            node.y += round(node.vy * sf)
            
    ## 2) Fruchterman-Reingold algorithms
    
    def fa(self, d, k):
        return (d**2)/k
    
    def fr(self, d, k):
        return -(k**2)/d
        
    def fruchterman_reingold_layout(self, nodes, limit, opd=0):
        t = 1
        if not opd:
            opd = sqrt(1200*700/len(self.plinks))
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
                    
        for l in self.plinks.values():
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
                for neighbor, _ in self.graph[node.id]['plink']:
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
    
    def bfs_spring(self, nodes, cf, k, sf, L0, vlinks, size=40, iterations=3):
        nodes = set(nodes)
        source = random.choice(list(nodes))
        # all nodes one step ahead of the already drawn area
        overall_frontier = {source}
        # all nodes which location has already been set
        seen = set(self.nodes.values()) - nodes
        # virtuals nodes are the centers of previously clusterized area:
        # they are not connected to any another node, but are equivalent to a
        # coulomb forces of all cluster nodes
        virtual_nodes = set()
        # dict to associate a virtual node to its frontier
        # knowing this association will later allow us to create links
        # between virtual nodes before applying a spring algorithm to virtual
        # nodes
        vnode_to_frontier = {}
        # dict to keep track of all virtual node <-> cluster association
        # this allows us to recompute all cluster nodes position after 
        # applying the spring algorithm on virtual nodes
        vnode_to_cluster = {}
        # number of cluster
        nb_cluster = 0
        # total number of nodes
        n = len(self.nodes)
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
            new_vnode = self.create_virtual_nodes(new_cluster, nb_cluster)
            vnode_to_cluster[new_vnode] = new_cluster
            vnode_to_frontier[new_vnode] = new_frontier
            virtual_nodes |= {new_vnode}
        
        if vlinks:
            # we create virtual links between virtual nodes, whenever needed
            for vnodeA in virtual_nodes:
                for vnodeB in virtual_nodes:
                    if vnode_to_cluster[vnodeA] & vnode_to_frontier[vnodeB]:
                        self.lf(source=vnodeA, destination=vnodeB)
        
        # we then apply a spring algorithm on the virtual nodes only
        # we first store the initial position to compute the difference 
        # with the position after the algorithm has been executed
        # we then move all clusters nodes by the same difference
        initial_position = {}
        for vnode in virtual_nodes:
            initial_position[vnode] = (vnode.x, vnode.y)
        for i in range(iterations):
            self.spring_layout(virtual_nodes, cf, k, sf, L0)
        for vnode, cluster in vnode_to_cluster.items():
            x0, y0 = initial_position[vnode]
            dx, dy = vnode.x - x0, vnode.y - y0
            for node in cluster:
                node.x, node.y = node.x + dx, node.y + dy
                        
        for node in virtual_nodes:
            for link in self.remove_node(node):
                self.remove_link(link)
