import tkinter as tk
from tkinter import ttk
from miscellaneous import ObjectListbox

class AutonomousSystem(object):
    class_type = "AS"
    # TODO AS doit avoir un pool_AS contenant route, node, trunk, edge + area
    # ce qui permet de ne pas avoir de disjonction de cas pour add par exemple
    def __init__(self, name, type, trunks=set(), nodes=set()):
        self.name = name
        self.type = type
        self.trunks = trunks
        # set the AS of the trunk
        for trunk in self.trunks:
            trunk.AS = self
        self.nodes = nodes
        # at initialization, we populate the nodes set
        for node in self.nodes:
            node.AS.add(self)
        for trunk in self.trunks:
            self.nodes.update((trunk.source, trunk.destination))
            # and we update the nodes with its new domain
            trunk.source.AS.add(self)
            trunk.destination.AS.add(self)
        self.edges = set()
        self.area = {Area("backbone")}
        # management window of the AS 
        self.management = None
        
    def __repr__(self):
        return self.name
        
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name
        
    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __hash__(self):
        return hash(self.name)
        
    def add_to_AS(self, obj):
        if(obj.class_type == "node"):
            self.nodes.add(obj)
            obj.AS.add(self)
        else:
            self.trunks.add(obj)
            obj.AS = self
            self.nodes.update((obj.source, obj.destination)) 
            
    def add_to_edges(self, node):
        self.edges.add(node)
        
    def remove_from_edges(self, node):
        self.edges.discard(node)
                
    def remove_obj_from_AS(self, obj):
        if(obj.network_type == "node"):
            self.nodes.discard(obj)
            obj.AS.remove(self)
            self.remove_from_edges(obj)
        elif(obj.network_type == "trunk"):
            if(obj.AS):
                self.trunks.discard(obj)
                obj.AS = None
        
class Area(AutonomousSystem):
    
    class_type = "area"
    
    def __init__(self, name, type="trunks"):
        self.name = name
        self.type = type
        
class ASManagement(tk.Toplevel):
    def __init__(self, scenario, AS):
        super().__init__()
        self.scenario = scenario
        self.AS = AS
        self.geometry("345x220")
        self.title("Manage AS")
        self.configure(background="#A1DBCD")
        self.obj_type = ("trunk", "node", "edge") 
        
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
            tk.Label(self, bg="#A1DBCD", text=" ".join(("Domain",type,"s"))).grid(row=1, column=2*index)
            listbox = ObjectListbox(self, activestyle="none", width=15, height=7)
            self.dict_listbox[type] = listbox
            yscroll = tk.Scrollbar(self, command=self.dict_listbox[type].yview, orient=tk.VERTICAL)
            listbox.configure(yscrollcommand=yscroll.set)
            listbox.bind("<<ListboxSelect>>", lambda e, type=type: self.highlight_object(e, type))
            listbox.grid(row=2, column=2*index)
            yscroll.grid(row=2, column=1+2*index, sticky="ns")
            
        for trunk in AS.trunks:
            self.dict_listbox["trunk"].insert(trunk)
        
        for node in AS.nodes:
            self.dict_listbox["node"].insert(node)
        
        # find edge nodes of the AS
        self.button_find_edge_nodes = ttk.Button(self, text="Find edges", command=lambda: self.find_edge_nodes())
        self.button_create_route = ttk.Button(self, text="Create route", command=lambda: self.create_routes())
        
        # find domain trunks: the trunks between nodes of the AS
        self.button_find_trunks = ttk.Button(self, text="Find trunks", command=lambda: self.find_trunks())
        
        # operation on nodes
        self.button_remove_node_from_AS = ttk.Button(self, text="Remove node", command=lambda: self.remove_selected_node_from_AS())
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
        
        # find the edges at initialization
        self.find_edge_nodes()
        
    # function to change the focus
    def change_focus(self):
        self.wm_attributes('-topmost', self.var_focus.get())
        
    # function to highlight the selected object on the canvas
    def highlight_object(self, event, type):
        selected_object = self.dict_listbox[type].selected()
        if(type == "trunk"):
            selected_object = self.scenario.link_factory(name=selected_object)
        else:
            selected_object = self.scenario.node_factory(name=selected_object)
        self.scenario.unhighlight_all()
        self.scenario.highlight_objects(selected_object)
        
    def add_to_edges(self):
        selected_node = self.dict_listbox["node"].get(self.dict_listbox["node"].curselection())
        self.dict_listbox["edge"].insert(selected_node) 
        selected_node = self.scenario.node_factory(name=selected_node)
        self.AS.add_to_edges(selected_node)
            
    def remove_from_edges(self):
        selected = self.scenario.node_factory(name=self.dict_listbox["edge"].pop_selected()) 
        self.AS.remove_from_edges(selected)
        
    def add_to_AS(self, *objects):
        for obj in objects:
            self.dict_listbox[obj.network_type].insert(obj)
            self.AS.add_to_AS(obj)
            
    def remove_obj_from_AS(self, *objects):
        for obj in objects:
            if(obj.network_type == "node"):
                # remove the node from nodes/edges listbox
                self.dict_listbox["node"].pop(obj)
                self.dict_listbox["edge"].pop(obj)
                # update the AS topology in the network
            elif(obj.network_type == "trunk"):
                self.dict_listbox["trunk"].pop(obj)
            self.AS.remove_obj_from_AS(obj)
        
    def find_edge_nodes(self):
        self.dict_listbox["edge"].delete(0, tk.END)
        for edge in self.scenario.find_edge_nodes(self.AS):
            self.dict_listbox["edge"].insert(edge)
            
    def find_trunks(self):
        trunks_between_domain_nodes = set()
        for node in self.AS.nodes:
            for adj_trunk in self.scenario.graph[node]["trunk"]:
                neighbor = adj_trunk.destination if node == adj_trunk.source else adj_trunk.source
                if(neighbor in self.AS.nodes):
                    trunks_between_domain_nodes.add(adj_trunk)
        self.add_to_AS(*trunks_between_domain_nodes)
        
    def create_routes(self):
        for eA in self.AS.edges:
            for eB in self.AS.edges:
                if(eA != eB and not self.scenario.is_connected(eA, eB, "route")):
                    route_name = "-".join(str(eA), str(eB))
                    new_route = self.scenario.link_factory(link_type="route", name=route_name, s=eA, d=eB)
                    _, new_route.path = self.scenario.dijkstra(eA, eB, allowed_nodes=self.AS.nodes, allowed_trunks=self.AS.trunks)
                    self.scenario.create_link(new_route)
                    
class ChangeAS(tk.Toplevel):
    def __init__(self, scenario, mode, obj, AS=set()):
        super().__init__()
        self.geometry("30x65")
        titles = {"add": "Add to AS", "remove": "Remove from AS", "manage": "Manage AS"}
        self.title(titles[mode])
        self.configure(background="#A1DBCD")
        # always at least one row and one column with a weight > 0
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        if(mode == "add"):
            text = "Choose AS"
            command = lambda: self.add_to_AS(scenario, *obj)
            values = tuple(map(str, scenario.pn["AS"].values()))
        elif(mode == "manage"):
            text = "Manage AS"
            values = tuple(map(str, AS))
            command = lambda: self.manage_AS(scenario)
        elif(mode == "remove"):
            text = "Remove from AS"
            values = tuple(map(str, AS))
            command = lambda: self.remove_from_AS(scenario, *obj)
        
        # List of existing AS
        self.AS_list = ttk.Combobox(self, width=9)
        self.AS_list["values"] = values
        self.AS_list.current(0)
        self.AS_list.grid(row=0, column=0, columnspan=2, pady=5, padx=5, sticky="nsew")
        
        # Button to add in an AS
        self.button_add_AS = ttk.Button(self, text=text, command=command)
        ttk.Style().configure("TButton", background="#A1DBCD")
        self.button_add_AS.grid(row=1, column=0, columnspan=2, pady=5, padx=5, sticky="nsew")
        
    # merge these three functions into one with the mode 
    # they share the check + destroy
    def add_to_AS(self, scenario, *objects):
        if(self.AS_list.get() != "Choose AS"):
            selected_AS = scenario.AS_factory(name=self.AS_list.get())
            selected_AS.management.add_to_AS(*objects)
            self.destroy()
            
    def remove_from_AS(self, scenario, *objects):
        if(self.AS_list.get() != "Choose AS"):
            selected_AS = scenario.AS_factory(name=self.AS_list.get())
            selected_AS.management.remove_obj_from_AS(*objects)
            self.destroy()
        
    def manage_AS(self, scenario):
        if(self.AS_list.get() != "Choose AS"):
            selected_AS = scenario.AS_factory(name=self.AS_list.get())
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
        new_AS = scenario.AS_factory(name=self.var_name.get(), type=self.var_AS_type.get(), trunks=so["link"], nodes=so["node"])
        new_AS.management = ASManagement(scenario, new_AS)
        self.destroy()
            