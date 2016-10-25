# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

from collections import defaultdict

## Nodes
class Node(object):
    
    class_type = type = 'node'
    
    def __init__(
                 self,
                 id,
                 name, 
                 x = 600, 
                 y = 300, 
                 longitude = 0, 
                 latitude = 0, 
                 ipaddress = None,
                 subnetmask = None,
                 LB_paths = 1
                 ):
        self.id = id
        self.name = name
        self.longitude = int(longitude)
        self.latitude = int(latitude)
        self.ipaddress = ipaddress
        self.subnetmask = subnetmask
        # self id and id of the corresponding label on the canvas
        self.oval = {layer: None for layer in range(5)}
        # image of the node at all three layers: physical, logical and traffic
        self.image = {layer: None for layer in range(5)}
        self.layer_line = {layer: None for layer in range(5)}
        self.lid = None
        self.lpos = None
        self.size = 8
        # position of a node (conversion decimal string to int in case of export)
        self.x = int(float(x))
        self.y = int(float(y))
        # velocity of a node for graph drawing algorithm
        self.vx = 0
        self.vy = 0
        # list of AS to which the node belongs. AS is actually a dictionnary
        # associating an AS to a set of area the node belongs to
        self.AS = defaultdict(set)
        # number of path considered for load-balancing
        self.LB_paths = LB_paths
        # virtual factor for BFS-clusterization drawing
        self.virtual_factor = 1
        
    def __repr__(self):
        return self.name
        
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name
        
    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __hash__(self):
        return hash(self.name)
        
    def __lt__(self, other):
        return hash(self.name)
        
class Router(Node):
    
    color = 'magenta'
    subtype = 'router'
    layer = 3
    imagex, imagey = 33, 25
    
    def __init__(self, *args):
        args = list(args)
        # when a node is created from the scenario left-click binding, we
        # pass the (x, y) coordinates to nf, adding up to exactly 5 parameters.
        # if there are more parameters import, it is an excel import and we
        # pop the router's specific properties beforehand.
        if len(args) > 5:
            self.bgp_AS = args.pop()
            self.default_route = args.pop()
        else:
            self.bgp_AS = None
            self.default_route = None
        # routing table: binds an IP address to a cost / next-hop
        self.rt = {}
        # bgp table
        self.bgpt = defaultdict(set)
        # the default route is the gateway of last resort: 
        # it is the IP address of the next-hop (either loopback or interface)
        super().__init__(*args)
        
class Switch(Node):

    color = 'black'
    subtype = 'switch'
    layer = 2
    imagex, imagey = 54, 36
    
    def __init__(self, *args):
        super().__init__(*args)
        
class OXC(Node):

    color = 'pink'
    subtype = 'oxc'
    layer = 2
    imagex, imagey = 35, 32
    
    def __init__(self, *args):
        super().__init__(*args)
        
class Host(Node):

    color = 'blue'
    subtype = 'host'
    layer = 3
    imagex, imagey = 35, 32
    
    def __init__(self, *args):
        super().__init__(*args)
        self.rt = {}
        self.default_route = None
        
class Regenerator(Node):

    color = 'black'
    subtype = 'regenerator'
    layer = 1
    imagex, imagey = 64, 48
    
    def __init__(self, *args):
        super().__init__(*args)
        
class Splitter(Node):

    color = 'black'
    subtype = 'splitter'
    layer = 1
    imagex, imagey = 64, 50
    
    def __init__(self, *args):
        super().__init__(*args)
        
class Antenna(Node):

    color = 'black'
    subtype = 'antenna'
    layer = 1
    imagex, imagey = 35, 32
    
    def __init__(self, *args):
        super().__init__(*args)
        
class Cloud(Node):

    color = 'black'
    subtype = 'cloud'
    layer = 3
    imagex, imagey = 60, 35
    
    def __init__(self, *args):
        super().__init__(*args)
        
## Links
class Link(object):
    
    class_type = 'link'
    
    def __init__(self, id, name, source, destination, distance=0, bandwidth=0.):
        self.id = id
        self.name = name
        self.source = source
        self.destination = destination
        self.distance = int(distance)
        self.bandwidth = float(bandwidth)
        # self id and id of the corresponding label on the canvas
        self.line = None
        self.lid = None
        # self.iid is the id of the interface labels, used to display
        # interfaces specific properties (ip addresses, names, etc) as well
        # as trunk asymmetric (directional) properties (capacity, flow, etc)
        self.ilid = [None]*2
        
    def __repr__(self):
        return self.name
        
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name
        
    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __hash__(self):
        return hash(self.name)

class Trunk(Link):
    
    type = 'trunk'
    layer = 0
    dash = ()

    def __init__(
                 self, 
                 id,
                 name, 
                 source, 
                 destination,
                 interface = 'GE',
                 distance = 0., 
                 costSD = 1., 
                 costDS = 1., 
                 capacitySD = 3, 
                 capacityDS = 3, 
                 ipaddressS = None, 
                 subnetmaskS = None,
                 interfaceS = None,
                 ipaddressD = None, 
                 subnetmaskD = None, 
                 interfaceD = None
                 ):
                     
        super().__init__(id, name, source, destination, distance)
        self.interface = interface
        self.costSD, self.costDS = int(costSD), int(costDS)
        self.capacitySD, self.capacityDS = int(capacitySD), int(capacityDS)
        self.ipaddressS = ipaddressS
        self.subnetmaskS = subnetmaskS
        self.interfaceS = interfaceS
        self.ipaddressD = ipaddressD
        self.subnetmaskD = subnetmaskD
        self.interfaceD = interfaceD
        self.sntw = None
        self.trafficSD = self.trafficDS = 0.
        self.wctrafficSD = self.wctrafficDS = 0.
        self.wcfailure = None
        self.flowSD = self.flowDS = 0.
        # list of AS to which the trunks belongs. AS is actually a dictionnary
        # associating an AS to a set of area the trunks belongs to
        self.AS = defaultdict(set)
        
    def __lt__(self, other):
        return hash(self.name)
        
    def __call__(self, property, node, value=None):
        # can be used both as a getter and a setter, depending on 
        # whether a value is provided or not
        dir = (node == self.source)*'SD' or 'DS'
        if property in ('subnetmask', 'interface', 'ipaddress'):
            dir = dir[:-1]
        if value:
            setattr(self, property + dir, value)
        else:
            return getattr(self, property + dir)
            
class L2VC(Link):
    
    type = 'l2vc'
    subtype = 'l2vc'
    layer = 1
    color = 'pink'
    dash = ()

    def __init__(
                 self, 
                 id,
                 name, 
                 source, 
                 destination
                 ):
        super().__init__(id, name, source, destination)
        self.linkS = None
        self.linkD = None
        
    def __lt__(self, other):
        return hash(self.name)
        
    def __call__(self, property, node, value=None):
        # can be used both as a getter and a setter, depending on 
        # whether a value is provided or not
        dir = (node == self.source)*'S' or 'D'
        if value:
            setattr(self, property + dir, value)
        else:
            return getattr(self, property + dir)
        
class L3VC(Link):
    
    type = 'l3vc'
    subtype = 'l3vc'
    layer = 2
    color = 'black'
    dash = ()

    def __init__(
                 self, 
                 id,
                 name, 
                 source, 
                 destination
                 ): 
        super().__init__(id, name, source, destination)
        self.linkS = None
        self.linkD = None
        
    def __lt__(self, other):
        return hash(self.name)
        
    def __call__(self, property, node, value=None):
        # can be used both as a getter and a setter, depending on 
        # whether a value is provided or not
        dir = (node == self.source)*'S' or 'D'
        if value:
            setattr(self, property + dir, value)
        else:
            return getattr(self, property + dir)
        
class Ethernet(Trunk):
    
    color = 'blue'
    protocol = subtype = 'ethernet'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
class WDMFiber(Trunk):
    
    color = 'orange'
    protocol = subtype = 'wdm'
    
    def __init__(self, *args):
        args = list(args)
        if len(args) > 4:
            self.lambda_capacity = args.pop()
        else:
            self.lambda_capacity = 88
        super().__init__(*args)
        
class Route(Link):
    
    type = 'route'
    dash = (3,5)
    layer = 3
    
    def __init__(
                 self, 
                 id,
                 name, 
                 source, 
                 destination, 
                 distance = 0,
                 path_constraints = [], 
                 excluded_trunks = set(), 
                 excluded_nodes = set(), 
                 path = [], 
                 subnets = set(), 
                 cost = 1.,
                 traffic = 0,
                 ):
                     
        super().__init__(id, name, source, destination, distance)
        self.path_constraints = path_constraints
        self.excluded_nodes = excluded_nodes
        self.excluded_trunks = excluded_trunks
        self.path = path
        self.subnets = subnets
        self.cost = cost
        self.traffic = traffic
        
    def __call__(self, property, node, value=None):
        # can be used both as a getter and a setter, depending on 
        # whether a value is provided or not
        dir = (node == self.source)*'S' or 'D'
        if value:
            setattr(self, property + dir, value)
        else:
            return getattr(self, property + dir)
            
    def __lt__(self, other):
        return hash(self.name)
        
class StaticRoute(Route):

    color = 'violet'
    subtype = 'static route'
    
    def __init__(self, *args, **kwargs):
        args = list(args)
        if len(args) > 4:
            self.ad = args.pop()
            self.dst_sntw = args.pop()
            self.nh_ip = args.pop()
        else:
            self.nh_ip = None
            self.dst_sntw = None
            self.ad = 1
        super().__init__(*args)
        
class BGPPeering(Route):

    color = 'violet'
    subtype = 'BGP peering'
    
    def __init__(self, *args, **kwargs):
        args = list(args)
        if len(args) > 4:
            self.weightD = args.pop()
            self.weightS = args.pop()
            self.ipS = args.pop()
            self.ipD = args.pop()
            self.bgp_type = args.pop()
            
        else:
            self.weightD = 0
            self.weightS = 0
            self.ipS = None
            self.ipD = None
            self.bgp_type = 'eBGP'
        super().__init__(*args)
        
class VirtualLink(Route):

    color = 'violet'
    subtype = 'OSPF virtual link'
    
    def __init__(self, *args, **kwargs):
        args = list(args)
        if len(args) > 4:
            self.nh_tk = args.pop()
            self.dst_ip = args.pop()
        else:
            self.nh_tk = None
            self.dst_ip = None
        super().__init__(*args)
        
class LSP(Route):

    color = 'violet'
    subtype = 'Label Switched Path'
    
    def __init__(self, *args, **kwargs):
        args = list(args)
        if len(args) > 4:
            self.lsp_type = args.pop()
            self.path = args.pop()
        else:
            self.lsp_type = None
            self.path = []
        super().__init__(*args)

        
class Traffic(Link):
    type = 'traffic'
    subtype = type
    dash = (7,1,1,1)
    color = 'purple'
    layer = 4
    
    def __init__(
                 self, 
                 id,
                 name, 
                 source, 
                 destination, 
                 subnet = 0, 
                 throughput = 15, 
                 path = []
                 ):
        super().__init__(id, name, source, destination)
        # throughput in Mbps
        self.throughput = throughput
        self.subnet = subnet
        self.path = path
        
class RoutedTraffic(Traffic):
    
    color = 'forest green'
    subtype = 'routed traffic'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
class StaticTraffic(Traffic):
    
    color = 'chartreuse'
    subtype = 'static traffic'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
