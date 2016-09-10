# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk
from tkinter import ttk
from miscellaneous.custom_toplevel import FocusTopLevel
from collections import OrderedDict

class GraphAlgorithmWindow(FocusTopLevel):
    def __init__(self, master):
        super().__init__()
        self.ms = master
        self.title("Advanced graph options")

        ## Shortest path section
        
        # shortest path algorithms include:
        #   - shortest path with A* (Dijkstra)
        #   - shortest path with Bellman-Ford
        #   - shortest path with Floyd-Warshall
        #   - shortest path with Linear programming

        # label frame for shortest path algorithms
        self.lf_sp = ttk.Labelframe(self, padding=(6, 6, 12, 12), 
                                            text='Shortest path algorithms')
        self.lf_sp.grid(row=1, column=0, columnspan=2, pady=5, padx=5, 
                                                                sticky='nsew')

        self.sp_algorithms = OrderedDict([
        ("Constrained A*", self.ms.cs.ntw.A_star),
        ("Bellman-Ford algorithm", self.ms.cs.ntw.bellman_ford),
        ("Floyd-Warshall algorithm", self.ms.cs.ntw.floyd_warshall),
        ("Linear programming", self.ms.cs.ntw.LP_SP_formulation)
        ])

        # List of shortest path algorithms
        self.sp_list = ttk.Combobox(self, width=9)
        self.sp_list["values"] = tuple(self.sp_algorithms.keys())
        self.sp_list.current(0)
        self.sp_list.grid(in_=self.lf_sp, row=0, column=0,
                                columnspan=2, pady=5, padx=5, sticky="nsew")
                                
        self.sp_src_label = ttk.Label(self, text="Source :")
        self.sp_src_entry = ttk.Entry(self)
        self.sp_src_label.grid(in_=self.lf_sp, row=1, column=0, pady=5, padx=5, sticky=tk.W)
        self.sp_src_entry.grid(in_=self.lf_sp, row=1, column=1, pady=5, padx=5, sticky=tk.W)
        
        self.sp_dest_label = ttk.Label(self, text="Destination :")
        self.sp_dest_entry = ttk.Entry(self)
        self.sp_dest_label.grid(in_=self.lf_sp, row=2, column=0, pady=5, padx=5, sticky=tk.W)
        self.sp_dest_entry.grid(in_=self.lf_sp, row=2, column=1, pady=5, padx=5, sticky=tk.W)
        
        self.bt_sp = ttk.Button(self, text="Compute path", command=self.compute_sp)
        self.bt_sp.grid(in_=self.lf_sp, row=3, column=0, columnspan=2, pady=5, padx=5)
        
        ## Maximum flow section
        
        # maximum flow algorithms include:
        #   - maximum flow with Ford-Fulkerson
        #   - maximum flow with Edmond-Karps
        #   - maximum flow with Dinic
        #   - maximum flow with Linear programming
        
        # label frame for maximum flow algorithms
        self.lf_mflow = ttk.Labelframe(self, padding=(6, 6, 12, 12), 
                                            text='Maximum flow algorithms')
        self.lf_mflow.grid(row=1, column=2, columnspan=2, pady=5, padx=5, 
                                                                sticky='nsew')
                                                                
        self.mflow_algorithms = OrderedDict([
        ("Ford-Fulkerson", self.ms.cs.ntw.ford_fulkerson),
        ("Edmond-Karps", self.ms.cs.ntw.edmonds_karp),
        ("Dinic", self.ms.cs.ntw.dinic),
        ("Linear programming", self.ms.cs.ntw.LP_MF_formulation)
        ])
        
        # List of flow path algorithms
        self.mflow_list = ttk.Combobox(self, width=9)
        self.mflow_list["values"] = tuple(self.mflow_algorithms.keys())
        self.mflow_list.current(0)
        self.mflow_list.grid(in_=self.lf_mflow, row=0, column=0,
                                columnspan=2, pady=5, padx=5, sticky="nsew")
        self.mflow_list.bind('<<ComboboxSelected>>', self.readonly)
                                        
        self.mflow_src_label = ttk.Label(self, text="Source :")
        self.mflow_src_entry = ttk.Entry(self)
        self.mflow_src_label.grid(in_=self.lf_mflow, row=1, column=0, pady=5, padx=5, sticky=tk.W)
        self.mflow_src_entry.grid(in_=self.lf_mflow, row=1, column=1, pady=5, padx=5, sticky=tk.W)
        
        self.mflow_dest_label = ttk.Label(self, text="Destination :")
        self.mflow_dest_entry = ttk.Entry(self)
        self.mflow_dest_label.grid(in_=self.lf_mflow, row=2, column=0, pady=5, padx=5, sticky=tk.W)
        self.mflow_dest_entry.grid(in_=self.lf_mflow, row=2, column=1, pady=5, padx=5, sticky=tk.W)
        
        self.bt_mflow = ttk.Button(self, text="Compute flow", command=self.compute_mflow)
        self.bt_mflow.grid(in_=self.lf_mflow, row=4, column=0, columnspan=2, pady=5, padx=5)
        
        ## K link-disjoint shortest paths section
        
        # K link-disjoint shortest paths algorithms include:
        #   - constrained A*
        #   - Bhandari algorithm
        #   - Suurbale algorithm
        #   - Linear programming

        # label frame for shortest pair algorithms
        self.lf_spair = ttk.Labelframe(self, padding=(6, 6, 12, 12), 
                                            text='K link-disjoint shortest paths algorithms')
        self.lf_spair.grid(row=2, column=0, columnspan=2, pady=5, padx=5, 
                                                                sticky='nsew')

        self.spair_algorithms = OrderedDict([
        ("Constrained A*", self.ms.cs.ntw.A_star_shortest_pair),
        ("Bhandari algorithm", self.ms.cs.ntw.bhandari),
        ("Suurbale algorithm", self.ms.cs.ntw.suurbale),
        ("Linear programming", lambda: "to repair")
        ])

        # List of shortest path algorithms
        self.spair_list = ttk.Combobox(self, width=9)
        self.spair_list["values"] = tuple(self.spair_algorithms.keys())
        self.spair_list.current(0)
        self.spair_list.grid(in_=self.lf_spair, row=0, column=0,
                                columnspan=2, pady=5, padx=5, sticky="nsew")
                                
        self.spair_src_label = ttk.Label(self, text="Source :")
        self.spair_src_entry = ttk.Entry(self)
        self.spair_src_label.grid(in_=self.lf_spair, row=1, column=0, pady=5, padx=5, sticky=tk.W)
        self.spair_src_entry.grid(in_=self.lf_spair, row=1, column=1, pady=5, padx=5, sticky=tk.W)
        
        self.spair_dest_label = ttk.Label(self, text="Destination :")
        self.spair_dest_entry = ttk.Entry(self)
        self.spair_dest_label.grid(in_=self.lf_spair, row=2, column=0, pady=5, padx=5, sticky=tk.W)
        self.spair_dest_entry.grid(in_=self.lf_spair, row=2, column=1, pady=5, padx=5, sticky=tk.W)
        
        self.nb_paths_label = ttk.Label(self, text="Number of paths :")
        self.nb_paths_label.grid(in_=self.lf_spair, row=3, column=0, pady=5, padx=5, sticky=tk.W)
        self.nb_paths_entry = ttk.Entry(self)
        self.nb_paths_entry.grid(in_=self.lf_spair, row=3, column=1, pady=5, padx=5, sticky=tk.W)
        
        self.bt_spair = ttk.Button(self, text="Compute paths", command=self.compute_spair)
        self.bt_spair.grid(in_=self.lf_spair, row=4, column=0, columnspan=2, pady=5, padx=5)
        
        ## Minimum-cost flow section
        
        # minimum-cost flow algorithms include:
        #   - minimum-cost flow with Linear programming
        #   - minimum-cost flow with Klein (cycle-cancelling algorithm)
        
        # label frame for maximum flow algorithms
        self.lf_mcflow = ttk.Labelframe(self, padding=(6, 6, 12, 12), 
                                        text='Minimum-cost flow algorithms')
        self.lf_mcflow.grid(row=2, column=2, columnspan=2, pady=5, padx=5, 
                                                                sticky='nsew')
        
        self.mcflow_algorithms = OrderedDict([
        ("Linear programming", self.ms.cs.ntw.LP_MCF_formulation),
        ("Klein", lambda: "to be implemented")
        ])
        
        # List of flow path algorithms
        self.mcflow_list = ttk.Combobox(self, width=9)
        self.mcflow_list["values"] = tuple(self.mcflow_algorithms.keys())
        self.mcflow_list.current(0)
        self.mcflow_list.grid(in_=self.lf_mcflow, row=0, column=0,
                                columnspan=2, pady=5, padx=5, sticky="nsew")
        self.mcflow_list.bind('<<ComboboxSelected>>', self.readonly)
                                        
        self.mcflow_src_label = ttk.Label(self, text="Source :")
        self.mcflow_src_entry = ttk.Entry(self)
        self.mcflow_src_label.grid(in_=self.lf_mcflow, row=1, column=0, pady=5, padx=5, sticky=tk.W)
        self.mcflow_src_entry.grid(in_=self.lf_mcflow, row=1, column=1, pady=5, padx=5, sticky=tk.W)
        
        self.mcflow_dest_label = ttk.Label(self, text="Destination :")
        self.mcflow_dest_entry = ttk.Entry(self)
        self.mcflow_dest_label.grid(in_=self.lf_mcflow, row=2, column=0, pady=5, padx=5, sticky=tk.W)
        self.mcflow_dest_entry.grid(in_=self.lf_mcflow, row=2, column=1, pady=5, padx=5, sticky=tk.W)
        
        self.bt_mcflow = ttk.Button(self, text="Compute cost", command=self.compute_mcflow)
        self.bt_mcflow.grid(in_=self.lf_mcflow, row=4, column=0, columnspan=2, pady=5, padx=5)
        
        self.flow_label = ttk.Label(self, text="Flow :")
        self.flow_label.grid(in_=self.lf_mcflow, row=3, column=0, pady=5, padx=5, sticky=tk.W)
        self.flow_entry = ttk.Entry(self)
        self.flow_entry.grid(in_=self.lf_mcflow, row=3, column=1, pady=5, padx=5, sticky=tk.W)

        # hide the window when closed
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        self.withdraw()
        
    def readonly(self, event):
        if self.flow_list.get()[-4:-1] == "MCF":
            self.max_flow_entry.config(state=tk.NORMAL)
        else:
            self.max_flow_entry.config(state="readonly")
                                        
    def compute_sp(self):
        source = self.ms.cs.ntw.nf(name=self.sp_src_entry.get())
        destination = self.ms.cs.ntw.nf(name=self.sp_dest_entry.get())
        algorithm = self.sp_list.get()
        nodes, trunks = self.sp_algorithms[algorithm](source, destination)
        self.ms.cs.highlight_objects(*(nodes + trunks))
        
    def compute_spair(self):
        source = self.ms.cs.ntw.nf(name=self.spair_src_entry.get())
        destination = self.ms.cs.ntw.nf(name=self.spair_dest_entry.get())
        algorithm = self.spair_list.get()
        nodes, trunks = self.spair_algorithms[algorithm](source, destination)
        self.ms.cs.highlight_objects(*(nodes + trunks))
        
    def compute_mflow(self):
        source = self.ms.cs.ntw.nf(name=self.mflow_src_entry.get())
        destination = self.ms.cs.ntw.nf(name=self.mflow_dest_entry.get())
        algorithm = self.mflow_algorithms[self.mflow_list.get()]
        flow = algorithm(source, destination)   
        print(flow)
        
    def compute_mcflow(self):
        source = self.ms.cs.ntw.nf(name=self.mcflow_src_entry.get())
        destination = self.ms.cs.ntw.nf(name=self.mcflow_dest_entry.get())
        flow = self.flow_entry.get()
        algorithm = self.mcflow_algorithms[self.mcflow_list.get()]
        cost = algorithm(source, destination, flow)   
        print(cost)
