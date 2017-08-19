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
    
    def __repr__(self):
        return str(self)
        
class TextProperty(str, Property):
    
    def __new__(cls, value):
        return str.__new__(cls, value)
        
class IntProperty(int, Property):
    
    # int is immutable: it cannot be modified after creation
    # we must use __new__ instead of __init_
    
    def __new__(cls, value):
        return int.__new__(cls, value)
        
class FloatProperty(float, Property):
    
    def __new__(cls, value):
        return float.__new__(cls, value)
        
class ListProperty(list, Property):
    
    def __new__(cls, values=None):
        if values is None:
            return []
        else:
            return list.__new__(cls, values)
        
class SetProperty(set, Property):
    
    def __init__(self, value):
        if value is None:
            self.value = set()
        else:
            self.value = set.__init__(value)
        return self.value
        
class NodeProperty(Property):
    
    conversion_needed = True
    converter = 'convert_node'
    
    def __new__(cls, node):
        return node
        
class LinkProperty(Property):
    
    conversion_needed = True
    converter = 'convert_link'
    
    def __new__(cls, link):
        return link
        
## Object properties

class ID(IntProperty):
    
    name = 'id'
    pretty_name = 'ID'
    
    def __new__(cls, value):
        return super().__new__(cls, value)

class Name(TextProperty):
    
    name = 'name'
    pretty_name = 'Name'
    
    def __new__(cls, value=''):
        return super().__new__(cls, value)
        
class Subtype(TextProperty):
    
    name = 'subtype'
    pretty_name = 'Subtype'
    
    def __new__(cls, value):
        return super().__new__(cls, value)
        
## Node property

class Vendor(TextProperty):
    
    name = 'vendor'
    pretty_name = 'Vendor'
    multiple_values = True
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
    
    def __new__(cls, value='Cisco'):
        return super().__new__(cls, value)
        
class OperatingSystem(TextProperty):
    
    name = 'operating_system'
    pretty_name = 'Operating System'
    multiple_values = True
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
              'Pluribus'
              ]
    
    def __new__(cls, value='IOS'):
        return super().__new__(cls, value)
        
class IP_Address(TextProperty):
    
    name = 'ip_address'
    pretty_name = 'IP address'
    
    def __new__(cls, value='0.0.0.0'):
        return super().__new__(cls, value)
        
class MAC_Address(TextProperty):
    
    name = 'mac_address'
    pretty_name = 'MAC address'
    
    def __new__(cls, value='00:00:00:00:00:00'):
        return super().__new__(cls, value)
        
class SubnetMask(TextProperty):
    
    name = 'subnet_mask'
    pretty_name = 'Subnet Mask'
    
    def __new__(cls, value='255.255.255.255'):
        return super().__new__(cls, value)
        
class Username(TextProperty):
    
    name = 'username'
    pretty_name = 'Username'
    
    def __new__(cls, value=''):
        return super().__new__(cls, value)
        
class Password(TextProperty):
    
    name = 'password'
    pretty_name = 'Password'
    hide_view = True
    
    def __new__(cls, value=''):
        return super().__new__(cls, value)
        
class EnablePassword(TextProperty):
    
    name = 'enable_password'
    pretty_name = 'Enable password'
    hide_view = True
    
    def __new__(cls, value=''):
        return super().__new__(cls, value)
        
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
    
    def __init__(self, value=None):
        super().__init__(value)
        
class AS(SetProperty):
    
    name = 'AS'
    pretty_name = 'Autonomous Systems'
    
    def __init__(self, value=None):
        super().__init__(value)
        
## Link property
        
class Source(NodeProperty):
    
    name = 'source'
    pretty_name = 'Source'
    
    def __new__(self, value):
        return value
        
class Destination(NodeProperty):
    
    name = 'destination'
    pretty_name = 'Destination'
    
    def __new__(self, value):
        return value
        
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

class Throughput(IntProperty):
    
    name = 'throughput'
    pretty_name = 'Throughput'
    
    def __new__(cls, value=0):
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
                    # 'interfaceS': InterfaceS,
                    # 'interfaceD': InterfaceD,
                    'distance': Distance,
                    'costSD': CostSD,
                    'costDS': CostDS,
                    'capacitySD': CapacitySD,
                    'capacityDS': CapacityDS,
                    'operating_system': OperatingSystem,
                    'password': Password,
                    'trafficSD': TrafficSD,
                    'trafficDS': TrafficDS,
                    'subnetwork': Subnetwork,
                    'linkS': LinkS,
                    'linkD': LinkD,
                    'throughput': Throughput,
                    'username': Username,
                    'link': Link,
                    'node': Node,
                    'role': Role,
                    'cost': Cost,
                    'priority': Priority,
                    'vendor': Vendor,
                    }
               
# Pretty name -> property class association
pretty_name_to_class = {property_class.pretty_name: property_class 
                        for property_class in property_classes.values()}
                        