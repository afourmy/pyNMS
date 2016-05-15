import tkinter as tk

class PathFinding(tk.Toplevel):
    def __init__(self, master):
        super().__init__()
        self.geometry("220x400")
        self.title("Find the shortest path")
        
        # this allows to change the behavior of closing the window. 
        # I don't want the window to be destroyed, simply hidden
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        
        # chemin à highlighter
        # TODO virer path link car current route devrait suffir
        self.path_link = None
        self.current_route = None
        
        # Label for source, destination, excluded nodes/links and path constraints
        self.label_source_node = tk.Label(self, text = "Source node")
        self.label_destination_node = tk.Label(self, text = "Destination node")
        self.label_excluded_links = tk.Label(self, text = "Excluded links")
        self.label_excluded_nodes = tk.Label(self, text = "Excluded nodes")
        self.label_path_constraints = tk.Label(self, text = "Path constraints")
        self.label_route_name = tk.Label(self, text = "Route name")
        
        # Entry boxes and textvar for all parameters / constraints
        self.var_route_name = tk.StringVar()
        self.var_source_node = tk.StringVar()
        self.var_destination_node = tk.StringVar()
        self.var_excluded_links = tk.StringVar()
        self.var_excluded_nodes = tk.StringVar()
        self.var_path_constraints = tk.StringVar()
        
        # total flow label
        self.var_total_flow = tk.StringVar()
        self.label_total_flow = tk.Label(self, textvariable = self.var_total_flow)
        
        self.entry_source_node  = tk.Entry(self, text=self.var_source_node, width=15)
        self.entry_destination_node = tk.Entry(self, text=self.var_destination_node, width=15)
        self.entry_excluded_links = tk.Entry(self, text=self.var_excluded_links, width=15)
        self.entry_excluded_nodes = tk.Entry(self, text=self.var_excluded_nodes, width=15)
        self.entry_path_constraints = tk.Entry(self, text=self.var_path_constraints, width=15)
        self.entry_route_name = tk.Entry(self, text=self.var_route_name, width=15)
        
        self.button_compute_path = tk.Button(self, text='Compute path', command = lambda: self.find_path(master), width=12, height=1)
        self.button_highlight_path = tk.Button(self, text='Highlight path', command = lambda: master.current_scenario.highlight_objects(*self.path_link), width=12, height=1)
        self.button_unhighlight = tk.Button(self, text='Unhighlight', command = lambda: master.current_scenario.unhighlight_all(), width=12, height=1)
        self.button_reset = tk.Button(self, text='Reset fields', command = lambda: self.reset_fields(), width=12, height=1)
        self.button_create_route = tk.Button(self, text='Create route', command = lambda: self.create_route(master), width=12, height=1)
        self.button_flow = tk.Button(self, text='flow', command = lambda: self.flow(network), width=12, height=1)
        
        # List of routes
        self.var_route = tk.StringVar()
        self.choices = [route for route in master.current_scenario.pool_network["route"].values()] or [""]
        self.route_list = tk.OptionMenu(self, self.var_route, *self.choices if self.choices else [""])
        self.button_select_route = tk.Button(self, text="Select route", command=lambda: self.select_route())
        
        self.label_source_node.grid(row=0, column=0, pady=5, padx=5, sticky=tk.W)
        self.label_destination_node.grid(row=1, column=0, pady=5, padx=5, sticky=tk.W)
        self.label_excluded_links.grid(row=2, column=0, pady=5, padx=5, sticky=tk.W)
        self.label_excluded_nodes.grid(row=3, column=0, pady=5, padx=5, sticky=tk.W)
        self.label_path_constraints.grid(row=4, column=0, pady=5, padx=5, sticky=tk.W)
        self.label_route_name.grid(row=5, column=0, pady=5, padx=5, sticky=tk.W)
        
        self.entry_source_node.grid(row=0, column=1, sticky=tk.W)
        self.entry_destination_node.grid(row=1, column=1, sticky=tk.W)
        self.entry_excluded_links.grid(row=2, column=1, sticky=tk.W)
        self.entry_excluded_nodes.grid(row=3, column=1, sticky=tk.W)
        self.entry_path_constraints.grid(row=4, column=1, sticky=tk.W)
        self.entry_route_name.grid(row=5, column=1, sticky=tk.W)
        
        self.button_compute_path.grid(row=6,column=0, pady=5, padx=5, sticky=tk.W)
        self.button_highlight_path.grid(row=6,column=1, pady=5, padx=5, sticky=tk.W)
        self.button_unhighlight.grid(row=7,column=0, pady=5, padx=5, sticky=tk.W)
        self.button_reset.grid(row=7,column=1, pady=5, padx=5, sticky=tk.W)
        
        self.button_create_route.grid(row=10,column=0, pady=5, padx=5, sticky=tk.W)
        self.route_list.grid(row=10, column=1, sticky=tk.W)
        
        self.button_select_route.grid(row=11, column=0, sticky=tk.W)
        self.button_flow.grid(row=11, column=1, sticky=tk.W)
        self.label_total_flow.grid(row=12, column=0, sticky=tk.W)
        
        self.withdraw()
        
    def select_route(self):
        if(self.current_route):
            self.var_route_name.set(self.current_route.name)
            self.var_source_node.set(self.current_route.source)
            self.var_destination_node.set(self.current_route.destination)
            self.var_excluded_links.set(",".join(map(str,self.current_route.excluded_trunks)))
            self.var_excluded_nodes.set(",".join(map(str,self.current_route.excluded_nodes)))
            self.var_path_constraints.set(",".join(map(str,self.current_route.path_constraints)))
    
    def reset_fields(self):
        self.var_route_name.set("")
        self.var_source_node.set("")
        self.var_destination_node.set("")
        self.var_excluded_links.set("")
        self.var_excluded_nodes.set("")
        self.var_path_constraints.set("")
    
    def get_user_input(self, master):
        name = self.var_route_name.get()
        source = master.current_scenario.node_factory(self.entry_source_node.get())
        destination = master.current_scenario.node_factory(self.entry_destination_node.get())
        excluded_links = filter(None, self.entry_excluded_links.get().split(","))
        excluded_nodes = filter(None, self.entry_excluded_nodes.get().split(","))
        path_constraints = filter(None, self.entry_path_constraints.get().split(","))
        if(excluded_links):
            l_excluded_links = [master.current_scenario.link_factory(name=t) for t in excluded_links]
        if(excluded_nodes):
            l_excluded_nodes = [master.current_scenario.node_factory(n) for n in excluded_nodes]
        if(path_constraints):
            l_path_constraints = [master.current_scenario.node_factory(n) for n in path_constraints]
        return (name, source, destination, l_excluded_links, l_excluded_nodes, l_path_constraints)
    
    # TODO K-shortest path with BFS
    def find_path(self, master):
        # name, *parameters = self.get_user_input(master)
        # path_node, self.path_link = master.current_scenario.hop_count(*parameters)
        # if(not path_node):
        #     print("no path found")
        _, source, *e = self.get_user_input(master)
        print(source)
        for p in master.current_scenario.all_paths(source):
            print(p)
            
        
    def create_route(self, master):
        name, *parameters = self.get_user_input(network)
        new_route = master.current_scenario.link_factory("route", name, *parameters)
        master.create_link(new_route)
        path_nodes, path_links = master.current_scenario.hop_count(*parameters)
        new_route.path = path_links
        self.route_list["menu"].add_command(label=new_route, command=tk._setit(self.var_route, new_route.name))
            
    def flow(self, master):
        total_flow = master.current_scenario.ford_fulkerson(master.current_scenario.node_factory(self.entry_source_node.get()), master.current_scenario.node_factory(self.entry_destination_node.get()))
        self.var_total_flow.set(str(total_flow))
