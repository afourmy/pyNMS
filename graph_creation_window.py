import tkinter as tk

class AdvancedGraphOptionsWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__()
        self.geometry("600x300")
        self.title("Advanced graph options")
        
        # selection des paths par l'utilisateur
        self.button_create_hypercube = tk.Button(self, text='Create hypercube', command = lambda: self.add_nodes(master), width=12, height=1)
        self.button_create_square_tiling = tk.Button(self, text='Create square tiling', command = lambda: self.add_links(master), width=12, height=1)
        self.button_connected_components = tk.Button(self, text='Find connected components', command = lambda: self.master.current_scenario.connected_components(master), width=12, height=1)
        self.button_highlight_connected_components = tk.Button(self, text='Highlight connected components', command = lambda: self.highlight_connected_components(), width=12, height=1)
        
        # affichage des buttons / label dans la grille
        self.button_create_hypercube.grid(row=0,column=0, pady=5, padx=5, sticky=tk.W)
        self.button_create_square_tiling.grid(row=1,column=0, pady=5, padx=5, sticky=tk.W)
        self.button_connected_components.grid(row=9,column=0, pady=5, padx=5, sticky=tk.W)
        self.button_highlight_connected_components.grid(row=10,column=0, pady=5, padx=5, sticky=tk.W)
        
        self.withdraw()
        
    def highlight_connected_components(self, master):
        self.unhighlight()
        connected_components = master.current_scenario.connected_components()
        for idx, connex_set in enumerate(connected_components):
            for n in connex_set:
                for adjacent_node in master.current_scenario.graph[n]:
                    link = master.current_scenario.link_factory(n, adjacent_node, "trunk")
                    master.canvas.itemconfig(link.line, fill=self.default_colors[idx], width=self.LINK_WIDTH)