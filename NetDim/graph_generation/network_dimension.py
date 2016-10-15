# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk
from tkinter import ttk
from miscellaneous.custom_toplevel import CustomTopLevel

class NetworkDimension(CustomTopLevel):    
    def __init__(self, scenario, type):
        super().__init__()
        self.title("Dimension")
        self.type = type
        self.scenario = scenario
        
        self.dict_type_to_function = {
        "star": lambda n, st: scenario.ntw.star(n - 1, st),
        "ring": lambda n, st: scenario.ntw.ring(n, st),
        "full-mesh": lambda n, st: scenario.ntw.full_mesh(n, st),
        "tree": lambda n, st: scenario.ntw.tree(n, st),
        "square-tiling": lambda n, st: scenario.ntw.square_tiling(n + 1, st),
        "hypercube": lambda n, st: scenario.ntw.hypercube(n - 1, st),
        "kneser": lambda n, k, st: scenario.ntw.kneser(n+1, k, st),
        "petersen": lambda n, k, st: scenario.ntw.petersen(n, k, st)
        }
        
        # offset used to add the addition "k" parameter in the gui
        self.offset = type in ("kneser", "petersen")
    
        # Network dimension
        if type == "tree":
            self.dimension = ttk.Label(self, text="Depth of the tree")
        elif self.offset:
            self.dimension = ttk.Label(self, text="N")
        elif type in ("square-tiling", "hypercube"):
            self.dimension = ttk.Label(self, text="Dimension")
        else:
            self.dimension = ttk.Label(self, text="Number of nodes")
            
        if self.offset:
            self.k = ttk.Label(self, text="K")
            self.entry_k = tk.Entry(self, width=4)
            self.k.grid(row=1, column=0, sticky=tk.W)
            self.entry_k.grid(row=1, column=1, sticky=tk.W)
            
        self.var_dimension = tk.IntVar()
        self.var_dimension.set(4)
        self.entry_dimension = tk.Entry(self, textvariable=self.var_dimension, 
                                                                    width=4)
        
        # List of node type
        self.node_type = ttk.Label(self, text="Type of node")
        self.var_node_type = tk.StringVar()
        self.node_type_list = ttk.Combobox(self, textvariable=self.var_node_type, 
                                                                    width=7)
        self.node_type_list["values"] = scenario.ntw.node_subtype
        self.node_type_list.current(0)
    
        # confirmation button
        self.button_confirmation = ttk.Button(self, text="OK", command=
                                                lambda: self.create_graph())
        
        # position in the grid
        self.dimension.grid(row=0, column=0, pady=5, padx=5, sticky=tk.W)
        self.entry_dimension.grid(row=0, column=1, sticky=tk.W)
        self.node_type.grid(row=1+self.offset, column=0, pady=5, padx=5, 
                                                                    sticky=tk.W)
        self.node_type_list.grid(row=1+self.offset,column=1, pady=5, padx=5, 
                                                                    sticky=tk.W)
        self.button_confirmation.grid(row=2, column=0, columnspan=2, pady=5, 
                                                        padx=5, sticky="nsew")
                                                        
    def create_graph(self):
        if self.offset:
            params = (
                      int(self.var_dimension.get()),
                      int(self.entry_k.get()),
                      self.var_node_type.get()
                      )
        else:
            params = (
                      int(self.var_dimension.get()),
                      self.var_node_type.get()
                      )

        self.dict_type_to_function[self.type](*params)
        
        # convergence
        self.scenario.draw_all(random=False)
        self.destroy()