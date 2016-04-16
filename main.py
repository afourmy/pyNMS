path_app = "C:\\Users\\afourmy\\Desktop\\Sauvegarde\\Python\\Network"

# add the path to the module in sys.path
import sys
if path_app not in sys.path:
    sys.path.append(path_app)

import tkinter as tk
import network
import collections
import random
import node
import link
import LSP
import math

class NetworkSimulator(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
            
        # ----- Programme principal : -----
        self.title("Network simulator")
    
        # ----- Menus : -----
        menubar = tk.Menu(self)
        main_menu = tk.Menu(menubar, tearoff=0)
        main_menu.add_command(label="Graph creation", command=lambda: self.modify_graph())
        main_menu.add_command(label="Flow creation", command=lambda: self.nothing())
        main_menu.add_separator()
        main_menu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="Main",menu=main_menu)
        menu_drawing = tk.Menu(menubar, tearoff=0)
        menu_drawing.add_command(label="Force-based drawing", command=lambda: self.graph_layout())
        menu_drawing.add_command(label="Random drawing", command=lambda: self.random_drawing())
        menubar.add_cascade(label="Network drawing",menu=menu_drawing)
        menu_routing = tk.Menu(menubar, tearoff=0)
        menu_routing.add_command(label="Find path", command=lambda: self.graph_path())
        menu_routing.add_command(label="Route flows", command=lambda: self.nothing())
        menubar.add_cascade(label="Network routing",menu=menu_routing)
        menu_options = tk.Menu(menubar, tearoff=0)
        menu_options.add_command(label="Label display", command=lambda: self.label_display())
        menubar.add_cascade(label="Options",menu=menu_options)
        
        self.config(menu=menubar)
    
        # create a canvas
        self.canvas = tk.Canvas(width=900, height=900, background="bisque")
        self.canvas.pack(fill="both", expand=True)

        # this data is used to keep track of an item being dragged
        self._drag_data = {"x": 0, "y": 0, "item": None}
        self._job = None
        self.node_id_to_node = {}
        self.link_id_to_trunk = {}
        self.attached_link = collections.defaultdict(set)
        self.link_info = {}
        self.node_to_label_id = {}
        self.link_to_label_id = {}        
        
        # default colors for highlighting areas
        self.default_colors = ["white", "black", "red", "green", "blue", "cyan", "yellow", "magenta"]

        # use the right-click to move the background
        self.canvas.bind("<ButtonPress-3>", self.scroll_start)
        self.canvas.bind("<B3-Motion>", self.scroll_move)
        
        # add bindings for clicking, dragging and releasing over nodes with "token" tag
        self.canvas.tag_bind("token", "<ButtonPress-1>", self.find_closest)
        self.canvas.tag_bind("token", "<ButtonRelease-1>", self.release_node)
        self.canvas.tag_bind("token", "<B1-Motion>", self.node_motion)
        
    def scroll_start(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        
    # cancel the on-going job (e.g graph drawing)
    def _cancel(self):
        if self._job is not None:
            app.after_cancel(self._job)
            self._job = None

    def _create_token(self, coord, color):
        (x,y) = coord
        return self.canvas.create_oval(x-3, y-3, x+3, y+3, outline=color, fill=color, tags=("token"))
    
    def _create_node_label(self, node):
        label_id = self.canvas.create_text(node.x + 5, node.y + 5, anchor="nw")
        self.canvas.itemconfig(label_id, text=node.name, fill="blue")
        self.node_to_label_id[node] = label_id
    
    def _create_link_label(self, link):
        middle_x = link.source.x + (link.destination.x - link.source.x)//2
        middle_y = link.source.y + (link.destination.y - link.source.y)//2
        diff_x = abs(link.source.x - link.destination.x)
        label_id = self.canvas.create_text(middle_x, middle_y, anchor="nw", fill="red")
        self.canvas.itemconfig(label_id, text=link.capacity)
        self.link_to_label_id[link] = label_id
        
    def find_closest(self, event):
        # record the item and its location
        self._cancel()
        self._drag_data["item"] = self.canvas.find_closest(event.x, event.y)[0]
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def release_node(self, event):
        # reset the drag information
        self._drag_data["item"] = None
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0

    def node_motion(self, event):
        # compute how much this object has moved
        item = self._drag_data["item"]
        delta_x = event.x - self._drag_data["x"]
        delta_y = event.y - self._drag_data["y"]
        
        # move the object the appropriate amount
        self.canvas.move(item, delta_x, delta_y)
        
        # record the new position
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        node = self.node_id_to_node[item]
        
        # update coordinates of the node object
        node.x = event.x
        node.y = event.y
        
        # update node label coordinates
        self.canvas.coords(self.node_to_label_id[node], node.x + 5, node.y + 5)
        
        # update links coordinates
        for link in self.attached_link[node]:
            coords = self.canvas.coords(link.line)
            if(self.link_info[link][0] == node):
                coords[0] += delta_x
                coords[1] += delta_y
            else:
                coords[2] += delta_x
                coords[3] += delta_y
            self.canvas.coords(link.line, *coords)
            
            # update link label coordinates
            middle_x = link.source.x + (link.destination.x - link.source.x)//2
            middle_y = link.source.y + (link.destination.y - link.source.y)//2
            diff_x = abs(link.source.x - link.destination.x)
            self.canvas.coords(self.link_to_label_id[link], middle_x + 5*(diff_x < 10), middle_y)
            
    def random_drawing(self):
        self._cancel()
        self.canvas.delete("all")
        for n in ntw.nodes:
            n.x, n.y = random.randint(100,700), random.randint(100,700)
            n.oval = self._create_token((n.x, n.y), "black")
            self.node_id_to_node[n.oval] = n
            self._create_node_label(n)
            
        for t in ntw.trunks:
            t.line = self.canvas.create_line(t.source.x, t.source.y, t.destination.x, t.destination.y, tags=t.name, width=2)
            self._create_link_label(t)
            self.link_id_to_trunk[t.line] = t
            self.attached_link[t.source].add(t)
            self.attached_link[t.destination].add(t)
            self.link_info[t] = [t.source, t.destination]
            
    def unhighlight(self):
        for link in ntw.trunks:
            self.canvas.itemconfig(link.line, fill="black", width=2)
            
    def label_display(self):
        graph_label_window = tk.Toplevel()
        graph_label_window.geometry("600x300")
        graph_label_window.title("Modify the label display")
        
        var_label = tk.StringVar(graph_label_window)
        # by default, the cost is displayed
        var_label.set('cost')
        choices = ["cost", "capacity"]
        
        label_options = tk.OptionMenu(graph_label_window, var_label, *choices)
        select_label = tk.Button(graph_label_window, text="Apply", command=lambda: select_label(self))
        label_options.grid(row=1, column=0, sticky=tk.W)
        select_label.grid(row=1, column=1, sticky=tk.W)
        
        def select_label(self):
            label = var_label.get()
            for link in ntw.trunks:
                test = eval("link." + label)
                self.canvas.itemconfig(self.link_to_label_id[link], text=test)
            
    def graph_path(self):
        graph_path_window = tk.Toplevel()
        graph_path_window.geometry("600x400")
        graph_path_window.title("Find the shortest path")
        
        # label with the path as a variable
        var_path_found = tk.StringVar()
        var_path_found.set("")
        label_path_found = tk.Label(graph_path_window, textvariable = var_path_found)
        
        # Label for source, destination, excluded nodes/links and path constraints
        label_source_node = tk.Label(graph_path_window, text = "Source node")
        label_destination_node = tk.Label(graph_path_window, text = "Destination node")
        label_excluded_links = tk.Label(graph_path_window, text = "Excluded links")
        label_excluded_nodes = tk.Label(graph_path_window, text = "Excluded nodes")
        label_path_constraints = tk.Label(graph_path_window, text = "Path constraints")
        label_LSP_name = tk.Label(graph_path_window, text = "LSP name")
        
        # Entry boxes and textvar for all parameters / constraints
        var_source_node = tk.StringVar()
        var_source_node.set("")
        var_destination_node = tk.StringVar()
        var_destination_node.set("")
        var_excluded_links = tk.StringVar()
        var_excluded_links.set("")
        var_excluded_nodes = tk.StringVar()
        var_excluded_nodes.set("")
        var_path_constraints = tk.StringVar()
        var_path_constraints.set("")
        var_LSP_name = tk.StringVar()
        var_LSP_name.set("")
        entry_source_node  = tk.Entry(graph_path_window, text=var_source_node, width=15)
        entry_destination_node = tk.Entry(graph_path_window, text=var_destination_node, width=15)
        entry_excluded_links = tk.Entry(graph_path_window, text=var_excluded_links, width=15)
        entry_excluded_nodes = tk.Entry(graph_path_window, text=var_excluded_nodes, width=15)
        entry_path_constraints = tk.Entry(graph_path_window, text=var_path_constraints, width=15)
        entry_LSP_name = tk.Entry(graph_path_window, text=var_LSP_name, width=15)
        
        button_compute_path = tk.Button(graph_path_window, text='Compute path', command = lambda: find_path(), width=12, height=1)
        button_highlight_path = tk.Button(graph_path_window, text='Highlight path', command = lambda: highlight_path(self), width=12, height=1)
        button_unhighlight = tk.Button(graph_path_window, text='Remove highlight', command = lambda: self.unhighlight(), width=12, height=1)
        button_reset = tk.Button(graph_path_window, text='Reset fields', command = lambda: reset_fields(), width=12, height=1)
        button_create_LSP = tk.Button(graph_path_window, text='Create LSP', command = lambda: create_LSP(), width=12, height=1)
        button_flow = tk.Button(graph_path_window, text='flow', command = lambda: flow(), width=12, height=1)
        
        # List of LSP
        var_LSP = tk.StringVar()
        var_LSP.set("")
        choices = [LSP for LSP in ntw.LSPs] or [""]
        LSP_list = tk.OptionMenu(graph_path_window, var_LSP, *choices)
        button_select_LSP = tk.Button(graph_path_window, text="Select LSP", command=lambda: select_LSP(var_LSP))
        
        label_source_node.grid(row=0, column=0, pady=5, padx=5, sticky=tk.W)
        label_destination_node.grid(row=1, column=0, pady=5, padx=5, sticky=tk.W)
        label_excluded_links.grid(row=2, column=0, pady=5, padx=5, sticky=tk.W)
        label_excluded_nodes.grid(row=3, column=0, pady=5, padx=5, sticky=tk.W)
        label_path_constraints.grid(row=4, column=0, pady=5, padx=5, sticky=tk.W)
        label_LSP_name.grid(row=7, column=0, pady=5, padx=5, sticky=tk.W)
        
        entry_source_node.grid(row=0, column=1, sticky=tk.W)
        entry_destination_node.grid(row=1, column=1, sticky=tk.W)
        entry_excluded_links.grid(row=2, column=1, sticky=tk.W)
        entry_excluded_nodes.grid(row=3, column=1, sticky=tk.W)
        entry_path_constraints.grid(row=4, column=1, sticky=tk.W)
        entry_LSP_name.grid(row=7, column=1, sticky=tk.W)
        
        button_compute_path.grid(row=5,column=0, pady=5, padx=5, sticky=tk.W)
        button_highlight_path.grid(row=5,column=1, pady=5, padx=5, sticky=tk.W)
        button_unhighlight.grid(row=6,column=0, pady=5, padx=5, sticky=tk.W)
        button_reset.grid(row=6,column=1, pady=5, padx=5, sticky=tk.W)
        button_create_LSP.grid(row=7,column=2, pady=5, padx=5, sticky=tk.W)
        
        label_path_found.grid(row=6,column=0, pady=5, padx=5, sticky=tk.W)
        LSP_list.grid(row=8, column=0, sticky=tk.W)
        button_select_LSP.grid(row=8, column=1, sticky=tk.W)
        button_flow.grid(row=10, column=0, sticky=tk.W)
        
        def select_LSP(LSP):
            current_LSP = ntw.LSP_factory(LSP.get())
            if(current_LSP.name):
                var_source_node.set(current_LSP.ingress)
                var_destination_node.set(current_LSP.egress)
                var_excluded_links.set(",".join(map(str,current_LSP.excluded_trunks)).replace("-",""))
                var_excluded_nodes.set(",".join(map(str,current_LSP.excluded_nodes)))
                var_path_constraints.set(",".join(map(str,current_LSP.path_constraints)))
                var_LSP_name.set(current_LSP.name)
        
        def reset_fields():
            var_source_node.set("")
            var_destination_node.set("")
            var_excluded_links.set("")
            var_excluded_nodes.set("")
            var_path_constraints.set("")
            var_LSP_name.set("")
        
        def get_user_input():
            source = node.Node(entry_source_node.get())
            destination = node.Node(entry_destination_node.get())
            excluded_links = filter(None, entry_excluded_links.get().split(","))
            excluded_nodes = filter(None, entry_excluded_nodes.get().split(","))
            path_constraints = filter(None, entry_path_constraints.get().split(","))
            if(excluded_links):
                l_excluded_links = [ntw.trunk_factory(node.Node(t[0]),node.Node(t[1])) for t in excluded_links]
            if(excluded_nodes):
                l_excluded_nodes = [node.Node(n) for n in excluded_nodes]
            if(path_constraints):
                l_path_constraints = [node.Node(n) for n in path_constraints]
            return (source, destination, l_excluded_links, l_excluded_nodes, l_path_constraints)
        
        def find_path():
            ntw.current_path = ntw.hop_count(*get_user_input())
            var_path_found.set(ntw.current_path)
            
        def create_LSP():
            name = entry_LSP_name.get()
            new_LSP = ntw.LSP_factory(name, *get_user_input())
            LSP_list["menu"].add_command(label=new_LSP, command=tk._setit(var_LSP, new_LSP.name))

        def highlight_path(self):
            self.unhighlight()
            path = ntw.current_path
            for segment in zip(path, path[1:]):
                link = ntw.trunk_factory(*segment)
                self.canvas.itemconfig(link.line, fill="red", width=5)
                
        def flow():
            ntw.ford_fulkerson(node.Node(entry_source_node.get()), node.Node(entry_destination_node.get()))
                
    def modify_graph(self):
        newfenetre = tk.Toplevel()
        newfenetre.geometry("600x300")
        newfenetre.title("Create or modify the graph")
    
        # affichage des paths définis par l'utilisateur. Affichage par défaut: valeur des global variables associées.
        Var_add_nodes = tk.StringVar()
        Var_add_nodes.set("")
        entry_add_nodes = tk.Entry(newfenetre, textvariable= Var_add_nodes, width=80)
        
        Var_add_links = tk.StringVar()
        Var_add_links.set("")
        entry_add_links = tk.Entry(newfenetre, textvariable = Var_add_links, width=80)
        
        Var_fast_creation = tk.StringVar()
        Var_fast_creation.set("")
        entry_fast_creation = tk.Entry(newfenetre, textvariable = Var_fast_creation, width=80)
        
        var_meshed_square = tk.IntVar()
        var_meshed_square.set("3")
        entry_meshed_square = tk.Entry(newfenetre, textvariable = var_meshed_square, width=15)
        
        var_hypercube = tk.IntVar()
        var_hypercube.set("3")
        entry_hypercube = tk.Entry(newfenetre, textvariable = var_hypercube, width=15)
        
        # selection des paths par l'utilisateur
        bouton_add_nodes = tk.Button(newfenetre, text='Add nodes', command = lambda: add_nodes(), width=12, height=1)
        bouton_add_links = tk.Button(newfenetre, text='Add links', command = lambda: add_links(), width=12, height=1)
        bouton_fast_creation = tk.Button(newfenetre, text='Fast creation', command = lambda: automatic_graph_creation(), width=12, height=1)
        bouton_erase_graph = tk.Button(newfenetre, text='Erase graph', command = lambda: erase_graph(self), width=12, height=1)
        bouton_connex = tk.Button(newfenetre, text='Find connected components', command = lambda: ntw.connected_components(), width=12, height=1)
        bouton_meshed_square = tk.Button(newfenetre, text='Meshed square', command = lambda: meshed_square(self), width=12, height=1)
        bouton_hypercube = tk.Button(newfenetre, text='Hypercube', command = lambda: hypercube(self), width=12, height=1)
        bouton_highlight_connected_components = tk.Button(newfenetre, text='Highlight connected components', command = lambda: highlight_connected_components(self), width=12, height=1)
        
        # affichage des boutons / label dans la grille
        bouton_add_nodes.grid(row=0,column=0, pady=5, padx=5, sticky=tk.W)
        bouton_add_links.grid(row=1,column=0, pady=5, padx=5, sticky=tk.W)
        bouton_fast_creation.grid(row=2,column=0, pady=5, padx=5, sticky=tk.W)
        entry_add_nodes.grid(row=0, column=1, sticky=tk.W)
        entry_add_links.grid(row=1, column=1, sticky=tk.W)
        entry_fast_creation.grid(row=2, column=1, sticky=tk.W)
        bouton_meshed_square.grid(row=6,column=0, pady=5, padx=5, sticky=tk.W)
        entry_meshed_square.grid(row=6, column=1, sticky=tk.W)
        bouton_hypercube.grid(row=7,column=0, pady=5, padx=5, sticky=tk.W)
        entry_hypercube.grid(row=7, column=1, sticky=tk.W)
        bouton_erase_graph.grid(row=8,column=0, pady=5, padx=5, sticky=tk.W)
        bouton_connex.grid(row=9,column=0, pady=5, padx=5, sticky=tk.W)
        bouton_highlight_connected_components.grid(row=10,column=0, pady=5, padx=5, sticky=tk.W)
        
        # label qui affiche ntw.graph
        string_graph = tk.StringVar()
        string_graph.set("")
        label_graph = tk.Label(newfenetre, textvariable=string_graph)
        label_graph.grid(row=9, column=1, pady=5, padx=5, sticky=tk.W)
        
        # nodes and links of the graph
        string_nodes = tk.StringVar()
        string_nodes.set("")
        label_nodes = tk.Label(newfenetre, textvariable=string_nodes)
        label_nodes.grid(row=10, column=1, pady=5, padx=5, sticky=tk.W)
        string_links = tk.StringVar()
        string_links.set("")
        label_links = tk.Label(newfenetre, textvariable=string_links)
        label_links.grid(row=11, column=1, pady=5, padx=5, sticky=tk.W)
        string_connected_components = tk.StringVar()
        string_connected_components.set("")
        label_connected_components = tk.Label(newfenetre, textvariable=string_connected_components)
        label_connected_components.grid(row=12, column=0, pady=5, padx=5, sticky=tk.W)
        
        def update_graph():
            string_graph.set(str(ntw.graph))
            string_nodes.set(str(ntw.nodes))
            string_links.set(str(ntw.trunks))
                
        def add_nodes():
            user_input = entry_add_nodes.get().replace(" ","")
            for s in user_input.split(","):
                ntw.add_nodes(node.Node(s))
            update_graph()
            
        def add_links():
            user_input = entry_add_links.get().replace(" ","")
            for s in user_input.split(","):
                source, destination = s.split(".")
                ntw.add_trunks(ntw.trunk_factory(node.Node(source), node.Node(destination)))
            update_graph()
            
        def erase_graph(self):
            ntw.clear()
            self._drag_data = {"x": 0, "y": 0, "item": None}
            self.node_id_to_node = {}
            self.link_id_to_trunk = {}
            self.attached_link = collections.defaultdict(set)
            self.link_info = {}
            self.node_to_label_id = {}
            
        def automatic_graph_creation():
            user_input = entry_fast_creation.get().replace(" ","")
            ntw.fast_graph_definition(user_input)
            update_graph()
            
        def highlight_connected_components(self):
            self.unhighlight()
            connected_components = ntw.connected_components()
            for idx, connex_set in enumerate(connected_components):
                for n in connex_set:
                    for link in self.attached_link[n]:
                        self.canvas.itemconfig(link.line, fill=self.default_colors[idx], width=2)
            
        def meshed_square(self):
            erase_graph(self)
            ntw.generate_meshed_square(int(entry_meshed_square.get()))
            update_graph()
            
        def hypercube(self):
            erase_graph(self)
            ntw.generate_hypercube(int(entry_hypercube.get()))
            update_graph()
            
    def graph_layout(self):        
        newfenetre = tk.Toplevel()
        newfenetre.geometry("600x300")
        newfenetre.title("Graph drawing with force-directed algorithms")
        ender_variables = []
    
        # Variables de masse
        # Alpha
        label_alpha = tk.Label(newfenetre, text = "Alpha")
        var_alpha = tk.DoubleVar()
        var_alpha.set(1.0)
        ender_variables.append(var_alpha)
        entry_alpha = tk.Entry(newfenetre, textvariable=var_alpha, width=15)
        
        # Beta
        label_beta = tk.Label(newfenetre, text = "Beta")
        var_beta = tk.IntVar()
        var_beta.set(100000)
        ender_variables.append(var_beta)
        entry_beta = tk.Entry(newfenetre, textvariable = var_beta, width=15)
        
        # k
        label_k = tk.Label(newfenetre, text = "k")
        var_k = tk.DoubleVar()
        var_k.set(0.5)
        ender_variables.append(var_k)
        entry_k = tk.Entry(newfenetre, textvariable = var_k, width=15)
        
        # Variables de dumping
        # Eta
        label_eta = tk.Label(newfenetre, text = "Eta")
        var_eta = tk.DoubleVar()
        var_eta.set(0.5)
        ender_variables.append(var_eta)
        entry_eta = tk.Entry(newfenetre, textvariable = var_eta, width=15)
        
        # Delta
        label_delta = tk.Label(newfenetre, text = "Delta")
        var_delta = tk.DoubleVar()
        var_delta.set(0.35)
        ender_variables.append(var_delta)
        entry_delta = tk.Entry(newfenetre, textvariable = var_delta, width=15)
        
        # optimal pairwise distance
        label_opd = tk.Label(newfenetre, text = "Optimal pairwise distance")
        var_opd = tk.DoubleVar()
        initialize_opd = str(math.sqrt(500*500/len(ntw.nodes))) if ntw.nodes else 0
        var_opd.set(initialize_opd )
        entry_opd = tk.Entry(newfenetre, textvariable = var_opd, width=15)
        
        # Raideur du ressort d
        label_raideur = tk.Label(newfenetre, text = "Raideur")
        var_raideur = tk.DoubleVar()
        var_raideur.set(1.0)
        ender_variables.append(var_raideur)
        entry_raideur = tk.Entry(newfenetre, textvariable=var_raideur, width=15)
        
        # drawing button
        bouton_force_based = tk.Button(newfenetre, text="Force-based", command = lambda: basic(self), width=18, height=1)
        bouton_reingold = tk.Button(newfenetre, text="Fruchtemann-reingold", command = lambda: frucht(self), width=18, height=1)
        bouton_random = tk.Button(newfenetre, text="Random drawing", command = lambda: self.random_drawing(), width=18, height=1)
        bouton_stop = tk.Button(newfenetre, text="Stop drawing", command = lambda: self._cancel(), width=18, height=1)
        
        # affichage des boutons / label dans la grille
        label_alpha.grid(row=0, column=0, pady=5, padx=5, sticky=tk.W)
        entry_alpha.grid(row=0, column=1, sticky=tk.W)
        label_beta.grid(row=1, column=0, pady=5, padx=5, sticky=tk.W)
        entry_beta.grid(row=1, column=1, sticky=tk.W)
        label_k.grid(row=2, column=0, pady=5, padx=5, sticky=tk.W)
        entry_k.grid(row=2, column=1, sticky=tk.W)
        label_eta.grid(row=3, column=0, pady=5, padx=5, sticky=tk.W)
        entry_eta.grid(row=3, column=1, sticky=tk.W)
        label_delta.grid(row=4, column=0, pady=5, padx=5, sticky=tk.W)
        entry_delta.grid(row=4, column=1, sticky=tk.W)
        label_raideur.grid(row=5, column=0, pady=5, padx=5, sticky=tk.W)
        entry_raideur.grid(row=5, column=1, sticky=tk.W)
        label_opd.grid(row=0, column=2, pady=5, padx=5, sticky=tk.W)
        entry_opd.grid(row=0, column=3, sticky=tk.W)

        bouton_force_based.grid(row=7,column=1, pady=5, padx=5, sticky=tk.E)
        bouton_reingold.grid(row=7,column=3, pady=5, padx=5, sticky=tk.E)
        bouton_random.grid(row=7,column=0, pady=5, padx=5, sticky=tk.E)
        bouton_stop.grid(row=7,column=2, pady=5, padx=5, sticky=tk.E)
        
        # retrieve variables values
        alpha, beta, k, eta, delta, raideur = [v.get() for v in ender_variables]
            
        def move_oval(self, n):
            newx, newy = int(n.x), int(n.y)
            self.canvas.coords(n.oval, newx - 5, newy - 5, newx + 5, newy + 5)
            self.canvas.coords(self.node_to_label_id[n], newx + 5, newy + 5)
            
        def move_links(self, n):
            # update links coordinates
            for link in self.attached_link[n]:
                coords = self.canvas.coords(link.line)
                if(self.link_info[link][0] == n):
                    coords[:2] = int(n.x), int(n.y)
                else:
                    coords[2:] = int(n.x), int(n.y)
                self.canvas.coords(link.line, *coords)
                
                # update link label coordinates
                middle_x = link.source.x + (link.destination.x - link.source.x)//2
                middle_y = link.source.y + (link.destination.y - link.source.y)//2
                self.canvas.coords(self.link_to_label_id[link], middle_x, middle_y)
            
        def basic(self):
            ntw.move_basic(*(v.get() for v in ender_variables))                
            for n in ntw.nodes:
                move_oval(self, n)
                move_links(self, n) 
            # stop job if convergence reached
            if(all(-10**(-2) < n.vx * n.vy < 10**(-2) for n in ntw.nodes)):
                return self._cancel()
            self._job = app.after(1, lambda: basic(self))
            
        def frucht(self):
            ntw.fruchterman(var_opd.get())     
            for n in ntw.nodes:
                move_oval(self, n)
                move_links(self, n) 
            # stop job if convergence reached
            if(all(-10**(-2) < n.vx * n.vy < 10**(-2) for n in ntw.nodes)):
                return self._cancel()
            self._job = app.after(1, lambda: frucht(self))
            
if __name__ == "__main__":
    ntw = network.Network("Network")
    #ntw.fast_graph_definition("ABBCCDDEEA")
    # A = Node("A")
    # B = Node("B")
    # C = Node("C")
    # ntw.add_nodes(A, B, C)
    # AB = Trunk(Node("A"), Node("B"))
    # BC = Trunk(B, C)
    # AC = Trunk(A, C)
    # ntw.add_trunks(AB, BC, AC)
    app = NetworkSimulator()
    app.mainloop()