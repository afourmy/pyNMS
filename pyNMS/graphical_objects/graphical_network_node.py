from .graphical_container_node import GraphicalContainerNode
from views.internal_node_view import InternalNodeView
from miscellaneous.decorators import overrider

class GraphicalNetworkNode(GraphicalContainerNode):
    
    def __init__(self, view, node=None):
        super().__init__(view, node)
        