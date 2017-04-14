# NetDim (contact@netdim.fr)

from .geographical_view import GeographicalView
from .insite_view import InSiteView
from networks import site_network
from menus.site_selection_rightclick_menu import SiteSelectionRightClickMenu
from menus.site_general_rightclick_menu import SiteGeneralRightClickMenu
from miscellaneous.decorators import update_coordinates, overrider

class SiteView(GeographicalView):

    def __init__(self, *args, **kwargs):
        self.network = site_network.SiteNetwork(self)
        super().__init__(*args, **kwargs)
        
        # add binding for right-click menu 
        self.cvs.tag_bind('object', '<ButtonPress-3>',
                                lambda e: SiteSelectionRightClickMenu(e, self))
                                
        # add binding to enter a site 
        self.cvs.tag_bind('site', '<Double-Button-1>', self.enter_closest_site)
        
    def general_menu(self, event):
        x, y = self._start_pos_main_node
        # if the right-click button was pressed, but the position of the 
        # canvas when the button is released hasn't changed, we create
        # the general right-click menu
        if (x, y) == (event.x, event.y):
            SiteGeneralRightClickMenu(event, self)
           
    @update_coordinates
    def enter_closest_site(self, event):
        closest_site_id = self.cvs.find_closest(event.x, event.y)[0]
        selected_site = self.object_id_to_object[closest_site_id]
        self.ms.view_menu.enter_site(selected_site)