# NetDim (contact@netdim.fr)

from .geographical_view import GeographicalView
from networks import main_network
from menus.network_selection_rightclick_menu import NetworkSelectionRightClickMenu
from menus.network_general_rightclick_menu import NetworkGeneralRightClickMenu

class NetworkView(GeographicalView):

    def __init__(self, *args, **kwargs):
        self.network = main_network.MainNetwork(self)
        super().__init__(*args, **kwargs)
        
        # add binding for right-click menu 
        self.cvs.tag_bind('object', '<ButtonPress-3>',
                lambda e: NetworkSelectionRightClickMenu(e, self.controller))
                            
    def general_menu(self, event):
        x, y = self.start_pos_main_node
        # if the right-click button was pressed, but the position of the 
        # canvas when the button is released hasn't changed, we create
        # the general right-click menu
        if (x, y) == (event.x, event.y):
            NetworkGeneralRightClickMenu(event, self.controller)
