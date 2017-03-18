from .geo_scenario import GeoScenario
from networks import main_network
from menus.network_selection_rightclick_menu import NetworkSelectionRightClickMenu

class NetworkScenario(GeoScenario):

    def __init__(self, *args, **kwargs):
        self.ntw = main_network.MainNetwork(self)
        super().__init__(*args, **kwargs)
        
        # add binding for right-click menu 
        self.cvs.tag_bind('object', '<ButtonPress-3>',
                            lambda e: NetworkSelectionRightClickMenu(e, self))
