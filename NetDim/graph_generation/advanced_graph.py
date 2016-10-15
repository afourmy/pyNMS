# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk
from tkinter import ttk
from miscellaneous.custom_toplevel import FocusTopLevel
from os.path import join
from PIL import ImageTk
from graph_generation.network_dimension import NetworkDimension

class AdvancedGraph(FocusTopLevel):
    
    def __init__(self, master):
        
        self.ms = master
        super().__init__()
        font = ("Helvetica", 8, "bold")
        
        images = (
        ("square-tiling", (100, 100)),
        ("hypercube", (100, 100)),
        ("kneser", (100, 100)),
        ("petersen", (100, 100))
        )

        self.dict_images = {}
        
        for image_type, image_size in images:
            img_path = join(self.ms.path_icon, image_type + ".png")
            img_pil = ImageTk.Image.open(img_path).resize(image_size)
            img = ImageTk.PhotoImage(img_pil)
            self.dict_images[image_type] = img
            
        button_config = (
        ("square-tiling", (0, 0), "Square tiling"),
        ("hypercube", (0, 1), "Hypercube"),
        ("kneser", (1, 0), "Kneser"),
        ("petersen", (1, 1), "Petersen")
        )
        
        # label frame for the infinite graph generation button
        self.lf_inf_graph = ttk.Labelframe(self, padding=(6, 6, 12, 12), 
                                            text='Infinite graph generation')
        self.lf_inf_graph.grid(row=1, column=0, columnspan=2, pady=5, padx=5, 
                                                                sticky='nsew')
                                                        
        for bt_type, (row, col), bt_text in button_config:
            bt = tk.Button(self, bg="#A1DBCD", text=bt_text, 
                    command=lambda t=bt_type: NetworkDimension(self.ms.cs, t))
            bt.grid(in_=self.lf_inf_graph, row=row, column=col, pady=5, padx=5)
            bt.config(image=self.dict_images[bt_type], compound="top", font=font)
                                                        
        self.lf_classic_graph = ttk.Labelframe(self, padding=(6, 6, 12, 12), 
                                            text='Classic graph generation')
        self.lf_classic_graph.grid(row=1, column=3, columnspan=2, pady=5, 
                                                        padx=5, sticky='nsew')
                                        
        self.graph_properties = {
        "Desargues": (3, 4, 2),
        "graph-test": (4, 5, 4)
        }
        
        # List of classic graphs
        self.graph_list = ttk.Combobox(self, width=9)
        self.graph_list["values"] = tuple(self.graph_properties.keys())
        self.graph_list.current(0)
        self.graph_list.grid(in_=self.lf_classic_graph, row=0, column=0,
                                columnspan=2, pady=5, padx=5, sticky="nsew")
        self.graph_list.bind('<<ComboboxSelected>>',
                                        lambda e: self.update_properties())
        
        properties = (
        "Number of nodes :",
        "Number of links :",
        "Chromatic number :"
        )
        
        self.var_labels = []
        
        for idx, property in enumerate(properties, 1):
            label_property = ttk.Label(self, text=property)
            label_property.grid(in_=self.lf_classic_graph, row=idx, column=0, 
                                                pady=5, padx=5, sticky=tk.W)
            label_value = ttk.Label(self, text="", width=3)
            label_value.grid(in_=self.lf_classic_graph, row=idx, column=1, 
                                                pady=5, padx=5, sticky=tk.W)
            self.var_labels.append(label_value)
            
        self.bt_gen = ttk.Button(self, text="Generate", command=self.generate)
        self.bt_gen.grid(in_=self.lf_classic_graph, row=len(properties)+1, 
                                        column=0, columnspan=2, pady=5, padx=5)
                                        
        self.graph_generation = {
        "Desargues": lambda: self.ms.cs.ntw.petersen(5, 2, "oxc"),
        "graph-test": lambda: self.ms.cs.ntw.petersen(6, 3, "router")
        }
            
        self.update_properties()
        # hide the window when closed
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        self.withdraw()
                                        
    # when a graph is selected, the properties are updated accordingly
    def update_properties(self):
        selected_graph = self.graph_list.get()
        for idx, value in enumerate(self.graph_properties[selected_graph]):
            self.var_labels[idx].configure(text=value)
            
    def generate(self):
        selected_graph = self.graph_list.get()
        self.graph_generation[selected_graph]()
        self.ms.cs.draw_all(random=False)