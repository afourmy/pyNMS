# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

from miscellaneous.custom_toplevel import FocusTopLevel
import tkinter as tk
from tkinter import ttk

class RWAWindow(FocusTopLevel):
    def __init__(self, master):
        super().__init__()   
        self.ms = master   
        self.title("Routing and Wavelength Assignment")
                        
        # label frame
        self.lf_rwa = ttk.Labelframe(self, padding=(6, 6, 12, 12), 
                                    text='Routing and Wavelength Assignment')
        self.lf_rwa.grid(column=0, columnspan=2, pady=5, padx=5, 
                                                        row=1, sticky='nsew')
                                                        
        ## Graph transformation and scenario name
                
        self.sco_name = ttk.Label(self, text="Scenario name :")
        self.sco_name.grid(in_=self.lf_rwa, row=0, column=0, pady=5, padx=5,
                                                                    sticky="w")
        self.entry_sco = ttk.Entry(self, width=20)
        self.entry_sco.grid(in_=self.lf_rwa, row=0, column=1, pady=5, padx=5,
                                                                    sticky="e")
        
        self.button_gt = ttk.Button(self, text="Graph transformation", 
                                                command=self.transform_graph)
        self.button_gt.grid(in_=self.lf_rwa, row=1, column=0, columnspan=2, 
                                        pady=5, padx=5, sticky="nsew")
        
        ## RWA algorithm:
        
        # label "algorithm"
        self.algorithm = ttk.Label(self, text="Algorithm :")
        self.algorithm.grid(in_=self.lf_rwa, row=2, column=0, pady=5, padx=5,
                                                                    sticky="w")
        
        # combobox for the user to change the RWA algorithm
        self.var_rwa_type = tk.StringVar()
        self.rwa_list = ttk.Combobox(self, 
                                    textvariable=self.var_rwa_type, width=17)
        self.rwa_list["values"] = (
                                       "Linear programming", 
                                       "Largest degree first"
                                       )
        self.rwa_list.set("Linear programming")
        self.rwa_list.grid(in_=self.lf_rwa, row=2, column=1, 
                                                    pady=5, padx=5, sticky="e")
                                                    
        self.button_run_alg = ttk.Button(self, text="Run algorithm", 
                                                command=self.run_algorithm)
        self.button_run_alg.grid(in_=self.lf_rwa, row=3, column=0, columnspan=2, 
                                        pady=5, padx=5, sticky="nsew")
        
        # hide the window when closed
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        # hide at creation
        self.withdraw()
        
    def transform_graph(self):
        name = self.entry_sco.get()
        self.ms.cs.ntw.RWA_graph_transformation(name)

    def run_algorithm(self):
        algorithm = self.var_rwa_type.get()
        if algorithm == "Linear programming":
            self.ms.cs.ntw.LP_RWA_formulation()
        else:
            self.ms.cs.ntw.largest_degree_first()
        