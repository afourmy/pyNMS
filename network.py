from collections import defaultdict
from heapq import heappop, heappush
import link
import node
import AS
import math
import random

class Network(object):
    
    node_type_to_class = {
    "router": node.Router,
    "oxc": node.OXC,
    "host": node.Host,
    "antenna": node.Antenna
    }
    
    link_type_to_class = {
    "trunk": link.Trunk, 
    "route": link.Route,
    "traffic": link.Traffic
    }
    
    def __init__(self, name):
        self.name = name
        self.pool_network = {"trunk": {}, "node": {}, "route": {}, "traffic": {}, "AS": {}}
        self.graph = defaultdict(lambda: defaultdict(set))
            
    def link_factory(self, link_type="trunk", name=None, s=None, d=None, *param):
        if not name:
            name = link_type + str(len(self.pool_network[link_type]))
        # creation link in the s-d direction if no link at all yet
        if not name in self.pool_network[link_type]:
            new_link = Network.link_type_to_class[link_type](name, s, d, *param)
            self.pool_network[link_type][name] = new_link
            self.graph[s][link_type].add(new_link)
            self.graph[d][link_type].add(new_link)
        return self.pool_network[link_type][name]
        
    def node_factory(self, name=None, node_type="router", pos_x=100, pos_y=100):
        if not name:
            name = "node" + str(len(self.pool_network["node"]))
        if name not in self.pool_network["node"]:
            self.pool_network["node"][name] = Network.node_type_to_class[node_type](name, pos_x, pos_y)
        return self.pool_network["node"][name]
        
    def AS_factory(self, name=None, type="RIP", links=set()):
        if not name:
            name = "AS" + str(len(self.pool_network["AS"]))
        if name not in self.pool_network["AS"]:
            self.pool_network["AS"][name] = AS.AutonomousSystem(name, type, links)
        return self.pool_network["AS"][name]
            
    def erase_network(self):
        self.graph.clear()
        for dict_of_objects in self.pool_network:
            self.pool_network[dict_of_objects].clear()
            
    def remove_node_from_network(self, node):
        self.pool_network["node"].pop(node.name, None)
        # je récupère les noeuds adjacents pour supprimer les liens
        dict_of_connected_links = self.graph.pop(node, None)
        if(dict_of_connected_links): # en cas de multiple deletion, peut être None
            for type_link in dict_of_connected_links.keys():
                for connected_link in dict_of_connected_links[type_link]:
                    neighbor = connected_link.destination if node == connected_link.source else connected_link.source
                    self.graph[neighbor][type_link].discard(connected_link)
                    yield self.pool_network[type_link].pop(connected_link.name, None)
            
    def remove_link_from_network(self, link):
        self.graph[link.source][link.type].discard(link)
        self.graph[link.destination][link.type].discard(link)
        self.pool_network[link.type].pop(link.name, None)
        
    # this function relates to AS but must be in network, because we need to 
    # know what's not in the AS to find the edge nodes
    def find_edge_nodes(self, AS):
        AS.edges.clear()
        for node in AS.nodes:
            if(any(link not in AS.links for link in self.graph[node]["trunk"])):
                AS.edges.add(node)
                yield node
            
    def is_connected(self, nodeA, nodeB, link_type):
        return any(l.source == nodeA or l.destination == nodeA for l in self.graph[nodeB][link_type])
        
    def number_of_links_between(self, nodeA, nodeB):
        sum = 0
        for link_type in ["trunk", "route", "traffic"]:
            for link in self.graph[nodeA][link_type]:
                if(link.source == nodeB or link.destination == nodeB):
                    sum += 1
        return sum
            
    def fast_graph_definition(self, string):
        """ Allow to create graph quickly with a single string """
        for source, destination in zip(string[::2], string[1::2]):
            source, destination = self.node_factory(source), self.node_factory(destination)
            trunk = self.link_factory(source, destination)
        
    def _bfs(self, source):
        visited = set()
        layer = {source}
        while layer:
            temp = layer
            layer = set()
            for node in temp:
                if node not in visited:
                    visited.add(node)
                    layer.update(self.graph[node])
                    yield node

                    
    def connected_components(self):
        visited = set()
        connected_components = []
        for node in self.graph:
            if node not in visited:
                new_connected_set = set(self._bfs(node))
                connected_components.append(new_connected_set)
                visited.update(new_connected_set)
        return connected_components
            
    def hop_count(self, source, target, excluded_trunks=None, excluded_nodes=None, path_constraints=None, allowed_trunks=None, allowed_nodes=None):
        # Complexity: O(|V| + |E|log|V|)
        
        # initialize parameters
        if(excluded_nodes is None):
            excluded_nodes = []
        if(excluded_trunks is None):
            excluded_trunks = []
        if(path_constraints is None):
            path_constraints = []
        if(allowed_trunks is None):
            allowed_trunks = self.pool_network["trunk"].values()
        if(allowed_nodes is None):
            allowed_nodes = self.pool_network["node"].values()
            print(allowed_nodes)
            
        full_path_node, full_path_link = [], []
        constraints = [source] + path_constraints + [target]
        for s, t in zip(constraints, constraints[1:]):
            # find the SP from s to t
            prec_node = {i: None for i in allowed_nodes}
            prec_link = {i: None for i in allowed_nodes}
            visited = {i: False for i in allowed_nodes}
            dist = {i: float('inf') for i in allowed_nodes}
            dist[s] = 0
            heap = [(0, s)]
            while heap:
                dist_node, node = heappop(heap)  
                if not visited[node]:
                    visited[node] = True
                    if node == t:
                        break
                    for connected_link in self.graph[node]["trunk"]:
                        neighbor = connected_link.destination if node == connected_link.source else connected_link.source
                        # excluded and allowed nodes
                        if neighbor in excluded_nodes or neighbor not in allowed_nodes: continue
                        # excluded and allowed trunks
                        if connected_link in excluded_trunks or connected_link not in allowed_trunks: continue
                        dist_neighbor = dist_node + 1
                        if dist_neighbor < dist[neighbor]:
                            dist[neighbor] = dist_neighbor
                            prec_node[neighbor] = node
                            prec_link[neighbor] = connected_link
                            heappush(heap, (dist_neighbor, neighbor))
            
            # traceback the path from target to source
            if(visited[t]):
                curr, path_node, path_link = t, [t], [prec_link[t]]
                while(curr != s):
                    curr = prec_node[curr]
                    path_link.append(prec_link[curr])
                    path_node.append(curr)
                full_path_node += [path_node[:-1][::-1]]
                full_path_link += [path_link[:-1][::-1]]
            else:
                return [], []
        return sum(full_path_node, [source]), sum(full_path_link, [])
        
    def reset_flow(self):
        for link in self.pool_network["trunk"].values():
            link.flow["SD"] = 0
            link.flow["DS"] = 0
        
    def _augment_ff(self, val, current_node, target, visit):
        visit[current_node] = True
        if(current_node == target):
            return val
        for attached_link in self.graph[current_node]["trunk"]:
            neighbor = attached_link.destination if current_node == attached_link.source else attached_link.source
            direction = current_node == attached_link.source
            sd, ds = direction*"SD" or "DS", direction*"DS" or "SD"
            cap = attached_link.capacity[sd]
            current_flow = attached_link.flow[sd]
            if cap > current_flow and not visit[neighbor]:
                residual_capacity = min(val, cap - current_flow)
                global_flow = self._augment_ff(residual_capacity, neighbor, target, visit)
                if(global_flow > 0):
                    attached_link.flow[sd] += global_flow
                    attached_link.flow[ds] -= global_flow
                    return global_flow
        return False
        
    def ford_fulkerson(self, source, destination):
        n = len(self.pool_network["node"])
        self.reset_flow()
        while(self._augment_ff(float("inf"), source, destination, {n:0 for n in self.pool_network["node"].values()})):
            pass
        # flow leaving from the source 
        sum = 0
        for attached_link in self.graph[source]["trunk"]:
            sum += attached_link.flow[(source == attached_link.source)*"SD" or "DS"]
        return sum
        
    def route_flows(self):
        for flow in self.flows:
            constraints = flow.routing_policy.get_constraints()
            flow.path = self.constrained_hop_count(flow.ingress, flow.egress, *constraints)
            
    def distance(self, p, q): 
        return math.sqrt(p*p + q*q)
            
    def force_de_coulomb(self, dx, dy, dist, beta):
        c = dist and beta/dist**3
        return (-c*dx, -c*dy)
        
    def force_de_hooke(self, dx, dy, dist, dij, k):
        dl = dist - dij
        const = k * dl / dist
        return (const * dx, const * dy)
            
    def move_basic(self, alpha, beta, k, eta, delta, raideur):            
        for nodeA in self.pool_network["node"].values():
            Fx, Fy = 0, 0
            for nodeB in self.pool_network["node"].values():
                if(nodeA != nodeB):
                    dx, dy = nodeB.x - nodeA.x, nodeB.y - nodeA.y
                    dist = self.distance(dx, dy)
                    F_hooke, F_coulomb = [0]*2, [0]*2
                    if(self.is_connected(nodeA, nodeB, "trunk")):
                        F_hooke = self.force_de_hooke(dx, dy, dist, raideur, k) 
                    F_coulomb = self.force_de_coulomb(dx, dy, dist, beta)
                    Fx += F_hooke[0] + F_coulomb[0]
                    Fy += F_hooke[1] + F_coulomb[1]
            nodeA.vx = (nodeA.vx + alpha * Fx * delta) * eta
            nodeA.vy = (nodeA.vy + alpha * Fy * delta) * eta
    
        for n in self.pool_network["node"].values():
            n.x += round(n.vx * delta)
            n.y += round(n.vy * delta)
            
    def fa(self, d, k):
        return (d**2)/k
    
    def fr(self, d, k):
        return -(k**2)/d
        
    def fruchterman(self, k):
        t = 1
        for nA in self.pool_network["node"].values():
            nA.vx, nA.vy = 0, 0
            for nB in self.pool_network["node"].values():
                if(nA != nB):
                    deltax = nA.x - nB.x
                    deltay = nA.y - nB.y
                    dist = self.distance(deltax, deltay)
                    if(dist):
                        nA.vx += (deltay*(k**2))/dist**3
                        nA.vy += (deltay*(k**2))/dist**3                        
                    
        for l in filter(None,self.pool_network["trunk"].values()):
            deltax = l.source.x - l.destination.x
            deltay = l.source.y - l.destination.y
            dist = self.distance(deltax, deltay)
            if(dist):
                l.source.vx -= (dist*deltax)/k
                l.source.vy -= (dist*deltay)/k
                l.destination.vx += (dist*deltax)/k
                l.destination.vy += (dist*deltay)/k
            
        for n in self.pool_network["node"].values():
            d = self.distance(n.vx, n.vy)
            n.x += ((n.vx)/(math.sqrt(d)+0.1))
            n.y += ((n.vy)/(math.sqrt(d)+0.1))
            # n.x = min(700, max(0, n.x))
            # n.y = min(700, max(0, n.y))
            
        t *= 0.99
            
    def generate_hypercube(self, n):
        i = 0
        graph_nodes = [self.node_factory(str(0))]
        graph_links = []
        while(i < n+1):
            for k in range(len(graph_nodes)):
                # creation des noeuds du deuxième hypercube de dimension n-1
                graph_nodes.append(self.node_factory(str(k+2**i)))
            for trunk in graph_links[:]:
                # connexion des deux hypercube de dimension n-1
                source, destination = trunk.source, trunk.destination
                graph_links.append(self.link_factory(s=self.node_factory(str(int(source.name)+2**i)), d=self.node_factory(str(int(destination.name)+2**i))))
            for k in range(len(graph_nodes)//2):
                # creation des liens du deuxième hypercube
                graph_links.append(self.link_factory(s=graph_nodes[k], d=graph_nodes[k+2**i]))
            i += 1
            
    def generate_meshed_square(self, n):
        for i in range(n**2):
            if(i-1 > -1 and i%n):
                self.link_factory(s=self.node_factory(str(i)), d=self.node_factory(str(i-1)))
            if(i+n < n**2):
                self.link_factory(s=self.node_factory(str(i)), d=self.node_factory(str(i+n)))
                
    def generate_tree(self, n):
        for i in range(2**n-1):
            self.link_factory(s=self.node_factory(str(i)), d=self.node_factory(str(2*i+1)))
            self.link_factory(s=self.node_factory(str(i)), d=self.node_factory(str(2*i+2)))
            
    def generate_star(self, n):
        nb_node = len(self.pool_network["node"])
        for i in range(n):
            self.link_factory(s=self.node_factory(str(nb_node)), d=self.node_factory(str(nb_node+1+i)))
            
    def generate_full_mesh(self, n):
        nb_node = len(self.pool_network["node"])
        for i in range(n):
            for j in range(i):
                self.link_factory(s=self.node_factory(str(nb_node+j)), d=self.node_factory(str(nb_node+i)))
                
    def generate_ring(self, n):
        nb_node = len(self.pool_network["node"])
        for i in range(n):
            self.link_factory(s=self.node_factory(str(nb_node+i)), d=self.node_factory(str(nb_node+1+i)))
        self.link_factory(s=self.node_factory(str(nb_node)), d=self.node_factory(str(nb_node+n)))
            

    