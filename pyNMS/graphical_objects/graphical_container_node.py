from .graphical_node import GraphicalNode
from views.internal_node_view import InternalNodeView
from miscellaneous.decorators import overrider

class GraphicalContainerNode(GraphicalNode):
    
    def __init__(self, view, node=None):
        super().__init__(view, node)
        self.internal_view = InternalNodeView(self, view.controller)
            
    # enter the internal node view
    def mouseDoubleClickEvent(self, event):
        self.controller.current_project.show_internal_view(self)
        super().mouseDoubleClickEvent(event)
        