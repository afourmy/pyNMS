## Nodes
class Node(object):
    
    class_type = "node"
    network_type = class_type
    
    def __init__(self, name, x=100, y=100, longitude=0, latitude=0):
        self.name = name
        self.longitude = int(longitude)
        self.latitude = int(latitude)
        self.oval = None
        self.image = None
        # id of the corresponding label
        self.lid = None
        self.size = 8
        # position of a node (conversion decimal string to int in case of export)
        self.x = int(float(x))
        self.y = int(float(y))
        # velocity of a node for graph drawing algorithm
        self.vx = 0
        self.vy = 0
        # list of AS to which the node belongs
        self.AS = set()
        
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
    
    color = "magenta"
    type = "router"
    imagex, imagey = 33, 25
    
    def __init__(self, name, x=100, y=100, longitude=0, latitude=0):
        super().__init__(name, x, y, longitude, latitude)
        
class OXC(Node):

    color = "pink"
    type = "oxc"
    imagex, imagey = 35, 32
    
    def __init__(self, name, x=100, y=100, longitude=0, latitude=0):
        super().__init__(name, x, y, longitude, latitude)
        
class Host(Node):

    color = "blue"
    type = "host"
    imagex, imagey = 35, 32
    
    def __init__(self, name, x=100, y=100, longitude=0, latitude=0):
        super().__init__(name, x, y, longitude, latitude)
        
class Antenna(Node):

    color = "black"
    type = "antenna"
    imagex, imagey = 35, 32
    
    def __init__(self, name, x=100, y=100, longitude=0, latitude=0):
        super().__init__(name, x, y, longitude, latitude)
        
class Regenerator(Node):

    color = "black"
    type = "antenna"
    imagex, imagey = 35, 32
    
    def __init__(self, name, x=100, y=100, longitude=0, latitude=0):
        super().__init__(name, x, y, longitude, latitude)
        
class Splitter(Node):

    color = "black"
    type = "antenna"
    imagex, imagey = 35, 32
    
    def __init__(self, name, x=100, y=100, longitude=0, latitude=0):
        super().__init__(name, x, y, longitude, latitude)
        
## Links
class Link(object):
    
    class_type = "link"
    
    def __init__(self, name, source, destination, distance=0):
        self.name = name
        self.source = source
        self.destination = destination
        self.distance = int(distance)
        self.line = None
        # id of the corresponding label
        self.lid = None
        # AS to which the link belongs
        self.AS = None
        
    def __repr__(self):
        return self.name
        
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name
        
    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __hash__(self):
        return hash(self.name)

class Trunk(Link):
    type = "trunk"
    network_type = type
    color = "blue"
    dash = ()

    def __init__(self, name, source, destination, distance=0, costSD=1, costDS=1, capacitySD=3, capacityDS=3):
        super().__init__(name, source, destination, distance)
        self.costSD, self.costDS = int(costSD), int(costDS)
        self.capacitySD, self.capacityDS = int(capacitySD), int(capacityDS)
        self.flowSD, self.flowDS = 0, 0
        
class Ethernet(Trunk):
    def __init__(self, name, source, destination, cost=1, capacitySD=3, capacityDS=3, interface="GE"):
        super().__init__(name, source, destination, cost=1, capacitySD=3, capacityDS=3)
        self.interface = interface
        
class WDMFiber(Trunk):
    def __init__(self, name, source, destination, cost=1, capacitySD=3, capacityDS=3, interface="GE"):
        super().__init__(name, source, destination, cost=1, capacitySD=3, capacityDS=3, interface="GE", lambda_capacity=88)
        self.interface = interface
        self.lambda_capacity = lambda_capacity
        
class Route(Link):
    type = "route"
    network_type = type
    dash = (3,5)
    color = "green"
    
    def __init__(self, name, source, destination, excluded_trunks=[], excluded_nodes=[], path_constraints=[], subnets=set(), path=[], AS=None):
        super().__init__(name, source, destination)
        self.path_constraints = path_constraints
        self.excluded_nodes = excluded_nodes
        self.excluded_trunks = excluded_trunks
        self.path = path
        self.subnets = subnets
        
class Traffic(Link):
    type = "traffic"
    network_type = type
    dash = (7,1,1,1)
    color = "purple"
    
    def __init__(self, name, source, destination, subnet=0, traffic=0):
        super().__init__(name, source, destination)
        self.traffic = traffic
        self.subnet = subnet
