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
import menus
import math
import object_management_window
import path_finding_window

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
        main_menu.add_command(label="Link management", command=lambda: self.link_management_window.deiconify())
        main_menu.add_command(label="Node management", command=lambda: self.node_management_window.deiconify())
        main_menu.add_separator()
        main_menu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="Main",menu=main_menu)
        menu_drawing = tk.Menu(menubar, tearoff=0)
        menu_drawing.add_command(label="Default drawing parameters", command=lambda: self.graph_layout())
        menu_drawing.add_command(label="Random drawing", command=lambda: self.random_drawing())
        menu_drawing.add_command(label="Spring-based drawing", command=lambda: self.spring_based_drawing())
        menu_drawing.add_command(label="Stop drawing", command=lambda: self._cancel())
        menubar.add_cascade(label="Network drawing",menu=menu_drawing)
        menu_routing = tk.Menu(menubar, tearoff=0)
        menu_routing.add_command(label="Find path", command=lambda: self.path_finding_window.deiconify())
        menu_routing.add_command(label="Route flows", command=lambda: self.nothing())
        menubar.add_cascade(label="Network routing",menu=menu_routing)

        menu_options = tk.Menu(menubar, tearoff=0)        
        # menu to choose which label to display for links
        menu_link_label = tk.Menu(menubar, tearoff=0)
        menu_link_label.add_command(label="Name", command=lambda: self._refresh_link_labels("name"))
        menu_link_label.add_command(label="Cost", command=lambda: self._refresh_link_labels("cost"))
        menu_link_label.add_command(label="Capacity", command=lambda: self._refresh_link_labels("capacity"))
        menu_link_label.add_command(label="Flow", command=lambda: self._refresh_link_labels("flow"))
        # menu to choose which label to display for nodes
        menu_node_label = tk.Menu(menubar, tearoff=0)
        menu_node_label.add_command(label="Name", command=lambda: self._refresh_node_label("name"))
        menu_node_label.add_command(label="Position", command=lambda: self._refresh_node_label("position"))
        # add the node and link label menus to the option menu
        menu_options.add_cascade(label="Link label", menu=menu_link_label)
        menu_options.add_cascade(label="Node label", menu=menu_node_label)
        
        menubar.add_cascade(label="Options",menu=menu_options)
        self.config(menu=menubar)
    
        # create a frame
        self.frame = tk.Frame(width=200,height=600, borderwidth=3, relief="solid", background="#a1dbcd")
        self.frame.pack(fill=tk.NONE, side=tk.LEFT)
        
        # create a canvas
        self.canvas = tk.Canvas(width=1100, height=600, background="bisque")
        self.canvas.pack(fill=tk.NONE, side=tk.LEFT)

        self._job = None
        self.object_id_to_object = {}
        self.node_to_label_id = {}
        self.link_to_label_id = {}
        
        # default colors for highlighting areas
        self.default_colors = ["black", "red", "green", "blue", "cyan", "yellow", "magenta"]
        
        # default link width and node size
        self.LINK_WIDTH = 5
        self.NODE_SIZE = 8
        
        # default label display
        self._current_node_label = "name"
        self._current_link_label = "cost"

        # node and link management windows
        self.node_management_window = object_management_window.NodeManagement(self, ntw)
        self.link_management_window = object_management_window.LinkManagement(self, ntw)
        
        # path finding window
        self.path_finding_window = path_finding_window.PathFinding(self, ntw)
        
        self.switch_binding("creation")
        
        # TODO: refactor with class 
        # http://stackoverflow.com/questions/15464386/how-to-pass-values-to-popup-command-on-right-click-in-python-tkinter
        # the menu
        
        # parameters for spring-based drawing
        self.alpha = 1.0
        self.beta = 100000
        self.k = 0.5
        self.eta = 0.5
        self.delta = 0.35
        self.raideur = 1.0
        self.opd = 0
    
    # TODO : move labels along with zoom/unzoom
    # TODO: fix the zoom unzoom: it does not consider the right point after moving canvas
    # http://stackoverflow.com/questions/18884220/moving-around-a-python-canvas-without-using-scrollbars
    def switch_binding(self, mode):
        if(mode == "motion"):
            # use the right-click to move the background
            self.canvas.bind("<ButtonPress-3>", self.scroll_start)
            self.canvas.bind("<B3-Motion>", self.scroll_move)
            
            # add bindings to drag a node with left-click
            self.canvas.tag_bind("node", "<Button-1>", self.move_closest_node)
            self.canvas.tag_bind("node", "<B1-Motion>", self.node_motion)
            
            # highlight the path of a route with left-click
            self.canvas.tag_bind("route", "<ButtonPress-1>", self.closest_route_path)
            
            # zoom and unzoom on windows
            self.canvas.bind("<MouseWheel>",self.zoomer)
            # same on linux
            self.canvas.bind("<Button-4>", self.zoomerP)
            self.canvas.bind("<Button-5>", self.zoomerM)
            
            # add binding for right-click menu on nodes
            self.right_click_menu_nodes = menus.RightClickMenuNode(self)
            self.canvas.tag_bind("node", "<ButtonPress-3>",lambda e: self.right_click_menu_nodes.popup(e))
            
            # add binding for right-click menu on links
            self.right_click_menu_links = menus.RightClickMenuLink(self)
            self.canvas.tag_bind("trunk", "<ButtonPress-3>",lambda e: self.right_click_menu_links.popup(e))
            
        if(mode == "creation"):
            # add bindings to drag a node with left-click
            self.canvas.bind("<Button-1>", self.big_create_node)
            
    def big_create_node(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        new_node = ntw.node_factory(pos_x = x, pos_y = y)
        new_node.oval = self.create_node(x, y,"blue")
        self.object_id_to_object[new_node.oval] = new_node
        self.create_node_label(new_node)

    def scroll_start(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        
    # zoom for windows
    def zoomer(self, event):
        if(event.delta > 0):
            self.canvas.scale("all", event.x, event.y, 1.1, 1.1)
        elif(event.delta < 0):
            self.canvas.scale("all", event.y, event.y, 0.9, 0.9)
        self.canvas.configure(scrollregion = self.canvas.bbox("all"))
        
    # zoom for linux
    def zoomerP(self,event):
        self.canvas.scale("all", event.x, event.y, 1.1, 1.1)
        self.canvas.configure(scrollregion = self.canvas.bbox("all"))
        
    def zoomerM(self,event):
        self.canvas.scale("all", event.x, event.y, 0.9, 0.9)
        self.canvas.configure(scrollregion = self.canvas.bbox("all"))
        
    # cancel the on-going job (e.g graph drawing)
    def _cancel(self):
        if self._job is not None:
            app.after_cancel(self._job)
            self._job = None

    def create_node(self, x, y, color):
        return self.canvas.create_oval(x-15, y-15, x+15, y+15, outline=color, fill=color, tags=("node"))
        
    def create_link(self, link):
        link.line = self.canvas.create_line(link.source.x, link.source.y, link.destination.x, link.destination.y, arrow=tk.LAST, arrowshape=(6,8,3), tags=(link.type), fill=link.color, width=self.LINK_WIDTH, dash=link.dash)
        self.object_id_to_object[link.line] = link
        self._create_link_label(link)
        
    def remove_node(self, node):
        self._cancel()
        self.canvas.delete(node.oval)
        self.canvas.delete(self.node_to_label_id[node])
        for link in ntw.remove_node(node):
            self.remove_link(link)
            
    def remove_link(self, link):
        self._cancel()
        self.canvas.delete(link.line)
        self.canvas.delete(self.link_to_label_id[link])
        ntw.remove_link(link)
    
    def create_node_label(self, node):
        label_id = self.canvas.create_text(node.x + 5, node.y + 5, anchor="nw")
        value = eval("node." + self._current_node_label)
        self.canvas.itemconfig(label_id, text=value, fill="blue")
        self.node_to_label_id[node] = label_id
    
    def _create_link_label(self, link):
        middle_x = link.source.x + (link.destination.x - link.source.x)//2
        middle_y = link.source.y + (link.destination.y - link.source.y)//2
        label_id = self.canvas.create_text(middle_x, middle_y, anchor="nw", fill="red")
        self.link_to_label_id[link] = label_id
        
    def closest_route_path(self, event):
        self.unhighlight()
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        route = self.object_id_to_object[self.canvas.find_closest(x, y)[0]]
        self.highlight_path(route.path)
        
    def move_closest_node(self, event):
        # record the item and its location
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.drag_item = self.canvas.find_closest(x, y)[0]

    def node_motion(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        # record the new position
        node = self.object_id_to_object[self.drag_item]
        # update coordinates of the node and move it
        node.x, node.y = x, y
        self.move_node(node)
            
    def random_drawing(self):
        self._cancel()
        self.canvas.delete("all")
        for n in ntw.pool_node.values():
            n.x, n.y = random.randint(100,700), random.randint(100,700)
            n.oval = self.canvas.create_oval(n.x-15, n.y-15, n.x+15, n.y+15, outline="magenta", fill="magenta", tags=("node"))
            self.object_id_to_object[n.oval] = n
            self.create_node_label(n)

        for t in list(ntw.pool_trunk.values())+list(ntw.pool_route.values())+list(ntw.pool_traffic.values()):
             self.create_link(t)
        
        self._refresh_link_labels(self._current_link_label)
            
    def unhighlight(self):
        for link in ntw.pool_trunk.values():
            self.canvas.itemconfig(link.line, fill="black", width=self.LINK_WIDTH)
            
    def highlight_path(self, path):
        self.unhighlight()
        for segment in path:
            self.canvas.itemconfig(segment.line, fill="red", width=5)
            
    # refresh the label for one link with the current link label
    def _refresh_link_label(self, current_link):
        value = eval("current_link." + self._current_link_label)
        label_id = self.link_to_label_id[current_link]
        if(self._current_link_label in ["capacity", "flow"]):
            self.canvas.itemconfig(label_id, text="{}/{}".format(value["SD"], value["DS"]))
        else:
            self.canvas.itemconfig(label_id, text=value)
            
    # change label: refresh it for all links
    def _refresh_link_labels(self, var_label):
        self._current_link_label = var_label
        for link in ntw.pool_trunk.values():
            self._refresh_link_label(link)
            
    def label_display(self):
        graph_label_window = tk.Toplevel()
        graph_label_window.geometry("600x300")
        graph_label_window.title("Modify the label display")
        var_label = tk.StringVar(graph_label_window)
        
        # current default link label is the default choice
        var_label.set(self._current_link_label)
        choices = ["cost", "capacity", "flow"]
        label_options = tk.OptionMenu(graph_label_window, var_label, *choices)
        
        select_label = tk.Button(graph_label_window, text="Apply", command=lambda: self._refresh_link_labels(var_label.get()))
        label_options.grid(row=1, column=0, sticky=tk.W)
        select_label.grid(row=1, column=1, sticky=tk.W)
        
    def move_node(self, n):
        newx, newy = int(n.x), int(n.y)
        s = self.NODE_SIZE
        self.canvas.coords(n.oval, newx - s, newy - s, newx + s, newy + s)
        self.canvas.coords(self.node_to_label_id[n], newx + 5, newy + 5)
    
        # update links coordinates
        for type_link in ntw.graph[n].keys():
            for link in ntw.graph[n][type_link]:
                coords = self.canvas.coords(link.line)
                c = 2*(link.source != n)
                coords[c], coords[c+1] = int(n.x), int(n.y)
                self.canvas.coords(link.line, *coords)
                
                # update link label coordinates
                middle_x = link.source.x + (link.destination.x - link.source.x)//2
                middle_y = link.source.y + (link.destination.y - link.source.y)//2
                self.canvas.coords(self.link_to_label_id[link], middle_x, middle_y)
            
    def spring_based_drawing(self):
        # if the canvas is empty, random drawing required first
        if(not self.object_id_to_object):
            self.random_drawing()
        ntw.move_basic(self.alpha, self.beta, self.k, self.eta, self.delta, self.raideur)                
        for n in ntw.pool_node.values():
            self.move_node(n)
        self._job = app.after(1, lambda: self.spring_based_drawing())
        
    def frucht(self):
        # update the optimal pairwise distance
        self.opd = math.sqrt(500*500/len(ntw.pool_node.values())) if ntw.pool_node.values() else 0
        ntw.fruchterman(self.opd)     
        for n in ntw.pool_node.values():
            self.move_node(n)
        # stop job if convergence reached
        if(all(-10**(-2) < n.vx * n.vy < 10**(-2) for n in ntw.pool_node.values())):
            return self._cancel()
        self._job = app.after(1, lambda: self.frucht())
                
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
        bouton_tree = tk.Button(newfenetre, text='tree', command = lambda: tree(self), width=12, height=1)
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
        bouton_tree.grid(row=11,column=0, pady=5, padx=5, sticky=tk.W)
        
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
            string_nodes.set("Nodes: " + ",".join([str(n) for n in ntw.pool_node.keys()]))
            string_links.set("Links: " + ",".join([str(t) for t in ntw.pool_trunk.keys()]))
                
        def add_nodes():
            user_input = entry_add_nodes.get().replace(" ","")
            for s in user_input.split(","):
                ntw.node_factory(s)
            update_graph()
            
        def add_links():
            user_input = entry_add_links.get().replace(" ","")
            for s in user_input.split(","):
                source, destination = s.split(".")
                ntw.link_factory(ntw.node_factory(source), ntw.node_factory(destination), "trunk")
            update_graph()
            
        def erase_graph(self):
            ntw.clear()
            self._drag_data = {"x": 0, "y": 0, "item": None}
            self.object_id_to_object = {}
            self.attached_link = collections.defaultdict(set)
            
        def automatic_graph_creation():
            user_input = entry_fast_creation.get().replace(" ","")
            ntw.fast_graph_definition(user_input)
            update_graph()
            
        def highlight_connected_components(self):
            self.unhighlight()
            connected_components = ntw.connected_components()
            for idx, connex_set in enumerate(connected_components):
                for n in connex_set:
                    for adjacent_node in ntw.graph[n]:
                        link = ntw.link_factory(n, adjacent_node, "trunk")
                        self.canvas.itemconfig(link.line, fill=self.default_colors[idx], width=self.LINK_WIDTH)
            
        def meshed_square(self):
            erase_graph(self)
            ntw.generate_meshed_square(int(entry_meshed_square.get()))
            update_graph()
            
        def hypercube(self):
            erase_graph(self)
            ntw.generate_hypercube(int(entry_hypercube.get()))
            update_graph()
            
        def tree(self):
            erase_graph(self)
            ntw.generate_star(int(entry_hypercube.get()))
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
        var_alpha.set(self.alpha)
        ender_variables.append(var_alpha)
        entry_alpha = tk.Entry(newfenetre, textvariable=var_alpha, width=15)
        
        # Beta
        label_beta = tk.Label(newfenetre, text = "Beta")
        var_beta = tk.IntVar()
        var_beta.set(self.beta)
        ender_variables.append(var_beta)
        entry_beta = tk.Entry(newfenetre, textvariable = var_beta, width=15)
        
        # k
        label_k = tk.Label(newfenetre, text = "k")
        var_k = tk.DoubleVar()
        var_k.set(self.k)
        ender_variables.append(var_k)
        entry_k = tk.Entry(newfenetre, textvariable = var_k, width=15)
        
        # Variables de dumping
        # Eta
        label_eta = tk.Label(newfenetre, text = "Eta")
        var_eta = tk.DoubleVar()
        var_eta.set(self.eta)
        ender_variables.append(var_eta)
        entry_eta = tk.Entry(newfenetre, textvariable = var_eta, width=15)
        
        # Delta
        label_delta = tk.Label(newfenetre, text = "Delta")
        var_delta = tk.DoubleVar()
        var_delta.set(self.delta)
        ender_variables.append(var_delta)
        entry_delta = tk.Entry(newfenetre, textvariable = var_delta, width=15)
        
        # optimal pairwise distance
        label_opd = tk.Label(newfenetre, text = "Optimal pairwise distance")
        var_opd = tk.DoubleVar()
        var_opd.set(str(self.opd))
        entry_opd = tk.Entry(newfenetre, textvariable = var_opd, width=15)
        
        # Raideur du ressort d
        label_raideur = tk.Label(newfenetre, text = "Raideur")
        var_raideur = tk.DoubleVar()
        var_raideur.set(self.raideur)
        ender_variables.append(var_raideur)
        entry_raideur = tk.Entry(newfenetre, textvariable=var_raideur, width=15)
        
        # drawing button
        bouton_force_based = tk.Button(newfenetre, text="Force-based", command = lambda: self.spring_based_drawing(), width=18, height=1)
        bouton_reingold = tk.Button(newfenetre, text="Fruchtemann-reingold", command = lambda: self.frucht(), width=18, height=1)
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
            
if __name__ == "__main__":
    ntw = network.Network("Network")
    app = NetworkSimulator()
    app.mainloop()