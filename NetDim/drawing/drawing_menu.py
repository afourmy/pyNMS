# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk

class DrawingMenu(tk.Menu):
    #TODO does the menu destroy itself ? I don't thing so
    def __init__(self, scenario, nodes):
        super().__init__(tearoff=0)
        self.cs = scenario
        
        cmds = {
        "Random": lambda: self.random(nodes),
        "FBA": lambda: scenario.automatic_drawing(nodes),
        "BFSC": lambda: scenario.bfs_cluster_drawing(nodes),
        "Both": lambda: self.both(nodes)
        }
    
        self.add_command(label="Random layout", command=cmds["Random"])
        self.add_command(label="Force-based layout", command=cmds["FBA"])
        self.add_command(label="BFS-clusterization layout", command=cmds["BFSC"])
        self.add_command(label="Both", command=cmds["Both"])
                                            
    def both(self, nodes):
        self.cs.draw_objects(nodes, True)
        self.cs.automatic_drawing(nodes)
        
    def random(self, nodes):
        self.cs.draw_objects(nodes)
        self.cs.move_nodes(nodes)
        