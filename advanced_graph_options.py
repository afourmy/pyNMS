import tkinter as tk
from tkinter import ttk

class AdvancedGraphOptionsWindow(tk.Toplevel):
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
        self.button_create_square_tiling = ttk.Button(self, text='Create square tiling', command = lambda: self.add_links(master))
        self.button_highlight_connected_components = ttk.Button(self, text='Highlight connected components', command = lambda: self.highlight_connected_components(master))
        self.button_maximum_flow = ttk.Button(self, text='Maximum flow', command = lambda: self.maximum_flow(master))
        
        # affichage des buttons / label dans la grille
        self.button_create_hypercube.grid(row=0,column=0, pady=5, padx=5, sticky=tk.W)
        self.button_create_square_tiling.grid(row=0,column=1, pady=5, padx=5, sticky=tk.W)
        self.button_highlight_connected_components.grid(row=1,column=1, pady=5, padx=5, sticky=tk.W)
        self.button_maximum_flow.grid(row=1,column=1, pady=5, padx=5, sticky=tk.W)
        
        self.label_source.grid(row=3,column=0, pady=5, padx=5, sticky=tk.W)
        self.label_destination.grid(row=4,column=0, pady=5, padx=5, sticky=tk.W)
        self.entry_source.grid(row=3,column=1, pady=5, padx=5, sticky=tk.W)
        self.entry_destination.grid(row=4,column=1, pady=5, padx=5, sticky=tk.W)
        
        self.withdraw()
        
    def highlight_connected_components(self, master):
        master.cs.unhighlight_all()
        for idx, connex_comp in enumerate(master.cs.connected_components()):
            for node in connex_comp:
                for adjacent_link in master.cs.graph[node]["trunk"]:
                    master.cs.itemconfig(adjacent_link.line, fill=master.cs.default_colors[idx])
                    
    def maximum_flow(self, master):
        source = master.cs.node_factory(name=self.entry_source.get())
        destination = master.cs.node_factory(name=self.entry_destination.get())
        flow = master.cs.edmonds_karp(source, destination)
        print(flow)
        
        
    # TODO K-shortest path with BFS
        # _, source, *e = self.get_user_input(master)
        # print(source)
        # for p in master.cs.all_paths(source):
        #     print(p)
        
    # TODO flow window
    # def flow(self, master):
    #     total_flow = master.cs.ford_fulkerson(master.cs.node_factory(self.entry_source_node.get()), master.cs.node_factory(self.entry_destination_node.get()))
    #     self.var_total_flow.set(str(total_flow))
        
        
                    