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
        main_menu.add_command(label="Link management", command=lambda: self.link_management())
        main_menu.add_command(label="Node management", command=lambda: self.node_management())
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
        menu_routing.add_command(label="Find path", command=lambda: self.graph_path())
        menu_routing.add_command(label="Route flows", command=lambda: self.nothing())
        menubar.add_cascade(label="Network routing",menu=menu_routing)

        menu_options = tk.Menu(menubar, tearoff=0)        
        # menu to choose which label to display for links
        menu_link_label = tk.Menu(menubar, tearoff=0)
        menu_link_label.add_command(label="Cost", command=lambda: self._change_link_label("cost"))
        menu_link_label.add_command(label="Capacity", command=lambda: self._change_link_label("capacity"))
        menu_link_label.add_command(label="Flow", command=lambda: self._change_link_label("flow"))
        # menu to choose which label to display for nodes
        menu_node_label = tk.Menu(menubar, tearoff=0)
        menu_node_label.add_command(label="Name", command=lambda: self._refresh_node_label("name"))
        menu_node_label.add_command(label="Position", command=lambda: self._refresh_node_label("position"))
        # add the node and link label menus to the option menu
        menu_options.add_cascade(label="Link label", menu=menu_link_label)
        menu_options.add_cascade(label="Node label", menu=menu_node_label)
        
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
        self.default_colors = ["black", "red", "green", "blue", "cyan", "yellow", "magenta"]
        
        # default link width and node size
        self.LINK_WIDTH = 4
        self.NODE_SIZE = 12
        
        # default label display
        self._current_node_label = "name"
        self._current_link_label = "cost"

        # use the right-click to move the background
        self.canvas.bind("<ButtonPress-3>", self.scroll_start)
        self.canvas.bind("<B3-Motion>", self.scroll_move)
        
        # add bindings for dragging a node with left-click
        self.canvas.tag_bind("node", "<ButtonPress-1>", self.move_closest_node)
        self.canvas.tag_bind("node", "<ButtonRelease-1>", self.release_node)
        self.canvas.tag_bind("node", "<B1-Motion>", self.node_motion)
        
        # add bindings for opening a property panel with right-click
        self.canvas.tag_bind("link", "<ButtonPress-3>", self.closest_link_parameters)
        self.canvas.tag_bind("node", "<ButtonPress-3>", self.closest_node_parameters)
        
        # parameters for spring-based drawing
        self.alpha = 1.0
        self.beta = 100000
        self.k = 0.5
        self.eta = 0.5
        self.delta = 0.35
        self.raideur = 1.0
        self.opd = 0
    
    def scroll_start(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        
    # cancel the on-going job (e.g graph drawing)
    def _cancel(self):
        if self._job is not None:
            app.after_cancel(self._job)
            self._job = None

    def _create_node(self, coord, color):
        x, y = coord
        return self.canvas.create_oval(x-15, y-15, x+15, y+15, outline=color, fill=color, tags=("node"))
    
    def _create_node_label(self, node):
        label_id = self.canvas.create_text(node.x + 5, node.y + 5, anchor="nw")
        value = eval("node." + self._current_node_label)
        self.canvas.itemconfig(label_id, text=value, fill="blue")
        self.node_to_label_id[node] = label_id
    
    def _create_link_label(self, link):
        middle_x = link.source.x + (link.destination.x - link.source.x)//2
        middle_y = link.source.y + (link.destination.y - link.source.y)//2
        label_id = self.canvas.create_text(middle_x, middle_y, anchor="nw", fill="red")
        self.link_to_label_id[link] = label_id
        
    def closest_link_parameters(self, event):
        link = self.link_id_to_trunk[self.canvas.find_closest(event.x, event.y)[0]]
        self.link_management(link)
        
    def closest_node_parameters(self, event):
        node = self.node_id_to_node[self.canvas.find_closest(event.x, event.y)[0]]
        self.node_management(node)
        
    def move_closest_node(self, event):
        # record the item and its location
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
            self.canvas.coords(self.link_to_label_id[link], middle_x, middle_y)
            
    def random_drawing(self):
        self._cancel()
        self.canvas.delete("all")
        for n in ntw.pool_node.values():
            n.x, n.y = random.randint(100,700), random.randint(100,700)
            n.oval = self._create_node((n.x, n.y), "magenta")
            self.node_id_to_node[n.oval] = n
            self._create_node_label(n)
            
        for t in filter(None,ntw.pool_trunk.values()):
            t.line = self.canvas.create_line(t.source.x, t.source.y, t.destination.x, t.destination.y, arrow=tk.LAST, arrowshape=(6,8,3), tags=("link"), width=self.LINK_WIDTH)
            self._create_link_label(t)
            self.link_id_to_trunk[t.line] = t
            self.attached_link[t.source].add(t)
            self.attached_link[t.destination].add(t)
            self.link_info[t] = [t.source, t.destination]
        
        self._change_link_label(self._current_link_label)
            
    def unhighlight(self):
        for link in ntw.pool_trunk.values():
            self.canvas.itemconfig(link.line, fill="black", width=self.LINK_WIDTH)
            
    # refresh the label for one link with the current link label
    def _refresh_link_label(self, current_link):
        value = eval("current_link." + self._current_link_label)
        label_id = self.link_to_label_id[current_link]
        if(self._current_link_label in ["capacity", "flow"]):
            self.canvas.itemconfig(label_id, text="{}/{}".format(value["SD"], value["DS"]))
        else:
            self.canvas.itemconfig(label_id, text=value)
            
    # change label: refresh it for all links
    def _change_link_label(self, var_label):
        self._current_link_label = var_label
        for link in filter(None,ntw.pool_trunk.values()):
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
        
        select_label = tk.Button(graph_label_window, text="Apply", command=lambda: self._change_link_label(var_label.get()))
        label_options.grid(row=1, column=0, sticky=tk.W)
        select_label.grid(row=1, column=1, sticky=tk.W)
        
    def move_oval(self, n):
        newx, newy = int(n.x), int(n.y)
        s = self.NODE_SIZE
        self.canvas.coords(n.oval, newx - s, newy - s, newx + s, newy + s)
        self.canvas.coords(self.node_to_label_id[n], newx + 5, newy + 5)
        
    def move_attached_links(self, n):
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
            
    def spring_based_drawing(self):
        # if the canvas is empty, random drawing required first
        if(not self.node_id_to_node):
            self.random_drawing()
        ntw.move_basic(self.alpha, self.beta, self.k, self.eta, self.delta, self.raideur)                
        for n in ntw.pool_node.values():
            self.move_oval(n)
            self.move_attached_links(n)
        self._job = app.after(1, lambda: self.spring_based_drawing())
        
    def frucht(self):
        # update the optimal pairwise distance
        self.opd = math.sqrt(500*500/len(ntw.pool_node.values())) if ntw.pool_node.values() else 0
        ntw.fruchterman(self.opd)     
        for n in ntw.pool_node.values():
            self.move_oval(n)
            self.move_attached_links(n)
        # stop job if convergence reached
        if(all(-10**(-2) < n.vx * n.vy < 10**(-2) for n in ntw.pool_node.values())):
            return self._cancel()
        self._job = app.after(1, lambda: self.frucht())
            
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
        button_create_LSP.grid(row=8,column=2, pady=5, padx=5, sticky=tk.W)
        
        label_path_found.grid(row=7,column=0, pady=5, padx=5, sticky=tk.W)
        LSP_list.grid(row=9, column=0, sticky=tk.W)
        button_select_LSP.grid(row=9, column=1, sticky=tk.W)
        button_flow.grid(row=11, column=0, sticky=tk.W)
        
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
            source = ntw.node_factory(entry_source_node.get())
            destination = ntw.node_factory(entry_destination_node.get())
            excluded_links = filter(None, entry_excluded_links.get().split(","))
            excluded_nodes = filter(None, entry_excluded_nodes.get().split(","))
            path_constraints = filter(None, entry_path_constraints.get().split(","))
            if(excluded_links):
                l_excluded_links = [ntw.trunk_factory(ntw.node_factory(t[0]),ntw.node_factory(t[1])) for t in excluded_links]
            if(excluded_nodes):
                l_excluded_nodes = [ntw.node_factory(n) for n in excluded_nodes]
            if(path_constraints):
                l_path_constraints = [ntw.node_factory(n) for n in path_constraints]
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
            ntw.ford_fulkerson(ntw.node_factory(entry_source_node.get()), ntw.node_factory(entry_destination_node.get()))
            
    def link_management(self, current_link=None):
        graph_path_window = tk.Toplevel()
        graph_path_window.geometry("300x200")
        graph_path_window.title("Manage link properties")
        
        # retrieve and save link data
        button_select_link = tk.Button(graph_path_window, text="Select link", command=lambda: select_link())
        button_save_link = tk.Button(graph_path_window, text="Save link", command=lambda: save_link(self, current_link))
        
        # Label for source, destination, excluded nodes/links and path constraints
        label_source_node = tk.Label(graph_path_window, text = "Source node")
        label_destination_node = tk.Label(graph_path_window, text = "Destination node")
        label_capacitySD = tk.Label(graph_path_window, text = "Capacity source -> destination")
        label_capacityDS = tk.Label(graph_path_window, text = "Capacity destination -> source")
        label_cost = tk.Label(graph_path_window, text = "Cost")
        
        # Entry boxes and textvar for all parameters / constraints
        var_source_node = tk.StringVar()
        var_destination_node = tk.StringVar()
        var_capacitySD = tk.StringVar()
        var_capacityDS = tk.StringVar()
        var_cost = tk.StringVar()
        
        # if the windows pops up from the right-click, init with link param
        if(current_link):
            var_source_node.set(str(current_link.source))
            var_destination_node.set(str(current_link.destination))
            var_capacitySD.set(str(current_link.capacity["SD"]))
            var_capacityDS.set(str(current_link.capacity["DS"]))
            var_cost.set(str(current_link.cost))
        else:
            var_source_node.set("")
            var_destination_node.set("")
            var_capacitySD.set("")
            var_capacityDS.set("")
            var_cost.set("")

        entry_source_node  = tk.Entry(graph_path_window, textvariable=var_source_node, width=15)
        entry_destination_node = tk.Entry(graph_path_window, textvariable=var_destination_node, width=15)
        entry_capacitySD = tk.Entry(graph_path_window, textvariable=var_capacitySD, width=15)
        entry_capacityDS = tk.Entry(graph_path_window, textvariable=var_capacityDS, width=15)
        entry_cost = tk.Entry(graph_path_window, text=var_cost, width=15)
        
        label_source_node.grid(row=0, column=0, pady=5, padx=5, sticky=tk.W)
        label_destination_node.grid(row=1, column=0, pady=5, padx=5, sticky=tk.W)
        label_capacitySD.grid(row=2, column=0, pady=5, padx=5, sticky=tk.W)
        label_capacityDS.grid(row=3, column=0, pady=5, padx=5, sticky=tk.W)
        label_cost.grid(row=4, column=0, pady=5, padx=5, sticky=tk.W)
        
        entry_source_node.grid(row=0, column=1, sticky=tk.W)
        entry_destination_node.grid(row=1, column=1, sticky=tk.W)
        entry_capacitySD.grid(row=2, column=1, sticky=tk.W)
        entry_capacityDS.grid(row=3, column=1, sticky=tk.W)
        entry_cost.grid(row=4, column=1, sticky=tk.W)
    
        button_select_link.grid(row=5,column=0, pady=5, padx=5, sticky=tk.W)
        button_save_link.grid(row=5,column=1, pady=5, padx=5, sticky=tk.W)
        
        def select_link():
            # to select a link in the window by looking at the src/dest
            src, dest = var_source_node.get(), var_destination_node.get()
            if(src and dest):
                current_link = ntw.trunk_factory(ntw.node_factory(src), ntw.node_factory(dest))
                var_capacitySD.set(str(current_link.capacity["SD"]))
                var_capacityDS.set(str(current_link.capacity["DS"]))
                var_cost.set(str(current_link.cost))
                
        def save_link(self, current_link):
            if(not current_link):
                src, dest = var_source_node.get(), var_destination_node.get()
                current_link = ntw.trunk_factory(ntw.node_factory(src), ntw.node_factory(dest))
            current_link.capacity["SD"] = int(var_capacitySD.get())
            current_link.capacity["DS"] = int(var_capacityDS.get())
            current_link.cost = int(var_cost.get())
            # refresh label for current link
            self._refresh_link_label(current_link)
                
    def node_management(self, current_node=None):
        graph_path_window = tk.Toplevel()
        graph_path_window.geometry("300x200")
        graph_path_window.title("Manage node properties")
        
        # retrieve and save node data
        button_select_node = tk.Button(graph_path_window, text="Select node", command=lambda: select_node())
        button_save_node = tk.Button(graph_path_window, text="Save node", command=lambda: save_node(current_node))
        
        # Label for name and position
        label_name = tk.Label(graph_path_window, text = "Name")
        label_x = tk.Label(graph_path_window, text = "Position x")
        label_y = tk.Label(graph_path_window, text = "Position y")
        
        # Entry boxes and textvar for all parameters
        var_name = tk.StringVar()
        var_x = tk.StringVar()
        var_y = tk.StringVar()
        
        if(current_node):
            var_name.set(current_node.name)
            var_x.set(str(current_node.x))
            var_y.set(str(current_node.y))

        else:
            var_name.set("")
            var_x.set("")
            var_y.set("")

        entry_name  = tk.Entry(graph_path_window, textvariable=var_name, width=15)
        entry_x = tk.Entry(graph_path_window, textvariable=var_x, width=15)
        entry_y = tk.Entry(graph_path_window, textvariable=var_y, width=15)
        
        label_name.grid(row=0, column=0, pady=5, padx=5, sticky=tk.W)
        label_x.grid(row=1, column=0, pady=5, padx=5, sticky=tk.W)
        label_y.grid(row=2, column=0, pady=5, padx=5, sticky=tk.W)
        
        entry_name.grid(row=0, column=1, sticky=tk.W)
        entry_x.grid(row=1, column=1, sticky=tk.W)
        entry_y.grid(row=2, column=1, sticky=tk.W)
    
        button_select_node.grid(row=5,column=0, pady=5, padx=5, sticky=tk.W)
        button_save_node.grid(row=5,column=1, pady=5, padx=5, sticky=tk.W)
        
        # to select a node in the window by looking at its name
        def select_node():
            current_node = ntw.node_factory(var_name.get())
            var_x.set(str(current_node.x))
            var_y.set(str(current_node.y))
                
        def save_node(current_node):
            if(not current_node):
                current_node = ntw.node_factory(var_name.get())
            current_node.x = int(var_x.get())
            current_node.y = int(var_y.get())
            # TODO: refresh label 
            #self.canvas.itemconfig(self.link_to_label_id[current_link], text=label_choice)
                
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
                ntw.add_trunk(ntw.trunk_factory(ntw.node_factory(source), ntw.node_factory(destination)))
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
                        self.canvas.itemconfig(link.line, fill=self.default_colors[idx], width=self.LINK_WIDTH)
            
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