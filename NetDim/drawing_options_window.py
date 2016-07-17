# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk
from tkinter import ttk
from miscellaneous import FocusTopLevel, CustomTopLevel

class DrawingOptions(FocusTopLevel):
    
    def __init__(self, master):
        
        self.ms = master
        super().__init__()
        
        self.drawing_algorithms = {
        "Spring layout": self.ms.cs.spring_based_drawing,
        "F-R layout": self.ms.cs.FR_drawing
        }
        
        self.title("Graph drawing with force-directed algorithms")
        self.vars = {"Spring layout": list(), "F-R layout": list()}
    
        self.lf_spring = ttk.Labelframe(self, padding=(6, 6, 12, 12), 
                                        text='Spring layout')
        self.lf_spring.grid(column=0, columnspan=2, pady=5, padx=5, row=1, sticky='nsew')
        self.lf_fr = ttk.Labelframe(self, padding=(6, 6, 12, 12), 
                                        text='F-R layout')
        self.lf_fr.grid(column=2, columnspan=2, pady=5, padx=5, row=1, sticky='nsew')
        
        # combobox for the user to change the drawing algorithm
        self.var_drawing_type = tk.StringVar()
        self.drawing_type_list = ttk.Combobox(self, 
                                textvariable=self.var_drawing_type, width=11)
        self.drawing_type_list["values"] = (
                                       "Spring layout", 
                                       "F-R layout"
                                       )
        self.drawing_type_list.current(0)
        self.drawing_type_list.grid(row=0, column=2, pady=5, padx=5, sticky=tk.W)
        
        self.alpha, self.beta, self.k, self.eta, self.delta, self.L0 = self.ms.drawing_param["Spring layout"]
        self.opd, self.limit = self.ms.drawing_param["F-R layout"]
        
        # Variables de masse
        # Alpha
        self.label_alpha = ttk.Label(self, text="Alpha")
        self.var_alpha = tk.DoubleVar()
        self.var_alpha.set(self.alpha)
        self.vars["Spring layout"].append(self.var_alpha)
        self.entry_alpha = tk.Entry(self, textvariable=self.var_alpha, width=6)
        
        # Beta
        self.label_beta = ttk.Label(self, text = "Beta")
        self.var_beta = tk.IntVar()
        self.var_beta.set(self.beta)
        self.vars["Spring layout"].append(self.var_beta)
        self.entry_beta = tk.Entry(self, textvariable=self.var_beta, width=6)
        
        # k
        self.label_k = ttk.Label(self, text = "k")
        self.var_k = tk.DoubleVar()
        self.var_k.set(self.k)
        self.vars["Spring layout"].append(self.var_k)
        self.entry_k = tk.Entry(self, textvariable=self.var_k, width=6)
        
        # Variables de dumping
        # Eta
        self.label_eta = ttk.Label(self, text = "Eta")
        self.var_eta = tk.DoubleVar()
        self.var_eta.set(self.eta)
        self.vars["Spring layout"].append(self.var_eta)
        self.entry_eta = tk.Entry(self, textvariable=self.var_eta, width=6)
        
        # Delta
        self.label_delta = ttk.Label(self, text = "Delta")
        self.var_delta = tk.DoubleVar()
        self.var_delta.set(self.delta)
        self.vars["Spring layout"].append(self.var_delta)
        self.entry_delta = tk.Entry(self, textvariable=self.var_delta, width=6)
        
        # Raideur du ressort d
        self.label_L0 = ttk.Label(self, text = "Raideur")
        self.var_L0 = tk.DoubleVar()
        self.var_L0.set(self.L0)
        self.vars["Spring layout"].append(self.var_L0)
        self.entry_L0 = tk.Entry(self, textvariable=self.var_L0, width=6)
        
        # optimal pairwise distance for fruchterman-reingold
        self.label_opd = ttk.Label(self, text = "OPD")
        self.var_opd = tk.DoubleVar()
        self.var_opd.set(self.opd)
        self.entry_opd = tk.Entry(self, textvariable=self.var_opd, width=6)
        self.vars["F-R layout"].append(self.var_opd)
        
        self.button_save = ttk.Button(self, text="Save", 
                                        command=lambda: self.save())
                                        
        # check button for nodes to stay in the screen 
        self.limit = tk.IntVar()
        self.button_limit = ttk.Checkbutton(self, text="Screen limit", 
                                                            variable=self.limit)
        self.limit.set(True)
        self.vars["F-R layout"].append(self.limit)
        
        # affichage des boutons / label dans la grille
        self.label_alpha.grid(in_=self.lf_spring, row=1, column=0, pady=5, padx=5, sticky=tk.W)
        self.entry_alpha.grid(in_=self.lf_spring, row=1, column=1, sticky=tk.W)
        self.label_beta.grid(in_=self.lf_spring, row=1, column=0, pady=5, padx=5, sticky=tk.W)
        self.entry_beta.grid(in_=self.lf_spring, row=1, column=1, sticky=tk.W)
        self.label_k.grid(in_=self.lf_spring, row=2, column=0, pady=5, padx=5, sticky=tk.W)
        self.entry_k.grid(in_=self.lf_spring, row=2, column=1, sticky=tk.W)
        self.label_eta.grid(in_=self.lf_spring, row=3, column=0, pady=5, padx=5, sticky=tk.W)
        self.entry_eta.grid(in_=self.lf_spring, row=3, column=1, sticky=tk.W)
        self.label_delta.grid(in_=self.lf_spring, row=4, column=0, pady=5, padx=5, sticky=tk.W)
        self.entry_delta.grid(in_=self.lf_spring, row=4, column=1, sticky=tk.W)
        self.label_L0.grid(in_=self.lf_spring, row=5, column=0, pady=5, padx=5, sticky=tk.W)
        self.entry_L0.grid(in_=self.lf_spring, row=5, column=1, sticky=tk.W)
        self.label_opd.grid(in_=self.lf_fr, row=0, column=0, pady=5, padx=5, sticky=tk.W)
        self.entry_opd.grid(in_=self.lf_fr, row=0, column=1, sticky=tk.W)
        self.button_limit.grid(in_=self.lf_fr, row=1, column=0, sticky=tk.W)
        self.button_save.grid(row=6, column=0, pady=5, padx=5, sticky=tk.W)
    
    def save(self):
        # retrieve variables values
        self.ms.drawing_algorithm = self.drawing_algorithms[self.var_drawing_type.get()]
        for algo in ("Spring layout", "F-R layout"):
            self.ms.drawing_param[algo] = tuple(float(v.get()) for v in self.vars[algo])
        
        
