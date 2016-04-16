path_app = "C:\\Users\\afourmy\\Desktop\\Sauvegarde\\Python\\Network"

# add the path to the module in sys.path
import sys
if path_app not in sys.path:
    sys.path.append(path_app)

from collections import defaultdict
from heapq import heappop, heappush
import link
import node
import LSP
import math

class Network(object):
    current_path = []
    pool_trunk={}
    pool_LSP={}
    
    def __init__(self, name):
        self.name = name
        self.nodes = set()
        self.trunks = set()
        self.flows = set()
        self.LSPs = set()
        self.graph = defaultdict(set)
        
    def add_nodes(self, *nodes):
        for node in nodes:
            self.nodes.add(node)
            if node not in self.graph.keys():
                self.graph[node] = set()
            
    def add_trunks(self, *trunks):
        for trunk in trunks:
            self.trunks.add(trunk)
            source, destination = trunk.source, trunk.destination
            self.nodes.update([source, destination])
            self.graph[source].add(destination)
            self.graph[destination].add(source)
            
    def trunk_factory(self, s, d):
        if (s, d) not in self.pool_trunk and (d, s) not in self.pool_trunk:
            self.pool_trunk[(s,d)] = link.Trunk(s, d)
            self.pool_trunk[(d,s)] = self.pool_trunk[(s,d)]
        return self.pool_trunk[(s,d)]
        
    def LSP_factory(self, *args):
        if args[0] not in self.pool_LSP:
            self.pool_LSP[args[0]] = LSP.LSP(*args)
        return self.pool_LSP[args[0]]
            
    def add_flow(self, *flows):
        for flow in flows:
            self.flows.add(flow)
            
    def clear(self):
        self.nodes.clear()
        self.trunks.clear()
        self.graph.clear()
        self.LSPs.clear()
        self.pool_trunk.clear()
        
    def remove_trunks(self, *trunks):
        for trunk in trunks:
            self.trunks.remove(trunk)
        source, destination = trunk.source, trunk.destination
        self.graph[source].discard(destination)
        self.graph[destination].discard(source)
            
    def remove_nodes(self, *nodes):
        self.nodes -= {node}
        adjacent_nodes = self.graph.pop(node, None)
        for neighbor in adjacent_nodes:
            self.graph[neighbor].discard(node)
            
    def is_connected(self, nodeA, nodeB):
        return nodeA in self.graph[nodeB]
            
    def fast_graph_definition(self, string):
        """ Allow to create graph quickly with a single string """
        for source, destination in zip(string[::2], string[1::2]):
            source, destination = node.Node(source), node.Node(destination)
            trunk = self.trunk_factory(source, destination)
            self.add_trunks(trunk)
        
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
            
    def hop_count(self, source, target, excluded_trunks=None, excluded_nodes=None, path_constraints=None):
        """
            Parameter self: we use self.graph view to compute the SP
            Parameter excluded_trunks: list of excluded trunks
            Parameter excluded_nodes: list of excluded nodes
            Returns: the path from the source to the target as an ordered list of nodes
            Complexity: O(|V| + |E|log|V|)
        """
        # initialize empty lists
        if(excluded_nodes is None):
            excluded_nodes = []
        if(excluded_trunks is None):
            excluded_trunks = []
        if(path_constraints is None):
            path_constraints = []
            
        full_path = []
        constraints = [source] + path_constraints + [target]
        for s, t in zip(constraints, constraints[1:]):
            # find the SP from s to t
            prec = {i: None for i in self.graph.keys()}
            visited = {i: False for i in self.graph.keys()}
            dist = {i: float('inf') for i in self.graph.keys()}
            dist[s] = 0
            heap = [(0, s)]
            while heap:
                dist_node, node = heappop(heap)  
                if not visited[node]:
                    visited[node] = True
                    if node == t:
                        break
                    for neighbor in self.graph[node]:
                        # excluded nodes
                        if neighbor in excluded_nodes: continue
                        # excluded links
                        if self.trunk_factory(node, neighbor) in excluded_trunks: continue
                        dist_neighbor = dist_node + int(node != neighbor)
                        if dist_neighbor < dist[neighbor]:
                            dist[neighbor] = dist_neighbor
                            prec[neighbor] = node
                            heappush(heap, (dist_neighbor, neighbor))
            
            # traceback the path from target to source
            if(visited[t]):
                curr, path = t, [t]
                while(curr != s):
                    curr = prec[curr]
                    path.append(curr)
                full_path += [path[:-1][::-1]]
            else:
                return "no path found"
        return sum(full_path, [source])
        
    def _augment(self, val, current_node, target, visit):
        visit[current_node] = True
        print(visit)
        if(current_node == target):
            return val
        for v in self.graph[current_node]:
            current_trunk = self.trunk_factory(current_node, v)
            cap = current_trunk.capacitySD
            current_flow = current_trunk.flowSD
            if cap > current_flow and not visit[v]:
                residual_capacity = min(val, cap - current_flow)
                global_flow = self._augment(residual_capacity, v, target, visit)
                if(global_flow):
                    current_trunk.flowSD += global_flow
                    current_trunk.flowDS -= global_flow
                    return global_flow
        return False
        
    def ford_fulkerson(self, source, destination):
        n = len(self.nodes)
        visit = {n:0 for n in self.nodes}
        i = 0
        while(self._augment(float("inf"), source, destination, visit) or i<5):
            print("lol")
            i += 1
        res = {t:t.flowSD for t in self.trunks}
        print(res)
        
    def route_flows(self):
        for flow in self.flows:
            constraints = flow.routing_policy.get_constraints()
            flow.path = self.constrained_hop_count(flow.ingress, flow.egress, *constraints)
    
    def show_flows_path(self):
        for flow in self.flows:
            print("Flow {} from {} to {}: {}\n".format(flow.name, flow.ingress, flow.egress, flow.path))
            
    def distance(self, p, q): 
        return math.sqrt(p*p + q*q)
            
    def force_de_coulomb(self, nodeA, nodeB, beta):
        dx, dy = nodeB.x - nodeA.x, nodeB.y - nodeA.y
        ds = self.distance(dx, dy)**3
        c = ds != 0 and beta/ds or 0
        return (-c*dx, -c*dy)
        
    def force_de_hooke(self, nodeA, nodeB, dij, k):
        dx, dy = nodeB.x - nodeA.x, nodeB.y - nodeA.y
        dl = self.distance(dx, dy) - dij
        const = k * dl / self.distance(dx, dy)
        return (const * dx, const * dy)
            
    def move_basic(self, alpha, beta, k, eta, delta, raideur):            
        ekint = [0.0, 0.0]
        for nodeA in self.nodes:
            Fx, Fy = 0, 0
            for nodeB in self.nodes:
                if(nodeA != nodeB):
                    Fij = [0]*4
                    if(self.is_connected(nodeA, nodeB)):
                        Fij[:2] = self.force_de_hooke(nodeA, nodeB, raideur, k) 
                    Fij[2:] = self.force_de_coulomb(nodeA, nodeB, beta)
                    Fx += Fij[0] + Fij[2]
                    Fy += Fij[1] + Fij[3]
            nodeA.vx = (nodeA.vx + alpha * Fx * delta) * eta
            nodeA.vy = (nodeA.vy + alpha * Fy * delta) * eta
            ekint[0] = ekint[0] + alpha * (nodeA.vx * nodeA.vx)
            ekint[1] = ekint[1] + alpha * (nodeA.vy * nodeA.vy)
    
        for n in self.nodes:
            n.x += n.vx * delta
            n.y += n.vy * delta
            
    def fa(self, d, k):
        return (d**2)/k
    
    def fr(self, d, k):
        return -(k**2)/d
        
    def fruchterman(self, k):
        t = 1
        for nA in self.nodes:
            nA.vx, nA.vy = 0, 0
            for nB in self.nodes:
                if(nA != nB):
                    deltax = nA.x - nB.x
                    deltay = nA.y - nB.y
                    dist = self.distance(deltax, deltay)
                    if(dist):
                        nA.vx += (deltay*(k**2))/dist**2
                        nA.vy += (deltay*(k**2))/dist**2                        
                    
        for l in self.trunks:
            deltax = l.source.x - l.destination.x
            deltay = l.source.y - l.destination.y
            dist = self.distance(deltax, deltay)
            if(dist):
                l.source.vx -= (dist*deltax)/k
                l.source.vy -= (dist*deltay)/k
                l.destination.vx += (dist*deltax)/k
                l.destination.vy += (dist*deltay)/k
            
        for n in self.nodes:
            d = self.distance(n.vx, n.vy)
            n.x += ((n.vx)/(math.sqrt(d)+0.1))
            n.y += ((n.vy)/(math.sqrt(d)+0.1))
            # n.x = min(700, max(0, n.x))
            # n.y = min(700, max(0, n.y))
            
        t *= 0.99
            
    def generate_hypercube(self, n):
        i = 0
        graph_nodes = [node.Node(str(0))]
        graph_links = []
        while(i < n+1):
            for k in range(len(graph_nodes)):
                # creation des noeuds du deuxième hypercube de dimension n-1
                graph_nodes.append(node.Node(str(k+2**i)))
                self.add_nodes(node.Node(str(k+2**i)))
            for trunk in graph_links[:]:
                # connexion des deux hypercube de dimension n-1
                source, destination = trunk.source, trunk.destination
                graph_links.append(self.trunk_factory(node.Node(str(int(source.name)+2**i)), node.Node(str(int(destination.name)+2**i))))
                self.add_trunks(self.trunk_factory(node.Node(str(int(source.name)+2**i)), node.Node(str(int(destination.name)+2**i))))
            for k in range(len(graph_nodes)//2):
                # creation des liens du deuxième hypercube
                graph_links.append(self.trunk_factory(graph_nodes[k], graph_nodes[k+2**i]))
                self.add_trunks(self.trunk_factory(graph_nodes[k], graph_nodes[k+2**i]))
            i += 1
            
    def generate_meshed_square(self, n):
        for i in range(n**2):
            self.add_nodes(node.Node(str(i)))
        for i in range(n**2):
            if(i-1 > -1 and i%n):
                self.add_trunks(self.trunk_factory(node.Node(str(i)), node.Node(str(i-1))))
            if(i+n < n**2):
                self.add_trunks(self.trunk_factory(node.Node(str(i)), node.Node(str(i+n))))
    