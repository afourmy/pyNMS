# NetDim
# Copyright (C) 2017 Antoine Fourmy (contact@netdim.fr)
# Released under the GNU General Public License GPLv3

import tkinter as tk
from graph_generation.multiple_objects import MultipleNodes

class NetworkGeneralRightClickMenu(tk.Menu):
    def __init__(self, event, scenario):
        super().__init__(tearoff=0)
        self.cs = scenario
        x, y = self.cs.cvs.canvasx(event.x), self.cs.cvs.canvasy(event.y)
        
        # change geographical projection
        projection_menu = tk.Menu(self, tearoff=0)

        projection_menu.add_command(
                label = 'Linear projection', 
                command= lambda: self.cs.change_projection('linear')
                )
        projection_menu.add_command(
                label = 'Mercator projection', 
                command= lambda: self.cs.change_projection('mercator')
                )
        projection_menu.add_command(
                label = 'Spherical projection', 
                command= lambda: self.cs.change_projection('globe')
                )

        self.add_cascade(label='Geographical projection', menu=projection_menu)
        
        # multiple nodes creation
        self.add_command(label='Create multiple nodes', 
                command=lambda: MultipleNodes(self.cs, x, y))
                
        # remove all failures if there is at least one
        if self.cs.ntw.failed_obj:
            self.add_command(label='Remove all failures',
                    command=lambda: self.remove_all_failures())
            self.add_separator()
                   
        # find networks
        self.add_command(label='Refresh', 
                command=lambda: self.refresh())
                
        # make the menu appear    
        self.tk_popup(event.x_root, event.y_root)

    def remove_all_failures(self):
        self.cs.remove_failures()
        self.destroy()
        
    def refresh(self):
        self.cs.ms.refresh()
        self.destroy()