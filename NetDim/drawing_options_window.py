# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk
from tkinter import ttk
from miscellaneous import FocusTopLevel, CustomTopLevel

class DrawingOptions(FocusTopLevel):
    def __init__(self, master):
        super().__init__()
        self.title("Graph drawing with force-directed algorithms")
        self.ender_variables = []
    
        # Variables de masse
        # Alpha
        self.label_alpha = ttk.Label(self, text="Alpha")
        self.var_alpha = tk.DoubleVar()
        self.var_alpha.set(master.alpha)
        self.ender_variables.append(self.var_alpha)
        self.entry_alpha = tk.Entry(self, textvariable=self.var_alpha, width=15)
        
        # Beta
        self.label_beta = ttk.Label(self, text = "Beta")
        self.var_beta = tk.IntVar()
        self.var_beta.set(master.beta)
        self.ender_variables.append(self.var_beta)
        self.entry_beta = tk.Entry(self, textvariable=self.var_beta, width=15)
        
        # k
        self.label_k = ttk.Label(self, text = "k")
        self.var_k = tk.DoubleVar()
        self.var_k.set(master.k)
        self.ender_variables.append(self.var_k)
        self.entry_k = tk.Entry(self, textvariable=self.var_k, width=15)
        
        # Variables de dumping
        # Eta
        self.label_eta = ttk.Label(self, text = "Eta")
        self.var_eta = tk.DoubleVar()
        self.var_eta.set(master.eta)
        self.ender_variables.append(self.var_eta)
        self.entry_eta = tk.Entry(self, textvariable=self.var_eta, width=15)
        
        # Delta
        self.label_delta = ttk.Label(self, text = "Delta")
        self.var_delta = tk.DoubleVar()
        self.var_delta.set(master.delta)
        self.ender_variables.append(self.var_delta)
        self.entry_delta = tk.Entry(self, textvariable=self.var_delta, width=15)
        
        # optimal pairwise distance
        self.label_opd = ttk.Label(self, text = "Optimal pairwise distance")
        self.var_opd = tk.DoubleVar()
        self.var_opd.set(master.opd)
        self.entry_opd = tk.Entry(self, textvariable=self.var_opd, width=15)
        
        # Raideur du ressort d
        self.label_L0 = ttk.Label(self, text = "Raideur")
        self.var_L0 = tk.DoubleVar()
        self.var_L0.set(master.L0)
        self.ender_variables.append(self.var_L0)
        self.entry_L0 = tk.Entry(self, textvariable=self.var_L0, width=15)
        
        # drawing button
        self.bouton_force_based = ttk.Button(self, text="Force-based", command = lambda: self.spring_layout())
        self.bouton_reingold = ttk.Button(self, text="Fruchtemann-reingold", command = lambda: self.frucht())
        self.bouton_draw_graph = ttk.Button(self, text="Draw graph", command = lambda: self.draw_all())
        self.bouton_stop = ttk.Button(self, text="Stop drawing", command = lambda: self._cancel())
        
        # affichage des boutons / label dans la grille
        self.label_alpha.grid(row=1, column=0, pady=5, padx=5, sticky=tk.W)
        self.entry_alpha.grid(row=1, column=1, sticky=tk.W)
        self.label_beta.grid(row=1, column=0, pady=5, padx=5, sticky=tk.W)
        self.entry_beta.grid(row=1, column=1, sticky=tk.W)
        self.label_k.grid(row=2, column=0, pady=5, padx=5, sticky=tk.W)
        self.entry_k.grid(row=2, column=1, sticky=tk.W)
        self.label_eta.grid(row=3, column=0, pady=5, padx=5, sticky=tk.W)
        self.entry_eta.grid(row=3, column=1, sticky=tk.W)
        self.label_delta.grid(row=4, column=0, pady=5, padx=5, sticky=tk.W)
        self.entry_delta.grid(row=4, column=1, sticky=tk.W)
        self.label_L0.grid(row=5, column=0, pady=5, padx=5, sticky=tk.W)
        self.entry_L0.grid(row=5, column=1, sticky=tk.W)
        self.label_opd.grid(row=0, column=2, pady=5, padx=5, sticky=tk.W)
        self.entry_opd.grid(row=0, column=3, sticky=tk.W)

        self.bouton_force_based.grid(row=7,column=1, pady=5, padx=5, sticky=tk.E)
        self.bouton_reingold.grid(row=7,column=3, pady=5, padx=5, sticky=tk.E)
        self.bouton_draw_graph.grid(row=7,column=0, pady=5, padx=5, sticky=tk.E)
        self.bouton_stop.grid(row=7,column=2, pady=5, padx=5, sticky=tk.E)
        
        # hide the window when closed
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        self.withdraw()
    
    def save_value(self, master):
        # retrieve variables values
        master.alpha, master.beta, master.k, master.eta, master.delta, master.L0 = [v.get() for v in self.ender_variables]
        
class NetworkDrawing(CustomTopLevel):    
    def __init__(self, scenario, nodes):
        super().__init__()
        self.title("Network drawing")
        
        drawing_modes = (
        "Random",
        "Force-based",
        "Both"
        )
        
        # List of drawing modes
        self.drawing_label = ttk.Label(self, text="Drawing mode :")
        self.var_mode = tk.StringVar()
        self.drawing_mode = ttk.Combobox(self, textvariable=self.var_mode, width=20)
        self.drawing_mode["values"] = drawing_modes
        self.drawing_mode.current(0)
    
        # confirmation button
        self.OK_button = ttk.Button(self, text="OK",
                            command=lambda: self.draw_graph(scenario, nodes))
        
        # position in the grid
        self.drawing_label.grid(row=0, column=0, pady=5, padx=5)
        self.drawing_mode.grid(row=1, column=0, pady=5, padx=5, sticky="nsew")
        self.OK_button.grid(row=2, column=0, columnspan=2, pady=5, padx=5, sticky="nsew")
        
    def draw_graph(self, scenario, nodes):
        mode = self.var_mode.get()
        if mode == "Random":
            scenario.draw_objects(nodes, True)
        elif mode == "Force-based":
            scenario.spring_based_drawing(scenario.master, nodes)
        elif mode == "Both":
            scenario.draw_objects(nodes, True)
            scenario.spring_based_drawing(scenario.master, nodes)
        self.destroy()
        
        
