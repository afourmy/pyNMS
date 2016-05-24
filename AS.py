import tkinter as tk
from tkinter import ttk

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
        else:
            self.trunks.add(obj)
            obj.AS = self
            self.nodes.update((obj.source, obj.destination)) 
            
    def add_to_edges(self, node):
        self.edges.add(node)
        
    def remove_from_edges(self, node):
        self.edges.discard(node)
                
    def remove_node_from_AS(self, node):
        self.nodes.discard(node)
        self.remove_node_from_edge(node)
            
    def remove_node_from_edge(self, node):
        for AS in node.AS:
            self.edges.discard(node) 
        
    def remove_trunk_from_AS(self, trunk):
        if(trunk.AS):
            self.trunks.discard(trunk)
            trunk.AS = None
        
class Area(AutonomousSystem):
    
    class_type = "area"
    
    def __init__(self, name, type="trunks"):
        self.name = name
        self.type = type
        
class CustomListbox(tk.Listbox):
    def __contains__(self, str):
        return str in self.get(0, "end")

class ASManagement(tk.Toplevel):
    def __init__(self, scenario, AS):
        super().__init__()
        self.geometry("345x220")
        self.title("Manage AS")
        self.configure(background="#A1DBCD")
        self.obj_type = ("trunks", "nodes", "edges") 
        
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
            tk.Label(self, bg="#A1DBCD", text = "Domain " + type).grid(row=1, column=2*index)
            listbox = CustomListbox(self, activestyle="none", width=15, height=7)
            self.dict_listbox[type] = listbox
            yscroll = tk.Scrollbar(self, command=self.dict_listbox[type].yview, orient=tk.VERTICAL)
            listbox.configure(yscrollcommand=yscroll.set)
            listbox.bind("<<ListboxSelect>>", lambda e, type=type: self.highlight_object(e, scenario, type))
            listbox.grid(row=2, column=2*index)
            yscroll.grid(row=2, column=1+2*index, sticky="ns")
            
        for trunk in AS.trunks:
            self.dict_listbox["trunks"].insert(tk.END, trunk)
        
        for node in AS.nodes:
            self.dict_listbox["nodes"].insert(tk.END, node)
        
        # find edge nodes of the AS
        self.button_find_edge_nodes = ttk.Button(self, text="Find edges", command=lambda: self.find_edge_nodes(scenario, AS))
        self.button_create_route = ttk.Button(self, text="Create route", command=lambda: self.create_routes(scenario, AS))
        
        # find domain trunks: the trunks between nodes of the AS
        self.button_find_trunks = ttk.Button(self, text="Find trunks", command=lambda: self.find_trunks(scenario, AS))
        
        # operation on nodes
        self.button_remove_node_from_AS = ttk.Button(self, text="Remove node", command=lambda: self.remove_selected_node_from_AS(scenario, AS))
        self.button_add_to_edges = ttk.Button(self, text="Add to edges", command=lambda: self.add_to_edges(scenario, AS))
        self.button_remove_from_edges = ttk.Button(self, text="Remove edge", command=lambda: self.remove_from_edges(scenario, AS))
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
        self.find_edge_nodes(scenario, AS)
        
    # function to change the focus
    def change_focus(self):
        self.wm_attributes('-topmost', self.var_focus.get())
        
    # function to highlight the selected object on the canvas
    def highlight_object(self, event, scenario, type):
        a = self.dict_listbox[type].curselection()
        selected_object = self.dict_listbox[type].get(a)
        if(type == "trunks"):
            selected_object = scenario.link_factory(name=selected_object)
        else:
            selected_object = scenario.node_factory(name=selected_object)
        scenario.unhighlight_all()
        scenario.highlight_objects(selected_object)
        
    def add_to_edges(self, scenario, AS):
        self.selected_node = self.dict_listbox["nodes"].get(self.dict_listbox["nodes"].curselection())
        if(self.selected_node not in AS.management.dict_listbox["edges"]):
            AS.management.dict_listbox["edges"].insert(tk.END, self.selected_node) 
        self.selected_node = scenario.node_factory(name=self.selected_node)
        AS.add_to_edges(self.selected_node)
            
    def remove_from_edges(self, scenario, AS):
        self.selected_edge = self.dict_listbox["edges"].get(self.dict_listbox["edges"].curselection())
        index_edge = self.dict_listbox["edges"].get(0, tk.END).index(self.selected_edge)
        self.dict_listbox["edges"].delete(index_edge)
        self.selected_edge = scenario.node_factory(name=self.selected_edge) 
        AS.remove_from_edges(self.selected_edge)
        
    def add_to_AS(self, AS, *objects):
        for obj in objects:
            if(obj.class_type == "node"):
                if obj not in AS.nodes:
                    AS.management.dict_listbox["nodes"].insert(tk.END, obj)
            else:
                if obj not in AS.trunks:
                    AS.management.dict_listbox["trunks"].insert(tk.END, obj)
            AS.add_to_AS(obj)
        
    def find_edge_nodes(self, scenario, AS):
        self.dict_listbox["edges"].delete(0, tk.END)
        for edge in scenario.find_edge_nodes(AS):
            self.dict_listbox["edges"].insert(tk.END, edge)
            
    def find_trunks(self, scenario, AS):
        trunks_between_domain_nodes = set()
        for node in AS.nodes:
            for adj_trunk in scenario.graph[node]["trunk"]:
                neighbor = adj_trunk.destination if node == adj_trunk.source else adj_trunk.source
                if(neighbor in AS.nodes):
                    trunks_between_domain_nodes.add(adj_trunk)
        self.add_to_AS(AS, *trunks_between_domain_nodes)
            
    def remove_nodes_from_AS(self, AS, *nodes):
        for node in nodes:
            # remove the node from the AS management panel, in the nodes
            # listbox as well as in the edge listbox
            index_node = self.dict_listbox["nodes"].get(0, tk.END).index(repr(node))
            self.dict_listbox["nodes"].delete(index_node)
            if(node in AS.edges):
                index_edge = self.dict_listbox["edges"].get(0, tk.END).index(repr(node))
                self.dict_listbox["edges"].delete(index_edge)
            AS.remove_node_from_AS(node)
            
    def remove_selected_node_from_AS(self, scenario, AS):
        self.selected_node = self.dict_listbox["nodes"].get(self.dict_listbox["nodes"].curselection()) 
        self.selected_node = scenario.node_factory(name=self.selected_node)
        self.remove_nodes_from_AS(AS, self.selected_node)
        
    def remove_trunks_from_AS(self, *trunks):
        print(self.dict_listbox["trunks"])
        for trunk in trunks:
            print(trunk.name)
            if(trunk.name in self.dict_listbox["trunks"]):
                # remove the trunk from the AS management panel, in the trunks listbox
                index_trunk = self.dict_listbox["trunks"].get(0, tk.END).index(repr(trunk))
                self.dict_listbox["trunks"].delete(index_trunk)
                # update the AS topology in the network
                trunk.AS.remove_trunk_from_AS(trunk)
    
    def create_routes(self, scenario, AS):
        for edgeA in AS.edges:
            for edgeB in AS.edges:
                if(edgeA != edgeB and not scenario.is_connected(edgeA, edgeB, "route")):
                    new_route = scenario.link_factory(link_type="route", name=str(edgeA)+"-"+str(edgeB), s=edgeA, d=edgeB)
                    _, new_route.path = scenario.hop_count(edgeA, edgeB, allowed_nodes=AS.nodes, allowed_trunks=AS.trunks)
                    scenario.create_link(new_route)
                    
class AddToAS(tk.Toplevel):
    def __init__(self, scenario, *obj):
        super().__init__()
        self.geometry("30x65")
        self.title("Add to AS")
        self.configure(background="#A1DBCD")
        # always at least one row and one column with a weight > 0
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # List of existing AS
        self.var_AS = tk.StringVar()
        self.AS_list = ttk.Combobox(self, textvariable=self.var_AS, width=9)
        self.AS_list["values"] = [AS for AS in scenario.pn["AS"]]
        self.AS_list.current(0)
        self.AS_list.grid(row=0, column=0, columnspan=2, pady=5, padx=5, sticky="nsew")
        
        # Button to add in an AS
        self.button_add_AS = ttk.Button(self, text="Add", command=lambda: self.add_to_AS(scenario, *obj))
        ttk.Style().configure("TButton", background="#A1DBCD")
        self.button_add_AS.grid(row=1, column=0, columnspan=2, pady=5, padx=5, sticky="nsew")
        
    def add_to_AS(self, scenario, *objects):
        selected_AS = scenario.AS_factory(name=self.var_AS.get())
        selected_AS.management.add_to_AS(selected_AS, *objects)
        self.destroy()
        
# ManageAS is the window from which the user selects which AS to manage. This 
# applies only to node, since a trunk has only one domain.
class ManageAS(tk.Toplevel):
    def __init__(self, scenario, node):
        super().__init__()
        self.geometry("50x50")
        self.title("Manage AS")
        self.configure(background="#A1DBCD")
        
        # List of existing AS
        self.var_AS = tk.StringVar()
        self.AS_list = ttk.Combobox(self, textvariable=self.var_AS, width=6)
        self.AS_list["values"] = [str(AS) for AS in node.AS]
        self.AS_list.current(0)
        self.AS_list.grid(row=0, column=0, columnspan=2, pady=5, padx=5, sticky="nsew")

        # Button to open the management panel of the AS
        self.button_add_AS = ttk.Button(self, text="Add to AS", command=lambda: self.manage_AS(scenario, node))
        ttk.Style().configure("TButton", background="#A1DBCD")
        self.button_add_AS.grid(row=1, column=0, columnspan=2, pady=5, padx=5, sticky="nsew")
        
    def manage_AS(self, scenario, obj):
        selected_AS = scenario.AS_factory(name=self.var_AS.get())
        selected_AS.management.deiconify()
        self.destroy()
        
class ASCreation(tk.Toplevel):
    def __init__(self, scenario):
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
        self.button_create_AS = ttk.Button(self, text="Create AS", command=lambda: self.create_AS(scenario))
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

    def create_AS(self, scenario):
        new_AS = scenario.AS_factory(name=self.var_name.get(), type=self.var_AS_type.get(), trunks=scenario.so["link"], nodes=scenario.so["node"])
        new_AS.management = ASManagement(scenario, new_AS)
        scenario.so = {"node": set(), "link": set()}
        self.destroy()
            