import tkinter as tk
from tkinter import ttk
from miscellaneous import CustomTopLevel

class NetworkDimension(CustomTopLevel):    
    def __init__(self, scenario, type):
        super().__init__()
        self.title("Dimension")
        self.type = type
        self.scenario = scenario
        
        self.dict_type_to_function = {
        "star": lambda n, subtype: scenario.ntw.ring(n - 1, subtype),
        "ring": lambda n, subtype: scenario.ntw.ring(n, subtype),
        "full-mesh": lambda n, subtype: scenario.ntw.full_mesh(n, subtype),
        "tree": lambda n, subtype: scenario.ntw.tree(n, subtype),
        "kneser": lambda n, k, subtype: scenario.ntw.kneser(n, k, subtype)
        }
    
        # Network dimension
        if type == "tree":
            self.dimension = ttk.Label(self, text="Depth of the tree")
        elif type == "kneser":
            self.dimension = ttk.Label(self, text="N")
        else:
            self.dimension = ttk.Label(self, text="Number of nodes")
            
        if type == "kneser":
            self.k = ttk.Label(self, text="K")
            self.entry_k = tk.Entry(self, width=4)
            self.k.grid(row=1, column=0, sticky=tk.W)
            self.entry_k.grid(row=1, column=1, sticky=tk.W)
            
        offset = int(type == "kneser")
            
        self.var_dimension = tk.IntVar()
        self.var_dimension.set(4)
        self.entry_dimension = tk.Entry(self, textvariable=self.var_dimension, width=4)
        
        # List of node type
        self.node_type = ttk.Label(self, text="Type of node")
        self.var_node_type = tk.StringVar()
        self.node_type_list = ttk.Combobox(self, textvariable=self.var_node_type, width=7)
        self.node_type_list["values"] = scenario.ntw.node_type
        self.node_type_list.current(0)
    
        # confirmation button
        self.button_confirmation = ttk.Button(self, text="OK", command=
                                                lambda: self.create_graph())
        
        # position in the grid
        self.dimension.grid(row=0, column=0, pady=5, padx=5, sticky=tk.W)
        self.entry_dimension.grid(row=0, column=1, sticky=tk.W)
        self.node_type.grid(row=1+offset, column=0, pady=5, padx=5, sticky=tk.W)
        self.node_type_list.grid(row=1+offset,column=1, pady=5, padx=5, sticky=tk.W)
        self.button_confirmation.grid(row=2, column=0, columnspan=2, pady=5, padx=5, sticky="nsew")
        
    def create_graph(self):
        if self.type == "kneser":
            params = (
                      int(self.var_dimension.get()) + 1,
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
            
class GraphGeneration(CustomTopLevel):
    
    def __init__(self, master):
        
        self.ms = master
        super().__init__()
        
        self.bt_gkneser = ttk.Button(self, text="Generalized Kneser graph", 
                        command=lambda: NetworkDimension(self.ms.cs, "kneser"))
                        
        self.bt_gkneser.grid(row=0, column=0, pady=5, padx=5, sticky=tk.W)
        
        self.withdraw()