# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

from collections import defaultdict

# decorating __init__ to initialize properties
def initializer(default_properties):
    def inner_decorator(init):
        def wrapper(self, **kw):
            for k in kw:
                setattr(self, k, kw[k])
            for property in default_properties:
                value = default_properties[property]
                if not hasattr(self, property):
                    # if the value should be an empty list / set, we make
                    # sure it refers to different objects in memory by using eval
                    try:
                        setattr(self, property, eval(value))
                    except (TypeError, NameError):
                        setattr(self, property, value)
            init(self)
        return wrapper
    return inner_decorator

## NetDim object

class NDobject(object):
    
        # an object in NetDim belongs to one or several groups, which we can
        # use as a filter to display a subset of objects
        # each site corresponds to a "site" node, but the filter can also be
        # a set of sites, in which case any object that belongs to at least
        # one site of the user-defined filter will be displayed
    ie_properties = {
                    'id': None,
                    'sites': set(),
                    'name': None
                    }
                    
    @initializer(ie_properties)
    def __init__(self):
        pass


## Nodes
class Node(NDobject):
    
    class_type = type = 'node'
    ie_properties = {
                    'x' : 600, 
                    'y' : 300, 
                    'longitude' : 0, 
                    'latitude' : 0, 
                    'ipaddress' : None,
                    'subnetmask' : None,
                    'LB_paths' : 1
                    }
                    
    @initializer(ie_properties)
    def __init__(self):
        # self id and id of the corresponding label on the canvas
        self.oval = {layer: None for layer in range(5)}
        # image of the node at all three layers: physical, logical and traffic
        self.image = {layer: None for layer in range(5)}
        self.layer_line = {layer: None for layer in range(5)}
        self.lid = None
        self.lpos = None
        self.size = 8
        # velocity of a node for graph drawing algorithm
        self.vx = 0
        self.vy = 0
        # list of AS to which the node belongs. AS is actually a dictionnary
        # associating an AS to a set of area the node belongs to
        self.AS = defaultdict(set)
        # virtual factor for BFS-clusterization drawing
        self.virtual_factor = 1
        super().__init__()
        
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
    
    ie_properties = {
                    'bgp_AS' : None, 
                    'default_route' : None
                    }
                    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        # routing table: binds an IP address to a cost / next-hop
        self.rt = {}
        # bgp table
        self.bgpt = defaultdict(set)
        # the default route is the gateway of last resort: 
        # it is the IP address of the next-hop (either loopback or interface)
        super().__init__()
        
class Switch(Node):

    color = 'black'
    subtype = 'switch'
    layer = 2
    imagex, imagey = 54, 36
    
    ie_properties = {}
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        super().__init__()
        
class OXC(Node):

    color = 'pink'
    subtype = 'oxc'
    layer = 2
    imagex, imagey = 35, 32
    
    ie_properties = {}
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        super().__init__()
        
class Host(Node):

    color = 'blue'
    subtype = 'host'
    layer = 3
    imagex, imagey = 35, 32
    
    ie_properties = {}
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        self.rt = {}
        self.default_route = None
        super().__init__()
        
class Regenerator(Node):

    color = 'black'
    subtype = 'regenerator'
    layer = 1
    imagex, imagey = 64, 48
    
    ie_properties = {}
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        super().__init__()
        
class Splitter(Node):

    color = 'black'
    subtype = 'splitter'
    layer = 1
    imagex, imagey = 64, 50
    
    ie_properties = {}
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        super().__init__()
        
class Antenna(Node):

    color = 'black'
    subtype = 'antenna'
    layer = 1
    imagex, imagey = 35, 32
    
    ie_properties = {}
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        super().__init__()
        
class Cloud(Node):

    color = 'black'
    subtype = 'cloud'
    layer = 3
    imagex, imagey = 60, 35
    
    ie_properties = {}
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        super().__init__()
        
## Links
class Link(NDobject):
    
    class_type = 'link'
    
    def __init__(self):
        # self id and id of the corresponding label on the canvas
        self.line = None
        self.lid = None
        # self.iid is the id of the interface labels, used to display
        # interfaces specific properties (ip addresses, names, etc) as well
        # as trunk asymmetric (directional) properties (capacity, flow, etc)
        self.ilid = [None]*2
        super().__init__()
        
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
    
    ie_properties = {
                    'interface' : 'GE',
                    'distance' : 0., 
                    'costSD' : 1., 
                    'costDS' : 1., 
                    'capacitySD' : 3, 
                    'capacityDS' : 3, 
                    'ipaddressS' : None, 
                    'subnetmaskS' : None,
                    'interfaceS' : None,
                    'macaddressS' : None,
                    'ipaddressD' : None, 
                    'subnetmaskD' : None, 
                    'interfaceD' : None,
                    'macaddressD' : None
                    }

    @initializer(ie_properties)
    def __init__(self):
        self.sntw = None
        self.trafficSD = self.trafficDS = 0.
        self.wctrafficSD = self.wctrafficDS = 0.
        self.wcfailure = None
        self.flowSD = self.flowDS = 0.
        # list of AS to which the trunks belongs. AS is actually a dictionnary
        # associating an AS to a set of area the trunks belongs to
        self.AS = defaultdict(set)
        super().__init__()
        
    def __lt__(self, other):
        return hash(self.name)
        
    def __call__(self, property, node, value=None):
        # can be used both as a getter and a setter, depending on 
        # whether a value is provided or not
        dir = (node == self.source)*'SD' or 'DS'
        if property in ('subnetmask', 'interface', 'ipaddress', 'macaddress'):
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
    
    ie_properties = {}

    @initializer(ie_properties)
    def __init__(self, **kwargs):
        self.linkS = None
        self.linkD = None
        super().__init__()
        
    def __lt__(self, other):
        return hash(self.name)
        
    def __call__(self, property, node, value=None):
        # can be used both as a getter and a setter, depending on 
        # whether a value is provided or not
        # if the property doesn't exist for a virtual connection, we look at
        # the equivalent property for the associated physical link
        dir = (node == self.source)*'S' or 'D'
        if hasattr(self, property + dir):
            if value:
                setattr(self, property + dir, value)
            else:
                return getattr(self, property + dir)
        else:
            getattr(self, 'link' + dir)(property, node, value)
        
class L3VC(Link):
    
    type = 'l3vc'
    subtype = 'l3vc'
    layer = 2
    color = 'black'
    dash = ()
    
    ie_properties = {}

    @initializer(ie_properties)
    def __init__(self, **kwargs):
        self.linkS = None
        self.linkD = None
        super().__init__()
        
    def __lt__(self, other):
        return hash(self.name)
        
    def __call__(self, property, node, value=None):
        # can be used both as a getter and a setter, depending on 
        # whether a value is provided or not
        # if the property doesn't exist for a virtual connection, we look at
        # the equivalent property for the associated physical link
        dir = (node == self.source)*'S' or 'D'
        if hasattr(self, property + dir):
            if value:
                setattr(self, property + dir, value)
            else:
                return getattr(self, property + dir)
        else:
            getattr(self, 'link' + dir)(property, node, value)
        
class Ethernet(Trunk):
    
    color = 'blue'
    protocol = subtype = 'ethernet'
    
    ie_properties = {}
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        super().__init__()
        
class WDMFiber(Trunk):
    
    color = 'orange'
    protocol = subtype = 'wdm'
    
    ie_properties = {
                    'lambda_capacity' : 88
                    }
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        super().__init__()
        
class Route(Link):
    
    type = 'route'
    dash = (3,5)
    layer = 3
    
    ie_properties = {}
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        super().__init__()
        
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
    
    ie_properties = {
                    'nh_ip' : None,
                    'dst_sntw' : None, 
                    'ad' : 1, 
                    }
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        super().__init__()
        
class BGPPeering(Route):

    color = 'violet'
    subtype = 'BGP peering'
    
    ie_properties = {
                    'weightD' : 0,
                    'weightS' : 0, 
                    'ipS' : None, 
                    'ipD': None,
                    'bgp_type': 'eBGP'
                    }
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        super().__init__()
        
class VirtualLink(Route):

    color = 'violet'
    subtype = 'OSPF virtual link'
    
    ie_properties = {}
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        super().__init__()
        
class LSP(Route):

    color = 'violet'
    subtype = 'Label Switched Path'
    
    ie_properties = {
                    'lsp_type': None,
                    'path' : 'list()', 
                    'cost' : 1,
                    'traffic' : 0
                    }
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        super().__init__()

        
class Traffic(Link):
    type = 'traffic'
    subtype = type
    dash = (7,1,1,1)
    color = 'purple'
    layer = 4
    
    ie_properties = {
                    'throughput': 15
                    }
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        super().__init__()
        
class RoutedTraffic(Traffic):
        
    color = 'forest green'
    subtype = 'routed traffic'
    
    ie_properties = {}
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        super().__init__()
        
class StaticTraffic(Traffic):
    
    color = 'chartreuse'
    subtype = 'static traffic'
    
    ie_properties = {
                    'path_constraints' : '[]', 
                    'excluded_trunks' : 'set()', 
                    'excluded_nodes' : 'set()', 
                    'path' : '[]', 
                    }
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        super().__init__()
