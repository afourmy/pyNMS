class Link(object):
    
    class_type = "link"
    
    def __init__(self, name, source, destination):
        self.name = name
        self.source = source
        self.destination = destination
        self.line = None
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
    color = "blue"
    dash = ()
    type = "trunk"

    def __init__(self, name, source, destination, cost=1, capacitySD=3, capacityDS=3):
        super().__init__(name, source, destination)
        self.cost = cost
        self.capacity = {"SD": 3, "DS": 3}
        self.flow = {"SD": 0, "DS": 0}
        
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
    dash = (7,1,1,1)
    color = "purple"
    
    def __init__(self, name, source, destination, subnet=0, traffic=0):
        super().__init__(name, source, destination)
        self.traffic = traffic
        self.subnet = subnet
