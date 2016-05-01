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
        self.area = {Area("backbone", objects=self.links)}
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
        
class Area(object):
    
    class_type = "area"
    
    def __init__(self, name, type="links", objects=set()):
        self.name = name
        self.type = type
        self.objects = objects
        
    def __repr__(self):
        return self.name
        
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name
        
    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __hash__(self):
        return hash(self.name)
        
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
        self.listbox_links = CustomListbox(self, width=15, height=7)
        for trunk in AS.links:
            self.listbox_links.insert(tk.END, trunk)
        
        self.listbox_nodes = CustomListbox(self, width=15, height=7)
        for node in AS.nodes:
            self.listbox_nodes.insert(tk.END, node)
            
        self.listbox_edges = CustomListbox(self, width=15, height=7)
        
        # create a vertical scrollbar to the right of the listbox for nodes and links
        self.yscroll_links = tk.Scrollbar(self, command=self.listbox_links.yview, orient=tk.VERTICAL)
        self.listbox_links.configure(yscrollcommand=self.yscroll_links.set)
        self.listbox_links.bind("<<ListboxSelect>>", self.select_object)
        
        self.yscroll_nodes = tk.Scrollbar(self, command=self.listbox_nodes.yview, orient=tk.VERTICAL)
        self.listbox_nodes.configure(yscrollcommand=self.yscroll_nodes.set)
        self.listbox_nodes.bind("<<ListboxSelect>>", self.select_object)
        
        self.yscroll_edges = tk.Scrollbar(self, command=self.listbox_edges.yview, orient=tk.VERTICAL)
        self.listbox_edges.configure(yscrollcommand=self.yscroll_edges.set)
        self.listbox_edges.bind("<<ListboxSelect>>", self.select_object)
        
        # find edge nodes of the AS
        self.button_find_edge_nodes = tk.Button(self, text="Find edge nodes", command=lambda: self.find_edge_nodes(scenario, AS))
        self.button_create_route = tk.Button(self, text="Create route", command=lambda: self.create_route(scenario, AS))
        
        # button for manage AS panel to grab focus
        self.var_focus = tk.IntVar()
        self.var_focus.set(0)
        self.checkbutton_focus = tk.Checkbutton(self, text="Focus", variable=self.var_focus, command=self.change_focus)
                
        # place the widget in the grid
        self.listbox_links.grid(row=0, column=0)
        self.yscroll_links.grid(row=0, column=1, sticky=tk.N+tk.S)
        self.listbox_nodes.grid(row=0, column=2)
        self.yscroll_nodes.grid(row=0, column=3, sticky=tk.N+tk.S)
        self.listbox_edges.grid(row=0, column=4)
        self.yscroll_edges.grid(row=0, column=5, sticky=tk.N+tk.S)
        self.button_find_edge_nodes.grid(row=1, column=0, columnspan=2)
        self.button_create_route.grid(row=2, column=0, columnspan=2)
        self.checkbutton_focus.grid(row=3, column=0, columnspan=2)
        self.find_edge_nodes(scenario, AS)
        
    # function to change the focus
    def change_focus(self):
        self.wm_attributes('-topmost', self.var_focus.get())
        
    def select_object(self, event):
        self.selected_object = self.listbox_links.get(self.listbox_links.curselection())  
        
    def find_edge_nodes(self, scenario, AS):
        for edge in scenario.find_edge_nodes(AS):
            if repr(edge) not in self.listbox_edges:
                self.listbox_edges.insert(tk.END, edge)
    
    # TODO les liens utilisés DOIVENT appartenir à l'AS
    def create_route(self, scenario, AS):
        for edgeA in AS.edges:
            for edgeB in AS.edges:
                if(edgeA != edgeB and not scenario.is_connected(edgeA, edgeB, "route")):
                    new_route = scenario.link_factory(link_type="route", name=str(edgeA)+"-"+str(edgeB), s=edgeA, d=edgeB)
                    new_route.AS = AS
                    _, new_route.path = scenario.hop_count(edgeA, edgeB)
                    scenario.create_link(new_route)