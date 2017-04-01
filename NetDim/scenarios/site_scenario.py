# NetDim
# Copyright (C) 2017 Antoine Fourmy (contact@netdim.fr)

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
                                
        # add binding to enter a site 
        self.cvs.tag_bind('site', '<Double-Button-1>', self.enter_closest_site)
        
    def adapt_coordinates(function):
        def wrapper(self, event, *others):
            event.x, event.y = self.cvs.canvasx(event.x), self.cvs.canvasy(event.y)
            function(self, event, *others)
        return wrapper
        
    def general_menu(self, event):
        x, y = self._start_pos_main_node
        # if the right-click button was pressed, but the position of the 
        # canvas when the button is released hasn't changed, we create
        # the general right-click menu
        if (x, y) == (event.x, event.y):
            SiteGeneralRightClickMenu(event, self)
           
    @adapt_coordinates
    def enter_closest_site(self, event):
        closest_site_id = self.cvs.find_closest(event.x, event.y)[0]
        selected_site = self.object_id_to_object[closest_site_id]
        self.ms.view_menu.enter_site(selected_site)