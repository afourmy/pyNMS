# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk
from tkinter import ttk, messagebox
from miscellaneous import FocusTopLevel

# http://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter
# TODO: only one window containing all 5 frames
class ObjectManagementWindow(FocusTopLevel):
    
    read_only = (
                 "source", 
                 "destination",
                 "path",
                 "flowSD",
                 "flowDS", 
                 "AS"
                )
                
    property_list = {
    "interface": ("FE", "GE", "10GE", "40GE", "100GE")
    }
                
    def __init__(self, master, type):
        super().__init__()
        self.ms = master
        n = len(self.ms.object_properties[type])
        self.title("Manage {} properties".format(type))

        # current node which properties are displayed
        self.current_obj = None
        # current path of the object: computing a path is not saving it
        self.current_path = None

        # create the property window
        self.dict_var = {}
        for index, property in enumerate(self.ms.object_properties[type]):
            
            # creation of the label associated to the property
            text = self.ms.prop_to_nice_name[property]
            label = tk.Label(self, text=text, bg="#A1DBCD")
            label.grid(row=index+1, pady=1, padx=5, column=0, sticky=tk.W)
            str_var = tk.StringVar()
            
            # value of the property: drop-down list or entry
            if property in self.property_list:
                pvalue = ttk.Combobox(self, textvariable=str_var, width=12)
                pvalue["values"] = self.property_list[property]
            else:
                s = "readonly" if property in self.read_only else tk.NORMAL
                pvalue = tk.Entry(self, textvariable=str_var, width=15, state=s)
                
            pvalue.grid(row=index+1, pady=1, padx=5, column=1, sticky=tk.W)
            self.dict_var[property] = str_var
    
        # route finding possibilities for a route 
        if type == "route":
            self.button_compute_path = ttk.Button(self, text="Compute path", 
                                    command=lambda: self.find_path())
            self.button_compute_path.grid(row=n+1, column=0, columnspan=2, 
                                                                pady=5, padx=5)
                                                                
        self.button_save_obj = ttk.Button(self, text="Save", 
                                    command=lambda: self.save_obj())
        self.button_save_obj.grid(row=0,column=1, columnspan=2, pady=5, padx=5)
        
        # when the window is closed, save all parameters (in case the user
        # made a change), then withdraw the window.
        self.protocol("WM_DELETE_WINDOW", lambda: self.save_and_withdraw())
        self.withdraw()
        
    # this function converts the user-defined constraints to python objects.
    # it is used both when reading the user inputs, and when saving the 
    # route properties.
    def conv(self, property):
        value = self.dict_var[property].get().replace(" ","").split(",")
        if property == "excluded_trunks":
            return {self.ms.cs.ntw.lf(name=t) for t in filter(None, value)}
        elif property == "excluded_nodes":
            return {self.ms.cs.ntw.nf(name=n) for n in filter(None, value)}
        else:
            return [self.ms.cs.ntw.nf(name=n) for n in filter(None, value)]
    
    def get_user_input(self):
        name = self.dict_var["name"].get()
        source = self.ms.cs.ntw.nf(name=self.dict_var["source"].get())
        destination = self.ms.cs.ntw.nf(name=self.dict_var["destination"].get())
        return (
                name, 
                source, 
                destination, 
                self.conv("excluded_trunks"), 
                self.conv("excluded_nodes"), 
                self.conv("path_constraints")
                )
        
    def find_path(self):
        name, *parameters = self.get_user_input()
        route_path_nodes, route_path_links = self.ms.cs.ntw.A_star(*parameters)
        
        if route_path_links:
            self.ms.cs.unhighlight_all()
            self.current_path = route_path_links
            self.dict_var["path"].set(route_path_links)
            self.ms.cs.highlight_objects(*route_path_links)
        else:
            self.ms.cs.unhighlight_all()
            # activate focus to prevent the messagebox from removing the window
            self.var_focus.set(1)
            self.change_focus()
            messagebox.showinfo("Warning", "No path found")
        
    def save_obj(self):
        for property, str_var in self.dict_var.items():
            # update dict when the object is renamed
            # if it is a node, we need to remove and read the entry in the graph dict
            # for all objects, we need to update pn
            if property == "name":
                name = getattr(self.current_obj, property)
                if name != str_var.get():
                    if self.current_obj.type == "node":
                        adj_links = self.ms.cs.ntw.graph.pop(self.current_obj, None)
                    old_name = name
                    del self.ms.cs.ntw.pn[self.current_obj.type][old_name]
                    setattr(self.current_obj, property, str_var.get())
                    self.ms.cs.ntw.pn[self.current_obj.type][str_var.get()] = self.current_obj
                    if self.current_obj.type == "node":
                        self.ms.cs.ntw.graph[self.current_obj] = adj_links
            elif property == "path":
                setattr(self.current_obj, property, self.current_path)
            else:
                if property not in self.read_only:
                    if property in ("path_constraints", "excluded_nodes", "excluded_trunks"): 
                        value = self.conv(property)
                    else:
                        value = self.ms.prop_to_type[property](str_var.get())
                    setattr(self.current_obj, property, value)
            # refresh the label if it was changed
            self.ms.cs.refresh_label(self.current_obj)
            # move the node on the canvas in case it's coordinates were updated
            if self.current_obj.class_type == "node":
                self.ms.cs.move_node(self.current_obj)
                
    def save_and_withdraw(self):
        self.save_obj()
        self.withdraw()
            
    def update(self):
        for property, str_var in self.dict_var.items():
            obj_prop = getattr(self.current_obj, property)
            if type(obj_prop) in (list, set):
                str_var.set(",".join(map(str, obj_prop)))
            else:
                str_var.set(obj_prop)
            # if there is a path, we set current_path in case the object is saved
            # without computing a new path
            if property == "path":
                self.current_path = self.current_obj.path
