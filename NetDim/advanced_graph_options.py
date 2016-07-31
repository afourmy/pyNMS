# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk
from tkinter import ttk
from miscellaneous import FocusTopLevel
from collections import OrderedDict

class AdvancedGraphOptionsWindow(FocusTopLevel):
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
                                            text='Shortest pair algorithms')
        self.lf_sp.grid(row=1, column=0, columnspan=2, pady=5, padx=5, 
                                                                sticky='nsew')

        self.sp_algorithms = OrderedDict([
        ("A* algorithm", self.ms.cs.ntw.A_star),
        ("Bellman-Ford algorithm", self.ms.cs.ntw.bellman_ford),
        ("Floyd-Warshall algorithm", self.ms.cs.ntw.floyd_warshall),
        ("Linear programming algorithm", self.ms.cs.ntw.LP_SP_formulation)
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
        
        ## Flow section
        
        # flow algorithms include:
        #   - maximum flow with Ford-Fulkerson
        #   - maximum flow with Edmond-Karps
        #   - maximum flow with Dinic
        #   - maximum flow with Linear programming
        #   - minimum-cost flow with Linear programming
        #   - minimum-cost flow with Klein (cycle-cancelling algorithm)
        
        # label frame for shortest path algorithms
        self.lf_flow = ttk.Labelframe(self, padding=(6, 6, 12, 12), 
                                            text='Flow algorithms')
        self.lf_flow.grid(row=1, column=2, columnspan=2, pady=5, padx=5, 
                                                                sticky='nsew')
                                                                
        self.flow_algorithms = OrderedDict([
        ("Ford-Fulkerson (MF)", self.ms.cs.ntw.ford_fulkerson),
        ("Edmond-Karps (MF)", self.ms.cs.ntw.edmonds_karp),
        ("Dinic (MF)", self.ms.cs.ntw.dinic),
        ("Linear programming (MF)", self.ms.cs.ntw.LP_MF_formulation),
        ("Linear programming (MCF)", self.ms.cs.ntw.LP_MCF_formulation),
        ("Klein (MCF)", lambda: "to be implemented")
        ])
        
        # List of flow path algorithms
        self.flow_list = ttk.Combobox(self, width=9)
        self.flow_list["values"] = tuple(self.flow_algorithms.keys())
        self.flow_list.current(0)
        self.flow_list.grid(in_=self.lf_flow, row=0, column=0,
                                columnspan=2, pady=5, padx=5, sticky="nsew")
        self.flow_list.bind('<<ComboboxSelected>>', self.readonly)
                                        
                                
        self.flow_src_label = ttk.Label(self, text="Source :")
        self.flow_src_entry = ttk.Entry(self)
        self.flow_src_label.grid(in_=self.lf_flow, row=1, column=0, pady=5, padx=5, sticky=tk.W)
        self.flow_src_entry.grid(in_=self.lf_flow, row=1, column=1, pady=5, padx=5, sticky=tk.W)
        
        self.flow_dest_label = ttk.Label(self, text="Destination :")
        self.flow_dest_entry = ttk.Entry(self)
        self.flow_dest_label.grid(in_=self.lf_flow, row=2, column=0, pady=5, padx=5, sticky=tk.W)
        self.flow_dest_entry.grid(in_=self.lf_flow, row=2, column=1, pady=5, padx=5, sticky=tk.W)
        
        self.max_flow_label = ttk.Label(self, text="Maximum flow :")
        self.max_flow_entry = ttk.Entry(self, state="readonly")
        self.max_flow_label.grid(in_=self.lf_flow, row=3, column=0, pady=5, padx=5, sticky=tk.W)
        self.max_flow_entry.grid(in_=self.lf_flow, row=3, column=1, pady=5, padx=5, sticky=tk.W,)
        
        self.bt_flow = ttk.Button(self, text="Compute flow", command=self.compute_flow)
        self.bt_flow.grid(in_=self.lf_flow, row=4, column=0, columnspan=2, pady=5, padx=5)
        
        ## Shortest pair section
        
        # shortest pair algorithms include:
        #   - shortest pair with A*
        #   - shortest pair with Bhandari
        #   - shortest pair with Suurbale
        #   - shortest pair with Linear programming

        # label frame for shortest pair algorithms
        self.lf_spair = ttk.Labelframe(self, padding=(6, 6, 12, 12), 
                                            text='Shortest path algorithms')
        self.lf_spair.grid(row=2, column=0, columnspan=2, pady=5, padx=5, 
                                                                sticky='nsew')

        self.spair_algorithms = OrderedDict([
        ("A* shortest pair algorithm", self.ms.cs.ntw.A_star_shortest_pair),
        ("Bhandari algorithm", self.ms.cs.ntw.bhandari),
        ("Suurbale algorithm", self.ms.cs.ntw.suurbale),
        ("Linear programming algorithm", lambda: "to repair")
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
        
        self.bt_spair = ttk.Button(self, text="Compute path", command=self.compute_spair)
        self.bt_spair.grid(in_=self.lf_spair, row=3, column=0, columnspan=2, pady=5, padx=5)

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
        
    def compute_flow(self):
        source = self.ms.cs.ntw.nf(name=self.flow_src_entry.get())
        destination = self.ms.cs.ntw.nf(name=self.flow_dest_entry.get())
        algorithm = self.flow_algorithms[self.flow_list.get()]
        if self.flow_list.get()[-4:-1] == "MCF":
            flow = self.ms.cs.ntw.nf(name=self.max_flow_entry.get())
            flow = algorithm(source, destination, flow)
        else:
            flow = algorithm(source, destination)   
        print(flow)
