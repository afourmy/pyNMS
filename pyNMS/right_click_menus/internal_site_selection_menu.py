from .network_selection_menu import NetworkSelectionMenu

class InternalSiteSelectionMenu(NetworkSelectionMenu):
    
    def __init__(self, controller):
        super().__init__(controller)
        
        self.addSeparator()
        
        self.addAction(self.remove_from_site_action)
        
    def remove_from_site(self):
        objects = set(self.view.get_obj(self.so))
        self.view.remove_from_site(*objects)