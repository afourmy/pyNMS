class Trunk(object):
    def __init__(self, source, destination, cost=1, capacitySD=3, capacityDS=3):
        self.source = source
        self.destination = destination
        self.name = source.name + destination.name
        self.cost = cost
        self.capacitySD = capacitySD
        self.capacityDS = capacityDS
        self.flowSD = 0
        self.flowDS = 0
        self.line = None
        
    def __repr__(self):
        return "{}-{}".format(self.source, self.destination)
        
    def __eq__(self, other):
        return isinstance(other, self.__class__)\
        and {self.source, self.destination} == {other.source, other.destination}
        
    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __hash__(self):
        return hash(self.name)