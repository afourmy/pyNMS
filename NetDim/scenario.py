# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk
import network
import menus
import random
from math import cos, sin, atan2, sqrt, radians

class Scenario(tk.Canvas):
    
    def __init__(self, master, name):
        super().__init__(width=1100, height=600, background="bisque")
        self.name = name
        self.ntw = network.Network(self)
        self.object_id_to_object = {}
        self.master = master
        
        # job running or not (e.g drawing)
        self._job = None
        # number of iteration of the graph layout algorithm
        self.drawing_iteration = 0
        
        # default colors for highlighting areas
        self.default_colors = ["black", "red", "green", "blue", "cyan", "yellow", "magenta"]
        
        # default link width and node size
        self.LINK_WIDTH = 5
        self.NODE_SIZE = 8
        
        # default label display
        self._current_object_label = {obj_type: "none" for obj_type in ("node", "trunk", "route", "traffic")}
        
        # creation mode, object type, and associated bindings
        self._start_position = [None]*2
        self._object_type = "trunk"
        self.drag_item = None
        self.temp_line = None
        
        # object selected for rectangle selection
        self.object_selection = "node"
        
        # used to move several node at once
        self._start_pos_main_node = [None]*2
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
        
        # id of the failure icon
        self.id_failure = None
        
        # list of currently selected object ("so")
        self.so = {"node": set(), "link": set()}
        
        # initialization of all bindings for nodes creation
        self.switch_binding()
        
        ## bindings that remain available in all modes
        # highlight the path of a route/traffic link with left-click
        self.tag_bind("route", "<ButtonPress-1>", self.closest_route_path)
        self.tag_bind("traffic", "<ButtonPress-1>", self.closest_traffic_path)
        
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
        
        # add nodes to a current selection by pressing control
        self.ctrl = False
        def change_ctrl(value):
            self.ctrl = value
        self.bind("<Control-KeyRelease>", lambda _: change_ctrl(False))
        self.bind("<Control-KeyPress>", lambda _: change_ctrl(True))
        
    def switch_binding(self):   
        # in case there were selected nodes, so that they don't remain highlighted
        self.unhighlight_all()
        
        if self._mode == "motion":
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
            
            if self._creation_mode in self.ntw.node_type_to_class:
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
            
    @adapt_coordinates
    def closest_route_path(self, event):
        self.unhighlight_all()
        route = self.object_id_to_object[self.find_closest(event.x, event.y)[0]]
        self.highlight_route(route)
        
    @adapt_coordinates
    def closest_traffic_path(self, event):
        self.unhighlight_all()
        traffic = self.object_id_to_object[self.find_closest(event.x, event.y)[0]]
        self.highlight_objects(*traffic.path)
        for route in filter(lambda l: l.network_type == "route", traffic.path):
            self.highlight_route(route)
            
    def highlight_route(self, route):
        ft = self.ntw.failed_trunk
        if ft in route.r_path:
            self.highlight_objects(*route.r_path[ft], color="gold", dash=True)
        else:
            self.highlight_objects(*route.path)
        
    @adapt_coordinates
    def find_closest_node(self, event):
        # record the item and its location
        self._dict_start_position.clear()
        self.drag_item = self.find_closest(event.x, event.y)[0]
        # save the initial position to compute the delta for multiple nodes motion
        main_node_selected = self.object_id_to_object[self.drag_item]
        self._start_pos_main_node = main_node_selected.x, main_node_selected.y
        if main_node_selected in self.so["node"]:
            # for all selected node (sn), we store the initial position
            for sn in self.so["node"]:
                self._dict_start_position[sn] = [sn.x, sn.y]
        else:
            # we forget about the old selection, consider only the 
            # newly selected node, and update the dict of start position
            self.so = {"node": {main_node_selected}, "link": set()}
            x, y = main_node_selected.x, main_node_selected.y
            self._dict_start_position[main_node_selected] = [x, y]
            # we also need to update the highlight to that the old selection
            # is no longer highlighted but the newly selected node is.
            self.unhighlight_all()
            self.highlight_objects(main_node_selected)
            
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
            if not self.ctrl:
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
        if self._start_position != [None]*2:
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
        if self._start_position != [None]*2:
            # delete the temporary lines
            self.delete(self.temp_line_x_top)
            self.delete(self.temp_line_x_bottom)
            self.delete(self.temp_line_y_left)
            self.delete(self.temp_line_y_right)
            # select all nodes enclosed in the rectangle
            start_x, start_y = self._start_position
            for obj in self.find_enclosed(start_x, start_y, event.x, event.y):
                if obj in self.object_id_to_object:
                    enclosed_obj = self.object_id_to_object[obj]
                    if enclosed_obj.class_type == self.object_selection:
                        self.so[self.object_selection].add(enclosed_obj)
            self.highlight_objects(*self.so["node"]|self.so["link"])
            self._start_position = [None]*2
        
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
        if self.drag_item in self.object_id_to_object: # to avoid labels
            destination_node = self.object_id_to_object[self.drag_item]
            if destination_node.class_type == "node": # because tag filtering doesn't work !
                # create the link and the associated line
                if start_node != destination_node:
                    new_link = self.ntw.lf(link_type=type, s=start_node, d=destination_node)
                    self.create_link(new_link)
              
    @adapt_coordinates
    def create_node_on_binding(self, event):
        new_node = self.ntw.nf(event.x, event.y, node_type=self._creation_mode)
        self.create_node(new_node)
        
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
            #node.size = abs(new_coords[0] - new_coords[2])/2 
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
        factor = 1.1 if event.delta > 0 else 0.9
        self.diff_y *= factor
        self.NODE_SIZE *= factor
        self.scale("all", event.x, event.y, factor, factor)
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
    
    def add_to_edges(self, AS, *nodes):
        for node in nodes:
            if node not in AS.edges:
                AS.edges.add(node)
                AS.management.listbox_edges.insert(tk.END, obj)

        
    ## Highlight and Unhighlight links and nodes (depending on class_type)
    def highlight_objects(self, *objects, color="red", dash=False):
        for obj in objects:
            if obj.class_type == "node":
                self.itemconfig(obj.oval, fill=color)
                self.itemconfig(obj.image[0], image=self.master.dict_image["red"][obj.type])
            elif obj.class_type == "link":
                dash = (3, 5) if dash else ()
                self.itemconfig(obj.line, fill=color, width=5, dash=dash)
                
    def unhighlight_objects(self, *objects):
        for obj in objects:
            if obj.class_type == "node":
                self.itemconfig(obj.oval, fill=obj.color)
                self.itemconfig(obj.image[0], image=self.master.dict_image["default"][obj.type])
            elif obj.class_type == "link":
                self.itemconfig(obj.line, fill=obj.color, width=self.LINK_WIDTH, dash=obj.dash)  
                
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
            label_type = self._current_object_label[current_object.network_type]
        label_id = current_object.lid
        if label_type == "none":
            self.itemconfig(label_id, text="")
        elif label_type in ("capacity", "flow", "cost", "traffic"):
            # retrieve the value of the parameter depending on label type
            valueSD = getattr(current_object, label_type + "SD")
            valueDS = getattr(current_object, label_type + "DS")
            if label_type == "traffic":
                text = str(valueSD + valueDS)
            else:
                text = "SD:{} | DS:{}".format(valueSD, valueDS)
            self.itemconfig(label_id, text=text)
        elif label_type == "position":
            text = "({}, {})".format(current_object.x, current_object.y)
            self.itemconfig(label_id, text=text)
        elif label_type == "ipaddress":
            valueS = getattr(current_object, label_type + "S")
            valueD = getattr(current_object, label_type + "D")
            s = getattr(current_object, "source")
            d = getattr(current_object, "destination")
            text = "{}: {}\n{}: {}".format(s, valueS, d, valueD)
            self.itemconfig(label_id, text=text)
        else:
            self.itemconfig(label_id, text=getattr(current_object, label_type))
        self.itemconfig(label_id, font="bold")
            
    # change label and refresh it for all objects
    def _refresh_object_labels(self, type, var_label=None):
        if var_label:
            self._current_object_label[type] = var_label
        for obj in self.ntw.pn[type].values():
            self._refresh_object_label(obj, self._current_object_label[type])
            
    def refresh_all_labels(self):
        for type in self.ntw.pn:
            self._refresh_object_labels(type)
            
    # show/hide display menu per type of objects
    def show_hide(self, menu, type, index):
        self.display_per_type[type] = not self.display_per_type[type]
        new_label = self.display_per_type[type]*"Hide" or "Show"
        menu.entryconfigure(index, label=" ".join((new_label, type)))
        new_state = tk.NORMAL if self.display_per_type[type] else tk.HIDDEN
        if type in self.ntw.node_type_to_class:
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
        s = self.NODE_SIZE

        for layer in self.layers[self.layered_display]:
            if n.image[layer]:
                y =  newy - layer*self.diff_y
                self.coords(n.image[layer], newx - (n.imagex)//2, y - (n.imagey)//2)
                self.coords(n.oval[layer], newx - s, y - s, newx + s, y + s)
            self.coords(n.lid, newx - 15, newy + 10)
        
        # move also the virtual line, which length depends on what layer exists
        if self.layered_display:
            for layer in range(1, 3):
                if n.layer_line[layer]:
                    self.coords(n.layer_line[layer], newx, newy, newx, newy - layer*self.diff_y)
    
        # update links coordinates
        for type_link in self.ntw.link_type:
            for neighbor, t in self.ntw.graph[n][type_link]:
                layer = "all" if not self.layered_display else t.layer
                link_to_coords = self.link_coordinates(n, neighbor, layer)
                for link in link_to_coords:
                    self.coords(link.line, *link_to_coords[link])
                    # update link label coordinates
                    self.update_link_label_coordinates(link)
                    # if there is a link in failure, we need to update the
                    # failure icon by retrieving the middle position of the arc
                    if link == self.ntw.failed_trunk:
                        mid_x, mid_y = link_to_coords[link][2:4]
                        self.coords(self.id_failure, mid_x, mid_y)
                    
    def update_link_label_coordinates(self, link):
        try:
            coeff = (link.destination.y - link.source.y) / (link.destination.x - link.source.x)
        except ZeroDivisionError:
            coeff = 0
        middle_x = link.lpos[0] + 4*(1+(coeff>0))
        middle_y = link.lpos[1] - 12*(coeff>0)
        self.coords(link.lid, middle_x, middle_y)
        
    def frucht(self):
        # update the optimal pairwise distance
        self.opd = sqrt(500*500/len(self.ntw.pn["node"].values())) if self.ntw.pn["node"].values() else 0
        self.ntw.fruchterman(self.opd)     
        for n in self.ntw.pn["node"].values():
            self.move_node(n)
        # stop job if convergence reached
        if all(-10**(-2) < n.vx * n.vy < 10**(-2) for n in self.ntw.pn["node"].values()):
            return self._cancel()
        self._job = self.after(1, lambda: self.ntw.frucht())
        
    # cancel the graph drawing job
    def _cancel(self):
        if self._job is not None:
            self.after_cancel(self._job)
            self._job = None
            
    ## TODO repair the 3D view
            
    def create_node(self, node, layer=0):
        s = self.NODE_SIZE
        curr_image = self.master.dict_image["default"][node.type]
        y = node.y - layer * self.diff_y
        tags = () if layer else (node.type, node.class_type, "object")
        node.image[layer] = self.create_image(node.x - (node.imagex)/2, 
                y - (node.imagey)/2, image=curr_image, anchor=tk.NW, tags=tags)
        node.oval[layer] = self.create_oval(node.x-s, y-s, node.x+s, y+s, 
                                outline=node.color, fill=node.color, tags=tags)
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
            d = ((id+1)//2) * 30 * (-1)**id
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
                    if self.layered_display and not node.layer_line[new_link.layer]:
                        coords = (node.x, node.y, node.x, node.y - new_link.layer * self.diff_y) 
                        node.layer_line[new_link.layer] = self.create_line(*coords, fill="black", width=1, dash=(3,5))
                        self.tag_lower(node.layer_line[new_link.layer])
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
        
    def erase_all(self):
        self.delete("all")
        
        for node in self.ntw.pn["node"].values():
            node.oval = {layer: None for layer in range(3)}
            node.image = {layer: None for layer in range(3)}
            node.layer_line = {layer: None for layer in range(1,3)}
            
        for link_type in self.ntw.link_type:
            for link in self.ntw.pn[link_type].values():
                link.line = None
                
    def switch_display_mode(self):
        self.layered_display = not self.layered_display
        
        if self.layered_display:
            self.planal_move(50)
            min_y = min(node.y for node in self.ntw.pn["node"].values())
            max_y = max(node.y for node in self.ntw.pn["node"].values())
            self.diff_y = max_y - min_y + 100
            
        self.draw_all(False)
            
    def planal_move(self, angle=45):
        min_y = min(node.y for node in self.ntw.pn["node"].values())
        max_y = max(node.y for node in self.ntw.pn["node"].values())
        
        for node in self.ntw.pn["node"].values():
            diff_y = abs(node.y - min_y)
            new_y = min_y + diff_y * cos(radians(angle))
            node.y = new_y
                    
    def remove_objects(self, *objects):
        for obj in objects:
            if obj.network_type not in ("traffic", "route"):
                for AS in list(obj.AS):
                    AS.management.remove_from_AS(obj)
            if obj.class_type == "node":
                self.delete(obj.oval[0], obj.image[0], obj.lid)
                self.remove_objects(*self.ntw.remove_node(obj))
                if self.layered_display:
                    for layer in (1, 2):
                        self.delete(
                                    obj.oval[layer], 
                                    obj.image[layer], 
                                    obj.layer_line[layer]
                                    )
            if obj.class_type == "link":
                # we remove the line as well as the label on the canvas
                self.delete(obj.line, obj.lid)
                # we remove the associated link in the network model
                self.ntw.remove_link(obj)
                # if the layered display is activate and the link 
                # to delete is not a physical link (trunk)
                if self.layered_display and obj.layer:
                    for edge in (obj.source, obj.destination):
                        # we check if there still are other links of the same
                        # type (i.e at the same layer) between the edge nodes
                        if not self.ntw.graph[edge][obj.network_type]:
                            # if that's not the case, we delete the upper-layer
                            # projection of the edge nodes, and reset the 
                            # associated "layer to projection id" dictionnary
                            self.delete(edge.oval[obj.layer], edge.image[obj.layer])
                            edge.image[obj.layer] = edge.oval[obj.layer] = None
                            # we delete the dashed "layer line" and reset the
                            # associated "layer to layer line id" dictionnary
                            self.delete(edge.layer_line[obj.layer])
                            edge.layer_line[obj.layer] = None
                        
    def draw_objects(self, objects, random_drawing):
        self._cancel()
        for obj in objects:
            if obj.network_type == "node":
                if random_drawing:
                    obj.x, obj.y = random.randint(100,700), random.randint(100,700)
                    self.move_node(obj)
                if not obj.image[0]: 
                    self.create_node(obj)
            else:
                self.create_link(obj)
             
    def draw_all(self, random=True):
        self.erase_all()
        for type in self.ntw.pn:
            self.draw_objects(self.ntw.pn[type].values(), random)
            
    def spring_based_drawing(self, master, nodes):
        if not self._job:
            # reset the number of iterations
            self.drawing_iteration = 0
        self.drawing_iteration += 1
        self.ntw.spring_layout(nodes, *self.master.drawing_param)
        if not self.drawing_iteration % 5:   
            for node in nodes:
                self.move_node(node)
        self._job = self.after(1, lambda: self.spring_based_drawing(master, nodes))
            
    ## Failure simulation
    
    def simulate_failure(self, trunk):
        self.delete(self.id_failure)
        self.ntw.failed_trunk = trunk
        source, destination = trunk.source, trunk.destination
        xA, yA, xB, yB = source.x, source.y, destination.x, destination.y
        self.id_failure = self.create_image(
                                            (xA+xB)/2, 
                                            (yA+yB)/2, 
                                            image = self.master.img_failure
                                            )