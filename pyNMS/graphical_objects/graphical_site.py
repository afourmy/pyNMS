from .graphical_node import GraphicalNode
from views.internal_site_view import InternalSiteView

class GraphicalSite(GraphicalNode):
    
    def __init__(self, view, node=None):
        super().__init__(view, node)
        self.site_view = InternalSiteView(self, self.controller)
        
    def mouseDoubleClickEvent(self, event):
        print('test')
        super(GraphicalSite, self).mouseDoubleClickEvent(event)
        