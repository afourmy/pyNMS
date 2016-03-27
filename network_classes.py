from collections import defaultdict
from heapq import heappop, heappush
from copy import deepcopy

class Network(object):
    def __init__(self, name):
        self.name = name
        self.nodes = set()
        self.trunks = set()
        self.graph = defaultdict(set)
        
    def add_nodes(self, *nodes):
        for node in nodes:
            self.nodes.add(node)
            
    def add_trunks(self, *trunks):
        for trunk in trunks:
            self.trunks.add(trunk)
            ingress, egress = trunk.ingress, trunk.egress
            self.nodes.update([ingress, egress])
            self.graph[ingress].add(egress)
            self.graph[egress].add(ingress)
            
    def clear(self):
        self.nodes.clear()
        self.trunks.clear()
        self.graph.clear()
        
    def remove_trunks(self, *trunks):
        for trunk in trunks:
            self.trunks.remove(trunk)
        ingress, egress = trunk.ingress, trunk.egress
        self.graph[ingress].discard(egress)
        self.graph[egress].discard(ingress)
            
    def remove_nodes(self, *nodes):
        self.nodes -= {node}
        adjacent_nodes = self.graph.pop(node, None)
        for neighbor in adjacent_nodes:
            self.graph[neighbor].discard(node)
            
    def fast_graph_definition(self, string):
        """
        Allow to create graph quickly with a single string
        "1234" will create the graph {"1": {"2"}, "2": {"1"}, "4": {"3"} ,"3": {"4"}}
        """
        if(len(string)%2 or not isinstance(string, str)):
            raise ValueError
        for ingress, egress in zip(string[::2], string[1::2]):
            ingress, egress = Node(ingress), Node(egress)
            trunk = Trunk(ingress, egress)
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
            ingress, egress = trunk.ingress, trunk.egress
            new_graph[ingress].discard(egress)
            new_graph[ingress].discard(egress)
            
        # exclude nodes from excluded nodes
        for node in excluded_nodes:
            adjacent_nodes = new_graph.pop(node, None)
            for neighbor in adjacent_nodes:
                new_graph[neighbor].discard(node)
        
        # find the SP on the new graph
        n = len(new_graph)
        prec = {i: None for i in new_graph}
        visited = {i: False for i in new_graph}
        dist = {i: float('inf') for i in new_graph}
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
            curr, path = target, str(target)
            while(curr != source):
                curr = prec[curr]
                path = str(curr) + path
            return path
        return "no path found"
        
    def constrained_hop_count(self, source, target, path_constraints, ex_trunks=None, ex_nodes=None):
        """ 
        Parameter path_constraints: path_constraints (ordered list of nodes)
        Parameter ex_trunks (optional): excluded_links (list of links)
        Parameter ex_nodes (optional): excluded_nodes (lists of nodes)
        """        
        path = ""
        pc = [source] + pc + [target]
        for s, t in zip(pc, pc[1:]):
            path += self.hop_count(s, t, el, en)[:-1]
        return path + t
    
class Trunk(object):
    def __init__(self, ingress, egress, cost=1, capacity=0):
        self.ingress = ingress
        self.egress = egress
        self.cost = cost
        self.capacity = capacity
        
    def __repr__(self):
        return "({}, {})".format(self.ingress, self.egress)
        
    def __eq__(self, other):
        return isinstance(other, self.__class__)\
        and {self.ingress, self.egress} == {other.ingress, other.egress}
        
    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __hash__(self):
        return 0
        
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
        
if(__name__ == "__main__"):
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
    ntw2.fast_graph_definition("ABBCCDDEEF")
    path = ntw2.hop_count(Node("A"), Node("F"))
