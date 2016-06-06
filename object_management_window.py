import tkinter as tk
from tkinter import ttk, messagebox
from miscellaneous import CustomTopLevel

# http://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter
# TODO: only one window containing all 5 frames
class ObjectManagementWindow(CustomTopLevel):
    def __init__(self, master, type):
        super().__init__()
        n = len(master.object_properties[type])
        size_per_type = {"router": "180x220", "oxc": "180x220", "host":"180x220", "antenna":"180x220",
        "regenerator": "180x220", "splitter": "180x220", "trunk": "190x360", "route": "220x370", "traffic": "250x300"}
        
        self.geometry(size_per_type[type])
        self.title("Manage {} properties".format(type))

        # current node which properties are displayed
        self.current_obj = None
        # current path of the object: computing a path is not saving it
        self.current_path = None

        # create the property window
        self.dict_var = {}
        for index, property in enumerate(master.object_properties[type]):
            str_var = tk.StringVar()
            self.dict_var[property] = str_var
            label = tk.Label(self, text=property.title(), bg="#A1DBCD")
            label.grid(row=index+1, pady=5, padx=5, column=0, sticky=tk.W)
            s = "readonly" if property in ("source","destination","path","flowSD","flowDS", "AS") else tk.NORMAL
            entry = tk.Entry(self, textvariable=str_var, width=15, state=s)
            entry.grid(row=index+1, pady=5, padx=5, column=1, sticky=tk.W)
    
        # route finding possibilities for a route 
        if(type == "route"):
            self.button_compute_path = ttk.Button(self, text="Compute path", command=lambda: self.find_path(master))
            self.button_compute_path.grid(row=n+1, column=0, columnspan=2, pady=5, padx=5)
        
        self.button_save_obj = ttk.Button(self, text="Save", command=lambda: self.save_obj(master))
        self.button_save_obj.grid(row=0,column=1, columnspan=2, pady=5, padx=5)
    
    def get_user_input(self, master):
        name = self.dict_var["name"].get()
        source = master.cs.ntw.nf(name=self.dict_var["source"].get())
        destination = master.cs.ntw.nf(name=self.dict_var["destination"].get())
        excluded_trunks = filter(None, self.dict_var["excluded_trunks"].get().strip().split(","))
        excluded_nodes = filter(None, self.dict_var["excluded_nodes"].get().strip().split(","))
        path_constraints = filter(None, self.dict_var["path_constraints"].get().strip().split(","))
        if(excluded_trunks):
            l_excluded_trunks = {master.cs.ntw.lf(name=t) for t in excluded_trunks}
        if(excluded_nodes):
            l_excluded_nodes = {master.cs.ntw.nf(name=n) for n in excluded_nodes}
        if(path_constraints):
            l_path_constraints = [master.cs.ntw.nf(name=n) for n in path_constraints]
        return (name, source, destination, l_excluded_trunks, l_excluded_nodes, l_path_constraints)
        
    def find_path(self, master):
        name, *parameters = self.get_user_input(master)
        route_path_nodes, route_path_links = master.cs.ntw.dijkstra(*parameters)
        
        # name, source, target, *e = self.get_user_input(master)
        # route_path_nodes, route_path_links = master.cs.ntw.bellman_ford(source, target)
        
        # _, source, *e = self.get_user_input(master)
        # print(source)
        # for p in master.cs.ntw.all_paths(source):
        #     print(p)
        
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
        
    def save_obj(self, master):
        for property, str_var in self.dict_var.items():
            # update dict when the object is renamed
            # if it is a node, we need to remove and readd the entry in the graph dict
            # for all objects, we need to update pn
            if(property == "name"):
                name = getattr(self.current_obj, property)
                if(name != str_var.get()):
                    if(self.current_obj.network_type == "node"):
                        adj_links = master.cs.ntw.graph.pop(self.current_obj, None)
                    old_name = name
                    del master.cs.ntw.pn[self.current_obj.network_type][old_name]
                    setattr(self.current_obj, property, str_var.get())
                    master.cs.ntw.pn[self.current_obj.network_type][str_var.get()] = self.current_obj
                    if(self.current_obj.network_type == "node"):
                        master.cs.ntw.graph[self.current_obj] = adj_links
            elif(property == "path"):
                setattr(self.current_obj, property, self.current_path)
            else:
                if(property not in ("source", "destination", "AS")):
                    setattr(self.current_obj, property, eval(str_var.get()))
            # refresh the label if it was changed
            master.cs._refresh_object_label(self.current_obj)
            # move the node on the canvas in case it's coordinates were updated
            if(self.current_obj.class_type == "node"):
                self.master.cs.move_node(self.current_obj)
            
    def update(self):
        for property, str_var in self.dict_var.items():
            obj_prop = getattr(self.current_obj, property)
            if(type(obj_prop) == list):
                str_var.set(",".join(map(str, obj_prop)))
            else:
                str_var.set(obj_prop)
            # if there is a path, we set current_path in case the object is saved
            # without computing a new path
            if(property == "path"):
                self.current_path = self.current_obj.path
