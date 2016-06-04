import tkinter as tk
import network
import menus
import random
from math import cos, sin, atan2, sqrt, radians

class Scenario(tk.Canvas):
    
    def __init__(self, master, name):
        super().__init__(width=1100, height=600, background="bisque")
        self.name = name
        self.ntw = network.Network()
        self.object_id_to_object = {}
        self.master = master
        
        # job running or not (e.g drawing)
        self._job = None
        
        # default colors for highlighting areas
        # TODO use this for the image dict
        self.default_colors = ["black", "red", "green", "blue", "cyan", "yellow", "magenta"]
        
        # default link width and node size
        self.LINK_WIDTH = 5
        
        # default label display
        self._current_object_label = {obj_type: "name" for obj_type in self.ntw.all_type}
        
        # creation mode, object type, and associated bindings
        self._start_position = [None, None]
        self._object_type = "trunk"
        self.drag_item = None
        self.temp_line = None
        
        # object selected for rectangle selection
        self.object_selection = "node"
        
        # used to move several node at once
        self._start_pos_main_node = [None, None]
        self._dict_start_position = {}
        
        # the default motion is creation of nodes
        self._mode = "motion"
        self._creation_mode = "router"
        
        # the default display is: with image
        self.display_image = True
        # 2D display or 3D display
        self.layered_display = False
        # if layered_display is false, there's only one layer (self.layers[0])
        # else we need a dictionnary associating a type to each layer
        self.layers = [(0,), {0: "trunk", 1: "route", 2: "traffic"}]
        # difference between each layer in pixel
        self.diff_y = 0
        
        # display state per type of objects
        self.display_per_type = {type: True for type in self.ntw.all_type}
        
        # list of currently selected object ("so")
        self.so = {"node": set(), "link": set()}
        
        # initialization of all bindings for nodes creation
        self.switch_binding()
        
        ## bindings that remain available in all modes
        # highlight the path of a route with left-click
        self.tag_bind("route", "<ButtonPress-1>", self.closest_route_path)
        
        # zoom and unzoom on windows
        self.bind("<MouseWheel>",self.zoomer)
        
        # same on linux
        self.bind("<Button-4>", self.zoomerP)
        self.bind("<Button-5>", self.zoomerM)
        
        # add binding for right-click menu 
        self.tag_bind("object", "<ButtonPress-3>",lambda e: menus.RightClickMenu(e, self))
        
        # use the right-click to move the background
        self.bind("<ButtonPress-3>", self.scroll_start)
        self.bind("<B3-Motion>", self.scroll_move)
        
        # initialize other bindings depending on the mode
        self.switch_binding()
        
        # switch the object rectangle selection by pressing space
        self.bind("<space>", self.change_object_selection)
        
    def switch_binding(self):   
        # in case there were selected nodes, so that they don't remain highlighted
        self.unhighlight_all()
        
        if(self._mode == "motion"):
            # unbind unecessary bindings
            self.unbind("<Button 1>")
            self.tag_unbind("node", "<Button-1>")
            self.tag_unbind("node", "<B1-Motion>")
            self.tag_unbind("node", "<ButtonRelease-1>")
            
            # set the focus on the canvas when clicking on it
            # allows for the keyboard binding to work properly
            self.bind("<1>", lambda event: self.focus_set())
            
            # add bindings to drag a node with left-click
            self.tag_bind("node", "<Button-1>", self.find_closest_node, add="+")
            for tag in ("node", "link"):
                self.tag_bind(tag, "<Button-1>", self.find_closest_object, add="+")
            self.tag_bind("node", "<B1-Motion>", self.node_motion)
            
            # add binding to select all nodes in a rectangle
            self.bind("<ButtonPress-1>", self.start_point_select_objects, add="+")
            self.bind("<B1-Motion>", self.rectangle_drawing)
            self.bind("<ButtonRelease-1>", self.end_point_select_nodes, add="+")
            
        else:
            # unbind unecessary bindings
            self.unbind("<Button-1>")
            self.unbind("<ButtonPress-1>")
            self.unbind("<ButtonRelease-1>")
            self.unbind("<ButtonMotion-1>")
            self.tag_unbind("node", "<Button-1>")
            
            if(self._creation_mode in self.ntw.node_type_to_class):
                # add bindings to create a node with left-click
                self.bind("<ButtonPress-1>", self.create_node_on_binding)
            
            else:
                # add bindings to create a link between two nodes
                self.tag_bind("node", "<Button-1>", self.start_link)
                self.tag_bind("node", "<B1-Motion>", self.line_creation)
                self.tag_bind("node", "<ButtonRelease-1>", lambda event, type=type: self.link_creation(event, self._creation_mode))
                
    def adapt_coordinates(function):
        def wrapper(self, event, *others):
            event.x, event.y = self.canvasx(event.x), self.canvasy(event.y)
            function(self, event, *others)
        return wrapper
                
    def closest_route_path(self, event):
        self.unhighlight_all()
        x, y = self.canvasx(event.x), self.canvasy(event.y)
        route = self.object_id_to_object[self.find_closest(x, y)[0]]
        self.highlight_objects(*route.path)
        
    @adapt_coordinates
    def find_closest_node(self, event):
        # record the item and its location
        self._dict_start_position.clear()
        self.drag_item = self.find_closest(event.x, event.y)[0]
        # save the initial position to compute the delta for multiple nodes motion
        main_node_selected = self.object_id_to_object[self.drag_item]
        self._start_pos_main_node = main_node_selected.x, main_node_selected.y
        for selected_node in self.so["node"]:
            self._dict_start_position[selected_node] = [selected_node.x, selected_node.y]
            
    @adapt_coordinates
    def find_closest_object(self, event):
        self.closest_object_id = self.find_closest(event.x, event.y)[0]
        object_selected = self.object_id_to_object[self.closest_object_id]
        # update the object management window if it is opened
        self.master.dict_obj_mgmt_window[object_selected.type].current_obj = object_selected
        self.master.dict_obj_mgmt_window[object_selected.type].update()

    @adapt_coordinates
    def node_motion(self, event):
        for selected_node in self.so["node"]:
            # the main node initial position, the main node current position, and
            # the other node initial position form a rectangle.
            # we find the position of the fourth vertix.
            x0, y0 = self._start_pos_main_node
            x1, y1 = self._dict_start_position[selected_node]
            selected_node.x, selected_node.y = x1 + (event.x - x0), y1 + (event.y - y0)
            self.move_node(selected_node)
        # record the new position
        node = self.object_id_to_object[self.drag_item]
        # update coordinates of the node and move it
        node.x, node.y = event.x, event.y
        self.move_node(node)
                
                
    def start_point_select_objects(self, event):
        x, y = self.canvasx(event.x), self.canvasy(event.y)
        # create the temporary line, only if there is nothing below
        # this is to avoid drawing a rectangle when moving a node
        if not self.find_overlapping(x-1, y-1, x+1, y+1):
            self.unhighlight_all()
            self.so = {"node": set(), "link": set()}
            self._start_position = x, y
            # create the temporary line
            x, y = self._start_position
            self.temp_line_x_top = self.create_line(x, y, x, y)
            self.temp_line_y_left = self.create_line(x, y, x, y)
            self.temp_line_y_right = self.create_line(x, y, x, y)
            self.temp_line_x_bottom = self.create_line(x, y, x, y)

    @adapt_coordinates
    def rectangle_drawing(self, event):
        # draw the line only if they were created in the first place
        if(self._start_position != [None, None]):
            # update the position of the temporary lines
            x0, y0 = self._start_position
            self.coords(self.temp_line_x_top, x0, y0, event.x, y0)
            self.coords(self.temp_line_y_left, x0, y0, x0, event.y)
            self.coords(self.temp_line_y_right, event.x, y0, event.x, event.y)
            self.coords(self.temp_line_x_bottom, x0, event.y, event.x, event.y)
    
    def change_object_selection(self, event=None):
        self.object_selection = (self.object_selection == "link")*"node" or "link" 

    @adapt_coordinates
    def end_point_select_nodes(self, event):
        if(self._start_position != [None, None]):
            # delete the temporary lines
            self.delete(self.temp_line_x_top)
            self.delete(self.temp_line_x_bottom)
            self.delete(self.temp_line_y_left)
            self.delete(self.temp_line_y_right)
            # select all nodes enclosed in the rectangle
            start_x, start_y = self._start_position
            for obj in self.find_enclosed(start_x, start_y, event.x, event.y):
                if(obj in self.object_id_to_object):
                    enclosed_obj = self.object_id_to_object[obj]
                    if(enclosed_obj.class_type == self.object_selection):
                        self.so[self.object_selection].add(enclosed_obj)
            self.highlight_objects(*self.so["node"]|self.so["link"])
            self._start_position = [None, None]
        
    @adapt_coordinates
    def start_link(self, event):
        self.drag_item = self.find_closest(event.x, event.y)[0]
        start_node = self.object_id_to_object[self.drag_item]
        self.temp_line = self.create_line(start_node.x, start_node.y, event.x, event.y, arrow=tk.LAST, arrowshape=(6,8,3))
        
    @adapt_coordinates
    def line_creation(self, event):
        # node from which the link starts
        start_node = self.object_id_to_object[self.drag_item]
        # create a line to show the link
        self.coords(self.temp_line, start_node.x, start_node.y, event.x, event.y)
        
    @adapt_coordinates
    def link_creation(self, event, type):
        # delete the temporary line
        self.delete(self.temp_line)
        # node from which the link starts
        start_node = self.object_id_to_object[self.drag_item]
        # node close to the point where the mouse button is released
        self.drag_item = self.find_closest(event.x, event.y)[0]
        if(self.drag_item in self.object_id_to_object): # to avoid labels
            destination_node = self.object_id_to_object[self.drag_item]
            if(destination_node.class_type == "node"): # because tag filtering doesn't work !
                # create the link and the associated line
                if(start_node != destination_node):
                    new_link = self.ntw.lf(link_type=type, s=start_node, d=destination_node)
                    self.create_link(new_link)
              
    @adapt_coordinates
    def create_node_on_binding(self, event):
        new_node = self.ntw.nf(event.x, event.y, node_type=self._creation_mode)
        self.create_node(new_node)
        
    def create_node(self, node, layer=0):
        s = node.size
        curr_image = self.master.dict_image["default"][node.type]
        y = node.y - layer * self.diff_y
        tags = () if layer else (node.type, node.class_type, "object")
        node.image[layer] = self.create_image(node.x - (node.imagex)/2, y - (node.imagey)/2, image=curr_image, anchor=tk.NW, tags=tags)
        node.oval[layer] = self.create_oval(node.x-s, y-s, node.x+s, y+s, outline=node.color, fill=node.color, tags=tags)
        # create/hide the image/the oval depending on the current mode
        self.itemconfig(node.oval[layer] if self.display_image else node.image[layer], state=tk.HIDDEN)
        if not layer:
            self.create_node_label(node)
            self.object_id_to_object[node.oval[layer]] = node
            self.object_id_to_object[node.image[layer]] = node
    
    def link_coordinates(self, source, destination, layer="all"):
        xA, yA, xB, yB = source.x, source.y, destination.x, destination.y
        angle = atan2(yB - yA, xB - xA)
        dict_link_to_coords = {}
        type = layer if layer == "all" else self.layers[1][layer]
        for id, link in enumerate(self.ntw.links_between(source, destination, type)):
            d = ((id+1)//2) * 20 * (-1)**id
            xC, yC = (xA+xB)/2 + d*sin(angle), (yA+yB)/2 - d*cos(angle)
            offset = 0 if layer == "all" else layer * self.diff_y
            dict_link_to_coords[link] = (xA, yA - offset, xC, yC - offset, xB, yB - offset)
            link.lpos = (xC, yC - offset)
        return dict_link_to_coords
        
    def create_link(self, new_link):
        edges = (new_link.source, new_link.destination)
        for node in edges:
            if not new_link.layer or self.layered_display:
                if not node.image[new_link.layer]:
                    self.create_node(node, new_link.layer)
                    self.delete(node.layer_line)
                    max_layer = 2 if self.ntw.graph[node]["traffic"] else 1 if self.ntw.graph[node]["route"] else 0
                    coords = (node.x, node.y, node.x, node.y - max_layer * self.diff_y) 
                    if self.layered_display:
                        node.layer_line = self.create_line(*coords, fill="black", width=1, dash=(3,5))
                        self.tag_lower(node.layer_line)
        current_layer = "all" if not self.layered_display else new_link.layer
        link_to_coords = self.link_coordinates(*edges, layer=current_layer)
        for link in link_to_coords:
            coords = link_to_coords[link]
            if not link.line:
                link.line = self.create_line(*coords, tags=(link.type, link.class_type, "object"), fill=link.color, width=self.LINK_WIDTH, dash=link.dash, smooth=True)
            else:
                self.coords(link.line, *coords)
        self.tag_lower(new_link.line)
        self.object_id_to_object[new_link.line] = new_link
        self._create_link_label(new_link)
        self._refresh_object_label(new_link)
        
    def planal_move(self, angle=45):
        self.delete("all")
        self.layered_display = not self.layered_display
        
        for node in self.ntw.pn["node"].values():
            node.oval = {layer: None for layer in range(3)}
            node.image = {layer: None for layer in range(3)}
            
        for link_type in self.ntw.link_type:
            for link in self.ntw.pn[link_type].values():
                link.line = None
        
        if self.layered_display:
        
            min_y = min(node.y for node in self.ntw.pn["node"].values())
            max_y = max(node.y for node in self.ntw.pn["node"].values())
            
            for node in self.ntw.pn["node"].values():
                diff_y = abs(node.y - min_y)
                new_y = min_y + diff_y * cos(radians(angle))
                node.y = new_y
                
            self.diff_y = max_y - min_y + 100
            
            for node in self.ntw.pn["node"].values():
                self.create_node(node)
                    
            for link_type in self.ntw.link_type:
                for link in self.ntw.pn[link_type].values():
                    self.create_link(link)
                    
        else:
            self.draw_all(False)
        
    def change_display(self):
        # flip the display from icon to oval and vice-versa, depend on display_image boolean
        self.display_image = not self.display_image
        for node in self.ntw.pn["node"].values():
            for layer in self.layers[self.layered_display]:
                self.itemconfig(node.oval[layer], state=tk.HIDDEN if self.display_image else tk.NORMAL)
                self.itemconfig(node.image[layer], state=tk.NORMAL if self.display_image else tk.HIDDEN)

    def scroll_start(self, event):
        self.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        self.scan_dragto(event.x, event.y, gain=1)

    ## Zoom / unzoom on the canvas
    
    def update_nodes_coordinates(self):
        # scaling changes the coordinates of the oval, and we update 
        # the corresponding node's coordinates accordingly
        for node in self.ntw.pn["node"].values():
            new_coords = self.coords(node.oval[0])
            node.x, node.y = (new_coords[0] + new_coords[2])/2, (new_coords[3] + new_coords[1])/2
            self.coords(node.lid, node.x - 15, node.y + 10)
            for layer in self.layers[self.layered_display]:
                if node.image[layer] or not layer:
                    x, y = node.x - (node.imagex)/2, node.y - layer*self.diff_y - (node.imagey)/2
                    self.coords(node.image[layer], x, y)
            if self.layered_display and node.layer_line:
                max_layer = 2 if self.ntw.graph[node]["traffic"] else 1 if self.ntw.graph[node]["route"] else 0
                self.coords(node.layer_line, node.x, node.y, node.x, node.y - max_layer*self.diff_y)
            # the oval was also resized while scaling
            node.size = abs(new_coords[0] - new_coords[2])/2 
            for type in self.ntw.link_type:
                for neighbor, t in self.ntw.graph[node][type]:
                    layer = "all" if not self.layered_display else t.layer
                    link_to_coords = self.link_coordinates(node, neighbor, layer)
                    for link in link_to_coords:
                        self.coords(link.line, *link_to_coords[link])
                        self.update_link_label_coordinates(link)
        
    @adapt_coordinates
    def zoomer(self, event):
        """ Zoom for window """
        self._cancel()
        if(event.delta > 0):
            self.scale("all", event.x, event.y, 1.1, 1.1)
            self.diff_y *= 1.1
        elif(event.delta < 0):
            self.scale("all", event.x, event.y, 0.9, 0.9)
            self.diff_y *= 0.9
        self.configure(scrollregion = self.bbox("all"))
        self.update_nodes_coordinates()
        
        
    @adapt_coordinates
    def zoomerP(self,event):
        """ Zoom for Linux """
        self._cancel()
        self.scale("all", event.x, event.y, 1.1, 1.1)
        self.configure(scrollregion = self.bbox("all"))
        self.update_nodes_coordinates()
        
    @adapt_coordinates
    def zoomerM(self,event):
        """ Zoom for Linux """
        self._cancel()
        self.scale("all", event.x, event.y, 0.9, 0.9)
        self.configure(scrollregion = self.bbox("all"))
        self.update_nodes_coordinates()
        
    # cancel the on-going job (e.g graph drawing)
    def _cancel(self):
        if self._job is not None:
            self.after_cancel(self._job)
            self._job = None
    
    def add_to_edges(self, AS, *nodes):
        for node in nodes:
            if node not in AS.edges:
                AS.edges.add(node)
                AS.management.listbox_edges.insert(tk.END, obj)
    # TODO refactor
    def remove_objects(self, *objects):
        for obj in objects:
            if(obj.class_type == "node"):
                self.delete(obj.oval[0], obj.image[0], obj.lid)
                self.remove_objects(*self.ntw.remove_node(obj))
                # we make a list of the keys of obj.AS because the dict size
                # will change while iterating
                for AS in list(obj.AS):
                    AS.management.remove_from_AS(obj)
                if self.layered_display:
                    self.delete(obj.layer_line)
                    for layer in (1, 2):
                        self.delete(obj.oval[layer], obj.image[layer])
            if(obj.class_type == "link"):
                self.delete(obj.line, obj.lid)
                self.ntw.remove_link(obj)
                # traffic links have no AS
                if(obj.network_type not in ("traffic", "route")):
                    # we make a list of the keys of obj.AS because the dict size
                    # will change while iterating
                    for AS in list(obj.AS):
                        AS.management.remove_from_AS(obj)
                if self.layered_display:
                    link_type = self.layers[1][obj.layer]
                    if not self.ntw.graph[obj.source][link_type]:
                        self.delete(obj.source.oval[obj.layer], obj.source.image[obj.layer])
                        self.delete(obj.source.layer_line)
                        obj.source.image[obj.layer], obj.source.oval[obj.layer] = None, None
                    if not self.ntw.graph[obj.destination][link_type]:
                        obj.destination.image[obj.layer], obj.destination.oval[obj.layer] = None, None
                        self.delete(obj.destination.oval[obj.layer], obj.destination.image[obj.layer])
                        self.delete(obj.destination.layer_line)
                        
    def draw_objects(self, objects, random_drawing):
        self._cancel()
        for obj in objects:
            if obj.network_type == "node":
                if(random_drawing):
                    obj.x, obj.y = random.randint(100,700), random.randint(100,700)
                    if not obj.image[0]: 
                        self.create_node(obj)
            else:
                self.create_link(obj)
             
    def draw_all(self, random=True):
        self.delete("all")
        
        for node in self.ntw.pn["node"].values():
            node.oval = {layer: None for layer in range(3)}
            node.image = {layer: None for layer in range(3)}
            
        for link_type in self.ntw.link_type:
            for link in self.ntw.pn[link_type].values():
                link.line = None
                
        for type in self.ntw.pn:
            # cannot draw an AS
            if type != "AS":
                self.draw_objects(self.ntw.pn[type].values(), random)
        
    ## Highlight and Unhighlight links and nodes (depending on class_type)
    def highlight_objects(self, *objects):
        for obj in objects:
            if(obj.class_type == "node"):
                self.itemconfig(obj.oval, fill="red")
                self.itemconfig(obj.image[0], image=self.master.dict_image["red"][obj.type])
            elif(obj.class_type == "link"):
                self.itemconfig(obj.line, fill="red", width=5)
                
    def unhighlight_objects(self, *objects):
        for obj in objects:
            if(obj.class_type == "node"):
                self.itemconfig(obj.oval, fill=obj.color)
                self.itemconfig(obj.image[0], image=self.master.dict_image["default"][obj.type])
            elif(obj.class_type == "link"):
                self.itemconfig(obj.line, fill=obj.color, width=self.LINK_WIDTH)  
                
    def unhighlight_all(self):
        for object_type in self.ntw.pn:
            self.unhighlight_objects(*self.ntw.pn[object_type].values())
                
    def create_node_label(self, node):
        node.lid = self.create_text(node.x - 15, node.y + 10, anchor="nw")
        self.itemconfig(node.lid, fill="blue", tags="label")
        # set the text of the label with refresh label
        self._refresh_object_label(node)
    
    def _create_link_label(self, link):
        try:
            coeff = (link.destination.y - link.source.y) / (link.destination.x - link.source.x)
        except ZeroDivisionError:
            coeff = 0
        middle_x = link.lpos[0] + 4*(1+(coeff>0))
        middle_y = link.lpos[1] - 12*(coeff>0)
        link.lid = self.create_text(middle_x, middle_y, anchor="nw", fill="red", tags="label")
        self._refresh_object_label(link)
        
    # refresh the label for one object with the current object label
    def _refresh_object_label(self, current_object, label_type=None):
        if not label_type:
            label_type = self._current_object_label[current_object.type]
        label_id = current_object.lid
        if label_type == "none":
            self.itemconfig(label_id, text="")
        elif(label_type in ["capacity", "flow", "cost"]):
            # retrieve the value of the parameter depending on label type
            valueSD = current_object.__dict__[label_type + "SD"]
            valueDS = current_object.__dict__[label_type + "DS"]
            self.itemconfig(label_id, text="SD:{} | DS:{}".format(valueSD, valueDS))
        elif(label_type == "position"):
            self.itemconfig(label_id, text="({}, {})".format(current_object.x, current_object.y))
        else:
            self.itemconfig(label_id, text=current_object.__dict__[label_type])
            
    # change label and refresh it for all objects
    def _refresh_object_labels(self, type, var_label):
        self._current_object_label[type] = var_label
        for obj in self.ntw.pn[type].values():
            self._refresh_object_label(obj, var_label)
            
    # show/hide display menu per type of objects
    def show_hide(self, menu, type, index):
        self.display_per_type[type] = not self.display_per_type[type]
        new_label = self.display_per_type[type]*"Hide" or "Show"
        menu.entryconfigure(index, label=" ".join((new_label, type)))
        new_state = tk.NORMAL if self.display_per_type[type] else tk.HIDDEN
        if(type in self.ntw.node_type_to_class):
            for node in filter(lambda o: o.type == type, self.ntw.pn["node"].values()):
                self.itemconfig(node.image[0] if self.display_image else node.oval, state=new_state)
                self.itemconfig(node.lid, state=new_state)
        else:
            for link in self.ntw.pn[type].values():
                self.itemconfig(link.line, state=new_state)
                self.itemconfig(link.lid, state=new_state)
        
    def erase_graph(self):
        self.object_id_to_object.clear()
        self.so = {"node": set(), "link": set()}
        self.temp_line = None
        self.drag_item = None
        
    def move_node(self, n):
        newx, newy = float(n.x), float(n.y)
        s = n.size

        for layer in self.layers[self.layered_display]:
            if n.image[layer]:
                y =  newy - layer*self.diff_y
                self.coords(n.image[layer], newx - (n.imagex)//2, y - (n.imagey)//2)
                self.coords(n.oval[layer], newx - s, y - s, newx + s, y + s)
            self.coords(n.lid, newx - 15, newy + 10)
        
        # move also the virtual line, which length depends on what layer exists
        if self.layered_display and n.layer_line:
            max_layer = 2 if self.ntw.graph[n]["traffic"] else 1 if self.ntw.graph[n]["route"] else 0
            self.coords(n.layer_line, newx, newy, newx, newy - max_layer*self.diff_y)
    
        # update links coordinates
        for type_link in self.ntw.link_type:
            for neighbor, t in self.ntw.graph[n][type_link]:
                layer = "all" if not self.layered_display else t.layer
                link_to_coords = self.link_coordinates(n, neighbor, layer)
                for link in link_to_coords:
                    self.coords(link.line, *link_to_coords[link])
                    # update link label coordinates
                    self.update_link_label_coordinates(link)
                    
    def update_link_label_coordinates(self, link):
        try:
            coeff = (link.destination.y - link.source.y) / (link.destination.x - link.source.x)
        except ZeroDivisionError:
            coeff = 0
        middle_x = link.lpos[0] + 4*(1+(coeff>0))
        middle_y = link.lpos[1] - 12*(coeff>0)
        self.coords(link.lid, middle_x, middle_y)
            
    def spring_based_drawing(self, master):
        # if the canvas is empty, drawing required first
        if not self._job:
            self.draw_all()
        self.ntw.spring_layout(master.alpha, master.beta, master.k, master.eta, master.delta, master.raideur)                
        for n in self.ntw.pn["node"].values():
            self.move_node(n)
        self._job = self.after(10, lambda: self.spring_based_drawing(master))
        
    def frucht(self):
        # update the optimal pairwise distance
        self.opd = sqrt(500*500/len(self.ntw.pn["node"].values())) if self.ntw.pn["node"].values() else 0
        self.ntw.fruchterman(self.opd)     
        for n in self.ntw.pn["node"].values():
            self.move_node(n)
        # stop job if convergence reached
        if(all(-10**(-2) < n.vx * n.vy < 10**(-2) for n in self.ntw.pn["node"].values())):
            return self._cancel()
        self._job = self.after(1, lambda: self.ntw.frucht())
            