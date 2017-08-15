# Copyright (C) 2017 Antoine Fourmy <antoine dot fourmy at gmail dot com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# ordered dicts are needed to have the same menu order 
from collections import defaultdict, OrderedDict
from .properties import *

# decorating __init__ to initialize properties
def initializer(init):
    def wrapper(self, **properties):
        for property_name, value in properties.items():
            # if the imported property is not an existing NetDim property,
            # we make sure to add it everywhere it is needed, so that it's
            # properly added to the model and displayed
            # it is also automatically made exportable
            if property_name not in property_classes:
                property_class = type(
                                      property_name, 
                                      (TextProperty,), 
                                      {
                                      'name': property_name, 
                                      'pretty_name': property_name
                                      })
                property_classes[property_name] = property_class
                for property_manager in (
                                        object_properties,
                                        object_ie,
                                        box_properties,
                                        ):
                    property_manager[self.__class__.subtype] += (property_class,)
            else:
                property_class = property_classes[property_name]
            setattr(self, property_name, property_class(value))
                
        for property_class in object_properties[self.__class__.subtype]:
            if not hasattr(self, property_class.name):
                # if the value should be an empty list / set, we make
                # sure it refers to different objects in memory by using eval
                try:
                    setattr(self, property_class.name, property_class())
                except (TypeError, NameError, SyntaxError):
                    setattr(self, property_class.name, property_class())
        init(self)
    return wrapper

    
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

obj_common_properties = ()

# 1) properties common to all nodes

# ordered dicts are needed to have the same menu order 
node_common_properties = obj_common_properties + (
Name, 
X, 
Y, 
Longitude, 
Latitude, 
LogicalX,
LogicalY,
IP_Address, 
SubnetMask, 
Sites,
AS,
)

# 2) properties common to all physical links

plink_common_properties = obj_common_properties + (
Name, 
Source, 
Destination, 
Interface,
InterfaceS,
InterfaceD,
Distance, 
CostSD, 
CostDS, 
CapacitySD, 
CapacityDS, 
# if there is no failure simulation, the traffic property tells us how
# much traffic is transiting on the plink in a 'no failure' situation
# if there is a link in failure, the traffic that is redirected will 
# also contribute to this 'traffic parameter'.
TrafficSD, 
TrafficDS,
# unlike the traffic property above, wctraffic is the worst case
# traffic. It is the traffic that we use for dimensioning purposes, and
# it considers the maximum traffic that the link must be able to 
# handle, considering all possible failure cases.
# 'wctrafficSD',
# 'wctrafficDS',
# # the plink which failure results in the worst case traffic
# 'wcfailure',
# 'flowSD', 
# 'flowDS',
Sites,
Subnetwork,
AS,
)

# 3) properties common to all interfaces

interface_common_properties = obj_common_properties + (
Name,
Link,
Node
)

# 4) properties common to all interfaces

ethernet_interface_properties = interface_common_properties + (
IP_Address,
SubnetMask,
MAC_Address
)

# 5) properties common to all routes

route_common_properties = obj_common_properties + (
Name,
Subtype,
Source, 
Destination,
Sites
)

# 6) properties common to all VC

vc_common_properties = (
Name,
Source, 
Destination,
LinkS,
LinkD,
Sites
)

# 7) properties common to all traffic links

traffic_common_properties = obj_common_properties + (
Name,
Subtype,
Source, 
Destination,
Throughput,
Sites
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
Name, 
Source, 
Destination, 
Interface,
Distance, 
CostSD, 
CostDS, 
CapacitySD, 
CapacityDS, 
Sites
)

# 3) import / export properties for routes
        
route_common_ie_properties = obj_common_properties + (
Name, 
Source, 
Destination, 
Sites
)

# 4) import / export properties for traffic links

traffic_common_ie_properties = obj_common_properties + (
Name, 
Source, 
Destination, 
Throughput, 
Sites
)

## Common properties per subtype
# properties shared by all objects of a given subtype

object_properties = OrderedDict([
('site', node_common_properties),
('router', node_common_properties),
('switch', node_common_properties),
('oxc', node_common_properties),
('host', node_common_properties),
('antenna', node_common_properties),
('regenerator', node_common_properties),
('splitter', node_common_properties),
('cloud', node_common_properties),
('firewall', node_common_properties),
('load_balancer', node_common_properties),
('server', node_common_properties),
('ethernet link', plink_common_properties),
('optical link', plink_common_properties),
('l2vc', vc_common_properties),
('l3vc', vc_common_properties),
('optical channel', route_common_properties),
('etherchannel', route_common_properties),
('pseudowire', route_common_properties),
('BGP peering', route_common_properties),
('routed traffic', traffic_common_properties),
('static traffic', traffic_common_properties),
('ethernet interface', ethernet_interface_properties),
('optical interface', interface_common_properties)
])

## Common Import / Export properties per subtype

object_ie = OrderedDict([
('site', node_common_ie_properties),
('router', node_common_ie_properties),
('switch', node_common_ie_properties),
('oxc', node_common_ie_properties),
('host', node_common_ie_properties),
('antenna', node_common_ie_properties),
('regenerator', node_common_ie_properties),
('splitter', node_common_ie_properties),
('cloud', node_common_ie_properties),
('firewall', node_common_ie_properties),
('load_balancer', node_common_ie_properties),
('server', node_common_ie_properties),
('ethernet link', plink_common_ie_properties),
('optical link', plink_common_ie_properties),
('optical channel', route_common_ie_properties),
('etherchannel', route_common_ie_properties),
('pseudowire', route_common_ie_properties),
('BGP peering', route_common_ie_properties),
('routed traffic', traffic_common_ie_properties),
('static traffic', traffic_common_ie_properties),
('ethernet interface', ethernet_interface_properties),
('optical interface', interface_common_properties)
])

## Interface basic and per-AS public properties

interface_public_properties = (
Link,
Node,
Name
)
                               
ethernet_interface_public_properties = interface_public_properties + (
IP_Address,
SubnetMask,
MAC_Address
)

ethernet_interface_perAS_properties = (
Cost,
Role,
Priority
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
('interface', ('name', 'ip_address', 'cost')),
])

subtype_labels = OrderedDict([
('site', node_common_ie_properties),
('router', node_common_ie_properties),
('switch', node_common_ie_properties),
('oxc', node_common_ie_properties),
('host', node_common_ie_properties),
('antenna', node_common_ie_properties),
('regenerator', node_common_ie_properties),
('splitter', node_common_ie_properties),
('cloud', node_common_ie_properties),
('firewall', node_common_ie_properties),
('load_balancer', node_common_ie_properties),
('server', node_common_ie_properties),
('ethernet link', plink_common_ie_properties),
('optical link', plink_common_ie_properties),
('optical channel', route_common_ie_properties),
('etherchannel', route_common_ie_properties),
('pseudowire', route_common_ie_properties),
('BGP peering', route_common_ie_properties),
('routed traffic', traffic_common_ie_properties),
('static traffic', traffic_common_ie_properties),
('ethernet interface', ethernet_interface_properties),
('optical interface', interface_common_properties)
])

## Box properties
# box properties defines which properties are to be displayed in the
# upper left corner of the canvas when hoverin over an object

node_box_properties = (
'name', 
'subtype',
'ip_address', 
'subnet_mask',
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
('site', node_box_properties),
('router', node_box_properties),
('switch', node_box_properties),
('oxc', node_box_properties),
('host', node_box_properties),
('antenna', node_box_properties),
('regenerator', node_box_properties),
('splitter', node_box_properties),
('cloud', node_box_properties),
('firewall', node_box_properties),
('load_balancer', node_box_properties),
('server', node_box_properties),
('ethernet link', plink_box_properties),
('optical link', plink_box_properties),
('l2vc', vc_box_properties),
('l3vc', vc_box_properties),
('optical channel', route_common_properties),
('etherchannel', route_common_properties),
('pseudowire', route_common_properties),
('BGP peering', route_common_properties),
('routed traffic', traffic_common_properties),
('static traffic', traffic_common_properties)
])

# Objects <-> User-friendly names

obj_to_name = {
'site': 'Site',
'router': 'Router',
'oxc': 'Optical switch',
'host': 'Host',
'antenna': 'Antenna',
'regenerator': 'Regenerator',
'splitter': 'Splitter',
'switch': 'Switch',
'cloud': 'Cloud',
'firewall': 'Firewall',
'load_balancer': 'Load Balancer',
'server': 'Server',
'ethernet link': 'Ethernet link',
'optical link': 'Optical link',
'l2vc': 'Layer-2 flow',
'l3vc': 'Layer-3 flow',
'optical channel': 'Optical Channel',
'etherchannel': 'Etherchannel',
'pseudowire': 'Pseudowire',
'BGP peering': 'BGP peering',
'routed traffic': 'Routed traffic',
'static traffic': 'Static traffic',
'ethernet interface': 'Ethernet interface',
'optical interface': 'Optical interface'
}

name_to_obj = {v: k for k, v in obj_to_name.items()}

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
    
    def __init__(self):
        self.gobject = {}
        # sites is the set of sites the object belongs to
        self.sites = set()
        
    def update_properties(self, kwargs):
        for k in kwargs:
            # if the imported property is not an existing NetDim property,
            # we make sure to add it everywhere it is needed, so that it's
            # properly added to the model and displayed
            # it is also automatically made exportable
            if k not in property_classes:
                new_property = type(k, (TextProperty,), {'name':k,
                                                    'pretty_name':k})
                property_classes[k] = new_property
                for property_manager in (
                                            object_properties,
                                            object_ie,
                                            box_properties,
                                            ):
                    property_manager[self.__class__.subtype] += (new_property,) 
            property = property_classes[k]
            setattr(self, k, property(kwargs[k]))

## Nodes
class Node(NDobject):
    
    class_type = type = 'node'

    def __init__(self):
        # dictionnary that associates a graphical item to a view
        self.gnode = {}

        # list of AS to which the node belongs. AS is actually a dictionnary
        # associating an AS to a set of area the node belongs to
        self.AS = defaultdict(set)

        # AS_properties contains all per-AS properties: It is a dictionnary 
        # which AS name are the keys (it is easier to store AS names rather 
        # than AS itself: if we have the AS, AS.name is the name, while if we 
        # have the name, it is more verbose to retrieve the AS itself)
        self.AS_properties = defaultdict(dict)
        
        # NAPALM data
        self.napalm_data = {}
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
        
    @initializer
    def __init__(self, **kwargs):
        # pool site: nodes and links that belong to the site
        self.ps = {'node': set(), 'link': set()}
        # sites can be either physical or logical: a physical site is a site
        # like a building or a shelter, that contains colocated network devices,
        # and a logical site is a way of filtering the view to a subset of 
        # objects 
        self.site_type = 'Physical'
        super().__init__()
        
    def add_to_site(self, *objects):
        for obj in objects:
            self.ps[obj.class_type].add(obj)
            obj.sites.add(self)

    def remove_from_site(self, *objects):
        for obj in objects:
            self.ps[obj.class_type].remove(obj)
            obj.sites.remove(self)
        
class Router(Node):
    
    color = 'magenta'
    subtype = 'router'
    layer = 3
    imagex, imagey = 33, 25
                    
    @initializer
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
    
    @initializer
    def __init__(self, **kwargs):
        # switching table: binds a MAC address to an outgoing interface
        self.st = {}
        super().__init__()
        
class OXC(Node):

    color = 'pink'
    subtype = 'oxc'
    layer = 2
    imagex, imagey = 35, 32
    
    @initializer
    def __init__(self, **kwargs):
        super().__init__()
        
class Host(Node):

    color = 'blue'
    subtype = 'host'
    layer = 3
    imagex, imagey = 35, 32
    
    @initializer
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
    
    @initializer
    def __init__(self, **kwargs):
        super().__init__()
        
class Splitter(Node):

    color = 'black'
    subtype = 'splitter'
    layer = 1
    imagex, imagey = 64, 50
    
    @initializer
    def __init__(self, **kwargs):
        super().__init__()
        
class Antenna(Node):

    color = 'black'
    subtype = 'antenna'
    layer = 1
    imagex, imagey = 35, 32
    
    @initializer
    def __init__(self, **kwargs):
        super().__init__()
        
class Cloud(Node):

    color = 'black'
    subtype = 'cloud'
    layer = 3
    imagex, imagey = 60, 35
    
    @initializer
    def __init__(self, **kwargs):
        super().__init__()
        
class Firewall(Node):

    color = 'black'
    subtype = 'firewall'
    layer = 3
    imagex, imagey = 40, 40
    
    @initializer
    def __init__(self, **kwargs):
        super().__init__()
        
class LoadBalancer(Node):

    color = 'black'
    subtype = 'load_balancer'
    layer = 3
    imagex, imagey = 46, 34
    
    @initializer
    def __init__(self, **kwargs):
        super().__init__()
        
class Server(Node):

    color = 'black'
    subtype = 'server'
    layer = 3
    imagex, imagey = 26, 26
    
    @initializer
    def __init__(self, **kwargs):
        super().__init__()
        
## Links
class Link(NDobject):
    
    class_type = 'link'
    
    def __init__(self):
        self.glink = {}
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
    
    @initializer
    def __init__(self, **kwargs):
        super().__init__()
        self.interfaceS = EthernetInterface(self.source, self)
        self.interfaceD = EthernetInterface(self.destination, self)
        
class OpticalLink(PhysicalLink):
    
    color = 'violet red'
    subtype = 'optical link'
    
    @initializer
    def __init__(self, **kwargs):
        super().__init__()
        self.interfaceS = OpticalInterface(self.source, self)
        self.interfaceD = OpticalInterface(self.destination, self)
            
class Interface(NDobject):
    
    type = 'interface'
        
    @initializer
    def __init__(self, **kwargs):
        # self.node = node
        # self.link = link
        # AS_properties contains all per-AS properties: interface cost, 
        # interface role. It is a dictionnary which AS name are the keys 
        # (it is easier to store AS names rather than AS itself: if we have the
        # AS, AS.name is the name, while if we have the name, it is more 
        # verbose to retrieve the AS itself)
        self.AS_properties = defaultdict(dict)
        super().__init__()
        
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
    
    def __init__(self, node, link, **kwargs):
        kwargs['node'] = node
        kwargs['link'] = link
        super().__init__(**kwargs)
        
class OpticalInterface(Interface):
    
    subtype = 'optical interface'
    
    def __init__(self, node, link, **kwargs):
        kwargs['node'] = node
        kwargs['link'] = link
        super().__init__(**kwargs)
        
class VirtualConnection(Link):  
    
    color = 'bisque3'
    dash = (3,5)

    @initializer
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

    @initializer
    def __init__(self, **kwargs):
        super().__init__()
        
class L3VC(VirtualConnection):
    
    type = 'l3link'
    subtype = 'l3vc'
    layer = 3
    
    @initializer
    def __init__(self, **kwargs):
        super().__init__()
        
class Route(Link):
        
    dash = ()
    
    @initializer
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
    
    @initializer
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
    
    @initializer
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
    
    @initializer
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
    
    @initializer
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
    
    @initializer
    def __init__(self, **kwargs):
        super().__init__()
        
class RoutedTraffic(Traffic):
        
    color = 'cyan4'
    subtype = 'routed traffic'
    
    @initializer
    def __init__(self, **kwargs):
        super().__init__()
        
class StaticTraffic(Traffic):
    
    color = 'green3'
    subtype = 'static traffic'
    
    @initializer
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
])

# layer 1 (physical links)
plink_class = OrderedDict([
('ethernet link', EthernetLink),
('optical link', OpticalLink)
])

# layer 2 (optical and ethernet)
l2link_class = OrderedDict([
('optical channel', OpticalChannel),
('etherchannel', EtherChannel)
])

# layer 3 (IP and above)
l3link_class = OrderedDict([
('pseudowire', PseudoWire),
('BGP peering', BGPPeering)
])

# layer 4 (traffic flows)
traffic_class = OrderedDict([
('routed traffic', RoutedTraffic),
('static traffic', StaticTraffic)
])

# virtual container
vc_class = OrderedDict([
('l2vc', L2VC),
('l3vc', L3VC),
])

link_class = OrderedDict()
for dclass in (plink_class, l2link_class, l3link_class, traffic_class):
    link_class.update(dclass)
    
# used in the link factory
link_class_with_vc = OrderedDict()
link_class_with_vc.update(vc_class)
link_class_with_vc.update(link_class)

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

# per-type name to object association
node_name_to_obj = OrderedDict((obj_to_name[node], node) for node in node_subtype)
link_name_to_obj = OrderedDict((obj_to_name[link], link) for link in link_subtype)
