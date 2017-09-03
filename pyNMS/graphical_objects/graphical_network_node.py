from .graphical_node import GraphicalNode
from views.internal_node_view import InternalNodeView
from miscellaneous.decorators import overrider

class GraphicalNetworkNode(GraphicalNode):
    
    def __init__(self, view, node=None):
        super().__init__(view, node)
        self.internal_view = InternalNodeView(self, view.controller)
        
    # itemChange is overriden for a Graphical Network Node, because a site 
    # has no attached link. It does not need to trigger the update position
    # method when on motion.
    @overrider(GraphicalNode)
    def itemChange(self, change, value):
        if change == self.ItemScenePositionHasChanged:
            for glink in self.view.attached_glinks(self):
                glink.update_position()
        return super().itemChange(change, value)
        
    # enter the internal node view containing the node's physical ports
    def mouseDoubleClickEvent(self, event):
        self.controller.current_project.show_internal_node_view(self)
        super().mouseDoubleClickEvent(event)
        