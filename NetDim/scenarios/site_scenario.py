from .geo_scenario import GeoScenario
from .insite_scenario import InSiteScenario
from networks import site_network
from menus.site_selection_rightclick_menu import SiteSelectionRightClickMenu
from menus.site_general_rightclick_menu import SiteGeneralRightClickMenu

def overrider(interface_class):
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider

class SiteScenario(GeoScenario):

    def __init__(self, *args, **kwargs):
        self.ntw = site_network.SiteNetwork(self)
        super().__init__(*args, **kwargs)
        
        # add binding for right-click menu 
        self.cvs.tag_bind('object', '<ButtonPress-3>',
                                lambda e: SiteSelectionRightClickMenu(e, self))
        
    def general_menu(self, event):
        x, y = self._start_pos_main_node
        # if the right-click button was pressed, but the position of the 
        # canvas when the button is released hasn't changed, we create
        # the general right-click menu
        if (x, y) == (event.x, event.y):
            SiteGeneralRightClickMenu(event, self)
        