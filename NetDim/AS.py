# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk
from tkinter import ttk
from miscellaneous import CustomTopLevel
from collections import defaultdict
import area
import AS_management

class AutonomousSystem(object):
    class_type = "AS"

    def __init__(self, scenario, type, name, trunks=set(), nodes=set(), edges=set(), imp=False):
        self.name = name
        self.type = type
        # pAS as in "pool AS": same as pool network
        self.pAS = {"trunk": trunks, "node": nodes, "edge": edges}
        # areas is a dict associating a name to an area
        self.areas = {}
        # routes is a dict of dict such that routes[eA][eB] returns the route
        # object going from edge A (source) to edge B (destination).
        self.routes = defaultdict(dict)
        for obj in nodes | trunks:
            obj.AS[self] = set()
        # management window of the AS 
        self.management = AS_management.ASManagement(scenario, self, imp)
        # imp tells us if the AS is imported or created from scratch.
        if not imp:
            self.area_factory("Backbone")
            
        # each type of algorithm will have a specific algorithm, that defines
        # how to compute a path in the AS
        self.AS_type_to_class = {
        "RIP": scenario.ntw.RIP_routing,
        "ISIS": scenario.ntw.ISIS_routing
        }
        self.algorithm = self.AS_type_to_class[type]
        
    def __repr__(self):
        return self.name
        
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name
        
    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __hash__(self):
        return hash(self.name)
        
    def area_factory(self, name, trunks=set(), nodes=set()):
        if name not in self.areas:
            self.areas[name] = area.Area(name, self, trunks, nodes)
        return self.areas[name]
        
    def add_to_AS(self, area, *objects):
        area.add_to_area(*objects)
        for obj in objects:
            # add objects in the AS corresponding pool
            self.pAS[obj.network_type].add(obj)
        
    def remove_from_AS(self, *objects):
        for obj in objects:
            # we remove the object from its pool in the AS
            self.pAS[obj.network_type].discard(obj)
            # we pop the AS from the dict of object AS, and retrieve the list
            # of area it belongs to in this AS
            obj_areas = obj.AS.pop(self, set())
            # for each area, we delete the object from the corresponding pool
            for area in obj_areas:
                area.remove_from_area(obj)
            # we also try to remove it from edge if it was a node
            self.pAS["edge"].discard(obj)
        
    def add_to_edges(self, node):
        self.pAS["edge"].add(node)
        
    def remove_from_edges(self, node):
        self.pAS["edge"].discard(node)
                    
class ModifyAS(CustomTopLevel):
    def __init__(self, scenario, mode, obj, AS=set()):
        super().__init__()
        self.geometry("30x90")
        # TODO put that in the dict
        titles = {
        "add": "Add to AS/area", 
        "remove": "Remove from AS", 
        "remove area": "Remove from area",
        "manage": "Manage AS"
        }
        self.title(titles[mode])
        # always at least one row and one column with a weight > 0
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # TODO make it a dict
        if mode == "add":
            command = lambda: self.add(scenario, *obj)
            values = tuple(map(str, scenario.ntw.pn["AS"].values()))
        elif mode == "remove":
            values = tuple(map(str, AS))
            command = lambda: self.remove_from_AS(scenario, *obj)
        elif mode == "remove area":
            values = tuple(map(str, AS))
            command = lambda: self.remove_from_area(scenario, *obj)
        elif mode == "manage":
            values = tuple(map(str, AS))
            command = lambda: self.manage_AS(scenario)
        
        # List of existing AS
        self.AS_list = ttk.Combobox(self, width=9)
        self.AS_list["values"] = values
        self.AS_list.current(0)
        self.AS_list.grid(row=0, column=0, columnspan=2, pady=5, padx=5, sticky="nsew")
        self.AS_list.bind('<<ComboboxSelected>>', lambda e: self.update_value(scenario))
        
        if mode in ("add", "remove area"):
            self.area_list = ttk.Combobox(self, width=9)
            self.update_value(scenario)
            self.area_list.current(0)
            self.area_list.grid(row=1, column=0, columnspan=2, pady=5, padx=5, sticky="nsew")
        
        # Button to add in an AS
        self.button_add_AS = ttk.Button(self, text="OK", command=command)
        #row = 2 if mode in ("add", "remove area") else 1
        self.button_add_AS.grid(row=2, column=0, columnspan=2, pady=5, padx=5, sticky="nsew")
        
    # when a different AS is selected, the area combobox is updated accordingly
    def update_value(self, scenario):
        selected_AS = scenario.ntw.AS_factory(name=self.AS_list.get())
        self.area_list["values"] = tuple(map(str, selected_AS.areas))
        
    # TODO merge these three functions into one with the mode 
    # they share the check + destroy
    def add(self, scenario, *objects):
        selected_AS = scenario.ntw.AS_factory(name=self.AS_list.get())
        selected_AS.management.add_to_AS(self.area_list.get(), *objects)
        self.destroy()
        
    def remove_from_area(self, scenario, *objects):
        selected_AS = scenario.ntw.AS_factory(name=self.AS_list.get())
        selected_AS.management.remove_from_area(self.area_list.get(), *objects)
        self.destroy()
        
    def remove_from_AS(self, scenario, *objects):
        selected_AS = scenario.ntw.AS_factory(name=self.AS_list.get())
        selected_AS.management.remove_from_AS(*objects)
        self.destroy()
        
    def manage_AS(self, scenario):
        selected_AS = scenario.ntw.AS_factory(name=self.AS_list.get())
        selected_AS.management.deiconify()
        self.destroy()
        
class ASCreation(CustomTopLevel):
    def __init__(self, scenario, so):
        super().__init__()
        self.geometry("120x100")
        self.title("Create AS")
        
        # List of AS type
        self.var_AS_type = tk.StringVar()
        self.AS_type_list = ttk.Combobox(self, textvariable=self.var_AS_type, width=6)
        self.AS_type_list["values"] = ("RIP", "IS-IS", "OSPF", "MPLS", "RSTP")
        self.AS_type_list.current(0)

        # retrieve and save node data
        self.button_create_AS = ttk.Button(self, text="Create AS", command=lambda: self.create_AS(scenario, so))
        
        # Label for the name/type of the AS
        self.label_name = tk.Label(self, bg="#A1DBCD", text="Name")
        self.label_type = tk.Label(self, bg="#A1DBCD", text="Type")
        
        # Entry box for the name of the AS
        self.var_name = tk.StringVar()
        self.entry_name  = tk.Entry(self, textvariable=self.var_name, width=10)
        
        self.label_name.grid(row=0, column=0, pady=5, padx=5, sticky=tk.W)
        self.entry_name.grid(row=0, column=1, sticky=tk.W)
        self.label_type.grid(row=1, column=0, pady=5, padx=5, sticky=tk.W)
        self.AS_type_list.grid(row=1,column=1, pady=5, padx=5, sticky=tk.W)
        self.button_create_AS.grid(row=3,column=0, columnspan=2, pady=5, padx=5)

    def create_AS(self, scenario, so):
        new_AS = scenario.ntw.AS_factory(name=self.var_name.get(), type=self.var_AS_type.get(), trunks=so["link"], nodes=so["node"])
        self.destroy()
            