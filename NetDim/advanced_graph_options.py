# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk
from tkinter import ttk
from miscellaneous import FocusTopLevel

class AdvancedGraphOptionsWindow(FocusTopLevel):
    def __init__(self, master):
        super().__init__()
        self.geometry("600x300")
        self.title("Advanced graph options")
        
        # Label for the name/type of the AS
        self.label_source = tk.Label(self, bg="#A1DBCD", text="Source")
        self.label_destination = tk.Label(self, bg="#A1DBCD", text="Destination")
        
        # Entry box for the name of the AS
        self.entry_source = tk.Entry(self, textvariable="", width=10)
        self.entry_destination = tk.Entry(self, textvariable="", width=10)
        
        # selection des paths par l'utilisateur
        self.button_create_hypercube = ttk.Button(self, text='Create hypercube', command = lambda: self.add_nodes(master))
        self.button_create_square_tiling = ttk.Button(self, text='Create square tiling', command = lambda: master.cs.ntw.generate_square_tiling(100, "router"))
        self.button_highlight_connected_components = ttk.Button(self, text='Highlight connected components', command = lambda: self.highlight_connected_components(master))
        self.button_LP = ttk.Button(self, text='LP', command = lambda: self.LP_SP(master))
        self.button_fulkerson = ttk.Button(self, text='Fulkerson', command = lambda: self.fulkerson(master))
        self.button_kruskal = ttk.Button(self, text='Minimum spanning tree', command = lambda: self.kruskal(master))
        
        # affichage des buttons / label dans la grille
        self.button_create_hypercube.grid(row=1,column=0, pady=5, padx=5, sticky=tk.W)
        self.button_create_square_tiling.grid(row=1,column=1, pady=5, padx=5, sticky=tk.W)
        self.button_highlight_connected_components.grid(row=2,column=3, pady=5, padx=5, sticky=tk.W)
        self.button_LP.grid(row=2,column=0, pady=5, padx=5, sticky=tk.W)
        self.button_fulkerson.grid(row=2,column=1, pady=5, padx=5, sticky=tk.W)
        self.button_kruskal.grid(row=5,column=1, pady=5, padx=5, sticky=tk.W)
        
        self.label_source.grid(row=3,column=0, pady=5, padx=5, sticky=tk.W)
        self.label_destination.grid(row=4,column=0, pady=5, padx=5, sticky=tk.W)
        self.entry_source.grid(row=3,column=1, pady=5, padx=5, sticky=tk.W)
        self.entry_destination.grid(row=4,column=1, pady=5, padx=5, sticky=tk.W)
        
        # hide the window when closed
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        self.withdraw()
        
    def highlight_connected_components(self, master):
        master.cs.unhighlight_all()
        for idx, connex_comp in enumerate(master.cs.ntw.connected_components()):
            for node in connex_comp:
                for adjacent_link in master.cs.ntw.graph[node]["trunk"]:
                    master.cs.itemconfig(adjacent_link.line, fill=master.cs.default_colors[idx])
                    
    def LP_SP(self, master):
        source = master.cs.ntw.nf(name=self.entry_source.get())
        destination = master.cs.ntw.nf(name=self.entry_destination.get())
        flow = master.cs.ntw.LP_SP_formulation(source, destination)
        print(flow)
        
    def fulkerson(self, master):
        source = master.cs.ntw.nf(name=self.entry_source.get())
        destination = master.cs.ntw.nf(name=self.entry_destination.get())
        flow = master.cs.ntw.edmonds_karp(source, destination)
        print(flow)
        
    def kruskal(self, master):
        links_mst = master.cs.ntw.kruskal(master.cs.ntw.pn["node"].values())
        master.cs.highlight_objects(*links_mst)
        
    # def generate_square_tiling(self, scenario):
    #     self.erase_graph(scenario)
    #     scenario.generate_meshed_square(self.var_dimension.get())
    #     
    # def generate_hypercube(self, scenario):
    #     self.erase_graph(scenario)
    #     scenario.generate_hypercube(self.var_dimension.get())
    #     
        
    # TODO K-shortest path with BFS
        # _, source, *e = self.get_user_input(master)
        # print(source)
        # for p in master.cs.ntw.all_paths(source):
        #     print(p)
        
    # TODO flow window
    # def flow(self, master):
    #     total_flow = master.cs.ntw.ford_fulkerson(master.cs.ntw.nf(self.entry_source_node.get()), master.cs.ntw.nf(self.entry_destination_node.get()))
    #     self.var_total_flow.set(str(total_flow))
        
        
                    