# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

from . import area
import tkinter as tk
from tkinter import ttk
from pythonic_tkinter.custom_widgets import CustomTopLevel
from pythonic_tkinter.custom_widgets import CustomFrame
from pythonic_tkinter.custom_listbox import ObjectListbox
from pythonic_tkinter.preconfigured_ttk_widgets import *

class ASManagement(CustomTopLevel):
    
    def __init__(self, AS, is_imported):
        super().__init__()
        self.AS = AS
        self.dict_listbox = {}
        self.title("Manage AS")
        
        # A ttk notebook made of two frames
        self.frame_notebook = ttk.Notebook(self)
        common_frame = CustomFrame(self.frame_notebook)
        self.frame_notebook.add(common_frame, text='Common management')
        self.frame_notebook.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        
        # label frame for properties
        lf_properties = Labelframe(common_frame)
        lf_properties.text = 'AS properties'
        
        obj_types = ('trunk', 'node') 
        
        label_name = Label(common_frame)
        label_name.text = "AS name"
        label_id = Label(common_frame)
        label_id.text = "AS ID"
        label_type = Label(common_frame)
        label_type.text = "AS Type"
        
        entry_name  = Entry(common_frame, width=10)
        entry_name.text = AS.name
        entry_id  = Entry(common_frame, width=10)
        entry_id.text = AS.id
        
        # the type of a domain cannot change after domain creation.
        AS_type = Label(common_frame) 
        AS_type.text = AS.AS_type
        
        lf_properties.grid(0, 0)
        label_name.grid(1, 0, in_=lf_properties)
        label_id.grid(2, 0, in_=lf_properties)
        label_type.grid(3, 0, in_=lf_properties)
        entry_name.grid(1, 1, in_=lf_properties)
        entry_id.grid(2, 1, in_=lf_properties)
        AS_type.grid(3, 1, in_=lf_properties)
        
        # label frame for links and nodes
        lf_objects = Labelframe(common_frame)
        lf_objects.text = 'AS objects'
        lf_objects.grid(1, 0)
        
        # listbox of all AS objects
        for index, type in enumerate(obj_types):
            label = Label(common_frame)
            label.text = "AS " + type + "s"
    
            listbox = Listbox(common_frame, activestyle="none", width=15, height=7, selectmode="extended")
                                            
            self.dict_listbox[type] = listbox
            yscroll = Scrollbar(common_frame)
            yscroll.command = self.dict_listbox[type].yview
                    
            listbox.configure(yscrollcommand=yscroll.set)
            listbox.bind("<<ListboxSelect>>", 
                            lambda e, type=type: self.highlight_object(e, type))
                            
            label.grid(0, 2 * index, in_=lf_objects)
            listbox.grid(1, 2 * index, in_=lf_objects)
            yscroll.grid(1, 1 + 2 * index, in_=lf_objects)
            
        # populate the listbox with all objects from which the AS was created
        for obj_type in obj_types:
            for obj in AS.pAS[obj_type]:
                self.dict_listbox[obj_type].insert(obj)
        
        # find domain trunks: the trunks between nodes of the AS
        button_find_trunks = Button(common_frame) 
        button_find_trunks.text = "Find trunks"
        button_find_trunks.command=lambda: self.find_trunks()
        
        # operation on nodes
        button_remove_node_from_AS = Button(common_frame) 
        button_remove_node_from_AS.text="Remove node"
        button_remove_node_from_AS.command = lambda: self.remove_selected("node")
        
        # buttons under the trunks column
        button_find_trunks.grid(2, 0, in_=lf_objects)
        
        # button under the nodes column
        button_remove_node_from_AS.grid(2, 2, in_=lf_objects)
        
        # hide the window when closed
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        
        # if the AS is created from an import, close the management window
        if is_imported: 
            self.withdraw()
            
    ## Functions used directly from the AS Management window
        
    # function to highlight the selected object on the canvas
    def highlight_object(self, event, obj_type):        
        self.AS.cs.unhighlight_all()
        for selected_object in self.dict_listbox[obj_type].selected():
            so = self.AS.cs.ntw.of(name=selected_object, _type=obj_type)
            self.AS.cs.highlight_objects(so)
            
    # remove the object selected in "obj_type" listbox from the AS
    def remove_selected(self, obj_type):
        # remove and retrieve the selected object in the listbox
        for selected_obj in self.dict_listbox[obj_type].pop_selected():
            # remove it from the AS as well
            so = self.AS.cs.ntw.of(name=selected_obj, _type=obj_type)
            print(so)
            self.AS.remove_from_AS(so)
        
    def add_to_AS(self, area, *objects):
        if self.AS.has_area:
            self.AS.add_to_AS(self.AS.areas[area], *objects)
        for obj in objects:
            self.dict_listbox[obj.type].insert(obj)
            
    def find_trunks(self):
        trunks_between_domain_nodes = set()
        for node in self.AS.pAS["node"]:
            for neighbor, adj_trunk in self.AS.cs.ntw.graph[node.id]["trunk"]:
                if neighbor in self.AS.pAS["node"]:
                    trunks_between_domain_nodes.add(adj_trunk)
        self.add_to_AS("Backbone", *trunks_between_domain_nodes)
            
    ## Functions used to modify AS from the right-click menu
                
    def remove_from_AS(self, *objects):
        self.AS.remove_from_AS(*objects)
        for obj in objects:
            if obj.type == "node":
                # remove the node from nodes listbox
                self.dict_listbox["node"].pop(obj)
            elif obj.type == "trunk":
                self.dict_listbox["trunk"].pop(obj)
            
class ASManagementWithArea(ASManagement):
    
    def __init__(self, *args):
        super().__init__(*args)
        
        self.area_frame = CustomFrame(self.frame_notebook)
        self.frame_notebook.add(self.area_frame, text='Area management')
        self.area_listbox = ("area names", "area trunks", "area nodes")
        
        # listbox for areas
        for index, type in enumerate(self.area_listbox):
            lbl = tk.Label(self.area_frame, bg="#A1DBCD", text=type.title())
            listbox = ObjectListbox(self.area_frame, activestyle="none", width=15, height=7)
            self.dict_listbox[type] = listbox
            yscroll = tk.Scrollbar(self.area_frame, 
                    command=self.dict_listbox[type].yview, orient=tk.VERTICAL)
            listbox.configure(yscrollcommand=yscroll.set)
            if type == "area names":
                listbox.bind("<<ListboxSelect>>", 
                            lambda e: self.display_area(e))
            else:
                listbox.bind("<<ListboxSelect>>", 
                            lambda e, type=type: self.highlight_object(e, type))
            lbl.grid(row=6, column=2*index)
            listbox.grid(row=7, column=2*index)
            yscroll.grid(row=7, column=1+2*index, sticky="ns")
                                                  
        # button to create an area
        self.button_create_area = ttk.Button(self.area_frame, text="Create area", 
                                command=lambda: area.CreateArea(self))
                                
        # button to delete an area
        self.button_delete_area = ttk.Button(self.area_frame, text="Delete area", 
                                command=lambda: self.delete_area())
            
        # button under the area column
        self.button_create_area.grid(row=8, column=0)
        self.button_delete_area.grid(row=9, column=0)
        
        # at first, the backbone is the only area: we insert it in the listbox
        self.dict_listbox["area names"].insert("Backbone")
        
    ## Functions used directly from the AS Management window

    def create_area(self, name, id):
        self.AS.area_factory(name, id)
        self.dict_listbox["area names"].insert(name)

    def delete_area(self):
        for area_name in self.dict_listbox["area names"].pop_selected():
            selected_area = self.AS.area_factory(name=area_name)
            self.AS.delete_area(selected_area)
                
    def display_area(self, event):
        for area in self.dict_listbox["area names"].selected():
            area = self.AS.area_factory(area)
            self.AS.cs.unhighlight_all()
            self.AS.cs.highlight_objects(*(area.pa["node"] | area.pa["trunk"]))
            self.dict_listbox["area nodes"].clear()
            self.dict_listbox["area trunks"].clear()
            for node in area.pa["node"]:
                self.dict_listbox["area nodes"].insert(node)
            for trunk in area.pa["trunk"]:
                self.dict_listbox["area trunks"].insert(trunk)
                
    ## Functions used to modify AS from the right-click menu
    
    def add_to_area(self, area, *objects):
        self.AS.areas[area].add_to_area(*objects)
            
    def remove_from_area(self, area, *objects):
        self.AS.areas[area].remove_from_area(*objects)
                
class RIP_Management(ASManagement):
    
    def __init__(self, *args):
        super().__init__(*args)
        
class ISIS_Management(ASManagementWithArea):
    
    def __init__(self, *args):
        super().__init__(*args)
        
        # interface to cost dictionnary. This is used for OSPF and IS-IS, 
        # because the cost of a trunk depends on the bandwidth.
        # Trunk_cost = Ref_BW / BW
        self.if_to_cost = {
        "FE": 10**7,
        "GE": 10**8,
        "10GE": 10**9,
        "40GE": 4*10**9,
        "100GE":10**10
        }
        
        self.button_update_cost = ttk.Button(self.area_frame, text="Update costs", 
                                command=lambda: self.update_cost())
        self.button_update_cost.grid(row=1, column=0, pady=5, padx=5, sticky="w")    
        
        self.button_update_topo = ttk.Button(self.area_frame, text="Update topology", 
                                command=lambda: self.update_AS_topology())
        self.button_update_topo.grid(row=2, column=0, pady=5, padx=5, sticky="w") 
        
    def update_AS_topology(self):
        
        self.AS.border_routers.clear()
        # reset all area trunks
        self.AS.areas["Backbone"].pa["trunk"].clear()
        
        for node in self.AS.pAS["node"]:
            
            # In IS-IS, a router has only one area
            node_area ,= node.AS[self.AS]
            
            for neighbor, adj_trunk in self.AS.cs.ntw.graph[node.id]["trunk"]:
                
                # A multi-area IS-IS AS is defined by the status of its nodes.
                # we automatically update the trunk area status, by considering 
                # that a trunk belong to an area as soon as both of its ends do.
                # A trunk between two L1/L2 routers that belong to different
                # areas will be considered as being part of the backbone.

                # we check that the neighbor belongs to the AS
                if self.AS in neighbor.AS:
                    # we retrieve the neighbor's area
                    neighbor_area ,= neighbor.AS[self.AS]
                    # if they are the same, we add the trunk to the area
                    if node_area == neighbor_area:
                        node_area.add_to_area(adj_trunk)
                    # if not, it is at the edge of two areas
                    # a router is considered L1/L2 if it has at least
                    # one neighbor which is in a different area.
                    else:
                        # we consider that the trunk belongs to the backbone,
                        # for interfaces to have IP addresses.
                        self.AS.areas["Backbone"].add_to_area(adj_trunk)
                        self.AS.border_routers.add(node)
                
    def update_cost(self):
        for trunk in self.AS.pAS["trunk"]:
            bw = self.if_to_cost[trunk.interface]
            # the cost of a link cannot be less than 1. This also means that,
            # by default, all interfaces from GE to 100GE will result in the
            # same metric: 1.
            cost = max(1, self.AS.ref_bw / bw)
            trunk.costSD = trunk.costDS = cost   
        
class OSPF_Management(ASManagementWithArea):
    
    def __init__(self, *args):
        super().__init__(*args)
        
        # interface to cost dictionnary. This is used for OSPF and IS-IS, 
        # because the cost of a trunk depends on the bandwidth.
        # Trunk_cost = Ref_BW / BW
        self.if_to_cost = {
        "FE": 10**7,
        "GE": 10**8,
        "10GE": 10**9,
        "40GE": 4*10**9,
        "100GE":10**10
        }

        # self.button_update_cost = ttk.Button(self, text="Update costs", 
        #                         command=lambda: self.update_cost())
        # self.button_update_cost.grid(row=1, column=0, pady=5, padx=5, sticky="w")    
        # 
        # self.button_update_topo = ttk.Button(self, text="Update topology", 
        #                         command=lambda: self.update_AS_topology())
        # self.button_update_topo.grid(row=2, column=0, pady=5, padx=5, sticky="w")
        
        #TODO ASBR stuff
        # self.button_add_to_edges = ttk.Button(self, text="Add to ASBR", 
        #                         command=lambda: self.add_to_edges())
        #                         
        # self.button_remove_from_edges = ttk.Button(self, text="Remove ASBR", 
        #                         command=lambda: self.remove_from_edges())
           
        # button under the edge column
        # self.button_add_to_edges.grid(row=6, column=2)
        # self.button_remove_from_edges.grid(row=7, column=2)
        # self.button_find_edge_nodes.grid(row=5, column=4)
        
        # combobox to choose the exit ASBR
        self.exit_asbr = tk.StringVar()
        self.router_list = ttk.Combobox(self, 
                                    textvariable=self.exit_asbr, width=10)
        self.router_list["values"] = (None,) + tuple(
                                        self.dict_listbox["node"].yield_all())
        self.exit_asbr.set(None)
        
        # hide the window when closed
        self.protocol("WM_DELETE_WINDOW", self.save_parameters)
        
    def update_AS_topology(self):
        
        self.AS.border_routers.clear()
        # reset all area nodes
        self.AS.areas["Backbone"].pa["node"].clear()
        
        for node in self.AS.pAS["node"]:
                
            # in OSPF, a router is considered ABR if it has attached
            # trunks that are in different area. Since we just updated 
            # the router's areas, all we need to check is that it has
            # at least 2 distinct areas.
            # an ABR is automatically part of the backbone area.
            if len(node.AS[self.AS]) > 1:
                self.AS.border_routers.add(node)
                self.AS.areas["Backbone"].add_to_area(node)
            
            for neighbor, adj_trunk in self.AS.cs.ntw.graph[node.id]["trunk"]:

                # a multi-area OSPF AS is defined by the area of its trunk.
                # we automatically update the node area status, by considering that a 
                # node belongs to an area as soon as one of its adjacent trunk does.
                for area in adj_trunk.AS[self.AS]:
                    area.add_to_area(node)
                
    def update_cost(self):
        for trunk in self.AS.pAS["trunk"]:
            bw = self.if_to_cost[trunk.interface]
            # the cost of a link cannot be less than 1. This also means that,
            # by default, all interfaces from GE to 100GE will result in the
            # same metric: 1.
            cost = max(1, self.AS.ref_bw / bw)
            trunk.costSD = trunk.costDS = cost 
            
    ## saving function: used when closing the window
    
    def save_parameters(self):
        if self.exit_asbr.get() != "None":
            exit_asbr = self.AS.cs.ntw.pn["node"][self.exit_asbr.get()]
            self.AS.exit_point = exit_asbr
        self.withdraw()
            
    # def add_to_ASBR(self):
    #     for selected_node in self.dict_listbox["ASBR"].selected():
    #         self.dict_listbox["ASBR"].insert(selected_node) 
    #         selected_node = self.AS.cs.ntw.nf(name=selected_node)
    #         self.AS.add_to_edges(selected_node)
    #         
    # def remove_from_edges(self):
    #     for selected_edge in self.dict_listbox["ASBR"].pop_selected():
    #         selected = self.AS.cs.ntw.nf(name=selected_edge) 
    #         self.AS.remove_from_edges(selected)
    #         
    # def find_edge_nodes(self):
    #     self.dict_listbox["ASBR"].clear()
    #     for edge in self.AS.cs.ntw.find_edge_nodes(self.AS):
    #         self.dict_listbox["ASBR"].insert(edge)    
