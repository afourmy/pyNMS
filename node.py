class Node(object):
    
    class_type = "node"
    
    def __init__(self, name, x, y):
        self.name = name
        self.oval = None
        self.image = None
        self.size = 8
        # position of a node
        self.x = x
        self.y = y
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
    default_imagex = 33
    default_imagey = 25
    
    def __init__(self, name, x, y):
        super().__init__(name, x, y)
        self.imagex = self.default_imagex
        self.imagey = self.default_imagey
        
class OXC(Node):

    color = "pink"
    type = "oxc"
    default_imagex = 35
    default_imagey = 32
    
    def __init__(self, name, x, y):
        super().__init__(name, x, y)
        self.imagex = self.default_imagex
        self.imagey = self.default_imagey
        
class Host(Node):

    color = "blue"
    type = "host"
    default_imagex = 35
    default_imagey = 32
    
    def __init__(self, name, x, y):
        super().__init__(name, x, y)
        self.imagex = self.default_imagex
        self.imagey = self.default_imagey
        
class Antenna(Node):

    color = "black"
    type = "antenna"
    default_imagex = 35
    default_imagey = 35
    
    def __init__(self, name, x, y):
        super().__init__(name, x, y)
        self.imagex = self.default_imagex
        self.imagey = self.default_imagey