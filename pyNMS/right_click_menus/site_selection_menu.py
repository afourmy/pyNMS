from .geographical_menu import GeographicalMenu

class SiteSelectionMenu(GeographicalMenu):
    
    def __init__(self, controller):
        super().__init__(controller)
        
        self.addAction(self.map_action)