# NetDim (contact@netdim.fr)

# ordered dicts are needed to have the same menu order 
from collections import defaultdict, OrderedDict

# decorating __init__ to initialize properties
def initializer(default_properties):
    def inner_decorator(init):
        def wrapper(self, *a, **kw):
            for k in kw:
                setattr(self, k, kw[k])
                # if the imported property is not an existing NetDim property,
                # we make sure to add it everywhere it is needed, so that it's
                # properly added to the model and displayed
                # it is also automatically made exportable
                if (k not in object_properties[self.__class__.subtype]
                        and k is not 'id'):
                    for property_manager in (
                                             object_properties,
                                             object_ie,
                                             box_properties,
                                             ):
                        property_manager[self.__class__.subtype] += (k,)
                    prop_to_name[k] = k
                    
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
    
## NetDim objects

nd_obj = {
'site': 'node',
'router': 'node',
'oxc': 'node',
'host': 'node',
'antenna': 'node',
'regenerator': 'node',
'splitter': 'node',
'cloud': 'node',
'switch': 'node',
'ethernet link': 'plink',
'optical link': 'plink',
'route': 'route',
'traffic': 'traffic'
}

## Types and subtypes

# subtype -> type mapping
subtype_to_type = {
'site': 'node',
'router': 'node',
'oxc': 'node',
'host': 'node',
'antenna': 'node',
'regenerator': 'node',
'splitter': 'node',
'switch': 'node',
'cloud': 'node',
'firewall': 'node',
'load_balancer': 'node',
'server': 'node',
'sdn_switch': 'node',
'sdn_controller': 'node',
'ethernet link': 'plink',
'optical link': 'plink',
'l2vc': 'l2link',
'l3vc': 'l3link',
'optical channel': 'l2link',
'etherchannel': 'l2link',
'pseudowire': 'l3link',
'BGP peering': 'l3link',
'routed traffic': 'traffic',
'static traffic': 'traffic',
'ethernet interface': 'interface',
'optical interface': 'interface'
}
    
## OBJECT PROPERTIES
# 'public' properties means that it is displayed in the GUI
# the user can see all public properties from the object management window

## Common properties 
# properties shared by all objects of a given type

# 0) properties common to all objects

obj_common_properties = (
)

# 1) properties common to all nodes

# ordered dicts are needed to have the same menu order 
node_common_properties = obj_common_properties + (
'name', 
'x', 
'y', 
'longitude', 
'latitude', 
'logical_x',
'logical_y',
'ipaddress', 
'subnetmask', 
'sites',
'AS',
)

# 2) properties common to all physical links

plink_common_properties = obj_common_properties + (
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

interface_common_properties = obj_common_properties + (
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

route_common_properties = obj_common_properties + (
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

traffic_common_properties = obj_common_properties + (
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
node_common_ie_properties = node_common_properties[:-2]

# 2) import / export properties for physical links

plink_common_ie_properties = obj_common_properties + (
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
        
route_common_ie_properties = obj_common_properties + (
'name',
'source', 
'destination',
'sites'
)

# 4) import / export properties for traffic links

traffic_common_ie_properties = obj_common_properties + (
'name', 
'source', 
'destination', 
'throughput',
'sites'
)

## Common properties per subtype
# properties shared by all objects of a given subtype

object_properties = OrderedDict([
('site', node_common_properties + ('site_type',)),
('router', node_common_properties + ('default_route',)),
('switch', node_common_properties + ('base_macaddress',)),
('oxc', node_common_properties),
('host', node_common_properties + ('mininet_name',)),
('antenna', node_common_properties),
('regenerator', node_common_properties),
('splitter', node_common_properties),
('cloud', node_common_properties),
('firewall', node_common_properties),
('load_balancer', node_common_properties),
('server', node_common_properties),
('sdn_switch', node_common_properties + ('mininet_name',)),
('sdn_controller', node_common_properties + ('mininet_name',)),

('ethernet link', plink_common_properties),
('optical link', plink_common_properties + ('lambda_capacity',)),

('l2vc', vc_common_properties),
('l3vc', vc_common_properties),

('optical channel', route_common_properties),
('etherchannel', route_common_properties),

('pseudowire', route_common_properties),

('BGP peering', route_common_properties + (
'bgp_type',
'ipS',
'ipD',
'weightS',
'weightD',
'AS'
)),

('routed traffic', traffic_common_properties + ('ipS', 'ipD')),
('static traffic', traffic_common_properties),

])

## Common Import / Export properties per subtype

object_ie = OrderedDict([
('site', node_common_ie_properties),
('router', node_common_ie_properties + ('default_route',)),
('switch', node_common_ie_properties + ('base_macaddress',)),
('oxc', node_common_ie_properties),
('host', node_common_ie_properties),
('antenna', node_common_ie_properties),
('regenerator', node_common_ie_properties),
('splitter', node_common_ie_properties),
('cloud', node_common_ie_properties),
('firewall', node_common_ie_properties),
('load_balancer', node_common_ie_properties),
('server', node_common_ie_properties),
('sdn_switch', node_common_ie_properties),
('sdn_controller', node_common_ie_properties),

('ethernet link', plink_common_ie_properties),
('optical link', plink_common_ie_properties + ('lambda_capacity',)),

('optical channel', route_common_ie_properties),
('etherchannel', route_common_ie_properties),

('pseudowire', route_common_ie_properties),

('BGP peering', route_common_ie_properties + (
'bgp_type',
'ipS',
'ipD',
'weightS',
'weightD'
)),

('routed traffic', traffic_common_ie_properties + (
'ipS',
'ipD'
)),
('static traffic', traffic_common_ie_properties),

('ethernet interface', ethernet_interface_properties),
('optical interface', interface_common_properties)
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

# top-level menu: all types with types common properties

type_labels = OrderedDict([
('node', node_common_ie_properties + ('position', 'coordinates')),
('plink', plink_common_ie_properties + ('capacity', 'flow', 'traffic', 'wctraffic')),
('l2link', route_common_ie_properties),
('l3link', route_common_ie_properties),
('traffic', traffic_common_ie_properties),
('interface', ('name', 'ipaddress', 'cost')),
])

## Box properties
# box properties defines which properties are to be displayed in the
# upper left corner of the canvas when hoverin over an object

node_box_properties = (
'name', 
'subtype',
'ipaddress', 
'subnetmask',
'longitude',
'latitude',
'logical_x',
'logical_y'
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
('site', node_box_properties + ('site_type',)),
('router', node_box_properties + ('default_route',)),
('switch', node_box_properties + ('base_macaddress',)),
('oxc', node_box_properties),
('host', node_box_properties + ('mininet_name',)),
('antenna', node_box_properties),
('regenerator', node_box_properties),
('splitter', node_box_properties),
('cloud', node_box_properties),
('firewall', node_box_properties),
('load_balancer', node_box_properties),
('server', node_box_properties),
('sdn_switch', node_box_properties + ('mininet_name',)),
('sdn_controller', node_box_properties + ('mininet_name',)),

('ethernet link', plink_box_properties),
('optical link', plink_box_properties + ('lambda_capacity',)),

('l2vc', vc_box_properties),
('l3vc', vc_box_properties),

('optical channel', route_common_properties),
('etherchannel', route_common_properties),

('pseudowire', route_common_properties),

('BGP peering', route_common_properties + (
'bgp_type',
'ipS',
'ipD',
'weightS',
'weightD'
)),

('routed traffic', traffic_common_properties),
('static traffic', traffic_common_properties)
])

# Properties <-> User-friendly names

prop_to_name = {
'coordinates': 'Coordinates',
'capacity': 'Capacity',
'flow': 'Flow',
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
'logical_x': 'Logical X coordinate',
'logical_y': 'Logical Y coordinate',
'costSD': 'Cost S -> D', 
'costDS': 'Cost D -> S', 
'cost': 'Cost',
'capacitySD': 'Capacity S -> D', 
'capacityDS': 'Capacity D -> S',
'traffic': 'Traffic',
'trafficSD': 'Traffic S -> D', 
'trafficDS': 'Traffic D -> S', 
'wctraffic': 'Worst case traffic',
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
'mininet_name': 'Mininet name',
'None': 'None',
'local_pref': 'Local preference',
'sntw': 'Subnetwork',
'throughput': 'Throughput',
'lambda_capacity': 'Lambda capacity',
'source': 'Source',
'destination': 'Destination',
'nh_tk': 'Next-hop plink',
'nh_ip': 'Next-hop IP',
'ipS': 'Source IP',
'ipD': 'Destination IP',
'dst_sntw': 'Destination subnetwork',
'ad': 'Administrative distance',
'router_id': 'Router ID',
'subtype': 'Type',
'bgp_type': 'BGP Type',
'path_constraints': 'Path constraints',
'excluded_nodes': 'Excluded nodes',
'excluded_plinks': 'Excluded physical links',
'path': 'Path',
'position': 'Position',
'subnets': 'Subnets', 
'site_type': 'Type of site',
'sites': 'Sites',
'AS': 'Autonomous system',
'role': 'Role',
'priority': 'Priority',
'base_macaddress': 'Base MAC address',
'weightS': 'Source weight',
'weightD': 'Destination weight'
}

name_to_prop = {v: k for k, v in prop_to_name.items()}

type_to_name = {
'node': 'Node',
'plink': 'Physical link',
'l2link': 'Layer-2 link',
'l3link': 'Layer-3 link',
'traffic': 'Traffic link',
'interface': 'Interface',
}

name_to_type = {v: k for k, v in type_to_name.items()}

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
                    'name': None,
                    }
                    
    @initializer(ie_properties)
    def __init__(self):
        # per-site id
        self.site_id = {}
        # sites is the set of sites the object belongs to
        self.sites = set()

## Nodes
class Node(NDobject):
    
    class_type = type = 'node'
    ie_properties = {
                    'x' : 0, 
                    'y' : 0, 
                    'longitude' : 48.856638, 
                    'latitude' : 2.352241, 
                    'logical_x': 0,
                    'logical_y': 0,
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
        self.size = 8
        # site coordinates: coordinates of the node for each site it belongs to
        # associate a site to a list of coordinates [x, y]
        self.site_coords = {}
        # site properties for site canvas
        self.site_oval = {}
        self.site_image = {}
        self.site_layer_line = {}
        self.site_lid = {}
        self.site_lpos = {}
        self.site_size = {}
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
        
    def __call__(self, AS, property, value=False):
        # can be used both as a getter and a setter, depending on 
        # whether a value is provided or not
        if value != False:
            self.AS_properties[AS][property] = value
        return self.AS_properties[AS][property]
        
class Site(Node):
    
    color = 'black'
    subtype = 'site'
    imagex, imagey = 50, 50
    layer = 1
        
    ie_properties = {
                    'x' : 600, 
                    'y' : 300, 
                    'longitude' : 0, 
                    'latitude' : 0, 
                    'logical_x': 0,
                    'logical_y': 0,
                    'ipaddress' : None,
                    'subnetmask' : None
                    }
                    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        # pool site: nodes and links that belong to the site
        self.ps = {'node': set(), 'link': set()}
        # sites can be either physical or logical: a physical site is a site
        # like a building or a shelter, that contains colocated network devices,
        # and a logical site is a way of filtering the view to a subset of 
        # objects 
        self.site_type = 'Physical'
        super().__init__()
        
    def get_obj(self):
        yield from self.ps['node']
        yield from self.ps['link']
        
    def add_to_site(self, *objects):
        for obj in objects:
            if obj in self.ps[obj.class_type]:
                continue
            self.ps[obj.class_type].add(obj)
            obj.sites.add(self)
            obj.site_id[self] = None
            if obj.class_type == 'node':
                # initialize all site properties
                obj.site_coords[self] = [600, 300]
                # site properties for site canvas
                obj.site_oval[self] = {layer: None for layer in range(1, 5)}
                obj.site_image[self] = {layer: None for layer in range(1, 5)}
                obj.site_layer_line[self] = {layer: None for layer in range(1, 5)}
                obj.site_lid[self] = None
                obj.site_size[self] = 8
                # draw the object in the insite view
                self.view.create_node(obj)
            else:
                # it is a link
                # add the edges first:
                for edge in (obj.source, obj.destination):
                    self.add_to_site(edge)
                obj.site_line[self] = None
                obj.site_lid[self] = None
                obj.site_ilid[self] = [None]*2
                obj.site_lpos[self] = [None]*2
                # draw the object in the insite view
                self.view.create_link(obj)

    def remove_from_site(self, *objects):
        for obj in objects:
            self.ps[obj.class_type].remove(obj)
            obj.sites.remove(self)
            if obj.class_type == 'node':
                obj.site_oval.pop(self)
                obj.site_image.pop(self)
                obj.site_layer_line.pop(self)
                obj.site_lid.pop(self)
                obj.site_size.pop(self)
            else:
                obj.site_line.pop(self)
                obj.site_lid.pop(self)
                obj.site_ilid.pop(self)
                obj.site_lpos.pop(self)
        
class Router(Node):
    
    color = 'magenta'
    subtype = 'router'
    layer = 3
    imagex, imagey = 33, 25
        
    ie_properties = {
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
        self.mininet_name = None
        super().__init__()
        
    def mininet_conf(self):
        return '{n} = net.addHost(\'{n}\')\n'.format(n=self.mininet_name)
        
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
        
class Firewall(Node):

    color = 'black'
    subtype = 'firewall'
    layer = 3
    imagex, imagey = 40, 40
    
    ie_properties = {}
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        super().__init__()
        
class LoadBalancer(Node):

    color = 'black'
    subtype = 'load_balancer'
    layer = 3
    imagex, imagey = 46, 34
    
    ie_properties = {}
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        super().__init__()
        
class Server(Node):

    color = 'black'
    subtype = 'server'
    layer = 3
    imagex, imagey = 26, 26
    
    ie_properties = {}
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        super().__init__()
        
class SDN_Switch(Node):

    color = 'black'
    subtype = 'sdn_switch'
    layer = 3
    imagex, imagey = 40, 40
    
    ie_properties = {}
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        self.mininet_name = None
        super().__init__()
        
    def mininet_conf(self):
        return '{n} = net.addSwitch(\'{n}\')\n'.format(n=self.mininet_name)
        
class SDN_Controller(Node):

    color = 'black'
    subtype = 'sdn_controller'
    layer = 3
    imagex, imagey = 40, 40
    
    ie_properties = {}
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        self.mininet_name = None
        super().__init__()
        
    def mininet_conf(self):
        return '{n} = net.addController(\'{n}\')\n'.format(n=self.mininet_name)
        
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
        self.lpos = [None]*2
        # site properties for site canvas
        self.site_line = {}
        self.site_lid = {}
        self.site_ilid = {}
        self.site_lpos = {}
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
        
    # value is initialied to False instead of None, because we may want
    # to set a property to None
    def __call__(self, property, node, value=False, AS=None):
        # can be used both as a getter and a setter, depending on 
        # whether a value is provided or not
        
        # first of all, this call function can be used to retrieve a 
        # link directional property ('SD', 'DS')
        # these properties are used for classic algorithms such as 
        # shortest paths and flow algorithms
        dir = (node == self.source)*'SD' or 'DS'
        if not AS and property in ('flow', 'cost', 'capacity', 'traffic', 'wctraffic'):
            if value != False:
                setattr(self, property + dir, value)
            else:
                return getattr(self, property + dir)
                
        else:
            # it can also be used to retrieve the value of a property of the 
            # interface attached to the node
            # if that property is 'interface', this interface object itself
            # will be retrieve
            interface = getattr(self, 'interface' + dir[:-1])
            if not AS:
                if property == 'interface':
                    return interface
                elif value == False:
                    return getattr(interface, property)
                else:
                    setattr(interface, property, value)
                
            # finally, if an AS is defined, it will retrieve the value of the 
            # per-AS property of the interface attached to the node
            # NOTE: it is the AS name, not the AS object itself
            else:
                if value == False:
                    return interface(AS, property)
                else:
                    interface(AS, property, value)

class EthernetLink(PhysicalLink):
    
    color = 'blue'
    subtype = 'ethernet link'
    
    ie_properties = {}
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        super().__init__()
        self.interfaceS = EthernetInterface(self.source, self)
        self.interfaceD = EthernetInterface(self.destination, self)
        
class OpticalLink(PhysicalLink):
    
    color = 'violet red'
    subtype = 'optical link'
    
    ie_properties = {
                    'lambda_capacity' : 88
                    }
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        super().__init__()
        self.interfaceS = OpticalInterface(self.source, self)
        self.interfaceD = OpticalInterface(self.destination, self)
            
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
        return self.node == other.node and self.link == other.link
                                            
    def __hash__(self):
        return hash(self.node) + hash(self.link)
        
    def __call__(self, AS, property, value=False):
        # can be used both as a getter and a setter, depending on 
        # whether a value is provided or not
        if value != False:
            self.AS_properties[AS][property] = value
        if property in self.AS_properties[AS]:
            return self.AS_properties[AS][property]
        else:
            return None
                    
class EthernetInterface(Interface):
    
    subtype = 'ethernet interface'
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
        
class OpticalInterface(Interface):
    
    subtype = 'optical interface'
    
    ie_properties = {}
    
    @initializer(ie_properties)
    def __init__(self, node, link, **kwargs):
        super().__init__(node, link)
        
class VirtualConnection(Link):  
    
    ie_properties = {}
    color = 'bisque3'
    dash = (3,5)

    @initializer(ie_properties)
    def __init__(self, **kwargs):
        self.linkS = None
        self.linkD = None
        super().__init__()
        
    def __lt__(self, other):
        return hash(self.name)
        
    def __call__(self, property, node, value=False):
        # can be used both as a getter and a setter, depending on 
        # whether a value is provided or not
        # if the property doesn't exist for a virtual connection, we look at
        # the equivalent property for the associated physical link
        dir = (node == self.source)*'S' or 'D'
        if hasattr(self, property + dir):
            if value != False:
                setattr(self, property + dir, value)
            else:
                return getattr(self, property + dir)
        else:
            return getattr(self, 'link' + dir)(property, node, value)  
            
class L2VC(VirtualConnection):
    
    type = 'l2link'
    subtype = 'l2vc'
    layer = 2
    
    ie_properties = {}

    @initializer(ie_properties)
    def __init__(self, **kwargs):
        super().__init__()
        
class L3VC(VirtualConnection):
    
    type = 'l3link'
    subtype = 'l3vc'
    layer = 3
    
    ie_properties = {}

    @initializer(ie_properties)
    def __init__(self, **kwargs):
        super().__init__()
        
class Route(Link):
        
    ie_properties = {
                    'path' : 'list()'
                    }
    dash = ()
    
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
        
class OpticalChannel(Route):

    type = 'l2link'
    subtype = 'optical channel'
    color = 'sienna1'
    layer = 2
    
    ie_properties = {}
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        # list of AS to which the physical links belongs. AS is actually 
        # a dictionnary associating an AS to a set of area the physical links 
        # belongs to
        self.AS = defaultdict(set)
        super().__init__()
        
class EtherChannel(Route):

    type = 'l2link'
    subtype = 'etherchannel'
    color = 'firebrick3'
    layer = 2
    
    ie_properties = {}
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        # list of AS to which the physical links belongs. AS is actually 
        # a dictionnary associating an AS to a set of area the physical links 
        # belongs to
        self.AS = defaultdict(set)
        super().__init__()
        
class PseudoWire(Route):

    type = 'l3link'
    subtype = 'pseudowire'
    color = 'purple2'
    layer = 3
    
    ie_properties = {}
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        # list of AS to which the physical links belongs. AS is actually 
        # a dictionnary associating an AS to a set of area the physical links 
        # belongs to
        self.AS = defaultdict(set)
        super().__init__()
        
class BGPPeering(Route):

    type = 'l3link'
    subtype = 'BGP peering'
    color = 'aquamarine2'
    layer = 3
    
    ie_properties = {
                    'weightD' : 0,
                    'weightS' : 0, 
                    'ipS' : None, 
                    'ipD': None,
                    'bgp_type': 'eBGP'
                    }
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        # list of AS to which the physical links belongs. AS is actually 
        # a dictionnary associating an AS to a set of area the physical links 
        # belongs to
        self.AS = defaultdict(set)
        super().__init__()
        
class Traffic(Link):
    
    type = 'traffic'
    subtype = type
    dash = (7,1,1,1)
    layer = 4
    
    ie_properties = {
                    'throughput': 15
                    }
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        super().__init__()
        
class RoutedTraffic(Traffic):
        
    color = 'cyan4'
    subtype = 'routed traffic'
    
    ie_properties = {
                    'ipS' : None, 
                    'ipD': None
                    }
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        super().__init__()
        
class StaticTraffic(Traffic):
    
    color = 'green3'
    subtype = 'static traffic'
    
    ie_properties = {
                    'path_constraints' : '[]', 
                    'excluded_plinks' : 'set()', 
                    'excluded_nodes' : 'set()', 
                    }
    
    @initializer(ie_properties)
    def __init__(self, **kwargs):
        super().__init__()
        
## NetDim classes

# ordered to keep the order when using the keys 
node_class = OrderedDict([
('router', Router),
('oxc', OXC),
('host', Host),
('antenna', Antenna),
('regenerator', Regenerator),
('splitter', Splitter),
('switch', Switch),
('cloud', Cloud),
('firewall', Firewall),
('load_balancer', LoadBalancer),
('server', Server),
('site', Site),
('sdn_switch', SDN_Switch),
('sdn_controller', SDN_Controller)
])

# layer 1 (physical links)
plink_class = OrderedDict([
('ethernet link', EthernetLink),
('optical link', OpticalLink)
])

# layer 2 (optical and ethernet)
l2link_class = OrderedDict([
('l2vc', L2VC),
('optical channel', OpticalChannel),
('etherchannel', EtherChannel)
])

# layer 3 (IP and above)
l3link_class = OrderedDict([
('l3vc', L3VC),
('pseudowire', PseudoWire),
('BGP peering', BGPPeering),
])

# layer 4 (traffic flows)
traffic_class = OrderedDict([
('routed traffic', RoutedTraffic),
('static traffic', StaticTraffic)
])

link_class = {}
for dclass in (plink_class, l2link_class, l3link_class, traffic_class):
    link_class.update(dclass)

link_type = ('plink', 'l2link', 'l3link', 'traffic')
node_subtype = tuple(node_class.keys())
link_subtype = tuple(link_class.keys())
all_subtypes = node_subtype + link_subtype

type_to_subtype = {
'node': tuple(node_class.keys()),
'plink': tuple(plink_class.keys()),
'l2link': tuple(l2link_class.keys()),
'l3link': tuple(l3link_class.keys()),
'traffic': tuple(traffic_class.keys()),
'interface': ('ethernet interface', 'optical interface')
}

