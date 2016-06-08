# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk
from tkinter import ttk
from miscellaneous import CustomTopLevel

class MainFrame(tk.Frame):
    
    def __init__(self, master):
        super().__init__(width=200,height=600, borderwidth=1, relief="solid", background="#A1DBCD")
        self.bg_color = "#E6E6FA"
        self.font = ("Helvetica", 8, "bold")
        self.type_to_button = {}
        
        self.type_to_action = {
        "netdim": lambda: master.cs.ntw.calculate_all(),
        "motion": lambda: self.switch_to(master, "motion"),
        "creation": lambda: self.switch_to(master, "creation"),
        "draw": lambda: master.cs.spring_based_drawing(master),
        "stop": lambda: master.cs._cancel(),
        "multi-layer": lambda: master.cs.switch_display_mode(),
        }
        
        for topo in ("tree", "star", "full-mesh", "ring"):
            self.type_to_action[topo] = lambda t=topo: NetworkDimension(master.cs, t)
            
        for obj_type in master.object_properties:
            self.type_to_action[obj_type] = lambda o=obj_type: self.change_creation_mode(master, o)
        
        for button_type, cmd in self.type_to_action.items():
            button = tk.Button(self, bg="#A1DBCD", relief=tk.FLAT, command=cmd)
            if button_type in ("trunk", "route", "traffic", "draw", "stop"):
                button.configure(text=button_type.capitalize(), compound="top", font=self.font)
            self.type_to_button[button_type] = button
        
        # netdim mode: motion or creation
        self.type_to_button["netdim"].grid(row=0, column=1, columnspan=2, rowspan=2, sticky="ew")
        self.type_to_button["motion"].grid(row=2, column=0, columnspan=2, rowspan=2, padx=20, pady=5, sticky="nsew")
        self.type_to_button["creation"].grid(row=2, column=2, columnspan=2, rowspan=2, pady=5, padx=5, sticky=tk.W)
        sep = ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=4, columnspan=4, sticky="ew")
        
        # creation mode: type of node or link
        label_creation_mode = tk.Label(self, text="Object creation", bg="#A1DBCD", font=self.font)
        label_creation_mode.grid(row=5, columnspan=4, sticky="ew")
        self.type_to_button["router"].grid(row=6, column=0, padx=2, sticky=tk.N)
        self.type_to_button["oxc"].grid(row=6, column=1, padx=2, sticky=tk.W)
        self.type_to_button["host"].grid(row=6, column=2, padx=2, sticky=tk.W)
        self.type_to_button["antenna"].grid(row=6, column=3, padx=2, sticky=tk.W)
        self.type_to_button["regenerator"].grid(row=7, column=0, padx=2, sticky=tk.W)
        self.type_to_button["splitter"].grid(row=7, column=1, padx=2, sticky=tk.W)
        self.type_to_button["trunk"].grid(row=7, column=2, columnspan=2, padx=2, sticky=tk.W)
        self.type_to_button["route"].grid(row=8, column=2, columnspan=2, pady=5, padx=5, sticky=tk.W)
        self.type_to_button["traffic"].grid(row=8, column=0, columnspan=2, pady=5, padx=5, sticky=tk.W)
        sep = ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=9, columnspan=4, sticky="ew")
        
        # drawing options
        label_drawing_options = tk.Label(self, text="Force-directed layout", bg="#A1DBCD", font=self.font)
        label_drawing_options.grid(row=10, columnspan=4, sticky="ew")
        self.type_to_button["draw"].grid(row=11, column=0, columnspan=2, pady=5, padx=20, sticky="nsew")
        self.type_to_button["stop"].grid(row=11, column=2, columnspan=2, pady=5, padx=20, sticky="nsew")
        sep = ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=12, columnspan=4, sticky="ew")
        
        # graph generation
        label_graph_generation = tk.Label(self, text="Graph generation", bg="#A1DBCD", font=self.font)
        label_graph_generation.grid(row=13, columnspan=4, sticky="ew")
        self.type_to_button["tree"].grid(row=14,column=0, sticky="w")
        self.type_to_button["star"].grid(row=14,column=1, sticky="w")
        self.type_to_button["full-mesh"].grid(row=14,column=2, sticky="w")
        self.type_to_button["ring"].grid(row=14,column=3, sticky="w")
        sep = ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=15, columnspan=4, sticky="ew")
        
        # multi-layer
        self.type_to_button["multi-layer"].grid(row=16, columnspan=4, sticky="ew")
        
    def switch_to(self, master, mode):
        alt_mode = "creation" if mode == "motion" else "motion"
        self.type_to_button[mode].config(relief=tk.SUNKEN)
        self.type_to_button[alt_mode].config(relief=tk.RAISED)
        master.cs._mode = mode
        master.cs.switch_binding()
        
    def change_creation_mode(self, master, mode):
        # change the mode to creation 
        self.switch_to(master, "creation")
        master.cs._creation_mode = mode
        for obj_type in self.type_to_button:
            if mode == obj_type:
                self.type_to_button[obj_type].config(relief=tk.SUNKEN)
            else:
                self.type_to_button[obj_type].config(relief=tk.FLAT)
        master.cs.switch_binding()
        
    def erase_graph(self, scenario):
        scenario.erase_graph()
        scenario.ntw.erase_network()
        
class NetworkDimension(CustomTopLevel):
    def __init__(self, scenario, type):
        super().__init__()
        self.geometry("145x70")
        self.title("Dimension")
    
        # Network dimension
        if type != "tree":
            self.dimension = tk.Label(self, bg="#A1DBCD", text="Number of nodes")
        else:
            self.dimension = tk.Label(self, bg="#A1DBCD", text="Depth of the tree")
        self.var_dimension = tk.IntVar()
        self.var_dimension.set(4)
        self.entry_dimension = tk.Entry(self, textvariable=self.var_dimension, width=4)
    
        # confirmation button
        self.button_confirmation = ttk.Button(self, text="OK", command=lambda: self.create_graph(scenario, type))
        
        # position in the grid
        self.dimension.grid(row=0, column=0, pady=5, padx=5, sticky=tk.W)
        self.entry_dimension.grid(row=0, column=1, sticky=tk.W)
        self.button_confirmation.grid(row=1, column=0, columnspan=2, pady=5, padx=5, sticky="nsew")
        
    def create_graph(self, scenario, type):
        #TODO make it a dict
        if type == "star":
            scenario.ntw.generate_star(self.var_dimension.get() - 1)
        elif type == "ring":
            scenario.ntw.generate_ring(self.var_dimension.get() - 1)
        elif type == "full-mesh":
            scenario.ntw.generate_full_mesh(self.var_dimension.get())
        else:
            scenario.ntw.generate_tree(self.var_dimension.get())
        scenario.draw_all(random=False)
        self.destroy()
        