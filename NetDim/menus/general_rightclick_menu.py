# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk
from drawing.drawing_menu import DrawingMenu
from graph_generation.multiple_objects import MultipleNodes

class GeneralRightClickMenu(tk.Menu):
    def __init__(self, event, scenario):
        super().__init__(tearoff=0)
        self.cs = scenario
        x, y = self.cs.canvasx(event.x), self.cs.canvasy(event.y)
        
        # drawing mode selection
        nodes = self.cs.ntw.pn["node"].values()
        self.add_cascade(label="Automatic layout", menu=DrawingMenu(self.cs, nodes))
        
        # stop drawing entry
        self.add_command(label="Stop drawing", command=lambda: self.cs._cancel())
        
        # remove all failures if there is at least one
        if self.cs.ntw.fdtks:
            self.add_separator()
            self.add_command(label="Remove all failures",
                    command=lambda: self.remove_all_failures())
                    
        self.add_separator()
                   
        # multiple nodes creation
        self.add_command(label="Create multiple nodes", 
                command=lambda: MultipleNodes(self.cs, x, y))
                
        # find networks
        self.add_command(label="Refresh", 
                command=lambda: self.network())
                
        # make the menu appear    
        self.tk_popup(event.x_root, event.y_root)

    def remove_all_failures(self):
        self.cs.remove_failures()
        self.destroy()
        
    def network(self):
        self.cs.refresh()
        self.destroy()