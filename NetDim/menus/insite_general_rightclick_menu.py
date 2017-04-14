# NetDim (contact@netdim.fr)

import tkinter as tk
from graph_generation.multiple_objects import MultipleNodes
from pythonic_tkinter.preconfigured_widgets import InMenu

class InSiteGeneralRightClickMenu(InMenu):
    def __init__(self, event, view):
        super().__init__(tearoff=0)
        self.cs = view
        x, y = self.cs.cvs.canvasx(event.x), self.cs.cvs.canvasy(event.y)
                
        # remove all failures if there is at least one
        if self.cs.ns.ntw.failed_obj | self.cs.site.ps['node'] | self.cs.site.ps['link']:
            self.add_command(label='Remove all failures',
                    command=lambda: self.remove_all_failures())
            self.add_separator()
                   
        # multiple nodes creation
        self.add_command(label='Create multiple nodes', 
                command=lambda: MultipleNodes(self.cs, x, y))
                
        # make the menu appear    
        self.tk_popup(event.x_root, event.y_root)

    def remove_all_failures(self):
        self.cs.remove_failures()
        self.destroy()
        
    def refresh(self):
        self.cs.ms.refresh()
        self.destroy()