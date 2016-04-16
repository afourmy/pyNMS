class LSP(object):
    def __init__(self, name, ingress, egress, path_constraints=[], excluded_nodes=[], excluded_trunks=[], demand=0, tag=0):
        self.name = name
        self.ingress = ingress
        self.egress = egress
        self.path_constraints = path_constraints
        self.excluded_nodes = excluded_nodes
        self.excluded_trunks = excluded_trunks
        self.demand = demand
        self.tag = tag
        self.path = path
        
    def __repr__(self):
        return "[{} ({}->{})]".format(self.name, self.ingress, self.egress)
        
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name
        
    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __hash__(self):
        return hash(self.name)