# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

# ordered dicts are needed to have the same menu order 
from collections import defaultdict, OrderedDict
import network

# decorating __init__ to initialize properties
def initializer(default_properties):
    def inner_decorator(init):
        def wrapper(self, *a, **kw):
            for k in kw:
                setattr(self, k, kw[k])
            for property in default_properties:
                value = default_properties[property]
                if not hasattr(self, property):
                    # if the value should be an empty list / set, we make
                    # sure it refers to different objects in memory by using eval
                    try:
                        setattr(self, property, eval(value))
                    except (TypeError, NameError, SyntaxError):
                        setattr(self, property, value)
            init(self, *a)
        return wrapper
    return inner_decorator
    
## Netdim objects

nd_obj = {
'router': 'node',
'oxc': 'node',
'host': 'node',
'antenna': 'node',
'regenerator': 'node',
'splitter': 'node',
'cloud': 'node',
'switch': 'node',
'ethernet': 'plink',
'wdm': 'plink',
'route': 'route',
'traffic': 'traffic'
}

## Types and subtypes

# subtype -> type mapping
subtype_to_type = {
'router': 'node',
'oxc': 'node',
'host': 'node',
'antenna': 'node',
'regenerator': 'node',
'splitter': 'node',
'switch': 'node',
'cloud': 'node',
'ethernet': 'plink',
'wdm': 'plink',
'l2vc': 'l2link',
'l3vc': 'l3link',
'static route': 'l3link',
'BGP peering': 'l3link',
'OSPF virtual link': 'l3link',
'Label Switched Path': 'l3link',
'routed traffic': 'traffic',
'static traffic': 'traffic'
}
    
## OBJECT PROPERTIES
# 'public' properties means that it is displayed in the GUI
# the user can see all public properties from the object management window

## Common properties 
# properties shared by all objects of a given type

# 1) properties common to all nodes

# ordered dicts are needed to have the same menu order 
node_common_properties = (
'name', 
'x', 
'y', 
'longitude', 
'latitude', 
'ipaddress', 
'subnetmask', 
'sites',
'AS',
)

# 2) properties common to all physical links

plink_common_properties = (
'name', 
'source', 
'destination', 
'interface',
'interfaceS',
'interfaceD',
'distance', 
'costSD', 
'costDS', 
'capacitySD', 
'capacityDS', 
# if there is no failure simulation, the traffic property tells us how
# much traffic is transiting on the plink in a 'no failure' situation
# if there is a link in failure, the traffic that is redirected will 
# also contribute to this 'traffic parameter'.
'trafficSD', 
'trafficDS',
# unlike the traffic property above, wctraffic is the worst case
# traffic. It is the traffic that we use for dimensioning purposes, and
# it considers the maximum traffic that the link must be able to 
# handle, considering all possible failure cases.
'wctrafficSD',
'wctrafficDS',
# the plink which failure results in the worst case traffic
'wcfailure',
'flowSD', 
'flowDS',
'sites',
'sntw',
'AS',
)

# 3) properties common to all interfaces

interface_common_properties = (
'link',
'node',
'name'
)

# 4) properties common to all interfaces

ethernet_interface_properties = interface_common_properties + (
'ipaddress',
'subnetmask',
'macaddress'
)

# 5) properties common to all routes

route_common_properties = (
'name',
'subtype',
'source', 
'destination',
'sites'
)

# 6) properties common to all VC

vc_common_properties = (
'name',
'source', 
'destination',
'linkS',
'linkD',
'sites'
)

# 7) properties common to all traffic links

traffic_common_properties = (
'name', 
'subtype',
'source', 
'destination', 
'throughput',
'sites'
)

## Common Import / Export properties

# 1) import / export properties for nodes

# we exclude the AS from node_common_properties. We don't need to 
# import/export the AS of a node, because when the AS itself is imported, 
# we rebuild #its logical topology, and that includes 
# rebuilding the nodes AS dict
node_common_ie_properties = node_common_properties[:-1]

# 2) import / export properties for physical links

plink_common_ie_properties = (
'name', 
'source', 
'destination', 
'interface',
'distance', 
'costSD', 
'costDS', 
'capacitySD', 
'capacityDS', 
'sites'
)

# 3) import / export properties for routes
        
route_common_ie_properties = (
'name',
'source', 
'destination',
'sites'
)

# 4) import / export properties for traffic links

traffic_common_ie_properties = (
'name', 
'source', 
'destination', 
'throughput',
'sites'
)

## Common properties per subtype
# properties shared by all objects of a given subtype

object_properties = OrderedDict([
('router', node_common_properties + ('default_route', 'bgp_AS')),
('switch', node_common_properties + ('base_macaddress',)),
('oxc', node_common_properties),
('host', node_common_properties),
('antenna', node_common_properties),
('regenerator', node_common_properties),
('splitter', node_common_properties),
('cloud', node_common_properties),

('ethernet', plink_common_properties),
('wdm', plink_common_properties + ('lambda_capacity',)),

('l2vc', vc_common_properties),
('l3vc', vc_common_properties),

('static route', route_common_properties + (
'nh_ip',
'dst_sntw',
'ad'
)),

('BGP peering', route_common_properties + (
'bgp_type',
'ipS',
'ipD',
'weightS',
'weightD'
)),

('OSPF virtual link', route_common_properties + (
'nh_tk',
'dst_sntw'
)),

('Label Switched Path', route_common_properties + (
'lsp_type',
'path'
)),

('routed traffic', traffic_common_properties + ('ipS', 'ipD')),
('static traffic', traffic_common_properties),

])

## Common Import / Export properties per subtype

object_ie = OrderedDict([
('router', node_common_ie_properties + ('default_route', 'bgp_AS')),
('switch', node_common_ie_properties + ('base_macaddress',)),
('oxc', node_common_ie_properties),
('host', node_common_ie_properties),
('antenna', node_common_ie_properties),
('regenerator', node_common_ie_properties),
('splitter', node_common_ie_properties),
('cloud', node_common_ie_properties),

('ethernet', plink_common_ie_properties),
('wdm', plink_common_ie_properties + ('lambda_capacity',)),

('static route', route_common_ie_properties + (
'nh_ip',
'dst_sntw',
'ad'
)),

('BGP peering', route_common_ie_properties + (
'bgp_type',
'ipS',
'ipD',
'weightS',
'weightD'
)),

('OSPF virtual link', route_common_ie_properties + (
'nh_tk',
'dst_ip'
)),

('Label Switched Path', route_common_ie_properties + (
'lsp_type',
'path'
)),

('routed traffic', traffic_common_ie_properties + (
'ipS',
'ipD'
)),
('static traffic', traffic_common_ie_properties),

('ethernet interface', ethernet_interface_properties),
('wdm interface', interface_common_properties)
])

## Interface basic and per-AS public properties

interface_public_properties = (
'link',
'node',
'name'
)
                               
ethernet_interface_public_properties = interface_public_properties + (
'ipaddress',
'subnetmask',
'macaddress'
)

ethernet_interface_perAS_properties = (
'cost',
'role',
'priority'
)

## Nodes per-AS properties

common_perAS_properties = ()

perAS_properties = OrderedDict([
('router', ('router_id', 'LB_paths')),
('switch', ('priority',)),
])

## Label properties
# properties used for the label menu

object_labels = OrderedDict([
('Node', 
(
'None', 
'Name', 
'Position', 
'Coordinates', 
'IPAddress',
'Default_Route'
)),

('Plink', 
(
'None', 
'Name', 
'Type',
'Distance', 
'Traffic', 
'WCTraffic',
'Sntw'
)),

('Interface', 
(
'None', 
'Name', 
'Cost',
'Capacity',
'Flow',
'IPaddress',
'Traffic', 
'WCTraffic',
)),

('L2link',
(
'None', 
'Name', 
)),

('L3link',
(
'None', 
'Name', 
)),

('Traffic', 
(
'None', 
'Name', 
'Throughput'
))])

## Box properties
# box properties defines which properties are to be displayed in the
# upper left corner of the canvas when hoverin over an object

node_box_properties = (
'name', 
'subtype',
'ipaddress', 
'subnetmask'
)

plink_box_properties = (
'name', 
'subtype',
'interface',
'interfaceS',
'interfaceD',
'source', 
'destination',
'sntw'
)

vc_box_properties = (
'name', 
'type',
'source', 
'destination',
'linkS',
'linkD'
)

box_properties = OrderedDict([
('router', node_box_properties + ('default_route', 'bgp_AS')),
('switch', node_box_properties + ('base_macaddress',)),
('oxc', node_box_properties),
('host', node_box_properties),
('antenna', node_box_properties),
('regenerator', node_box_properties),
('splitter', node_box_properties),
('cloud', node_box_properties),

('ethernet', plink_box_properties),
('wdm', plink_box_properties + ('lambda_capacity',)),

('l2vc', vc_box_properties),
('l3vc', vc_box_properties),

('static route', route_common_properties + (
'nh_ip',
'dst_sntw',
'ad'
)),

('BGP peering', route_common_properties + (
'bgp_type',
'ipS',
'ipD',
'weightS',
'weightD'
)),

('OSPF virtual link', route_common_properties + (
'nh_tk',
'dst_sntw'
)),

('Label Switched Path', route_common_properties + (
'lsp_type',
)),                

('routed traffic', traffic_common_properties),
('static traffic', traffic_common_properties)
])

# Properties <-> User-friendly names

prop_to_nice_name = {
'name': 'Name',
'type': 'Type',
'protocol': 'Protocol',
'interface': 'Interface',
'ipaddress': 'IP address',
'subnetmask': 'Subnet mask',
'LB_paths': 'Maximum paths (LB)',
'default_route': 'Default Route',
'x': 'X coordinate', 
'y': 'Y coordinate', 
'longitude': 'Longitude', 
'latitude': 'Latitude',
'distance': 'Distance',
'node': 'Node',
'link': 'Link',
'linkS': 'Source link',
'linkD': 'Destination link', 
'costSD': 'Cost S -> D', 
'costDS': 'Cost D -> S', 
'cost': 'Cost',
'capacitySD': 'Capacity S -> D', 
'capacityDS': 'Capacity D -> S', 
'traffic': 'Traffic',
'trafficSD': 'Traffic S -> D', 
'trafficDS': 'Traffic D -> S', 
'wctrafficSD': 'Worst case traffic S -> D', 
'wctrafficDS': 'Worst case traffic D -> S', 
'wcfailure': 'Worst case failure',
'flowSD': 'Flow S -> D', 
'flowDS': 'Flow D -> S', 
'ipaddressS': 'IP address (source)',
'subnetmaskS': 'Subnet mask (source)',
'ipaddressD': 'IP address (destination)',
'subnetmaskD': 'Subnet mask (destination)',
'interfaceS': 'Interface (source)',
'interfaceD': 'Interface (destination)',
'macaddressS': 'MAC address (source)',
'macaddressD': 'MAC address (destination)',
'macaddress': 'MAC address',
'weightS': 'Weight (source)',
'weightD': 'Weight (destination)',
'sntw': 'Subnetwork',
'throughput': 'Throughput',
'lambda_capacity': 'Lambda capacity',
'source': 'Source',
'destination': 'Destination',
'nh_tk': 'Next-hop plink',
'nh_ip': 'Next-hop IP',
'ipS': 'Source IP',
'ipD': 'Destination IP',
'bgp_AS': 'BGP AS',
'dst_sntw': 'Destination subnetwork',
'ad': 'Administrative distance',
'router_id': 'Router ID',
'subtype': 'Type',
'bgp_type': 'BGP Type',
'lsp_type': 'LSP Type',
'path_constraints': 'Path constraints',
'excluded_nodes': 'Excluded nodes',
'excluded_plinks': 'Excluded physical links',
'path': 'Path',
'subnets': 'Subnets', 
'sites': 'Sites',
'AS': 'Autonomous system',
'role': 'Role',
'priority': 'Priority',
'base_macaddress': 'Base MAC address'
}

name_to_prop = {v: k for k, v in prop_to_nice_name.items()}

## NetDim objects

class NDobject(object):
    
        # an object in NetDim belongs to one or several groups, which we can
        # use as a filter to display a subset of objects
        # each site corresponds to a 'site' node, but the filter can also be
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
                    'subnetmask' : None
                    }
                    
    @initializer(ie_properties)
    def __init__(self):
        # self id and id of the corresponding label on the canvas
        self.oval = {layer: None for layer in range(1, 5)}
        # image of the node at all three layers: physical, logical and traffic
        self.image = {layer: None for layer in range(1, 5)}
        self.layer_line = {layer: None for layer in range(1, 5)}
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
        # AS_properties contains all per-AS properties: It is a dictionnary 
        # which AS name are the keys (it is easier to store AS names rather 
        # than AS itself: if we have the AS, AS.name is the name, while if we 
        # have the name, it is more verbose to retrieve the AS itself)
        self.AS_properties = defaultdict(dict)
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
        
    def __call__(self, AS, property, value=None):
        # can be used both as a getter and a setter, depending on 
        # whether a value is provided or not
        if value:
            self.AS_properties[AS][property] = value
        return self.AS_properties[AS][property]
        
class Router(Node):
    
    color = 'magenta'
    subtype = 'router'
    layer = 3
    imagex, imagey = 33, 25
        
    ie_properties = {
                    'bgp_AS' : None, 
                    # the default route is the gateway of last resort: 
                    # it is the IP address of the next-hop 
                    # (either loopback or interface)
                    'default_route' : None
                    }
                    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        # routing table: binds an IP address to a cost / next-hop
        self.rt = {}
        # arp table: binds an IP to a tuple (MAC address, outgoing interface)
        self.arpt = {}
        # reverse arp table: the other way around
        self.rarpt = {}
        # bgp table
        self.bgpt = defaultdict(set)
        super().__init__()
        
class Switch(Node):

    color = 'black'
    subtype = 'switch'
    layer = 2
    imagex, imagey = 54, 36
    
    # each switch has a base mac address which is hardcoded in
    # hardware and cannot be changed. It is used for STP
    # root election, in case switches' priorities tie.
    ie_properties = {
                     'base_macaddress': '0A0000000000',
                     }
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        # switching table: binds a MAC address to an outgoing interface
        self.st = {}
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
        # as physical link asymmetric (directional) properties (capacity, flow, etc)
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

class PhysicalLink(Link):
    
    type = 'plink'
    layer = 1
    dash = ()
    
    ie_properties = {
                    'interface' : 'GE',
                    'distance' : 0., 
                    'costSD' : 1., 
                    'costDS' : 1., 
                    'capacitySD' : 3, 
                    'capacityDS' : 3
                    }

    @initializer(ie_properties)
    def __init__(self):
        self.sntw = None
        self.trafficSD = self.trafficDS = 0.
        self.wctrafficSD = self.wctrafficDS = 0.
        self.wcfailure = None
        self.flowSD = self.flowDS = 0.
        # list of AS to which the physical links belongs. AS is actually 
        # a dictionnary associating an AS to a set of area the physical links 
        # belongs to
        self.AS = defaultdict(set)
        super().__init__()
        
    @property
    def bw(self):
        return {
                'FE': 100,
                'GE': 10,
                '10GE': 1
                }[self.interface]
        
    def __lt__(self, other):
        return hash(self.name)
        
    def __call__(self, property, node, value=None):
        # can be used both as a getter and a setter, depending on 
        # whether a value is provided or not
        dir = (node == self.source)*'SD' or 'DS'
        if property in ('flow', 'cost', 'capacity', 'traffic', 'wctraffic'):
            if value:
                setattr(self, property + dir, value)
            else:
                return getattr(self, property + dir)
                
        else:
            interface = getattr(self, 'interface' + dir[:-1])
            if property == 'interface':
                return interface
            elif value:
                setattr(interface, property, value)
            else:
                print(getattr(interface, property))
                return getattr(interface, property)

class Ethernet(PhysicalLink):
    
    color = 'blue'
    protocol = subtype = 'ethernet'
    
    ie_properties = {}
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        super().__init__()
        self.interfaceS = EthernetInterface(self.source, self)
        self.interfaceD = EthernetInterface(self.destination, self)
        
class WDMFiber(PhysicalLink):
    
    color = 'orange'
    protocol = subtype = 'wdm'
    
    ie_properties = {
                    'lambda_capacity' : 88
                    }
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        super().__init__()
        self.interfaceS = WDMInterface(self.source, self)
        self.interfaceD = WDMInterface(self.destination, self)
            
class Interface(NDobject):
    
    type = 'interface'
    
    ie_properties = {
                    'name': 'none'
                    }
        
    @initializer(ie_properties)
    def __init__(self, node, link):
        self.node = node
        self.link = link
        # AS_properties contains all per-AS properties: interface cost, 
        # interface role. It is a dictionnary which AS name are the keys 
        # (it is easier to store AS names rather than AS itself: if we have the
        # AS, AS.name is the name, while if we have the name, it is more 
        # verbose to retrieve the AS itself)
        self.AS_properties = defaultdict(dict)
        super().__init__()
        
    def __repr__(self):
        return self.name
        
    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.node == other.node
                                            and self.link == other.link)
                    
    def __hash__(self):
        return hash(self.name)
        
    def __call__(self, AS, property, value=None):
        # can be used both as a getter and a setter, depending on 
        # whether a value is provided or not
        if value:
            self.AS_properties[AS][property] = value
        if property in self.AS_properties[AS]:
            return self.AS_properties[AS][property]
        else:
            return None
                    
class EthernetInterface(Interface):
    
    subtype = 'ethernet'
    public_properties = ethernet_interface_public_properties
    perAS_properties = ethernet_interface_perAS_properties
    
    ie_properties = {
                    'ipaddress' : 'none', 
                    'subnetmask' : 'none',
                    'macaddress' : 'none',
                    }
    
    @initializer(ie_properties)
    def __init__(self, node, link, **kwargs):
        super().__init__(node, link)
        
class WDMInterface(Interface):
    
    subtype = 'wdm'
    
    ie_properties = {}
    
    @initializer(ie_properties)
    def __init__(self, node, link, **kwargs):
        super().__init__(node, link)
            
class L2VC(Link):
    
    type = 'l2link'
    subtype = 'l2vc'
    layer = 2
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
    
    type = 'l3link'
    subtype = 'l3vc'
    layer = 3
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
            return getattr(self, 'link' + dir)(property, node, value)
        
class Route(Link):
    
    type = 'l3link'
    dash = (3,5)
    layer = 3
    
    ie_properties = {
                    'path' : 'list()'
                    }
    
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
    
    ie_properties = {
                    'ipS' : None, 
                    'ipD': None
                    }
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        super().__init__()
        
class StaticTraffic(Traffic):
    
    color = 'chartreuse'
    subtype = 'static traffic'
    
    ie_properties = {
                    'path_constraints' : '[]', 
                    'excluded_plinks' : 'set()', 
                    'excluded_nodes' : 'set()', 
                    }
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        super().__init__()
