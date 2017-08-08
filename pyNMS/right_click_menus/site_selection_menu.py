from .geographical_selection_menu import GeographicalSelectionMenu

class SiteSelectionMenu(GeographicalSelectionMenu):
    
    def __init__(self, controller):
        super().__init__(controller)
        
        self.addAction(self.map_action)