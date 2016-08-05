# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk
from tkinter import ttk
from collections import OrderedDict
from graph_generation import NetworkDimension
from miscellaneous import CustomTopLevel, ObjectListbox
import drawing_options_window

class MainFrame(tk.Frame):
    
    def __init__(self, master):
        super().__init__(
        width = 200,
        height = 600, 
        borderwidth = 1, 
        relief = "solid", 
        background = "#A1DBCD"
        )

        self.ms = master
        self.bg_color = "#E6E6FA"
        self.font = ("Helvetica", 8, "bold")
        
        functions = OrderedDict([
        ("Update AS topology", self.ms.cs.ntw.update_AS_topology),
        ("Interface allocation", self.ms.cs.ntw.interface_allocation),
        ("IP addressing", self.ms.cs.ntw.ip_allocation),
        ("Subnetwork allocation", self.ms.cs.ntw.subnetwork_allocation),
        ("WC trunk dimensioning", self.ms.cs.ntw.trunk_dimensioning),
        ("Create routing tables", self.ms.cs.ntw.rt_creation),
        ("Route traffic links", self.ms.cs.ntw.path_finder),
        ("Refresh labels", self.ms.cs.refresh_all_labels)
        ])
        
        self.type_to_button = {}
        
        self.type_to_action = {
        "netdim": lambda: Computation(self.ms, functions),
        "motion": lambda: self.switch_to("motion"),
        "multi-layer": lambda: self.ms.cs.switch_display_mode(),
        }
        
        for topo in ("tree", "star", "full-mesh", "ring"):
            self.type_to_action[topo] = lambda t=topo: NetworkDimension(self.ms.cs, t)
            
        for obj_type in self.ms.object_properties:
            cmd = lambda o=obj_type: self.change_creation_mode(o)
            self.type_to_action[obj_type] = cmd
        
        for button_type, cmd in self.type_to_action.items():
            button = tk.Button(self, bg="#A1DBCD", relief=tk.FLAT, command=cmd)
            if button_type in ("route", "traffic"):
                button.configure(text=button_type.capitalize(), 
                                            compound="top", font=self.font)
            elif button_type in ("ethernet", "wdm"):
                text = "Ethernet trunk" if button_type == "ethernet" else "WDM trunk"
                button.configure(text=text, compound="top", font=self.font)
            self.type_to_button[button_type] = button
        
        # netdim mode: motion or creation
        self.type_to_button["netdim"].grid(row=0, column=1, 
                    columnspan=2, rowspan=2, sticky="ew")
        self.type_to_button["motion"].grid(row=2, column=0, 
                    columnspan=2, rowspan=2, padx=20, pady=5, sticky="nsew")
        self.type_to_button["multi-layer"].grid(row=2, column=2, columnspan=2)
        
        sep = ttk.Separator(self, orient=tk.HORIZONTAL)
        sep.grid(row=4, columnspan=4, sticky="ew")
        
        # radio button to choose between link and node selection
        selection_value = tk.StringVar()
        selection_value.set("node") 
        # ttk radiobutton style
        ttk.Style().configure("TRadiobutton", background="#A1DBCD")
        node_selection = ttk.Radiobutton(self, text="Node selection",
                        variable=selection_value, value="node", 
                        command=lambda: self.change_selection("node"))
        link_selection = ttk.Radiobutton(self, text="Link selection",
                        variable=selection_value, value="link", 
                        command=lambda: self.change_selection("link"))
        
        # affichage des radio button
        node_selection.grid(row=5, column=0, columnspan=2, 
                                                pady=5, padx=5, sticky="w")
        link_selection.grid(row=5, column=2, columnspan=2, 
                                                pady=5, padx=5, sticky="w")
        
        sep = ttk.Separator(self, orient=tk.HORIZONTAL)
        sep.grid(row=6, columnspan=4, sticky="ew")
        
        # creation mode: type of node or link
        label_creation_mode = tk.Label(self, text="Object creation", 
                                            bg="#A1DBCD", font=self.font)
        label_creation_mode.grid(row=7, columnspan=4, sticky="ew")
        self.type_to_button["router"].grid(row=8, column=0, padx=2)
        self.type_to_button["switch"].grid(row=8, column=1, padx=2)
        self.type_to_button["oxc"].grid(row=8, column=2, padx=2)
        self.type_to_button["host"].grid(row=8, column=3, padx=2)
        self.type_to_button["regenerator"].grid(row=9, column=0, padx=2)
        self.type_to_button["splitter"].grid(row=9, column=1, padx=2)
        self.type_to_button["antenna"].grid(row=9, column=2, padx=2)
        self.type_to_button["cloud"].grid(row=9, column=3, padx=2)
        
        self.type_to_button["ethernet"].grid(row=10, column=0, columnspan=2, 
                                                pady=5, padx=5, sticky="nsew")
        self.type_to_button["wdm"].grid(row=10, column=2, columnspan=2, 
                                                pady=5, padx=5, sticky="nsew")
        self.type_to_button["route"].grid(row=11, column=2, columnspan=2, 
                                                pady=5, padx=5, sticky="nsew")
        self.type_to_button["traffic"].grid(row=11, column=0, columnspan=2, 
                                                pady=5, padx=5, sticky="nsew")
                                                
        sep = ttk.Separator(self, orient=tk.HORIZONTAL)
        sep.grid(row=12, columnspan=4, sticky="ew")
        
        # graph generation
        label_graph_generation = tk.Label(self, text="Graph generation", 
                                            bg="#A1DBCD", font=self.font)
        label_graph_generation.grid(row=16, columnspan=4, sticky="ew")
        self.type_to_button["tree"].grid(row=17,column=0, sticky="w")
        self.type_to_button["star"].grid(row=17,column=1, sticky="w")
        self.type_to_button["full-mesh"].grid(row=17,column=2, sticky="w")
        self.type_to_button["ring"].grid(row=17,column=3, sticky="w")

    def change_selection(self, mode):
        self.ms.cs.obj_selection = mode
        
    def switch_to(self, mode):
        relief = tk.SUNKEN if mode == "motion" else tk.RAISED
        self.type_to_button["motion"].config(relief=relief)
        self.ms.cs._mode = mode
        self.ms.cs.switch_binding()
        
    def change_creation_mode(self, mode):
        # change the mode to creation 
        self.switch_to("creation")
        self.ms.cs._creation_mode = mode
        for obj_type in self.type_to_button:
            if mode == obj_type:
                self.type_to_button[obj_type].config(relief=tk.SUNKEN)
            else:
                self.type_to_button[obj_type].config(relief=tk.FLAT)
        self.ms.cs.switch_binding()
        
    def erase_graph(self, scenario):
        scenario.erase_graph()
        scenario.ntw.erase_network()
        
class Computation(CustomTopLevel):    
            
    def __init__(self, master, functions):
        super().__init__()
        self.fcts = functions
        self.lb_functions = ObjectListbox(self, activestyle="none", width=15, 
                                            height=7, selectmode="extended")
                                            
        for function in self.fcts:
            self.lb_functions.insert(function) 
            
        # button to confirm selection and trigger functions
        self.OK_button = ttk.Button(self, text="OK", command=self.OK)
                                
        self.lb_functions.pack(fill=tk.BOTH, expand=1)
        self.OK_button.pack()
        
    def OK(self):
        for function in self.lb_functions.selected():
            print(function)
            self.fcts[function]()
        self.destroy()
        