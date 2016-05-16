import tkinter as tk

class GraphCreation(tk.Toplevel):
    def __init__(self, master):
        super().__init__()
        self.geometry("600x300")
        self.title("Create or modify the graph")

        # entry to define the graph
        self.var_add_nodes = tk.StringVar()
        self.entry_add_nodes = tk.Entry(self, textvariable=self.var_add_nodes, width=80)
        self.var_add_links = tk.StringVar()
        self.entry_add_links = tk.Entry(self, textvariable=self.var_add_links, width=80)
        self.var_fast_creation = tk.StringVar()
        self.entry_fast_creation = tk.Entry(self, textvariable=self.var_fast_creation, width=80)
        
        # selection des paths par l'utilisateur
        self.bouton_add_nodes = tk.Button(self, text='Add nodes', command = lambda: self.add_nodes(master), width=12, height=1)
        self.bouton_add_links = tk.Button(self, text='Add links', command = lambda: self.add_links(master), width=12, height=1)
        self.bouton_fast_creation = tk.Button(self, text='Fast creation', command = lambda: self.automatic_graph_creation(master), width=12, height=1)
        self.bouton_connex = tk.Button(self, text='Find connected components', command = lambda: self.master.current_scenario.connected_components(master), width=12, height=1)
        self.bouton_highlight_connected_components = tk.Button(self, text='Highlight connected components', command = lambda: self.highlight_connected_components(), width=12, height=1)
        
        # affichage des boutons / label dans la grille
        self.bouton_add_nodes.grid(row=0,column=0, pady=5, padx=5, sticky=tk.W)
        self.bouton_add_links.grid(row=1,column=0, pady=5, padx=5, sticky=tk.W)
        self.bouton_fast_creation.grid(row=2,column=0, pady=5, padx=5, sticky=tk.W)
        self.entry_add_nodes.grid(row=0, column=1, sticky=tk.W)
        self.entry_add_links.grid(row=1, column=1, sticky=tk.W)
        self.entry_fast_creation.grid(row=2, column=1, sticky=tk.W)
        self.bouton_connex.grid(row=9,column=0, pady=5, padx=5, sticky=tk.W)
        self.bouton_highlight_connected_components.grid(row=10,column=0, pady=5, padx=5, sticky=tk.W)
        
        self.withdraw()
            
    def add_nodes(self, master):
        user_input = self.entry_add_nodes.get().replace(" ","")
        for s in user_input.split(","):
            master.current_scenario.node_factory(s)
        
    def add_links(self, master):
        user_input = self.entry_add_links.get().replace(" ","")
        for s in user_input.split(","):
            source, destination = s.split(".")
        master.current_scenario.link_factory(master.current_scenario.node_factory(source), master.current_scenario.node_factory(destination), "trunk")
        
    def automatic_graph_creation(self, master):
        user_input = self.entry_fast_creation.get().replace(" ","")
        master.current_scenario.fast_graph_definition(user_input)
        
    def highlight_connected_components(self, master):
        self.unhighlight()
        connected_components = master.current_scenario.connected_components()
        for idx, connex_set in enumerate(connected_components):
            for n in connex_set:
                for adjacent_node in master.current_scenario.graph[n]:
                    link = master.current_scenario.link_factory(n, adjacent_node, "trunk")
                    master.canvas.itemconfig(link.line, fill=self.default_colors[idx], width=self.LINK_WIDTH)