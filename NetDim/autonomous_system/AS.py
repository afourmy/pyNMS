# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk
from tkinter import ttk
from miscellaneous.custom_toplevel import CustomTopLevel
from collections import defaultdict
from . import area
from . import AS_management

class AutonomousSystem(object):
    
    class_type = "AS"

    def __init__(
                 self, 
                 scenario,
                 type, 
                 name, 
                 id,
                 trunks = set(), 
                 nodes = set(), 
                 edges = set(), 
                 routes = set(), 
                 imp = False
                 ):
        self.name = name
        self.type = type
        self.id = id

        # pAS as in "pool AS": same as pool network
        self.pAS = {
        "trunk": set(trunks), 
        "node": set(nodes), 
        "edge": set(edges)
        }
        
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
            id = 2 if type == "ISIS" else 0
            self.area_factory("Backbone", id=id, trunks=trunks, nodes=nodes)
            
        # the metric used to compute the shortest path. By default, it is 
        # a hop count for a RIP AS, and bandwidth-dependent for ISIS or OSPF.
        # if the metric is bandwidth, it is calculated based on the interface
        # of the trunk, and a user-defined reference bandwidth.
        self.metric = {
        "RIP": "hop count",
        "ISIS": "bandwidth",
        "OSPF": "bandwidth",
        "BGP": None
        }[type]
        self.ref_bw = 10**8
        
        # for an IS-IS domain, this set contains all L1/L2 nodes.
        # for an OSPF domain, it contains all ABRs (Area Border Router)
        # else it shouldn't be used.
        self.border_routers = set()
        
        # node used to exit the domain (ASBR for OSPF)
        self.exit_point = None
        
        # unselect everything
        scenario.unhighlight_all()
        
    def __repr__(self):
        return self.name
        
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name
        
    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __hash__(self):
        return hash(self.name)
        
    def area_factory(self, name, id=0, trunks=set(), nodes=set()):
        if name not in self.areas:
            self.areas[name] = area.Area(name, id, self, trunks, nodes)
        return self.areas[name]
        
    def add_to_AS(self, area, *objects):
        area.add_to_area(*objects)
        for obj in objects:
            # add objects in the AS corresponding pool
            self.pAS[obj.type].add(obj)
        
    def remove_from_AS(self, *objects):
        for obj in objects:
            # we remove the object from its pool in the AS
            self.pAS[obj.type].discard(obj)
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
        
    def delete_area(self, area):
        # we remove the area of the AS areas dictionary
        area = self.areas.pop(area.name)
        for obj_type in ("node", "trunk"):
            for obj in area.pa[obj_type]:
                # we remove the area to the list of area in the AS 
                # dictionary, for all objects of the area
                obj.AS[area.AS].remove(area)
                    
class ModifyAS(CustomTopLevel):
    def __init__(self, scenario, mode, obj, AS=set()):
        super().__init__()
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

        if mode == "add":
            command = lambda: self.add(scenario, *obj)
            values = tuple(map(str, scenario.ntw.pnAS.values()))
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
        self.AS_list.grid(row=0, column=0, columnspan=2, 
                                            pady=5, padx=5, sticky="nsew")
        self.AS_list.bind('<<ComboboxSelected>>', 
                                        lambda e: self.update_value(scenario))
        
        if mode in ("add", "remove area"):
            self.area_list = ttk.Combobox(self, width=9)
            self.update_value(scenario)
            self.area_list.current(0)
            self.area_list.grid(row=1, column=0, columnspan=2, 
                                            pady=5, padx=5, sticky="nsew")
        
        # Button to add in an AS
        self.button_add_AS = ttk.Button(self, text="OK", command=command)
        #row = 2 if mode in ("add", "remove area") else 1
        self.button_add_AS.grid(row=2, column=0, columnspan=2, 
                                            pady=5, padx=5, sticky="nsew")
        
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
    def __init__(self, scenario, nodes, trunks):
        super().__init__()
        self.so = scenario.so
        self.title("Create AS")
        
        # List of AS type
        self.var_AS_type = tk.StringVar()
        self.AS_type_list = ttk.Combobox(self, 
                                    textvariable=self.var_AS_type, width=6)
        self.AS_type_list["values"] = ("RIP", "ISIS", "OSPF", "RSTP", "BGP")
        self.AS_type_list.current(0)

        # retrieve and save node data
        self.button_create_AS = ttk.Button(self, text="Create AS", 
                        command=lambda: self.create_AS(scenario, nodes, trunks))
        
        # Label for the name/type of the AS
        self.label_name = tk.Label(self, bg="#A1DBCD", text="Name")
        self.label_type = tk.Label(self, bg="#A1DBCD", text="Type")
        self.label_id = tk.Label(self, bg="#A1DBCD", text="ID")
        
        # Entry box for the name of the AS
        self.entry_name  = tk.Entry(self, width=10)
        self.entry_id  = tk.Entry(self, width=10)
        
        self.label_name.grid(row=0, column=0, pady=5, padx=5, sticky=tk.W)
        self.label_id.grid(row=1, column=0, pady=5, padx=5, sticky=tk.W)
        self.entry_name.grid(row=0, column=1, sticky=tk.W)
        self.entry_id.grid(row=1, column=1, sticky=tk.W)
        self.label_type.grid(row=2, column=0, pady=5, padx=5, sticky=tk.W)
        self.AS_type_list.grid(row=2, column=1, pady=5, padx=5, sticky=tk.W)
        self.button_create_AS.grid(row=3, column=0, columnspan=2, pady=5, padx=5)

    def create_AS(self, scenario, nodes, trunks):
        # automatic initialization of the AS id in case it is empty
        if self.entry_id.get():
            id = int(self.entry_id.get())
        else:
            id = len(scenario.ntw.pnAS) + 1
        
        new_AS = scenario.ntw.AS_factory(
                                         name = self.entry_name.get(), 
                                         _type = self.var_AS_type.get(), 
                                         id = id,
                                         trunks = trunks, 
                                         nodes = nodes
                                         )
        self.destroy()
            