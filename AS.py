import tkinter as tk
from tkinter import ttk
from miscellaneous import ObjectListbox, CustomTopLevel

class AutonomousSystem(object):
    class_type = "AS"

    def __init__(self, name, type, scenario, trunks=set(), nodes=set(), edges=set(), imp=False):
        self.name = name
        self.type = type
        # pAS as in "pool AS": same as pool network
        self.pAS = {"trunk": trunks, "node": nodes, "edge": edges}
        # areas is a dict associating a name to an area
        self.areas = {}
        for obj in nodes | trunks:
            obj.AS[self] = set()
        # management window of the AS 
        self.management = ASManagement(scenario, self, imp)
        # imp tells us if the AS is imported or created from scratch.
        if not imp:
            self.area_factory("Backbone")
        
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
            self.areas[name] = Area(name, self, trunks, nodes)
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
        
class Area(AutonomousSystem):
    
    class_type = "area"
    
    def __init__(self, name, AS, trunks, nodes):
        self.name = name
        self.AS = AS
        if not trunks:
            trunks = set()
        if not nodes:
            nodes = set()
        self.pa = {"node": nodes, "trunk": trunks}
        # update the AS dict for all objects, so that they are aware they
        # belong to this new area
        for obj in nodes | trunks:
            obj.AS[self.AS].add(self)
        # update the area dict of the AS with the new area
        self.AS.areas[name] = self
        # add the area to the AS management panel area listbox
        self.AS.management.create_area(name)
        
    def add_to_area(self, *objects):
        for obj in objects:
            self.pa[obj.network_type].add(obj)
            obj.AS[self.AS].add(self)
            
    def remove_from_area(self, *objects):
        for obj in objects:
            self.pa[obj.network_type].discard(obj)
            obj.AS[self.AS].discard(self)
        
# TODO switch to custom toplevel
class ASManagement(tk.Toplevel):
    def __init__(self, scenario, AS, imp):
        super().__init__()
        self.scenario = scenario
        self.AS = AS
        self.geometry("345x440")
        self.title("Manage AS")
        self.configure(background="#A1DBCD")
        self.obj_type = ("trunk", "node", "edge") 
        self.area_listbox = ("area names", "area trunks", "area nodes")
        
        # this allows to change the behavior of closing the window. 
        # I don't want the window to be destroyed, simply hidden
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        
        # button for manage AS panel to grab focus
        self.var_focus = tk.IntVar()
        self.var_focus.set(0)
        self.checkbutton_focus = tk.Checkbutton(self, bg="#A1DBCD", text="Focus", variable=self.var_focus, command=self.change_focus)
        self.checkbutton_focus.grid(row=0, column=0, columnspan=2)
        
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
              
        # if the AS is created from an import, close the management window
        if imp:
            self.withdraw()
        
        # find edge nodes of the AS
        self.button_find_edge_nodes = ttk.Button(self, text="Find edges", command=lambda: self.find_edge_nodes())
        self.button_create_route = ttk.Button(self, text="Create route", command=lambda: self.create_routes())
        
        # find domain trunks: the trunks between nodes of the AS
        self.button_find_trunks = ttk.Button(self, text="Find trunks", command=lambda: self.find_trunks())
        
        # operation on nodes
        self.button_remove_node_from_AS = ttk.Button(self, text="Remove node", command=lambda: self.remove_selected("node"))
        self.button_add_to_edges = ttk.Button(self, text="Add to edges", command=lambda: self.add_to_edges())
        self.button_remove_from_edges = ttk.Button(self, text="Remove edge", command=lambda: self.remove_from_edges())
        ttk.Style().configure("TButton", background="#A1DBCD")
        
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
        
        ## Area listbox 
        
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
            
        self.button_create_area = ttk.Button(self, text="Create area", command=lambda: CreateArea(self))
        self.button_create_area.grid(row=7, column=0)
        self.button_add_node_to_area = ttk.Button(self, text="Add node to area", command=lambda: self.add_selected_node_to_area())
        self.button_add_node_to_area.grid(row=7, column=2)
        
        # at first, the backbone is the only area: we insert it in the listbox
        self.dict_listbox["area names"].insert("Backbone")
        
    # function to change the focus
    def change_focus(self):
        self.wm_attributes('-topmost', self.var_focus.get())
        
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
                if(neighbor in self.AS.pAS["node"]):
                    trunks_between_domain_nodes.add(adj_trunk)
        self.add_to_AS("Backbone", *trunks_between_domain_nodes)
        
    def create_routes(self):
        for eA in self.AS.pAS["edge"]:
            for eB in self.AS.pAS["edge"]:
                if(eA != eB and not self.scenario.ntw.is_connected(eA, eB, "route")):
                    route_AB = "-".join((str(eA), str(eB)))
                    route_BA = "-".join((str(eB), str(eA)))
                    new_route_AB = self.scenario.ntw.lf(link_type="route", name=route_AB, s=eA, d=eB)
                    new_route_BA = self.scenario.ntw.lf(link_type="route", name=route_BA, s=eB, d=eA)
                    _, new_route_AB.path = self.scenario.ntw.ISIS_dijkstra(eA, eB, self.AS)
                    _, new_route_BA.path = self.scenario.ntw.ISIS_dijkstra(eB, eA, self.AS)
                    self.scenario.create_link(new_route_AB)
                    self.scenario.create_link(new_route_BA)
            
    def create_area(self, name):
        self.AS.area_factory(name)
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
            if(obj.network_type == "node"):
                # remove the node from nodes/edges listbox
                self.dict_listbox["node"].pop(obj)
                self.dict_listbox["edge"].pop(obj)
            elif(obj.network_type == "trunk"):
                self.dict_listbox["trunk"].pop(obj)
            
class CreateArea(tk.Toplevel):
    def __init__(self, asm):
        super().__init__()
        self.geometry("30x65")        
        self.title("Create area")   
        self.configure(background="#A1DBCD")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.entry_name = ttk.Entry(self, width=9)
        self.entry_name.grid(row=0, column=0, pady=5, padx=5)
        
        self.button_OK = ttk.Button(self, text="OK", command=lambda: self.create_area(asm))
        self.button_OK.grid(row=1, column=0, pady=5, padx=5, sticky="nsew")
        ttk.Style().configure("TButton", background="#A1DBCD")
        
    def create_area(self, asm):
        asm.create_area(self.entry_name.get())
        self.destroy()
                    
class ChangeAS(tk.Toplevel):
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
        self.configure(background="#A1DBCD")
        # always at least one row and one column with a weight > 0
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # TODO make it a dict
        if(mode == "add"):
            command = lambda: self.add(scenario, *obj)
            values = tuple(map(str, scenario.ntw.pn["AS"].values()))
        elif(mode == "remove"):
            values = tuple(map(str, AS))
            command = lambda: self.remove_from_AS(scenario, *obj)
        elif(mode == "remove area"):
            values = tuple(map(str, AS))
            command = lambda: self.remove_from_area(scenario, *obj)
        elif(mode == "manage"):
            values = tuple(map(str, AS))
            command = lambda: self.manage_AS(scenario)
        
        # List of existing AS
        self.AS_list = ttk.Combobox(self, width=9)
        self.AS_list["values"] = values
        self.AS_list.current(0)
        self.AS_list.grid(row=0, column=0, columnspan=2, pady=5, padx=5, sticky="nsew")
        self.AS_list.bind('<<ComboboxSelected>>', lambda e: self.update_value(scenario))
        
        if(mode in ("add", "remove area")):
            self.area_list = ttk.Combobox(self, width=9)
            self.update_value(scenario)
            self.area_list.current(0)
            self.area_list.grid(row=1, column=0, columnspan=2, pady=5, padx=5, sticky="nsew")
        
        # Button to add in an AS
        self.button_add_AS = ttk.Button(self, text="OK", command=command)
        ttk.Style().configure("TButton", background="#A1DBCD")
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
        
class ASCreation(tk.Toplevel):
    def __init__(self, scenario, so):
        super().__init__()
        self.geometry("120x100")
        self.title("Create AS")
        self.configure(background="#A1DBCD")
        
        # List of AS type
        self.var_AS_type = tk.StringVar()
        self.AS_type_list = ttk.Combobox(self, textvariable=self.var_AS_type, width=6)
        self.AS_type_list["values"] = ("RIP", "IS-IS", "OSPF", "MPLS", "RSTP")
        self.AS_type_list.current(0)

        # retrieve and save node data
        self.button_create_AS = ttk.Button(self, text="Create AS", command=lambda: self.create_AS(scenario, so))
        ttk.Style().configure("TButton", background="#A1DBCD")
        
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
            