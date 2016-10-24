# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk
from tkinter import ttk
from miscellaneous.custom_toplevel import CustomTopLevel
from miscellaneous.custom_listbox import ObjectListbox

class MultipleNodes(CustomTopLevel):    
    def __init__(self, scenario, x, y):
        super().__init__()
        self.title("Multiple nodes")
        self.cs = scenario
        
        self.nb_nodes = ttk.Label(self, text="Number of nodes")
        self.var_nodes = tk.IntVar()
        self.var_nodes.set(4)
        self.entry_nodes = tk.Entry(self, textvariable=self.var_nodes, width=4)
                                                                    
        
        # List of node type
        self.node_type = ttk.Label(self, text="Type of node")
        self.var_node_type = tk.StringVar()
        self.node_type_list = ttk.Combobox(self, textvariable=self.var_node_type, 
                                                                    width=7)
        self.node_type_list["values"] = scenario.ntw.node_subtype
        self.node_type_list.current(0)
    
        # confirmation button
        self.button_confirmation = ttk.Button(self, text="OK", command=
                                            lambda: self.create_nodes(x, y))
        
        # position in the grid
        self.nb_nodes.grid(row=0, column=0, pady=5, padx=5, sticky=tk.W)
        self.entry_nodes.grid(row=0, column=1, sticky=tk.W)
        self.node_type.grid(row=1, column=0, pady=5, padx=5, sticky=tk.W)
        self.node_type_list.grid(row=1,column=1, pady=5, padx=5, sticky=tk.W)
        self.button_confirmation.grid(row=2, column=0, columnspan=2, pady=5, 
                                                        padx=5, sticky="nsew")
        
    def create_nodes(self, x, y):
        self.cs.multiple_nodes(
                               self.var_nodes.get(), 
                               self.var_node_type.get(),
                               x,
                               y
                               )
        
        self.cs.draw_all(random=False)
        self.destroy()
        
class MultipleLinks(CustomTopLevel):    
    def __init__(self, scenario, source_nodes):
        super().__init__()
        self.title("Multiple links")
        self.cs = scenario
        
        self.dest_node = ttk.Label(self, text="Destination nodes :")

        self.listbox = ObjectListbox(self, activestyle="none", width=15, 
                                        height=7, selectmode="extended")
        yscroll = tk.Scrollbar(self, command=self.listbox.yview, orient=tk.VERTICAL)
        self.listbox.configure(yscrollcommand=yscroll.set)
        self.listbox.grid(row=1, column=0)
        yscroll.grid(row=1, column=1, sticky="ns")
        
        # add all nodes of the scenario to the listbox
        for node in self.cs.ntw.pn["node"].values():
            self.listbox.insert(node.name)
    
        # confirmation button
        self.button_confirmation = ttk.Button(self, text="OK", command=
                                        lambda: self.create_links(source_nodes))
        
        # position in the grid
        self.dest_node.grid(row=0, column=0, pady=5, padx=5, sticky=tk.W)
        self.button_confirmation.grid(row=2, column=0, columnspan=2, pady=5, 
                                                        padx=5, sticky="nsew")
        
    def create_links(self, source_nodes):
        print(source_nodes)
        for selected_node in self.listbox.selected():
            # retrieve the node object based on its name
            dest_node = self.cs.ntw.nf(name=selected_node)
            # create links from all selected nodes to the selected node
            self.cs.ntw.multiple_links(source_nodes, dest_node)
        
        self.cs.draw_all(random=False)
        self.destroy()