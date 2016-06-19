# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import area
import tkinter as tk
from tkinter import ttk
from miscellaneous import ObjectListbox, FocusTopLevel

class ASManagement(FocusTopLevel):
    def __init__(self, scenario, AS, imp):
        super().__init__()
        self.scenario = scenario
        self.AS = AS
        self.geometry("345x440")
        self.title("Manage AS")
        self.obj_type = ("trunk", "node", "edge") 
        self.area_listbox = ("area names", "area trunks", "area nodes")
        
        # listbox of all AS objects
        self.dict_listbox = {}
        for index, type in enumerate(self.obj_type):
            tk.Label(self, bg="#A1DBCD", text="".join(("AS ",type,"s"))).grid(row=1, column=2*index)
            listbox = ObjectListbox(self, activestyle="none", width=15, height=7)
            self.dict_listbox[type] = listbox
            yscroll = tk.Scrollbar(self, command=self.dict_listbox[type].yview, orient=tk.VERTICAL)
            listbox.configure(yscrollcommand=yscroll.set)
            listbox.bind("<<ListboxSelect>>", lambda e, type=type: self.highlight_object(e, type))
            listbox.grid(row=2, column=2*index)
            yscroll.grid(row=2, column=1+2*index, sticky="ns")
            
        # populate the listbox with all objects from which the AS was created
        for obj_type in ("trunk", "node", "edge"):
            for obj in AS.pAS[obj_type]:
                self.dict_listbox[obj_type].insert(obj)
                            
        # listbox for areas
        for index, type in enumerate(self.area_listbox):
            tk.Label(self, bg="#A1DBCD", text=type.title()).grid(row=5, column=2*index)
            listbox = ObjectListbox(self, activestyle="none", width=15, height=7)
            self.dict_listbox[type] = listbox
            yscroll = tk.Scrollbar(self, command=self.dict_listbox[type].yview, orient=tk.VERTICAL)
            listbox.configure(yscrollcommand=yscroll.set)
            if type == "area names":
                listbox.bind("<<ListboxSelect>>", lambda e: self.display_area(e))
            else:
                listbox.bind("<<ListboxSelect>>", lambda e, type=type: self.highlight_object(e, type))
            listbox.grid(row=6, column=2*index)
            yscroll.grid(row=6, column=1+2*index, sticky="ns")
        
        # find edge nodes of the AS
        self.button_find_edge_nodes = ttk.Button(self, text="Find edges", command=lambda: self.find_edge_nodes())
        self.button_create_route = ttk.Button(self, text="Create route", command=lambda: self.create_routes())
        
        # find domain trunks: the trunks between nodes of the AS
        self.button_find_trunks = ttk.Button(self, text="Find trunks", command=lambda: self.find_trunks())
        
        # operation on nodes
        self.button_remove_node_from_AS = ttk.Button(self, text="Remove node", command=lambda: self.remove_selected("node"))
        self.button_add_to_edges = ttk.Button(self, text="Add to edges", command=lambda: self.add_to_edges())
        self.button_remove_from_edges = ttk.Button(self, text="Remove edge", command=lambda: self.remove_from_edges())
        
        # buttons under the trunks column
        self.button_create_route.grid(row=3, column=0)
        self.button_find_trunks.grid(row=4, column=0)
        
        # button under the nodes column
        self.button_remove_node_from_AS.grid(row=3, column=2)
        self.button_add_to_edges.grid(row=4, column=2)
        self.button_remove_from_edges.grid(row=5)
        
        # button under the edge column
        self.button_find_edge_nodes.grid(row=3, column=4)
        self.button_remove_from_edges.grid(row=4, column=4)
            
        # button to create an area
        self.button_create_area = ttk.Button(self, text="Create area", command=lambda: area.CreateArea(self))
        self.button_create_area.grid(row=7, column=0)
        
        # at first, the backbone is the only area: we insert it in the listbox
        self.dict_listbox["area names"].insert("Backbone")
        
        # hide the window when closed
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        # if the AS is created from an import, close the management window
        print(imp)
        if imp: 
            print("test")
            self.withdraw()
        
    ## Functions used directly from the AS Management window
        
    # function to highlight the selected object on the canvas
    def highlight_object(self, event, obj_type):
        selected_object = self.dict_listbox[obj_type].selected()
        selected_object = self.scenario.ntw.of(name=selected_object, _type=obj_type)
        self.scenario.unhighlight_all()
        self.scenario.highlight_objects(selected_object)
        
    # remove the object selected in "obj_type" listbox from the AS
    def remove_selected(self, obj_type):
        # remove and retrieve the selected object in the listbox
        selected_obj = self.dict_listbox[obj_type].pop_selected()
        # remove it from the AS as well
        self.AS.remove_from_AS(self.scenario.ntw.of(name=selected_obj, _type=obj_type))
        
    def add_to_edges(self):
        selected_node = self.dict_listbox["node"].selected()
        self.dict_listbox["edge"].insert(selected_node) 
        selected_node = self.scenario.ntw.nf(name=selected_node)
        self.AS.add_to_edges(selected_node)
            
    def remove_from_edges(self):
        selected = self.scenario.ntw.nf(name=self.dict_listbox["edge"].pop_selected()) 
        self.AS.remove_from_edges(selected)
        
    def add_to_AS(self, area, *objects):
        self.AS.add_to_AS(self.AS.areas[area], *objects)
        for obj in objects:
            self.dict_listbox[obj.network_type].insert(obj)
            
    def find_edge_nodes(self):
        self.dict_listbox["edge"].clear()
        for edge in self.scenario.ntw.find_edge_nodes(self.AS):
            self.dict_listbox["edge"].insert(edge)
            
    def find_trunks(self):
        trunks_between_domain_nodes = set()
        for node in self.AS.pAS["node"]:
            for neighbor, adj_trunk in self.scenario.ntw.graph[node]["trunk"]:
                if neighbor in self.AS.pAS["node"]:
                    trunks_between_domain_nodes.add(adj_trunk)
        self.add_to_AS("Backbone", *trunks_between_domain_nodes)
        
    def create_routes(self):
        for eA in self.AS.pAS["edge"]:
            for eB in self.AS.pAS["edge"]:
                if eA != eB and eB not in self.AS.routes[eA]:
                    name = "->".join((str(eA), str(eB)))
                    route = self.scenario.ntw.lf(link_type="route", name=name, s=eA, d=eB)
                    _, route.path = self.AS.algorithm(eA, eB, self.AS)
                    route.AS = self.AS
                    self.AS.pAS["route"].add(route)
                    self.scenario.create_link(route)
                    
    def link_dimensioning(self):
        for route in self.AS.pAS["route"]:
            s, d = route.source, route.destination
            prec_node = s
            for trunk in route.path:
                # list of allowed trunks: all AS trunks but the failed one
                a_t = self.AS.pAS["trunk"] - {trunk}
                # apply the AS routing algorithm, ignoring the failed trunk
                _, recovery_path = self.AS.algorithm(s, d, self.AS, a_t=a_t)
                route.r_path[trunk] = recovery_path
                # we add the route traffic of the trunk (normal mode dimensioning)
                sd = (trunk.source == prec_node)*"SD" or "DS"
                trunk.__dict__["traffic" + sd] += route.traffic
                # update of the previous node
                prec_node = trunk.source if sd == "DS" else trunk.destination
            
    def create_area(self, name, id):
        self.AS.area_factory(name, id)
        self.dict_listbox["area names"].insert(name)
                
    def display_area(self, event):
        area = self.dict_listbox["area names"].selected()
        area = self.AS.area_factory(area)
        self.scenario.unhighlight_all()
        self.scenario.highlight_objects(*(area.pa["node"] | area.pa["trunk"]))
        self.dict_listbox["area nodes"].clear()
        self.dict_listbox["area trunks"].clear()
        for node in area.pa["node"]:
            self.dict_listbox["area nodes"].insert(node)
        for trunk in area.pa["trunk"]:
            self.dict_listbox["area trunks"].insert(trunk)
            
    ## Functions used to modify AS from the right-click menu
            
    def remove_from_area(self, area, *objects):
        self.AS.areas[area].remove_from_area(*objects)
                
    def remove_from_AS(self, *objects):
        self.AS.remove_from_AS(*objects)
        for obj in objects:
            if obj.network_type == "node":
                # remove the node from nodes/edges listbox
                self.dict_listbox["node"].pop(obj)
                self.dict_listbox["edge"].pop(obj)
            elif obj.network_type == "trunk":
                self.dict_listbox["trunk"].pop(obj)