from .geographical_menu import GeographicalMenu
from miscellaneous.site_operations import SiteOperations
from .network_selection_menu import NetworkSelectionMenu
from PyQt5.QtWidgets import QAction

class MainNetworkSelectionMenu(GeographicalMenu, NetworkSelectionMenu):
    
    def __init__(self, controller):
        super().__init__(controller)
        
        self.addSeparator()
        
        self.addAction(self.map_action)
        
        if self.all_sites:
            
            add_to_site = QAction('Add to site', self)        
            add_to_site.triggered.connect(self.add_to_site)
            self.addAction(add_to_site)
            
            if self.common_sites:
                
                self.addAction(self.remove_from_site_action)
                
    def remove_from_site(self):
        objects = set(self.view.get_obj(self.so))
        self.remove_window = SiteOperations('remove', objects, self.common_sites, self.controller)
        self.remove_window.show()