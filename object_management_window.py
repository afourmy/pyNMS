import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# http://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter
# TODO: only one window containing all 5 frames
class ObjectManagementWindow(tk.Toplevel):
    def __init__(self, master, type):
        super().__init__()
        n = len(master.object_properties[type])
        size_per_type = {"router": "180x200", "oxc": "180x200", "host":"180x200", "antenna":"180x200",
        "trunk": "190x260", "route": "220x350", "traffic": "250x300"}
        
        self.geometry(size_per_type[type])
        self.title("Manage {} properties".format(type))
        self.configure(background="#A1DBCD")
        # hide the window when closed
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        
        # current node which properties are displayed
        self.current_obj = None
        # current path of the object: computing a path is not saving it
        self.current_path = None
        
        # button for focus
        self.var_focus = tk.IntVar()
        self.checkbutton_focus = tk.Checkbutton(self, text="Focus", bg="#A1DBCD", variable=self.var_focus, command=self.change_focus)
        self.checkbutton_focus.grid(row=0, column=0, pady=5, padx=5, sticky=tk.W)
        
        # create the property window
        self.dict_var = {}
        for index, property in enumerate(master.object_properties[type]):
            str_var = tk.StringVar()
            self.dict_var[property] = str_var
            tk.Label(self, text=property.title(), bg="#A1DBCD").grid(row=index+1, pady=5, padx=5, column=0, sticky=tk.W)
            tk.Entry(self, textvariable=str_var, width=15, state="readonly" if property in ("source", "destination", "path") else tk.NORMAL).grid(row=index+1, pady=5, padx=5, column=1, sticky=tk.W)
        
        
        # route finding possibilities for a route 
        if(type == "route"):
            self.button_compute_path = ttk.Button(self, text="Compute path", command=lambda: self.find_path(master))
            self.button_compute_path.grid(row=n+1, column=0, columnspan=2, pady=5, padx=5)
        
        self.button_save_obj = ttk.Button(self, text="Save", command=lambda: self.save_obj(master))
        self.button_save_obj.grid(row=0,column=1, columnspan=2, pady=5, padx=5)
        ttk.Style().configure("TButton", background="#A1DBCD")
        self.withdraw()
    
    def get_user_input(self, master):
        name = self.dict_var["name"].get()
        source = master.cs.node_factory(self.dict_var["source"].get())
        destination = master.cs.node_factory(self.dict_var["destination"].get())
        excluded_trunks = filter(None, self.dict_var["excluded_trunks"].get().strip().split(","))
        excluded_nodes = filter(None, self.dict_var["excluded_nodes"].get().strip().split(","))
        path_constraints = filter(None, self.dict_var["path_constraints"].get().strip().split(","))
        if(excluded_trunks):
            l_excluded_trunks = [master.cs.link_factory(name=t) for t in excluded_trunks]
        if(excluded_nodes):
            l_excluded_nodes = [master.cs.node_factory(n) for n in excluded_nodes]
        if(path_constraints):
            l_path_constraints = [master.cs.node_factory(n) for n in path_constraints]
        return (name, source, destination, l_excluded_trunks, l_excluded_nodes, l_path_constraints)
        
    def find_path(self, master):
        name, *parameters = self.get_user_input(master)
        route_path_nodes, route_path_links = master.cs.hop_count(*parameters)
        if(route_path_links):
            master.cs.unhighlight_all()
            self.current_path = route_path_links
            self.dict_var["path"].set(route_path_links)
            master.cs.highlight_objects(*route_path_links)
        else:
            master.cs.unhighlight_all()
            # activate focus to prevent the messagebox from removing the window
            self.var_focus.set(1)
            self.change_focus()
            messagebox.showinfo("Warning", "No path found")
            
    # TODO K-shortest path with BFS
        # _, source, *e = self.get_user_input(master)
        # print(source)
        # for p in master.cs.all_paths(source):
        #     print(p)
        
    # TODO flow window
    # def flow(self, master):
    #     total_flow = master.cs.ford_fulkerson(master.cs.node_factory(self.entry_source_node.get()), master.cs.node_factory(self.entry_destination_node.get()))
    #     self.var_total_flow.set(str(total_flow))
        
    def change_focus(self):
        self.wm_attributes("-topmost", self.var_focus.get())
        
    def save_obj(self, master):
        for property, str_var in self.dict_var.items():
            # update dict when the object is renamed
            # if it is a node, we need to remove and readd the entry in the graph dict
            # for all objects, we need to update pn
            if(property == "name" and self.current_obj.__dict__[property] != str_var.get()):
                if(self.current_obj.network_type == "node"):
                    adj_links = master.cs.graph.pop(self.current_obj, None)
                old_name = self.current_obj.__dict__[property]
                del master.cs.pn[self.current_obj.network_type][old_name]
                self.current_obj.__dict__[property] = str_var.get()
                master.cs.pn[self.current_obj.network_type][str_var.get()] = self.current_obj
                if(self.current_obj.network_type == "node"):
                    master.cs.graph[self.current_obj] = adj_links
            if(property == "path"):
                self.current_obj.__dict__[property] = self.current_path
            elif(property in ("capacity", "cost", "flow")):
                self.current_obj.__dict__[property] = eval(str_var.get())
            # refresh the label if it was changed
            master.cs._refresh_object_label(self.current_obj)
            # move the node on the canvas in case it's coordinates were updated
            if(self.current_obj.class_type == "node"):
                self.master.cs.move_node(self.current_obj)
            
    def update(self):
        for property, str_var in self.dict_var.items():
            if(type(self.current_obj.__dict__[property]) == list):
                str_var.set(",".join(map(str,self.current_obj.__dict__[property])))
            else:
                str_var.set(self.current_obj.__dict__[property])
            # if there is a path, we set current_path in case the object is saved
            # without computing a new path
            if(property == "path"):
                self.current_path = self.current_obj.path
