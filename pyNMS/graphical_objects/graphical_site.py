from .graphical_node import GraphicalNode
from views.internal_site_view import InternalSiteView

class GraphicalSite(GraphicalNode):
    
    def __init__(self, view, node=None):
        super().__init__(view, node)
        self.internal_view = InternalSiteView(self, self.controller)
        
    def mouseDoubleClickEvent(self, event):
        self.controller.current_project.show_internal_view(self)
        super(GraphicalSite, self).mouseDoubleClickEvent(event)
        