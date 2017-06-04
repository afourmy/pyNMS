# NetDim (contact@netdim.fr)

import tkinter as tk
from graph_generation.multiple_objects import MultipleNodes
from miscellaneous.decorators import update_paths
from pythonic_tkinter.preconfigured_widgets import Menu

class SiteGeneralRightClickMenu(Menu):
    
    @update_paths
    def __init__(self, event, controller):
        super().__init__()
        x, y = self.view.cvs.canvasx(event.x), self.view.cvs.canvasy(event.y)
                
        # change geographical projection
        projection_menu = tk.Menu(self, tearoff=0)

        projection_menu.add_command(
                label = 'Linear projection', 
                command= lambda: self.cs.world_map.change_projection('linear')
                )
        projection_menu.add_command(
                label = 'Mercator projection', 
                command= lambda: self.cs.world_map.change_projection('mercator')
                )
        projection_menu.add_command(
                label = 'Spherical projection', 
                command= lambda: self.cs.world_map.change_projection('globe')
                )

        self.add_cascade(label='Geographical projection', menu=projection_menu)
        
        # multiple nodes creation
        self.add_command(label='Create multiple nodes', 
                command=lambda: MultipleNodes(self.cs, x, y))
                
        # make the menu appear    
        self.tk_popup(event.x_root, event.y_root)