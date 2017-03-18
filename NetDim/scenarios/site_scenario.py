from .geo_scenario import GeoScenario
from .insite_scenario import InSiteScenario
from networks import site_network
from menus.site_selection_rightclick_menu import SiteSelectionRightClickMenu

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
        
    @overrider(GeoScenario)
    def create_node(self, site, layer=1):
        super(GeoScenario, self).create_node(site)
        # we create the insite scenario for the new site
        site.scenario = InSiteScenario(site, self.ms, site.name)
        