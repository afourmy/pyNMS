# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk
from tkinter import ttk, messagebox
from miscellaneous.custom_toplevel import CustomTopLevel, FocusTopLevel

class ObjectManagementWindow(FocusTopLevel):
    
    read_only = (
                 "source", 
                 "destination",
                 "path",
                 "flowSD",
                 "flowDS", 
                 "bgp_AS",
                 "AS"
                )
                
    property_fixed_list = {
    "interface": ("FE", "GE", "10GE", "40GE", "100GE")
    }
    
    property_var_list = {
    "default_route": (None,),
    "nh_tk": (None,),
    "nh_ip": (None,),
    "ipS": (None,),
    "ipD": (None,),
    "dst_sntw": (None,)
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
            if property in self.property_fixed_list:
                pvalue = ttk.Combobox(self, textvariable=str_var, width=12)
                pvalue["values"] = self.property_fixed_list[property]
                self.dict_var[property] = str_var
            elif property in self.property_var_list:
                pvalue = ttk.Combobox(self, textvariable=str_var, width=12)
                pvalue["values"] = self.property_var_list[property]
                self.dict_var[property] = (pvalue, str_var)                    
            else:
                s = "readonly" if property in self.read_only else tk.NORMAL
                pvalue = tk.Entry(self, textvariable=str_var, width=15, state=s)
                self.dict_var[property] = str_var
                
            pvalue.grid(row=index+1, pady=1, padx=5, column=1, sticky=tk.W)
            
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
        nodes, trunks = self.ms.cs.ntw.A_star(*parameters)
        
        if trunks:
            self.ms.cs.unhighlight_all()
            self.current_path = trunks
            self.dict_var["path"].set(trunks)
            self.ms.cs.highlight_objects(*(nodes + trunks))
        else:
            self.ms.cs.unhighlight_all()
            # activate focus to prevent the messagebox from removing the window
            self.var_focus.set(1)
            self.change_focus()
            messagebox.showinfo("Warning", "No path found")
        
    def save_obj(self):
        for property, str_var in self.dict_var.items():
            # retrieve the value
            if property in self.property_var_list:
                combobox, var = str_var
                value = var.get()
            else:
                value = str_var.get()
            # convert "None" to None if necessary
            value = None if value == "None" else value              
            if property == "path":
                setattr(self.current_obj, property, self.current_path)
            elif property in self.property_var_list:
                setattr(self.current_obj, property, value)
            else:
                if property not in self.read_only:
                    if property in ("path_constraints", "excluded_nodes", "excluded_trunks"): 
                        value = self.conv(property)
                    else:
                        value = self.ms.prop_to_type[property](value)
                        if property == "name":
                            name = getattr(self.current_obj, property)
                            id = self.ms.cs.ntw.name_to_id.pop(name)
                            self.ms.cs.ntw.name_to_id[value] = id
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
            if property == "default_route":
                combobox, var = str_var
                # in practice, the default route can also be set as an outgoing
                # interface, but the router has to do an ARP request for each
                # unknown destination IP address to fill the destination 
                # MAC field of the Ethernet frame, which may result in 
                # ARP table being overloaded: to be avoided in real-life and
                # forbidden here.
                attached_ints = (None,) + tuple(filter(None, 
                                    self.ms.cs.ntw.nh_ips(self.current_obj)))
                combobox["values"] = attached_ints
                var.set(obj_prop)
            elif property == "nh_tk":
                combobox, var = str_var
                src_route = self.current_obj.source
                attached_ints = tuple(filter(None, (trunk for _, trunk 
                                in self.ms.cs.ntw.graph[src_route]["trunk"])))
                combobox["values"] = attached_ints
                var.set(obj_prop)
            elif property == "dst_sntw":
                combobox, var = str_var
                dest_node = self.current_obj.destination
                attached_ips = (None,) + tuple(filter(None, 
                            (trunk.sntw for _, trunk
                            in self.ms.cs.ntw.graph[dest_node]["trunk"]
                            ))) 
                combobox["values"] = attached_ips
                var.set(obj_prop)
            elif property == "ipS":
                combobox, var = str_var
                src = self.current_obj.source
                attached_ips = (None,) + tuple(filter(None, 
                                    self.ms.cs.ntw.attached_ips(src)))
                combobox["values"] = attached_ips
                var.set(obj_prop)
            elif property == "nh_ip":
                combobox, var = str_var
                nh_ips = (None,) + tuple(filter(None, 
                                    self.ms.cs.ntw.nh_ips(self.current_obj)))
                combobox["values"] = nh_ips
                var.set(obj_prop)
            elif property == "ipD":
                combobox, var = str_var
                dest = self.current_obj.destination
                attached_ips = (None,) + tuple(filter(None, 
                                    self.ms.cs.ntw.attached_ips(dest)))
                combobox["values"] = attached_ips
                var.set(obj_prop)
            elif property == "AS":
                str_var.set(",".join(map(str, obj_prop.keys())))
            elif type(obj_prop) in (list, set):
                str_var.set(",".join(map(str, obj_prop)))
            else:
                str_var.set(obj_prop)
            # if there is a path, we set current_path in case the object is saved
            # without computing a new path
            if property == "path":
                self.current_path = self.current_obj.path
                
class PropertyChanger(FocusTopLevel):
                                    
    def __init__(self, master, objects, type):
        super().__init__()
        self.ms = master
        print(objects, type)
        
        # list of properties
        self.var_property = tk.StringVar()
        self.property_list = ttk.Combobox(self, 
                                    textvariable=self.var_property, width=6)
        self.property_list["values"] = self.ms.object_properties[type]
        self.property_list.current(0)
        self.property_list.bind('<<ComboboxSelected>>',
                                        lambda e: self.update_property())
        self.property_list.grid(row=0, column=0, pady=5, padx=5)
                            
        self.entry_prop = ttk.Entry(self, width=9)
        self.entry_prop.grid(row=1, column=0, pady=5, padx=5)
        
        self.button_OK = ttk.Button(self, text="OK", 
                                        command=lambda: self.confirm(objects))
        self.button_OK.grid(row=2, column=0,
                                        pady=5, padx=5, sticky="nsew")
        
        # update property with first value of the list
        self.update_property()
        
    def update_property(self):
        self.property = self.var_property.get()
        
    def confirm(self, objects):
        value = self.ms.prop_to_type[self.property](self.entry_prop.get())
        for object in objects:
            setattr(object, self.property, value)
        self.destroy()
        