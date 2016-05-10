import tkinter as tk

class AutonomousSystem(object):
    
    class_type = "AS"
    
    def __init__(self, name, type, links=set()):
        self.name = name
        self.type = type
        self.links = links
        # set the AS of the link
        for link in self.links:
            link.AS = self
        self.nodes = set()
        # at initialization, we populate the nodes set
        for link in self.links:
            self.nodes.update((link.source, link.destination))
            # and we update the nodes with its new domain
            link.source.AS.add(self)
            link.destination.AS.add(self)
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
            self.links.add(obj)
            self.nodes.update((obj.source, obj.destination)) 
            
    def add_to_edges(self, node):
        self.edges.add(node)
        
    def remove_from_edges(self, node):
        self.edges.discard(node)
                
    def remove_node_from_AS(self, node):
        self.nodes.discard(node)
        self.remove_node_from_edge(node)
            
    def remove_node_from_edge(self, node):
        if(node in AS.edges):
            self.edges.discard(node) 
        
    def remove_link_from_AS(self, link):
        if(link.AS):
            self.links.discard(link)
        
class Area(AutonomousSystem):
    
    class_type = "area"
    
    def __init__(self, name, type="links"):
        self.name = name
        self.type = type
        
# TODO faire une classe de custom widget 
class CustomListbox(tk.Listbox):
    def __contains__(self, str):
        return str in self.get(0, "end")

class ASCreation(tk.Toplevel):
    def __init__(self, scenario):
        super().__init__()
        self.geometry("130x110")
        self.title("Create AS")
        
        # List of AS type
        self.var_AS_type = tk.StringVar()
        self.var_AS_type.set("RIP")
        self.choice_AS_type = ["RIP", "IS-IS", "OSPF", "MPLS", "RSTP"]
        self.AS_type_list = tk.OptionMenu(self, self.var_AS_type, *self.choice_AS_type)
        
        # retrieve and save node data
        self.button_create_AS = tk.Button(self, text="Create AS", command=lambda: self.create_AS(scenario))
        
        # Label for the name/type of the AS
        self.label_name = tk.Label(self, text = "Name")
        self.label_type = tk.Label(self, text = "Type")
        # Entry box for the name of the AS
        self.var_name = tk.StringVar()
        self.entry_name  = tk.Entry(self, textvariable=self.var_name, width=10)
        
        self.label_name.grid(row=0, column=0, pady=5, padx=5, sticky=tk.W)
        self.entry_name.grid(row=0, column=1, sticky=tk.W)
        self.label_type.grid(row=1, column=0, pady=5, padx=5, sticky=tk.W)
        self.AS_type_list.grid(row=1,column=1, pady=5, padx=5, sticky=tk.W)
        self.button_create_AS.grid(row=3,column=0, columnspan=2, pady=5, padx=5)

    def create_AS(self, scenario):
        new_AS = scenario.AS_factory(name=self.var_name.get(), type=self.var_AS_type.get(), links=scenario._selected_objects["link"])
        new_AS.management = ASManagement(scenario, new_AS)
        scenario._selected_objects = {"node": set(), "link": set()}
        self.destroy()

class ASManagement(tk.Toplevel):
    def __init__(self, scenario, AS):
        super().__init__()
        self.geometry("400x300")
        self.title("Manage AS")
        
        # object selected by the user in a listbox
        self.selected_object = None
        
        # this allows to change the behavior of closing the window. 
        # I don't want the window to be destroyed, simply hidden
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        
        # listbox of all AS objects
        self.label_links = tk.Label(self, text = "Domain links")
        self.listbox_links = CustomListbox(self, width=15, height=7)
        for trunk in AS.links:
            self.listbox_links.insert(tk.END, trunk)
        
        self.label_nodes = tk.Label(self, text = "Domain nodes")
        self.listbox_nodes = CustomListbox(self, width=15, height=7)
        for node in AS.nodes:
            self.listbox_nodes.insert(tk.END, node)
            
        self.label_edges = tk.Label(self, text = "Domain edges")
        self.listbox_edges = CustomListbox(self, width=15, height=7)
        
        # create a vertical scrollbar to the right of the listbox for nodes and links
        self.yscroll_links = tk.Scrollbar(self, command=self.listbox_links.yview, orient=tk.VERTICAL)
        self.listbox_links.configure(yscrollcommand=self.yscroll_links.set)
        # self.listbox_links.bind("<<ListboxSelect>>", self.select_object)
        
        self.yscroll_nodes = tk.Scrollbar(self, command=self.listbox_nodes.yview, orient=tk.VERTICAL)
        self.listbox_nodes.configure(yscrollcommand=self.yscroll_nodes.set)
        # self.listbox_nodes.bind("<<ListboxSelect>>", self.select_object)
        
        self.yscroll_edges = tk.Scrollbar(self, command=self.listbox_edges.yview, orient=tk.VERTICAL)
        self.listbox_edges.configure(yscrollcommand=self.yscroll_edges.set)
        # self.listbox_edges.bind("<<ListboxSelect>>", self.select_object)
        
        # find edge nodes of the AS
        self.button_find_edge_nodes = tk.Button(self, text="Find edge nodes", command=lambda: self.find_edge_nodes(scenario, AS))
        self.button_create_route = tk.Button(self, text="Create route", command=lambda: self.create_routes(scenario, AS))
        
        # operation on nodes
        self.button_remove_node_from_AS = tk.Button(self, text="Remove from AS", command=lambda: self.remove_selected_node_from_AS(scenario, AS))
        self.button_add_to_edges = tk.Button(self, text="Add to edges", command=lambda: self.add_to_edges(scenario, AS))
        self.button_remove_from_edges = tk.Button(self, text="Remove from edges", command=lambda: self.remove_from_edges(scenario, AS))
        
        # button for manage AS panel to grab focus
        self.var_focus = tk.IntVar()
        self.var_focus.set(0)
        self.checkbutton_focus = tk.Checkbutton(self, text="Focus", variable=self.var_focus, command=self.change_focus)
                
        # place the widget in the grid
        self.label_links.grid(row=0, column=0)
        self.label_nodes.grid(row=0, column=2)
        self.label_edges.grid(row=0, column=4)
        self.listbox_links.grid(row=1, column=0)
        self.yscroll_links.grid(row=1, column=1, sticky=tk.N+tk.S)
        self.listbox_nodes.grid(row=1, column=2)
        self.yscroll_nodes.grid(row=1, column=3, sticky=tk.N+tk.S)
        self.listbox_edges.grid(row=1, column=4)
        self.yscroll_edges.grid(row=1, column=5, sticky=tk.N+tk.S)
        
        self.button_create_route.grid(row=3, column=0, columnspan=2)
        
        # button under the nodes column
        self.button_remove_node_from_AS.grid(row=3, column=2, columnspan=2)
        self.button_add_to_edges.grid(row=4, column=2, columnspan=2)
        self.button_remove_from_edges.grid(row=5, column=2, columnspan=2)
        self.checkbutton_focus.grid(row=4, column=0, columnspan=2)
        
        # button under the edge column
        self.button_find_edge_nodes.grid(row=3, column=4, columnspan=2)
        self.button_remove_from_edges.grid(row=4, column=4, columnspan=2)
        
        # find the edges at initialization
        self.find_edge_nodes(scenario, AS)
        
    # function to change the focus
    def change_focus(self):
        self.wm_attributes('-topmost', self.var_focus.get())
        
    # function to retrieve the select object in a listbox
    def select_object(self, event):
        self.selected_object = self.listbox_links.get(self.listbox_links.curselection())  
        
    def add_to_edges(self, scenario, AS):
        self.selected_node = self.listbox_nodes.get(self.listbox_nodes.curselection())
        if(self.selected_node not in AS.management.listbox_edges):
            AS.management.listbox_edges.insert(tk.END, self.selected_node) 
        self.selected_node = scenario.node_factory(name=self.selected_node)
        AS.add_to_edges(self.selected_node)
            
    def remove_from_edges(self, scenario, AS):
        self.selected_edge = self.listbox_edges.get(self.listbox_edges.curselection())
        index_edge = self.listbox_edges.get(0, tk.END).index(self.selected_edge)
        self.listbox_edges.delete(index_edge)
        self.selected_edge = scenario.node_factory(name=self.selected_edge) 
        AS.remove_from_edges(self.selected_edge)
        
    def add_to_AS(self, AS, *objects):
        for obj in objects:
            if(obj.class_type == "node"):
                if obj not in AS.nodes:
                    AS.management.listbox_nodes.insert(tk.END, obj)
            else:
                if obj not in AS.links:
                    AS.management.listbox_links.insert(tk.END, obj)
            AS.add_to_AS(obj)
        
    def find_edge_nodes(self, scenario, AS):
        self.listbox_edges.delete(0, tk.END)
        for edge in scenario.find_edge_nodes(AS):
            self.listbox_edges.insert(tk.END, edge)
            
    def remove_nodes_from_AS(self, AS, *nodes):
        for node in nodes:
            # remove the node from the AS management panel, in the nodes
            # listbox as well as in the edge listbox
            index_node = self.listbox_nodes.get(0, tk.END).index(repr(node))
            self.listbox_nodes.delete(index_node)
            if(node in AS.edges):
                index_edge = self.listbox_edges.get(0, tk.END).index(repr(node))
                self.listbox_edges.delete(index_edge)
            AS.remove_node_from_AS(node, AS)
            
    def remove_selected_node_from_AS(self, scenario, AS):
        self.selected_node = self.listbox_nodes.get(self.listbox_nodes.curselection()) 
        self.selected_node = scenario.node_factory(name=self.selected_node)
        self.remove_nodes_from_AS(AS, self.selected_node)
        
    def remove_links_from_AS(self, *links):
        for link in links:
            # remove the link from the AS management panel, in the links listbox
            index_link = self.listbox_links.get(0, tk.END).index(repr(link))
            self.listbox_links.delete(index_link)
            # update the AS topology in the network
            AS.remove_link_from_AS(link)
    
    # TODO les liens utilisés DOIVENT appartenir à l'AS
    # modify hopcount to have  a list of allowed links and allowed nodes
    def create_routes(self, scenario, AS):
        for edgeA in AS.edges:
            for edgeB in AS.edges:
                if(edgeA != edgeB and not scenario.is_connected(edgeA, edgeB, "route")):
                    new_route = scenario.link_factory(link_type="route", name=str(edgeA)+"-"+str(edgeB), s=edgeA, d=edgeB)
                    new_route.AS = AS
                    _, new_route.path = scenario.hop_count(edgeA, edgeB)
                    scenario.create_link(new_route)
                    
class AddToAS(tk.Toplevel):
    def __init__(self, scenario, *obj):
        super().__init__()
        self.geometry("50x50")
        self.title("Add node to AS")
        
        # List of existing AS
        self.var_AS = tk.StringVar()
        self.existing_AS = [AS for AS in scenario.pool_network["AS"]]
        self.AS_list = tk.OptionMenu(self, self.var_AS, *self.existing_AS if self.existing_AS else [""])
        self.AS_list.grid(row=0, column=0, sticky=tk.W)
        
        # Button to add in an AS
        self.button_add_AS = tk.Button(self, text="Add to AS", command=lambda: self.add_to_AS(scenario, *obj))
        self.button_add_AS.grid(row=0, column=1, sticky=tk.W)
        
    def add_to_AS(self, scenario, *objects):
        selected_AS = scenario.AS_factory(name=self.var_AS.get())
        selected_AS.management.add_to_AS(selected_AS, *objects)
        self.destroy()
        
# ManageAS is the window from which the user selects which AS to manage. This 
# applies only to node, since a link has only one domain.
class ManageAS(tk.Toplevel):
    def __init__(self, scenario, node):
        super().__init__()
        self.geometry("50x50")
        self.title("Manage AS")
        
        # List of existing AS
        self.var_AS = tk.StringVar()
        self.node_AS = [AS for AS in node.AS]
        self.AS_list = tk.OptionMenu(self, self.var_AS, *self.node_AS)
        self.AS_list.grid(row=0, column=0, sticky=tk.W)
        
        # Button to open the management panel of the AS
        self.button_add_AS = tk.Button(self, text="Add to AS", command=lambda: self.manage_AS(scenario, node))
        self.button_add_AS.grid(row=0, column=1, sticky=tk.W)
        
    def manage_AS(self, scenario, obj):
        selected_AS = scenario.AS_factory(name=self.var_AS.get())
        selected_AS.management.deiconify()
        self.destroy()
            