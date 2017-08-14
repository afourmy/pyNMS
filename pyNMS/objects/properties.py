class Property():
    
    def __init__(self):
        pass
        
class TextProperty(str):
    
    def __init__(self, value):
        return str.__init__(value)
        
class IntProperty(int):
    
    def __init__(self, value):
        return int.__init__(value)
        
class FloatProperty(float):
    
    def __init__(self, value):
        return float.__init__(value)
        
class ListProperty(list):
    
    def __init__(self, value):
        if value is None:
            value = []
        return list.__init__(value)
        
class SetProperty(set):
    
    def __init__(self, value):
        if value is None:
            value = set()
        return set.__init__(value)
        
## Object properties

class ID(IntProperty):
    
    name = 'id'
    
    def __init__(self, value):
        super().__init__(value)

class Name(TextProperty):
    
    name = 'name'
    pretty_name = 'Name'
    
    def __init__(self, value):
        super().__init__(value)
        
class Subtype(TextProperty):
    
    name = 'subtype'
    pretty_name = 'Subtype'
    
    def __init__(self, value):
        super().__init__(value)
        
## Node property
        
class IP_Address(TextProperty):
    
    name = 'ip_address'
    pretty_name = 'IP address'
    
    def __init__(self, value='0.0.0.0'):
        super().__init__(value)
        
class MAC_Address(TextProperty):
    
    name = 'mac_address'
    pretty_name = 'MAC address'
    
    def __init__(self, value='00:00:00:00:00:00'):
        super().__init__(value)
        
class SubnetMask(TextProperty):
    
    name = 'subnet_mask'
    pretty_name = 'Subnet Mask'
    
    def __init__(self, value='255.255.255.255'):
        super().__init__(value)
        
class X(FloatProperty):
    
    name = 'x'
    pretty_name = 'X coordinate'
    
    def __init__(self, value=0.):
        super().__init__(value)
        
class Y(FloatProperty):
    
    name = 'y'
    pretty_name = 'Y coordinate'
    
    def __init__(self, value=0.):
        super().__init__(value)
        
class Longitude(FloatProperty):
    
    name = 'longitude'
    pretty_name = 'Longitude'
    
    def __init__(self, value=0.):
        super().__init__(value)
        
class Latitude(FloatProperty):
    
    name = 'latitude'
    pretty_name = 'Latitude'
    
    def __init__(self, value=0.):
        super().__init__(value)
        
class LogicalX(FloatProperty):
    
    name = 'logical_x'
    pretty_name = 'Logical X coordinate'
    
    def __init__(self, value=0.):
        super().__init__(value)
        
class LogicalY(FloatProperty):
    
    name ='logical_y'
    pretty_name = 'Logical Y coordinate'
    
    def __init__(self, value=0.):
        super().__init__(value)
        
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
        
class Source():
    
    name = 'source'
    pretty_name = 'Source'
    
    def __init__(self, value):
        self.value = value
        
class Destination():
    
    name = 'destination'
    pretty_name = 'Destination'
    
    def __init__(self, value):
        self.value = value
        
class Interface(TextProperty):
    
    name = 'interface'
    pretty_name = 'Interface'
    
    def __init__(self, value=''):
        super().__init__(value)
        
class InterfaceS(TextProperty):
    
    name = 'interfaceS'
    pretty_name = 'Source Interface'
    
    def __init__(self, value=''):
        super().__init__(value)
        
class InterfaceD(TextProperty):
    
    name = 'interfaceD'
    pretty_name = 'Destination Interface'
    
    def __init__(self, value=''):
        super().__init__(value)
        
class Distance(FloatProperty):
    
    name = 'distance'
    pretty_name = 'Distance'
    
    def __init__(self, value=0.):
        super().__init__(value)
        
class CostSD(IntProperty):
    
    name = 'costSD'
    pretty_name = 'S -> D cost'
    
    def __init__(self, value=0):
        super().__init__(value)
        
class CostDS(IntProperty):
    
    name = 'costDS'
    pretty_name = 'D -> S cost'
    
    def __init__(self, value=0):
        super().__init__(value)
        
class CapacitySD(IntProperty):
    
    name = 'capacitySD'
    pretty_name = 'S -> D capacity'
    
    def __init__(self, value=0):
        super().__init__(value)
        
class CapacityDS(IntProperty):
    
    name = 'capacityDS'
    pretty_name = 'D -> S capacity'
    
    def __init__(self, value=0):
        super().__init__(value)
        
class TrafficSD(IntProperty):
    
    name = 'trafficSD'
    pretty_name = 'S -> D traffic'
    
    def __init__(self, value=0):
        super().__init__(value)
        
class TrafficDS(IntProperty):
    
    name = 'trafficDS'
    pretty_name = 'D -> S traffic'
    
    def __init__(self, value=0):
        super().__init__(value)
        
class Subnetwork(TextProperty):
    
    name = 'subnetwork'
    pretty_name = 'Subnetwork'
    
    def __init__(self, value=''):
        super().__init__(value)
        
## VC properties

class LinkS():
    
    name = 'linkS'
    pretty_name = 'Source link'
    
    def __init__(self, value):
        self.value = value
        
class LinkD():
    
    name = 'linkD'
    pretty_name = 'Destination link'
    
    def __init__(self, value):
        self.value = value
        
## Traffic properties

class Throughput(IntProperty):
    
    name = 'throughput'
    pretty_name = 'Throughput'
    
    def __init__(self, value=0):
        super().__init__(value)
        
## Interface properties

class Link():
    
    name = 'link'
    pretty_name = 'Link'
    
    def __init__(self, value=''):
        self.value = value
        
class Node():
    
    name = 'node'
    pretty_name = 'Node'
    
    def __init__(self, value=''):
        self.value = value

        
property_classes = {
                    'id': ID,
                    'name': Name,
                    'subtype': Subtype,
                    'ip_address': IP_Address,
                    'subnet_mask': SubnetMask,
                    'x': X,
                    'y': Y,
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
                    'trafficSD': TrafficSD,
                    'trafficDS': TrafficDS,
                    'subnetwork': Subnetwork,
                    'linkS': LinkS,
                    'linkD': LinkD,
                    'throughput': Throughput
                    }
                        