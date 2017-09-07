from .graphical_network_node import GraphicalNetworkNode

class GraphicalInternalNode(GraphicalNode):
    
    def __init__(self, view, node=None):
        super().__init__(view, node)
        
        