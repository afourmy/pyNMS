class Node(object):
    def __init__(self, name):
        self.name = name
        self.oval = None
        # position of a node
        self.x = 100
        self.y = 100
        # velocity of a node for graph drawing algorithm
        self.vx = 0
        self.vy = 0
        
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