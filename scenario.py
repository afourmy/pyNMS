import tkinter as tk
import network
import menus
import random
import math

class Scenario(network.Network, tk.Canvas):
    
    def __init__(self, master, name):
        network.Network.__init__(self, name)
        tk.Canvas.__init__(self, width=1100, height=600, background="bisque")
        self.object_id_to_object = {}
        self.master = master
        
        # job running or not (e.g drawing)
        self._job = None
        
        # default colors for highlighting areas
        # TODO use this for the image dict
        self.default_colors = ["black", "red", "green", "blue", "cyan", "yellow", "magenta"]
        
        # default link width and node size
        self.LINK_WIDTH = 5
        self.test = []
        
        # default label display
        self._current_object_label = {obj_type: "name" for obj_type in self.all_type}
        
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
        # display state per type of objects
        self.display_per_type = {type: True for type in self.all_type}
        
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
            
            if(self._creation_mode in self.node_type_to_class):
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
                    new_link = self.link_factory(link_type=type, s=start_node, d=destination_node)
                    self.create_link(new_link)
              
    @adapt_coordinates
    def create_node_on_binding(self, event):
        new_node = self.node_factory(event.x, event.y, node_type=self._creation_mode)
        self.create_node(new_node)
        
    def create_node(self, node):
        s = node.size
        curr_image = self.master.dict_image["default"][node.type]
        node.image = self.create_image(node.x - (node.imagex)/2, node.y - (node.imagey)/2, image = curr_image, anchor = tk.NW, tags=(node.type, node.class_type, "object"))
        node.oval = self.create_oval(node.x-s, node.y-s, node.x+s, node.y+s, outline=node.color, fill=node.color, tags=(node.type, node.class_type, "object"))
        # create/hide the image/the oval depending on the current mode
        if(self.display_image):
            self.itemconfig(node.oval, state=tk.HIDDEN)
        else:
            self.itemconfig(node.image, state=tk.HIDDEN)
        self.object_id_to_object[node.oval] = node
        self.object_id_to_object[node.image] = node
        self.create_node_label(node)
        
    # TODO ellipse line
    def create_link(self, link):
        # we fist check how many links there are between the source/dest of the link
        # in order to compute the angle of the arc
        source, destination = link.source, link.destination
        nb_links = self.number_of_links_between(source, destination) - 1
        link.line = self.create_line(link.source.x, link.source.y, link.destination.x, link.destination.y, tags=(link.type, link.class_type, "object"), fill=link.color, width=self.LINK_WIDTH, dash=link.dash)
        self.tag_lower(link.line)
        self.object_id_to_object[link.line] = link
        self._create_link_label(link)
        self._refresh_object_label(link)
        
    def change_display(self):
        # flip the display from icon to oval and vice-versa, depend on display_image boolean
        self.display_image = not self.display_image
        for node in self.pn["node"].values():
            self.itemconfig(node.oval, state=tk.HIDDEN if self.display_image else tk.NORMAL)
            self.itemconfig(node.image, state=tk.NORMAL if self.display_image else tk.HIDDEN)

    def scroll_start(self, event):
        self.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        self.scan_dragto(event.x, event.y, gain=1)

    ## Zoom / unzoom on the canvas
    
    def update_nodes_coordinates(self):
        # scaling changes the coordinates of the oval, and we update 
        # the corresponding node's coordinates accordingly
        for node in self.pn["node"].values():
            new_coords = self.coords(node.oval)
            node.x, node.y = (new_coords[0] + new_coords[2])/2, (new_coords[3] + new_coords[1])/2
            self.coords(node.image, node.x - (node.imagex)/2, node.y - (node.imagey)/2)
            node.size = abs(new_coords[0] - new_coords[2])/2 # the oval was also resized while scaling
        
    @adapt_coordinates
    def zoomer(self, event):
        """ Zoom for window """
        self._cancel()
        if(event.delta > 0):
            self.scale("all", event.x, event.y, 1.1, 1.1)
        elif(event.delta < 0):
            self.scale("all", event.x, event.y, 0.9, 0.9)
        self.configure(scrollregion = self.bbox("all"))
        self.update_nodes_coordinates()
        self._refresh_labels_position()
        
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
        
    def remove_objects(self, *objects):
        for obj in objects:
            if(obj.class_type == "node"):
                self.delete(obj.oval, obj.image, obj.lid)
                self.remove_objects(*self.remove_node_from_network(obj))
                for AS in obj.AS:
                    AS.management.remove_nodes_from_AS(AS, obj)
            if(obj.class_type == "link"):
                self.delete(obj.line, obj.lid)
                self.remove_link_from_network(obj)
                if(obj.AS):
                    obj.AS.management.remove_trunks_from_AS(obj)
            
    def draw_objects(self, nodes, links, random_drawing):
        self._cancel()
        for n in nodes:
            if(random_drawing):
                n.x, n.y = random.randint(100,700), random.randint(100,700)
            self.create_node(n)

        for l in links:
            self.create_link(l)
             
    def draw_all(self, random=True):
        self.delete("all")
        all_links = list(self.pn["trunk"].values())\
        + list(self.pn["route"].values())\
        + list(self.pn["traffic"].values())
        self.draw_objects(self.pn["node"].values(),all_links, random)
        
    ## Highlight and Unhighlight links and nodes (depending on class_type)
    def highlight_objects(self, *objects):
        for obj in objects:
            if(obj.class_type == "node"):
                self.itemconfig(obj.oval, fill="red")
                self.itemconfig(obj.image, image=self.master.dict_image["red"][obj.type])
            elif(obj.class_type == "link"):
                self.itemconfig(obj.line, fill="red", width=5)
                
    def unhighlight_objects(self, *objects):
        for obj in objects:
            if(obj.class_type == "node"):
                self.itemconfig(obj.oval, fill=obj.color)
                self.itemconfig(obj.image, image=self.master.dict_image["default"][obj.type])
            elif(obj.class_type == "link"):
                self.itemconfig(obj.line, fill=obj.color, width=self.LINK_WIDTH)  
                
    def unhighlight_all(self):
        for object_type in self.pn:
            self.unhighlight_objects(*self.pn[object_type].values())
                
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
        middle_x = link.source.x + (link.destination.x - link.source.x)//2 + 4*(1+(coeff>0))
        middle_y = link.source.y + (link.destination.y - link.source.y)//2 - 12*(coeff>0)
        link.lid = self.create_text(middle_x, middle_y, anchor="nw", fill="red", tags="label")
        self._refresh_object_label(link)
        
    # refresh the label for one object with the current object label
    def _refresh_object_label(self, current_object, label_type=None):
        if not label_type:
            label_type = self._current_object_label[current_object.type]
        label_id = current_object.lid
        if label_type == "none":
            self.itemconfig(label_id, text="")
        elif(label_type in ["capacity", "flow"]):
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
        for obj in self.pn[type].values():
            self._refresh_object_label(obj, var_label)
            
    # refresh label position for all objects after zooming
    def _refresh_labels_position(self):
        for node in self.pn["node"].values():
            self.coords(node.lid, node.x - 15, node.y + 10)
        for type in self.link_type:
            for link in self.pn[type].values():
                try:
                    coeff = (link.destination.y - link.source.y) / (link.destination.x - link.source.x)
                except ZeroDivisionError:
                    coeff = 0
                middle_x = link.source.x + (link.destination.x - link.source.x)//2 + 4*(1+(coeff>0))
                middle_y = link.source.y + (link.destination.y - link.source.y)//2 - 12*(coeff>0)
                self.coords(link.lid, middle_x, middle_y)
            
    # show/hide display menu per type of objects
    def show_hide(self, menu, type, index):
        self.display_per_type[type] = not self.display_per_type[type]
        new_label = self.display_per_type[type]*"Hide" or "Show"
        menu.entryconfigure(index, label=" ".join((new_label, type)))
        new_state = tk.NORMAL if self.display_per_type[type] else tk.HIDDEN
        if(type in self.node_type_to_class):
            for node in filter(lambda o: o.type == type, self.pn["node"].values()):
                self.itemconfig(node.image if self.display_image else node.oval, state=new_state)
                self.itemconfig(node.lid, state=new_state)
        else:
            for link in self.pn[type].values():
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
        self.coords(n.image, newx - (n.imagex)//2, newy - (n.imagey)//2)
        self.coords(n.oval, newx - s, newy - s, newx + s, newy + s)
        self.coords(n.lid, newx - 15, newy + 10)
    
        # update links coordinates
        for type_link in self.graph[n]:
            for link in self.graph[n][type_link]:
                coords = self.coords(link.line)
                c = 2*(link.source != n)
                coords[c], coords[c+1] = int(n.x), int(n.y)
                self.coords(link.line, *coords)
                
                #TODO coeff and MIDDLE f(link) should be a specific function its used 3 times
                # update link label coordinates
                try:
                    coeff = (link.destination.y - link.source.y) / (link.destination.x - link.source.x)
                except ZeroDivisionError:
                    coeff = 0
                middle_x = link.source.x + (link.destination.x - link.source.x)//2 + 4*(1+(coeff>0))
                middle_y = link.source.y + (link.destination.y - link.source.y)//2 - 12*(coeff>0)
                self.coords(link.lid, middle_x, middle_y)
            
    def spring_based_drawing(self, master):
        # if the canvas is empty, drawing required first
        if not self._job:
            self.draw_all()
        self.spring_layout(master.alpha, master.beta, master.k, master.eta, master.delta, master.raideur)                
        for n in self.pn["node"].values():
            self.move_node(n)
        self._job = self.after(10, lambda: self.spring_based_drawing(master))
        
    def frucht(self):
        # update the optimal pairwise distance
        self.opd = math.sqrt(500*500/len(self.pn["node"].values())) if self.pn["node"].values() else 0
        self.fruchterman(self.opd)     
        for n in self.pn["node"].values():
            self.move_node(n)
        # stop job if convergence reached
        if(all(-10**(-2) < n.vx * n.vy < 10**(-2) for n in self.pn["node"].values())):
            return self._cancel()
        self._job = self.after(1, lambda: self.frucht())
            