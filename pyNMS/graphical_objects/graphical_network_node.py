from .graphical_node import GraphicalNode
from miscellaneous.decorators import overrider

class GraphicalNetworkNode(GraphicalNode):
    
    def __init__(self, view, node=None):
        super().__init__(view, node)
        
    # itemChange is overriden for a Graphical Network Node, because a site 
    # has no attached link. It does not need to trigger the update position
    # method when on motion.
    @overrider(GraphicalNode)
    def itemChange(self, change, value):
        if change == self.ItemScenePositionHasChanged:
            for glink in self.view.attached_glinks(self):
                glink.update_position()
        return super().itemChange(change, value)
        