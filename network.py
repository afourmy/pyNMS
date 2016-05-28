from collections import defaultdict, deque
from heapq import heappop, heappush
import miscellaneous
import objects
import AS
import math
import random
import numpy
from cvxopt import matrix, glpk

class Network(object):
    
    node_type_to_class = {
    "router": objects.Router,
    "oxc": objects.OXC,
    "host": objects.Host,
    "antenna": objects.Antenna,
    "regenerator": objects.Regenerator,
    "splitter": objects.Splitter
    }
    
    link_type_to_class = {
    "trunk": objects.Trunk, 
    "route": objects.Route,
    "traffic": objects.Traffic
    }
    
    link_type = tuple(link_type_to_class.keys())
    node_type = tuple(node_type_to_class.keys())
    all_type = link_type + node_type
    
    def __init__(self, name):
        self.name = name
        # pn for "pool network"
        self.pn = {"trunk": {}, "node": {}, "route": {}, "traffic": {}, "AS": {}}
        self.graph = defaultdict(lambda: defaultdict(set))
        self.cpt_link, self.cpt_node, self.cpt_AS = (0,)*3
            
    def link_factory(self, *param, link_type="trunk", name=None, s=None, d=None):
        if not name:
            name = link_type + str(self.cpt_link)
        # creation link in the s-d direction if no link at all yet
        if not name in self.pn[link_type]:
            new_link = Network.link_type_to_class[link_type](name, s, d, *param)
            self.cpt_link += 1
            self.pn[link_type][name] = new_link
            self.graph[s][link_type].add(new_link)
            self.graph[d][link_type].add(new_link)
        return self.pn[link_type][name]
        
    def node_factory(self, *param, node_type="router", name=None):
        if not name:
            name = "node" + str(self.cpt_node)
        if name not in self.pn["node"]:
            self.pn["node"][name] = Network.node_type_to_class[node_type](name, *param)
            self.cpt_node += 1
        return self.pn["node"][name]
        
    def AS_factory(self, name=None, type="RIP", trunks=set(), nodes=set()):
        if not name:
            name = "AS" + str(self.cpt_AS)
        if name not in self.pn["AS"]:
            self.pn["AS"][name] = AS.AutonomousSystem(name, type, trunks, nodes)
            self.cpt_AS += 1
        return self.pn["AS"][name]
        
    # TODO delete this when I import/export everythign: no longer needed
    def graph_from_names(self, source_name, destination_name, name=None):
        """ Create nodes and links from text name. Useful when importing the graph """
        source, destination = self.node_factory(source_name), self.node_factory(destination_name)
        link = self.link_factory(s=source,d=destination, name=name)
        return link
            
    def erase_network(self):
        self.graph.clear()
        for dict_of_objects in self.pn:
            self.pn[dict_of_objects].clear()
            
    def remove_node_from_network(self, node):
        self.pn["node"].pop(node.name, None)
        # retrieve adj links to delete them 
        dict_of_adj_links = self.graph.pop(node, None)
        if(dict_of_adj_links): # can be None if multiple deletion at once
            for type_link, adj_links in dict_of_adj_links.items():
                for adj_link in adj_links:
                    neighbor = adj_link.destination if node == adj_link.source else adj_link.source
                    self.graph[neighbor][type_link].discard(adj_link)
                    yield self.pn[type_link].pop(adj_link.name, None)
            
    def remove_link_from_network(self, link):
        self.graph[link.source][link.type].discard(link)
        self.graph[link.destination][link.type].discard(link)
        self.pn[link.type].pop(link.name, None)
        
    # this function relates to AS but must be in network, because we need to 
    # know what's not in the AS to find the edge nodes
    def find_edge_nodes(self, AS):
        AS.edges.clear()
        for node in AS.nodes:
            if(any(trunk not in AS.trunks for trunk in self.graph[node]["trunk"])):
                AS.edges.add(node)
                yield node
            
    def is_connected(self, nodeA, nodeB, link_type):
        return any(l.source == nodeA or l.destination == nodeA for l in self.graph[nodeB][link_type])
        
    def number_of_links_between(self, nodeA, nodeB):
        sum = 0
        for type in self.link_type:
            for link in self.graph[nodeA][type]:
                if(link.source == nodeB or link.destination == nodeB):
                    sum += 1
        return sum
        
    def bfs(self, source):
        visited = set()
        layer = {source}
        while layer:
            temp = layer
            layer = set()
            for node in temp:
                if node not in visited:
                    visited.add(node)
                    for adj_link in self.graph[node]["trunk"]:
                        neighbor = adj_link.destination if node == adj_link.source else adj_link.source
                        layer.add(neighbor)
                        yield neighbor
                    
    def connected_components(self):
        visited = set()
        for node in self.graph:
            if node not in visited:
                new_comp = set(self.bfs(node))
                visited.update(new_comp)
                yield new_comp
                
        ## Shortest path(s) algorithm: Dijkstra, Bellman-Ford, all-paths (BFS)
            
    def dijkstra(self, source, target, excluded_trunks=None, excluded_nodes=None, path_constraints=None, allowed_trunks=None, allowed_nodes=None):
        # Complexity: O(|V| + |E|log|V|)
        
        # initialize parameters
        if(excluded_nodes is None):
            excluded_nodes = []
        if(excluded_trunks is None):
            excluded_trunks = []
        if(path_constraints is None):
            path_constraints = []
        if(allowed_trunks is None):
            allowed_trunks = self.pn["trunk"].values()
        if(allowed_nodes is None):
            allowed_nodes = self.pn["node"].values()
            
        full_path_node, full_path_link = [], []
        constraints = [source] + path_constraints + [target]
        for s, t in zip(constraints, constraints[1:]):
            # find the SP from s to t
            prec_node = {i: None for i in allowed_nodes}
            prec_link = {i: None for i in allowed_nodes}
            visited = {i: False for i in allowed_nodes}
            dist = {i: float("inf") for i in allowed_nodes}
            dist[s] = 0
            heap = [(0, s)]
            while heap:
                dist_node, node = heappop(heap)  
                if not visited[node]:
                    visited[node] = True
                    if node == t:
                        break
                    for adj_trunk in self.graph[node]["trunk"]:
                        neighbor = adj_trunk.destination if node == adj_trunk.source else adj_trunk.source
                        sd = (node == adj_trunk.source)*"SD" or "DS"
                        # excluded and allowed nodes
                        if neighbor in excluded_nodes or neighbor not in allowed_nodes: continue
                        # excluded and allowed trunks
                        if adj_trunk in excluded_trunks or adj_trunk not in allowed_trunks: continue
                        dist_neighbor = dist_node + adj_trunk.__dict__["cost" + sd]
                        if dist_neighbor < dist[neighbor]:
                            dist[neighbor] = dist_neighbor
                            prec_node[neighbor] = node
                            prec_link[neighbor] = adj_trunk
                            heappush(heap, (dist_neighbor, neighbor))
            
            # traceback the path from t to s, for each (s,t) from source to target
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
        
    def bellman_ford(self, source, target, excluded_trunks=None, excluded_nodes=None, allowed_trunks=None, allowed_nodes=None):
        # Complexity: O(|V| + |E|log|V|)
        
        # initialize parameters
        if(excluded_nodes is None):
            excluded_nodes = []
        if(excluded_trunks is None):
            excluded_trunks = []
        if(allowed_trunks is None):
            allowed_trunks = self.pn["trunk"].values()
        if(allowed_nodes is None):
            allowed_nodes = self.pn["node"].values()

        n = len(allowed_nodes)
        prec_node = {i: None for i in allowed_nodes}
        prec_link = {i: None for i in allowed_nodes}
        dist = {i: float("inf") for i in allowed_nodes}
        dist[source] = 0
        
        for i in range(n+2):
            negative_cycle = False
            for node in allowed_nodes:
                for adj_trunk in self.graph[node]["trunk"]:
                    neighbor = adj_trunk.destination if node == adj_trunk.source else adj_trunk.source
                    sd = (node == adj_trunk.source)*"SD" or "DS", direction*"DS" or "SD"
                    # excluded and allowed nodes
                    if neighbor in excluded_nodes or neighbor not in allowed_nodes: continue
                    # excluded and allowed trunks
                    if adj_trunk in excluded_trunks or adj_trunk not in allowed_trunks: continue
                    dist_neighbor = dist[node] + adj_trunk.__dict__["cost" + sd]
                    if dist_neighbor < dist[neighbor]:
                        dist[neighbor] = dist_neighbor
                        prec_node[neighbor] = node
                        prec_link[neighbor] = adj_trunk
                        negative_cycle = True
                        
        # traceback the path from target to source
        if(dist[target] != float("inf")):
            curr, path_node, path_link = target, [target], [prec_link[target]]
            while(curr != source):
                curr = prec_node[curr]
                path_link.append(prec_link[curr])
                path_node.append(curr)
            return path_node[::-1], path_link[:-1][::-1]
        else:
            return [], []
        
    def all_paths(self, source, target=None):
        # generates all cycle-free paths from source to optional target
        path = [source]
        seen = {source}
        def find_all_paths():
            dead_end = True
            node = path[-1]
            if(node == target):
                yield list(path)
            else:
                for adj_trunk in self.graph[node]["trunk"]:
                    neighbor = adj_trunk.destination if node == adj_trunk.source else adj_trunk.source
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
        
    ## Flow algorithms: Ford-Fulkerson, Edmonds-Karp
        
    def reset_flow(self):
        for link in self.pn["trunk"].values():
            link.flowSD, link.flowDS = 0, 0
        
    def augment_ff(self, val, curr_node, target, visit):
        visit[curr_node] = True
        if(curr_node == target):
            return val
        for adj_link in self.graph[curr_node]["trunk"]:
            neighbor = adj_link.destination if curr_node == adj_link.source else adj_link.source
            direction = curr_node == adj_link.source
            sd, ds = direction*"SD" or "DS", direction*"DS" or "SD"
            cap = adj_link.__dict__["capacity" + sd]
            current_flow = adj_link.__dict__["flow" + sd]
            if cap > current_flow and not visit[neighbor]:
                residual_capacity = min(val, cap - current_flow)
                global_flow = self.augment_ff(residual_capacity, neighbor, target, visit)
                if(global_flow > 0):
                    adj_link.__dict__["flow" + sd] += global_flow
                    adj_link.__dict__["flow" + ds] -= global_flow
                    return global_flow
        return False
        
    def ford_fulkerson(self, source, destination):
        self.reset_flow()
        while(self.augment_ff(float("inf"), source, destination, {n:0 for n in self.graph})):
            pass
        # flow leaving from the source 
        return sum(adj.__dict__["flow" + (source == adj.source)*"SD" or "DS"] for adj in self.graph[source]["trunk"])
        
    def augment_ek(self, source, destination):
        res_cap = {n:0 for n in self.graph}
        augmenting_path = {n: None for n in self.graph}
        Q = deque()
        Q.append(source)
        augmenting_path[source] = source
        res_cap[source] = float("inf")
        while Q:
            curr_node = Q.popleft()
            for adj_link in self.graph[curr_node]["trunk"]:
                neighbor = adj_link.destination if curr_node == adj_link.source else adj_link.source
                direction = curr_node == adj_link.source
                sd, ds = direction*"SD" or "DS", direction*"DS" or "SD"
                residual = adj_link.__dict__["capacity" + sd] - adj_link.__dict__["flow" + sd]
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
        while(True):
            augmenting_path, global_flow = self.augment_ek(source, destination)
            if not global_flow:
                break
            curr_node = destination
            while curr_node != source:
                # find the trunk between the two nodes
                prec_node = augmenting_path[curr_node]
                find_trunk = lambda t: prec_node in (t.source, t.destination)
                trunk ,= filter(find_trunk, self.graph[curr_node]["trunk"])
                # define sd and ds depending on how the link is defined
                direction = curr_node == trunk.source
                sd, ds = direction*"SD" or "DS", direction*"DS" or "SD"
                trunk.__dict__["flow" + ds] += global_flow
                trunk.__dict__["flow" + sd] -= global_flow
                curr_node = prec_node 
        return sum(adj.__dict__["flow" + ((source == adj.source)*"SD" or "DS")] for adj in self.graph[source]["trunk"])
        
    ## Minimum Spanning Tree algorithms: Kruskal
        
    def kruskal(self, allowed_nodes):
        uf = miscellaneous.UnionFind(allowed_nodes)
        edges = []
        for node in self.graph:
            for adj_trunk in self.graph[node]["trunk"]:
                neighbor = adj_trunk.destination if node == adj_trunk.source else adj_trunk.source
                edges.append((adj_trunk.costSD, adj_trunk, node, neighbor))
        minimum_spanning_tree = []
        for w, t, u, v in sorted(edges, key=lambda x: x[0]):
            if uf.union(u, v):
                yield t
                
    ## Linear programming to solve the maximum flow problem
    
    def LP_MF_formulation(self, s, t):
        """
        Solves the mixed integer LP
            minimize    c'*x       
            subject to  G*x + s = h
                        A*x = b    
                        s >= 0
                        xi integer, forall i in I
                        
        using MOSEK 7.0.
        solsta, x = ilp(c, G, h, A=None, b=None, I=None).
        """
        n = 2*len(self.pn["trunk"])
        v = len(self.graph)
        c = []
        for node in self.graph:
            for trunk in self.graph[node]["trunk"]:
                c.append(node == s and trunk.source == s)
        A = []
        for node_r in self.graph:
            row = []
            if(node_r not in (s, t)):
                for node in self.graph:
                    for trunk in self.graph[node]["trunk"]:
                        row.append(1 if trunk.destination == node_r else -1 if trunk.source == node_r else 0)
                A.append(row)
        b = [0]*(v-2)
        G = []
        cpt = 0
        for node in self.graph:
            for trunk in self.graph[node]["trunk"]:
                row = [0]*n 
                row[cpt] = 1
                cpt += 1
                G.append(row)
        cpt = 0
        for node in self.graph:
            for trunk in self.graph[node]["trunk"]:
                row = [0]*n
                row[cpt] = -1
                cpt += 1
                G.append(row)
        h = []
        for node in self.graph:
            for trunk in self.graph[node]["trunk"]:
                neighbor = trunk.destination if node == trunk.source else trunk.source
                sd = (node == trunk.source)*"SD" or "DS"
                h.append(trunk.__dict__["capacity" + sd])
        h += [0]*n
        
        A = list(list(map(float, row)) for row in A)
        G = list(list(map(float, row)) for row in G)
        b = list(map(float, b))
        c = list(map(float, c))
        h = list(map(float, h))
        
        print(len(A[0]))
        print(len(A))
        print(len(G[0]))
        print(len(G))
        print(len(b))
        print(len(c))
        print(len(h))
        
        A = matrix(A)
        A = A.T
        G = matrix(G)
        G = G.T
        b = matrix(b)
        c = matrix(c)
        h = matrix(h)
        
        #print(A, b, c)
        solsta, x = glpk.ilp(-c, G, h, A, b)
        tot = 0
        for node in self.graph:
            for trunk in self.graph[node]["trunk"]:
                print(node, trunk)
        print(tot // 2)
        print(x)
  

                    
            
    ## Distance functions
    
    def distance(self, p, q): 
        return math.sqrt(p*p + q*q)
        
    # TODO take 2 node as argument and set the distance of trunk between them
    def haversine_distance(self, lon_nA, lat_nA, lon_nB, lat_nB):
        """ Earth distance between two nodes """
        
        # decimal degrees to radians conversion
        lon_nA, lat_nA, lon_nB, lat_nB = map(math.radians, (lon_nA, lat_nA, lon_nB, lat_nB))
    
        d_lon = lon_nB - lon_nA 
        d_lat = lat_nB - lat_nA 
        a = math.sin(d_lat/2)**2 + math.cos(lat_nA)*math.cos(lat_nB)*math.sin(d_lon/2)**2
        c = 2*math.asin(math.sqrt(a)) 
        r = 6371 # Radius of earth in kilometers. Use 3956 for miles
        return c*r
            
    ## Force functions
    
    def force_de_coulomb(self, dx, dy, dist, beta):
        c = dist and beta/dist**3
        return (-c*dx, -c*dy)
        
    def force_de_hooke(self, dx, dy, dist, dij, k):
        dl = dist - dij
        const = k * dl / dist
        return (const * dx, const * dy)
        
    def fa(self, d, k):
        return (d**2)/k
    
    def fr(self, d, k):
        return -(k**2)/d
        
    ## force-directed layout algorithms: Eades ("spring") and Fruchterman-Reingold algorithms
            
    def spring_layout(self, alpha, beta, k, eta, delta, raideur):            
        for nodeA in self.pn["node"].values():
            Fx, Fy = 0, 0
            for nodeB in self.pn["node"].values():
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
    
        for n in self.pn["node"].values():
            n.x += round(n.vx * delta)
            n.y += round(n.vy * delta)
        
    def fruchterman(self, k):
        t = 1
        for nA in self.pn["node"].values():
            nA.vx, nA.vy = 0, 0
            for nB in self.pn["node"].values():
                if(nA != nB):
                    deltax = nA.x - nB.x
                    deltay = nA.y - nB.y
                    dist = self.distance(deltax, deltay)
                    if(dist):
                        nA.vx += (deltay*(k**2))/dist**3
                        nA.vy += (deltay*(k**2))/dist**3                        
                    
        for l in filter(None,self.pn["trunk"].values()):
            deltax = l.source.x - l.destination.x
            deltay = l.source.y - l.destination.y
            dist = self.distance(deltax, deltay)
            if(dist):
                l.source.vx -= (dist*deltax)/k
                l.source.vy -= (dist*deltay)/k
                l.destination.vx += (dist*deltax)/k
                l.destination.vy += (dist*deltay)/k
            
        for n in self.pn["node"].values():
            d = self.distance(n.vx, n.vy)
            n.x += ((n.vx)/(math.sqrt(d)+0.1))
            n.y += ((n.vy)/(math.sqrt(d)+0.1))
            # n.x = min(700, max(0, n.x))
            # n.y = min(700, max(0, n.y))
            
        t *= 0.99
        
    ## graph generation functions: hypercube, square tiling, tree, star, full mesh, ring 
            
    def generate_hypercube(self, n):
        # we create a n-dim hypercube by connecting two (n-1)-dim hypercubes
        i = 0
        graph_nodes = [self.node_factory(str(0))]
        graph_links = []
        while(i < n+1):
            for k in range(len(graph_nodes)):
                # creation of the nodes of the second hypercube
                graph_nodes.append(self.node_factory(str(k+2**i)))
            for trunk in graph_links[:]:
                # connection of the two hypercubes
                source, destination = trunk.source, trunk.destination
                n1, n2 = str(int(source.name)+2**i), str(int(destination.name)+2**i)
                graph_links.append(self.link_factory(s=self.node_factory(n1), d=self.node_factory(n2)))
            for k in range(len(graph_nodes)//2):
                # creation of the links of the second hypercube
                graph_links.append(self.link_factory(s=graph_nodes[k], d=graph_nodes[k+2**i]))
            i += 1
            
    def generate_meshed_square(self, n):
        for i in range(n**2):
            n1, n2, n3 = str(i), str(i-1), str(i+n)
            if(i-1 > -1 and i%n):
                self.link_factory(s=self.node_factory(name=n1), d=self.node_factory(name=n2))
            if(i+n < n**2):
                self.link_factory(s=self.node_factory(name=n1), d=self.node_factory(name=n3))
                
    def generate_tree(self, n):
        for i in range(2**n-1):
            n1, n2, n3 = str(i), str(2*i+1), str(2*i+2)
            self.link_factory(s=self.node_factory(name=n1), d=self.node_factory(name=n2))
            self.link_factory(s=self.node_factory(name=n1), d=self.node_factory(name=n3))
            
    def generate_star(self, n):
        nb_node = len(self.pn["node"])
        for i in range(n):
            n1, n2 = str(nb_node), str(nb_node+1+i)
            self.link_factory(s=self.node_factory(name=n1), d=self.node_factory(name=n2))
            
    def generate_full_mesh(self, n):
        nb_node = len(self.pn["node"])
        for i in range(n):
            for j in range(i):
                n1, n2 = str(nb_node+j), str(nb_node+i)
                self.link_factory(s=self.node_factory(name=n1), d=self.node_factory(name=n2))
                
    def generate_ring(self, n):
        nb_node = len(self.pn["node"])
        for i in range(n):
            n1, n2 = str(nb_node+i), str(nb_node+(1+i)%n)
            self.link_factory(s=self.node_factory(name=n1), d=self.node_factory(name=n2))
            
            