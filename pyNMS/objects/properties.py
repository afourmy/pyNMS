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

# all classes have a name parameter: it is the name of the object variable
# all classes have a "pretty name": the name of the property when displayed
# in the GUI.
# MetaProperty is a metaclass for all properties: it implements the __repr__
# function to display the pretty name by calling str on the property class itself.

# Some classes like 'int' are immutables: they cannot be modified after creation
# we must use __new__ instead of __init_

class MetaProperty(type):
    
    def __repr__(self):
        return self.pretty_name

class Property(metaclass=MetaProperty):
    
    # whether we need to convert the property value into a pyNMS object or not
    conversion_needed = False
    # some properties have multiple values (defined as a list: property.values)
    multiple_values = False
    # for property such as password, we hide the view
    hide_view = False
    # by default, the property can be modified by the user. This wouldn't be the
    # case of a complex structure like a dictionnnary
    is_editable = True
    
    def __repr__(self):
        return str(self)
        
class TextProperty(str, Property):
    
    subtype = 'str'
    
    def __new__(cls, value):
        return str.__new__(cls, value)
        
class IntProperty(int, Property):
    
    subtype = 'int'
    
    def __new__(cls, value):
        return int.__new__(cls, int(value))
        
class FloatProperty(float, Property):
    
    subtype = 'float'
    
    def __new__(cls, value):
        return float.__new__(cls, float(value))
        
class ListProperty(list, Property):
    
    subtype = 'list'
    multiple_values = True
    choose_one_value = False
    
    def __new__(cls, values=None):
        if isinstance(values, str):
            values = eval(values)
        cls.values = values
        return values
        
class SetProperty(set, Property):
    
    subtype = 'set'
    multiple_values = True
    choose_one_value = True
    
    def __new__(cls, values=None):
        if isinstance(values, str):
            values = eval(values)
        cls.values = values
        return values
        
class DictProperty(set, Property):
    
    subtype = 'dict'
    # a dictionnary is a complex structure (it can contain other dict):
    # therefore, it cannot be edited graphically, only in YAML
    is_editable = False
    
    def __new__(cls, value):
        return value
        
class NodeProperty(Property):
    
    subtype = 'node'
    conversion_needed = True
    converter = 'convert_node'
    
    def __new__(cls, node):
        return node
        
class LinkProperty(Property):
    
    subtype = 'link'
    conversion_needed = True
    converter = 'convert_link'
    
    def __new__(cls, link):
        return link
        
class IPProperty(Property):
    
    subtype = 'ip'
    conversion_needed = True
    converter = 'convert_IP'
    
    def __new__(cls, ip):
        return ip
        
## Object properties

class ID(IntProperty):
    
    name = 'id'
    pretty_name = 'ID'
    
    def __new__(cls, value):
        return value

class Name(TextProperty):
    
    name = 'name'
    pretty_name = 'Name'
    
    def __new__(cls, value=''):
        return value
        
class Subtype(TextProperty):
    
    name = 'subtype'
    pretty_name = 'Subtype'
    
    def __new__(cls, value):
        return value
        
## Node property

class Vendor(ListProperty):
    
    name = 'vendor'
    pretty_name = 'Vendor'
    values = [
              'Cisco', 
              'Juniper', 
              'Arista',
              'Nokia', 
              'Huawei',
              'MikroTik', 
              'Fortinet', 
              'Palo Alto',
              'IBM', 
              'HP'
              ]
    choose_one_value = True
    
    def __new__(cls, value='Cisco'):
        return value
        
class OperatingSystem(ListProperty):
    
    name = 'operating_system'
    pretty_name = 'Operating System'
    
    values = [
              'IOS', 
              'IOSXR', 
              'NXOS', 
              'JunOS', 
              'EOS', 
              'FortiOS', 
              'PANOS',
              'MikroTik',
              'VyOS',
              'IBM', 
              'Pluribus',
              'linux'
              ]
    choose_one_value = True
    
    def __new__(cls, value='IOS'):
        return value
        
class NetmikoOperatingSystem(ListProperty):
    
    name = 'netmiko_operating_system'
    pretty_name = 'Netmiko Operating System'
    choose_one_value = True
    
    # from the netmiko module
    values = [
            'a10',
            'accedian',
            'alcatel_aos',
            'alcatel_sros',
            'arista_eos',
            'aruba_os',
            'avaya_ers',
            'avaya_vsp',
            'brocade_fastiron',
            'brocade_netiron',
            'brocade_nos',
            'brocade_vdx',
            'brocade_vyos',
            'checkpoint_gaia',
            'ciena_saos',
            'cisco_asa',
            'cisco_ios',
            'cisco_nxos',
            'cisco_s300',
            'cisco_tp',
            'cisco_wlc',
            'cisco_xe',
            'cisco_xr',
            'dell_force10',
            'dell_powerconnect',
            'eltex',
            'enterasys',
            'extreme',
            'extreme_wing',
            'f5_ltm',
            'fortinet',
            'generic_termserver',
            'hp_comware',
            'hp_procurve',
            'huawei',
            'juniper',
            'juniper_junos',
            'linux',
            'mellanox_ssh',
            'mrv_optiswitch',
            'ovs_linux',
            'paloalto_panos',
            'pluribus',
            'quanta_mesh',
            'ubiquiti_edge',
            'vyatta_vyos',
            'vyos',
            ]
    
    def __new__(cls, value='linux'):
        return value
        
class IP_Address(TextProperty):
    
    name = 'ip_address'
    pretty_name = 'IP address'
    
    def __new__(cls, value='0.0.0.0'):
        return value
        
class MAC_Address(TextProperty):
    
    name = 'mac_address'
    pretty_name = 'MAC address'
    
    def __new__(cls, value='00:00:00:00:00:00'):
        return value
        
class SubnetMask(TextProperty):
    
    name = 'subnet_mask'
    pretty_name = 'Subnet Mask'
    
    def __new__(cls, value='255.255.255.255'):
        return value
        
class Username(TextProperty):
    
    name = 'username'
    pretty_name = 'Username'
    
    def __new__(cls, value=''):
        return value
        
class Password(TextProperty):
    
    name = 'password'
    pretty_name = 'Password'
    hide_view = True
    
    def __new__(cls, value=''):
        return value
        
class EnablePassword(TextProperty):
    
    name = 'enable_password'
    pretty_name = 'Enable password'
    hide_view = True
    
    def __new__(cls, value=''):
        return value
        
class X(FloatProperty):
    
    name = 'x'
    pretty_name = 'X coordinate'
    
    def __new__(cls, value=0.):
        return super().__new__(cls, value)
        
class Y(FloatProperty):
    
    name = 'y'
    pretty_name = 'Y coordinate'
    
    def __new__(cls, value=0.):
        return super().__new__(cls, value)
        
class Longitude(FloatProperty):
    
    name = 'longitude'
    pretty_name = 'Longitude'
    
    def __new__(cls, value=0.):
        return super().__new__(cls, value)
        
class Latitude(FloatProperty):
    
    name = 'latitude'
    pretty_name = 'Latitude'
    
    def __new__(cls, value=0.):
        return super().__new__(cls, value)
        
class LogicalX(FloatProperty):
    
    name = 'logical_x'
    pretty_name = 'Logical X coordinate'
    
    def __new__(cls, value=0.):
        return super().__new__(cls, value)
        
class LogicalY(FloatProperty):
    
    name ='logical_y'
    pretty_name = 'Logical Y coordinate'
    
    def __new__(cls, value=0.):
        return super().__new__(cls, value)
        
class Sites(SetProperty):
    
    name = 'sites'
    pretty_name = 'Sites'
    
    def __new__(cls, values=None):
        if not values:
            values = set()
        cls.values = values
        return values
        
class AS(SetProperty):
    
    name = 'AS'
    pretty_name = 'Autonomous Systems'
    
    def __new__(cls, values=None):
        if not values:
            values = set()
        cls.values = values
        return values
        
## Per-AS node properties

class RouterID(TextProperty):
    
    name = 'router_id'
    pretty_name = 'Router ID'
    
    def __new__(cls, value=''):
        return super().__new__(cls, value)
        
class LB_Paths(IntProperty):
    
    name ='LB_paths'
    pretty_name = 'Load-balancing paths'
    
    def __new__(cls, value=4):
        return super().__new__(cls, value)
        
## Link property
        
class Source(NodeProperty):
    
    name = 'source'
    pretty_name = 'Source'
    
    def __new__(cls, value):
        return super().__new__(cls, value)
        
class Destination(NodeProperty):
    
    name = 'destination'
    pretty_name = 'Destination'
    
    def __new__(cls, value):
        return super().__new__(cls, value)
        
class Interface(TextProperty):
    
    name = 'interface'
    pretty_name = 'Interface'
    
    def __new__(cls, value='GE'):
        return super().__new__(cls, value)
        
class InterfaceS(TextProperty):
    
    name = 'interfaceS'
    pretty_name = 'Source Interface'
    
    def __new__(cls, value=''):
        return super().__new__(cls, value)
        
class InterfaceD(TextProperty):
    
    name = 'interfaceD'
    pretty_name = 'Destination Interface'
    
    def __new__(cls, value=''):
        return super().__new__(cls, value)
        
class Distance(FloatProperty):
    
    name = 'distance'
    pretty_name = 'Distance'
    
    def __new__(cls, value=0.):
        return super().__new__(cls, value)
        
class CostSD(IntProperty):
    
    name = 'costSD'
    pretty_name = 'S -> D cost'
    
    def __new__(cls, value=1):
        return super().__new__(cls, value)
        
class CostDS(IntProperty):
    
    name = 'costDS'
    pretty_name = 'D -> S cost'
    
    def __new__(cls, value=1):
        return super().__new__(cls, value)
        
class CapacitySD(IntProperty):
    
    name = 'capacitySD'
    pretty_name = 'S -> D capacity'
    
    def __new__(cls, value=3):
        return super().__new__(cls, value)
        
class CapacityDS(IntProperty):
    
    name = 'capacityDS'
    pretty_name = 'D -> S capacity'
    
    def __new__(cls, value=3):
        return super().__new__(cls, value)
        
class TrafficSD(IntProperty):
    
    name = 'trafficSD'
    pretty_name = 'S -> D traffic'
    
    def __new__(cls, value=0):
        return super().__new__(cls, value)
        
class TrafficDS(IntProperty):
    
    name = 'trafficDS'
    pretty_name = 'D -> S traffic'
    
    def __new__(cls, value=0):
        return super().__new__(cls, value)
        
class Subnetwork(TextProperty):
    
    name = 'subnetwork'
    pretty_name = 'Subnetwork'
    
    def __new__(cls, value=''):
        return super().__new__(cls, value)
        
## VC properties

class LinkS(LinkProperty):
    
    name = 'linkS'
    pretty_name = 'Source link'
    
    def __new__(cls, value=None):
        return super().__new__(cls, value)
        
class LinkD(LinkProperty):
    
    name = 'linkD'
    pretty_name = 'Destination link'
    
    def __new__(cls, value=None):
        return super().__new__(cls, value)
        
## Traffic properties

class Throughput(FloatProperty):
    
    name = 'throughput'
    pretty_name = 'Throughput'
    
    def __new__(cls, value=0.):
        return super().__new__(cls, value)
        
## Interface properties

class Link(LinkProperty):
    
    name = 'link'
    pretty_name = 'Link'
    
    def __init__(self, value):
        self.value = value
        
class Node(NodeProperty):
    
    name = 'node'
    pretty_name = 'Node'
    
    def __init__(self, value):
        self.value = value
        
class Cost(IntProperty):
    
    name = 'cost'
    pretty_name = 'Cost'
    
    def __new__(cls, value=0):
        return super().__new__(cls, value)
        
class Priority(IntProperty):
    
    name = 'priority'
    pretty_name = 'Priority'
    
    def __new__(cls, value=0):
        return super().__new__(cls, value)
        
class Role(TextProperty):
    
    name = 'role'
    pretty_name = 'Role'
    
    def __new__(cls, value=''):
        return super().__new__(cls, value)
        
## Traffic properties

class SourceIP(IPProperty):
    
    name = 'source_IP'
    pretty_name = 'Source IP'
    
    def __new__(cls, value='0.0.0.0/0'):
        return super().__new__(cls, value)
        
class DestinationIP(IPProperty):
    
    name = 'destination_IP'
    pretty_name = 'Destination IP'
    
    def __new__(cls, value='0.0.0.0/0'):
        return super().__new__(cls, value)
        
property_classes = {
                    'id': ID,
                    'name': Name,
                    'subtype': Subtype,
                    'ip_address': IP_Address,
                    'subnet_mask': SubnetMask,
                    'x': X,
                    'y': Y,
                    'enable_password': EnablePassword,
                    'longitude': Longitude,
                    'latitude': Latitude,
                    'logical_x': LogicalX,
                    'logical_y': LogicalY,
                    'sites': Sites,
                    'AS': AS,
                    'source': Source,
                    'destination': Destination,
                    'interface': Interface,
                    'interfaceS': InterfaceS,
                    'interfaceD': InterfaceD,
                    'distance': Distance,
                    'costSD': CostSD,
                    'costDS': CostDS,
                    'capacitySD': CapacitySD,
                    'capacityDS': CapacityDS,
                    'operating_system': OperatingSystem,
                    'netmiko_operating_system': NetmikoOperatingSystem,
                    'password': Password,
                    'trafficSD': TrafficSD,
                    'trafficDS': TrafficDS,
                    'subnetwork': Subnetwork,
                    'linkS': LinkS,
                    'linkD': LinkD,
                    'source_IP': SourceIP,
                    'destination_IP': DestinationIP,
                    'throughput': Throughput,
                    'username': Username,
                    'link': Link,
                    'node': Node,
                    'role': Role,
                    'router_id': RouterID,
                    'LB_paths': LB_Paths,
                    'cost': Cost,
                    'priority': Priority,
                    'vendor': Vendor,
                    }
               
# Pretty name -> property class association
pretty_name_to_class = {property_class.pretty_name: property_class 
                        for property_class in property_classes.values()}
                     
# Object class to property (ex: int -> IntProperty)
class_to_property = {
                    str: TextProperty,
                    int: IntProperty,
                    float: FloatProperty,
                    list: ListProperty,
                    set: SetProperty,
                    dict: DictProperty
                    }
                        