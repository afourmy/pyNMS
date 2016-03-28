from collections import defaultdict
from heapq import heappop, heappush
from copy import deepcopy

class Network(object):
    def __init__(self, name):
        self.name = name
        self.nodes = set()
        self.trunks = set()
        self.graph = defaultdict(set)
        self.flows = set()
        
    def add_nodes(self, *nodes):
        for node in nodes:
            self.nodes.add(node)
            
    def add_trunks(self, *trunks):
        for trunk in trunks:
            self.trunks.add(trunk)
            source, destination = trunk.source, trunk.destination
            self.nodes.update([source, destination])
            self.graph[source].add(destination)
            self.graph[destination].add(source)
            
    def add_flow(self, *flows):
        for flow in flows:
            self.flows.add(flow)
            
    def clear(self):
        self.nodes.clear()
        self.trunks.clear()
        self.graph.clear()
        
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
            
    def fast_graph_definition(self, string):
        """
        Allow to create graph quickly with a single string
        """
        if(len(string)%2 or not isinstance(string, str)):
            raise ValueError
        for source, destination in zip(string[::2], string[1::2]):
            source, destination = Node(source), Node(destination)
            trunk = Trunk(source, destination)
            self.add_trunks(trunk)
            
    def hop_count(self, source, target, excluded_trunks=None, excluded_nodes=None):
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
    
        new_graph = deepcopy(self.graph)
        
        # prune all the links in excluded_links from the original graph
        for trunk in excluded_trunks:
            src, dest = trunk.source, trunk.destination
            new_graph[src].discard(dest)
            new_graph[dest].discard(src)
            
        # exclude nodes from excluded nodes
        for node in excluded_nodes:
            adjacent_nodes = new_graph.pop(node, [])
            for neighbor in adjacent_nodes:
                new_graph[neighbor].discard(node)
        
        # find the SP on the new graph
        n = len(new_graph)
        prec = {i: None for i in new_graph.keys()}
        visited = {i: False for i in new_graph.keys()}
        dist = {i: float('inf') for i in new_graph.keys()}
        dist[source] = 0
        heap = [(0, source)]
        while heap:
            dist_node, node = heappop(heap)  
            if not visited[node]:
                visited[node] = True
                if node == target:
                    break
                for neighbor in new_graph[node]:
                    dist_neighbor = dist_node + int(node != neighbor)
                    if dist_neighbor < dist[neighbor]:
                        dist[neighbor] = dist_neighbor
                        prec[neighbor] = node
                        heappush(heap, (dist_neighbor, neighbor))
        
        # traceback the path from target to source
        if(visited[target]):
            curr, path = target, [target]
            while(curr != source):
                curr = prec[curr]
                path.append(curr)
            return path[::-1]
        return "no path found"
        
    def constrained_hop_count(self, source, target, path_constraints, ex_nodes=None, ex_trunks=None):
        """ 
        Parameter path_constraints: path_constraints (ordered list of nodes)
        Parameter ex_trunks (optional): excluded_links (list of links)
        Parameter ex_nodes (optional): excluded_nodes (lists of nodes)
        """        
        path = []
        path_constraints = [source] + path_constraints + [target]
        for s, t in zip(path_constraints, path_constraints[1:]):
            path += self.hop_count(s, t, ex_trunks, ex_nodes)[:-1]
        return sum([], path + [target])
        
    def route_flows(self):
        for flow in self.flows:
            constraints = flow.routing_policy.get_constraints()
            flow.path = self.constrained_hop_count(flow.ingress, flow.egress, *constraints)
    
    def show_flows_path(self):
        for flow in self.flows:
            print("Flow {} from {} to {}: {}\n".format(flow.name, flow.ingress, flow.egress, flow.path))
                
class RoutingPolicy(object):
    def __init__(self, name, path_constraints=[], excluded_nodes=[], excluded_trunks=[]):
        self.name = name
        self.path_constraints = path_constraints
        self.excluded_nodes = excluded_nodes
        self.excluded_trunks = excluded_trunks
        
    def __repr__(self):
        return self.name
        
    def get_constraints(self):
        return (self.path_constraints, self.excluded_nodes, self.excluded_trunks)
        
class TrafficFlow(object):
    def __init__(self, name, ingress, egress, routing_policy, demand=0):
        self.name = name
        self.ingress = ingress
        self.egress = egress
        self.routing_policy = routing_policy
        self.demand = demand
        # un path se définit comme une suite de trunk pour qu'il n'y ait pas d'ambiguité
        self.path = path
        
    def __repr__(self):
        return "[{} ({}->{})]".format(self.name, self.ingress, self.egress)
        
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name
        
    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __hash__(self):
        return hash(self.name)
    
class Trunk(object):
    def __init__(self, source, destination, cost=1, capacity=0):
        self.source = source
        self.destination = destination
        self.cost = cost
        self.capacity = capacity
        
    def __repr__(self):
        return "{}{}".format(self.source, self.destination)
        
    def __eq__(self, other):
        return isinstance(other, self.__class__)\
        and {self.source, self.destination} == {other.source, other.destination}
        
    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __hash__(self):
        return 1
        
class Node(object):
    def __init__(self, name):
        self.name = name
        
    def __repr__(self):
        return self.name
        
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name
        
    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __hash__(self):
        return hash(self.name)
        
    def __lt__(self, other):
        return 1
        
class Router(Node):
    def __init__(self, name, port_capacity = {"100GE": 0, "40GE": 0, "10GE": 0, "GE": 0, "FE": 0}):
        self.name = name
        self.port_capacity = port_capacity
        
        
if(__name__ == "__main__"):
    """
    Basic tests:
    ntw = Network("test")
    A = Node("A")
    B = Node("B")
    ntw.add_nodes(A, B)
    CD = Trunk("C", "D")
    ntw.add_trunks(CD)
    print(ntw.trunks)
    ntw.remove_trunks(CD)
    print(ntw.trunks)
    ntw2 = Network("test2")
    ntw2.fast_graph_definition("ABBCCDDEEF", Node)
    path = ntw2.hop_count(Node("A"), Node("F"))
    print(path)
    ntw3 = Network("test3")
    ntw3.fast_graph_definition("ABBCCDDEEF", str)
    path = ntw3.hop_count("A", "F")
    print(path)
    """
    
    # Allocate a routing policy to a flow to find the path
    ntw4 = Network("test4")
    ntw4.fast_graph_definition("ABBFFGGDDEBCCDBIIJJHHKKE")
    A = Node("A")
    E = Node("E")
    C = Node("C")
    D = Node("D")
    CD = Trunk(C, D)
    RP1 = RoutingPolicy("RP1", [Node("J")], [Node("H")], [])
    RP2 = RoutingPolicy("SP")
    flow1 = TrafficFlow("flow1", Node("A"), Node("E"), RP1, 1)
    flow2 = TrafficFlow("flow2", E, A, RP2, 2)
    ntw4.add_flow(flow1, flow2)
    ntw4.route_flows()