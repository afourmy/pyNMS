from .network_selection_menu import NetworkSelectionMenu

class InternalSiteSelectionMenu(NetworkSelectionMenu):
    
    def __init__(self, controller):
        super().__init__(controller)
        
        self.addSeparator()
        
        self.addAction(self.remove_from_site_action)
        
    def remove_from_site(self):
        self.view.remove_from_site(*self.objects)