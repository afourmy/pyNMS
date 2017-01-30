# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk
import network
import miscellaneous.search as search
import re
from pythonic_tkinter.preconfigured_widgets import *
from objects.objects import *
from menus.general_rightclick_menu import GeneralRightClickMenu
from menus.selection_rightclick_menu import SelectionRightClickMenu
from random import randint
from math import cos, sin, atan2, sqrt, radians

class Scenario(CustomFrame):
    
    def __init__(self, master, name):
        super().__init__(width=1300, height=800)
        self.grid(row=0, column=0)

        self.cvs = tk.Canvas(
                             self, 
                             bg = '#FFFFFF', 
                             width = 1300, 
                             height = 800,
                             )
                             
        hbar = Scrollbar(self, orient = tk.HORIZONTAL)
        hbar.pack(side=tk.BOTTOM,fill=tk.X)
        hbar.config(command=self.cvs.xview)
        
        vbar = Scrollbar(self, orient = tk.VERTICAL)
        vbar.pack(side=tk.RIGHT,fill=tk.Y)
        vbar.config(command=self.cvs.yview)
        
        self.cvs.config(width=1300, height=800)
        self.cvs.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.cvs.pack(side=tk.LEFT,expand=1,fill=tk.BOTH)
        
        self.name = name
        self.ntw = network.Network(self)
        self.object_id_to_object = {}
        self.ms = master
        
        # job running or not (e.g drawing)
        self._job = None
        # number of iteration of the graph layout algorithm
        self.drawing_iteration = 0
            
        # default link width and node size
        self.LINK_WIDTH = 5
        self.NODE_SIZE = 8
        
        # default label display
        self.current_label = dict.fromkeys(object_labels, 'none')
        
        # creation mode, object type, and associated bindings
        self._start_position = [None]*2
        self._object_type = 'plink'
        self.drag_item = None
        self.temp_line = None
        
        # object selected for rectangle selection
        self.obj_selection = 'node'
        
        # used to move several node at once
        self._start_pos_main_node = [None]*2
        self._dict_start_position = {}
        
        # the default motion is creation of nodes
        self._mode = 'motion'
        self._creation_mode = 'router'
        
        # 2D display or 3D display
        self.layered_display = False
        # number of layers
        self.nbl = 4
        # if layered_display is false, there's only one layer (self.layers[0])
        # else we need a dictionnary associating a type to each layer
        self.layers = [(0,), {1: 'plink', 2: 'l2link', 3: 'l3link', 4: 'traffic'}]
        # defines whether a layer should be display or not. By default,
        # IP and Ethernet virtual connections are not displayed.
        self.display_layer = [0] + [True] * self.nbl
        # difference between each layer in pixel
        self.diff_y = 0
        
        # display state per type of objects
        self.display_per_type = dict.fromkeys(self.ntw.all_subtypes, True)
        
        # indexes of the failure icons: dictionnary that bins
        # physical links item to the id of the associated icon
        self.id_fdtks = {}
        
        # list of currently selected object ('so')
        self.so = {'node': set(), 'link': set()}
        
        # source / destination indicators when a link is selected
        self.src_label = None
        self.dest_label = None
        
        # initialization of all bindings for nodes creation
        self.switch_binding()
        
        ## bindings that remain available in both modes
        # highlight the path of a route/traffic link with left-click
        self.cvs.tag_bind('route', '<ButtonPress-1>', self.closest_route_path)
        
        # zoom and unzoom on windows
        self.cvs.bind('<MouseWheel>',self.zoomer)
        
        # same on linux
        self.cvs.bind('<Button-4>', self.zoomerP)
        self.cvs.bind('<Button-5>', self.zoomerM)
        
        # add binding for right-click menu 
        self.cvs.tag_bind('object', '<ButtonPress-3>',
                                    lambda e: SelectionRightClickMenu(e, self))
        
        # use the right-click to move the background
        self.cvs.bind('<ButtonPress-3>', self.scroll_start)
        self.cvs.bind('<B3-Motion>', self.scroll_move)
        self.cvs.bind('<ButtonRelease-3>', self.general_menu)
        
        # use Ctrl+F to look for an object
        self.cvs.bind('<Control-Key-f>', lambda e: search.SearchObject(master))
        
        # initialize other bindings depending on the mode
        self.switch_binding()
        
        # window and highlight when hovering over an object
        self.cvs.bind('<Motion>', lambda e: self.motion(e))
        self.pwindow = None
        
        # we also keep track of the closest object for the motion function
        self.co = None
        
        # switch the object rectangle selection by pressing space
        self.cvs.bind('<space>', self.change_object_selection)
        
        # add nodes to a current selection by pressing control
        self.ctrl = False
        
        def change_ctrl(value):
            self.ctrl = value
            
        self.cvs.bind('<Control-KeyRelease>', lambda _: change_ctrl(False))
        self.cvs.bind('<Control-KeyPress>', lambda _: change_ctrl(True))
        
        # display/undisplay a layer by pressing the associated number
        for layer in range(1, self.nbl):
            self.cvs.bind(str(layer), lambda _, l=layer: self.invert_layer_display(l))
            
    ## Bindings
        
    def switch_binding(self):   
        # if there were selected nodes, so that they don't remain highlighted
        self.unhighlight_all()
        
        if self._mode == 'motion':
            # unbind unecessary bindings
            self.cvs.unbind('<Button 1>')
            self.cvs.tag_unbind('link', '<Button-1>')
            self.cvs.tag_unbind('node', '<Button-1>')
            self.cvs.tag_unbind('node', '<B1-Motion>')
            self.cvs.tag_unbind('node', '<ButtonRelease-1>')
            
            # set the focus on the canvas when clicking on it
            # allows for the keyboard binding to work properly
            self.cvs.bind('<1>', lambda event: self.cvs.focus_set())
            
            # add bindings to drag a node with left-click
            self.cvs.tag_bind('link', '<Button-1>', self.find_closest_link, add='+')
            self.cvs.tag_bind('node', '<Button-1>', self.find_closest_node, add='+')
            for tag in ('node', 'link'):
                self.cvs.tag_bind(tag, '<Button-1>', self.update_mgmt_window, add='+')
            self.cvs.tag_bind('node', '<B1-Motion>', self.node_motion)
            
            # add binding to select all nodes in a rectangle
            self.cvs.bind('<ButtonPress-1>', self.start_point_select_objects, add='+')
            self.cvs.bind('<B1-Motion>', self.rectangle_drawing)
            self.cvs.bind('<ButtonRelease-1>', self.end_point_select_nodes, add='+')
            
        else:
            # unbind unecessary bindings
            self.cvs.unbind('<Button-1>')
            self.cvs.unbind('<ButtonPress-1>')
            self.cvs.unbind('<ButtonRelease-1>')
            self.cvs.unbind('<ButtonMotion-1>')
            self.cvs.tag_unbind('node', '<Button-1>')
            self.cvs.tag_unbind('link', '<Button-1>')
            
            if self._creation_mode in self.ntw.node_class:
                # add bindings to create a node with left-click
                self.cvs.bind('<ButtonPress-1>', self.create_node_on_binding)
                
            elif self._creation_mode == 'rectangle':
                # add binding to draw a rectangle
                self.cvs.bind('<ButtonPress-1>', self.start_point_rectangle)
                self.cvs.bind('<B1-Motion>', self.rectangle_drawing)
            
            else:
                # add bindings to create a link between two nodes
                self.cvs.tag_bind('node', '<Button-1>', self.start_link)
                self.cvs.tag_bind('node', '<B1-Motion>', self.line_creation)
                release = lambda event, type=type: self.link_creation(
                                                    event, self._creation_mode)
                self.cvs.tag_bind('node', '<ButtonRelease-1>', release)
                
    def adapt_coordinates(function):
        def wrapper(self, event, *others):
            event.x, event.y = self.cvs.canvasx(event.x), self.cvs.canvasy(event.y)
            function(self, event, *others)
        return wrapper
                
    ## Drawing modes
    
    def start_point_rectangle(self, event):
        x, y = self.cvs.canvasx(event.x), self.cvs.canvasy(event.y)
        self._start_position = x, y
        self.temp_line_x_top = self.cvs.create_line(x, y, x, y)
        self.temp_line_y_left = self.cvs.create_line(x, y, x, y)
        self.temp_line_y_right = self.cvs.create_line(x, y, x, y)
        self.temp_line_x_bottom = self.cvs.create_line(x, y, x, y)
                
    def draw(self, mode):
        if self._creation_mode == 'text':
            LabelCreation(self)
        elif self._creation_mode == 'rectangle':
            pass
        
    def invert_layer_display(self, layer):
        self.display_layer[layer] = not self.display_layer[layer]
        self.draw_all(False)
            
    @adapt_coordinates
    def closest_route_path(self, event):
        self.unhighlight_all()
        route = self.object_id_to_object[self.cvs.find_closest(event.x, event.y)[0]]
        self.highlight_route(route)
            
    def highlight_route(self, route):
        self.highlight_objects(*route.path)
        
    @adapt_coordinates
    def find_closest_node(self, event):
        # record the item and its location
        self._dict_start_position.clear()
        self.drag_item = self.cvs.find_closest(event.x, event.y)[0]
        # save the initial position to compute the delta for multiple nodes motion
        main_node_selected = self.object_id_to_object[self.drag_item]
        merged_dict = main_node_selected.image.items()
        layer = [l for l, item_id in merged_dict if item_id == self.drag_item].pop()
        diff = layer * self.diff_y
        self._start_pos_main_node = main_node_selected.x, main_node_selected.y + diff
        if main_node_selected in self.so['node']:
            # for all selected node (sn), we store the initial position
            for sn in self.so['node']:
                self._dict_start_position[sn] = [sn.x, sn.y + diff]
        else:
            # if ctrl is not pressed, we forget about the old selection, 
            # consider only the newly selected node, and unhighlight everything
            if not self.ctrl:
                self.unhighlight_all()
            self.highlight_objects(main_node_selected)
            # we update the dict of start position
            x, y = main_node_selected.x, main_node_selected.y
            self._dict_start_position[main_node_selected] = [x, y]
            # we also need to update the highlight to that the old selection
            # is no longer highlighted but the newly selected node is.
            self.highlight_objects(main_node_selected)
            
    @adapt_coordinates
    def find_closest_link(self, event):
        closest_link = self.cvs.find_closest(event.x, event.y)[0]
        main_link_selected = self.object_id_to_object[closest_link]
        if not self.ctrl:
            self.unhighlight_all()
        self.highlight_objects(main_link_selected)
        source = main_link_selected.source
        destination = main_link_selected.destination
        if not self.src_label:
            font= ("Purisa", '12', 'bold')
            self.src_label = self.cvs.create_text(
                                              source.x, 
                                              source.y, 
                                              text = 'S', 
                                              font = font, 
                                              fill = 'yellow'
                                              )
            self.dest_label = self.cvs.create_text(
                                               destination.x, 
                                               destination.y, 
                                               text = 'D', 
                                               font = font, 
                                               fill = 'yellow'
                                               )
        if main_link_selected.type in ('traffic', 'route'):
            if hasattr(main_link_selected, 'path'):
                self.highlight_objects(*main_link_selected.path)

    def update_mgmt_window(self, event):
        if self.co:
            # update the object management window with the closest object
            self.ms.dict_obj_mgmt_window[self.co.subtype].current_obj = self.co
            self.ms.dict_obj_mgmt_window[self.co.subtype].update()
    
    @adapt_coordinates
    def motion(self, event):
        x, y = event.x, event.y
        # if there is at least one object on the canvas
        if self.cvs.find_closest(x, y):
            # we retrieve it
            co_id = self.cvs.find_closest(x, y)[0]
            if co_id in self.object_id_to_object:
                co = self.object_id_to_object[co_id]
                # we check if the closest object is under the mouse on the canvas
                if co_id in self.cvs.find_overlapping(x - 1, y - 1, x + 1, y + 1):
                    if co != self.co:
                        if self.pwindow:
                            self.pwindow.destroy()
                        if self.co and self.co not in self.so[self.co.class_type]:
                            self.unhighlight_objects(self.co)
                        self.co = co
                        if co not in self.so[co.class_type]:
                            self.highlight_objects(co, color='purple')
                        self.pwindow = tk.Toplevel(self)
                        self.pwindow.wm_overrideredirect(1)
                        text = '\n'.join(
                                         prop_to_nice_name[property] 
                                         + ' : ' + str(getattr(co, property)) 
                                         + ' ' for property in 
                                         box_properties[co.subtype]
                                         )
                        x0, y0 = self.ms.winfo_x() + 250, self.ms.winfo_y() + 75
                        self.pwindow.wm_geometry('+%d+%d' % (x0, y0))
                        try:
                            # mac os compatibility
                            self.pwindow.tk.call(
                                            '::tk::unsupported::MacWindowStyle',
                                            'style', 
                                            self.pwindow._w,
                                            'help', 
                                            'noActivates'
                                            )
                        except tk.TclError:
                            pass
                        label = tk.Label(
                                        self.pwindow, 
                                        text = text, 
                                        justify = tk.LEFT,
                                        background = '#ffffe0', 
                                        relief = tk.SOLID, 
                                        borderwidth = 1,
                                        font = ('tahoma', '8', 'normal')
                                        )
                        label.pack(ipadx=1)
                else:
                    if self.co:
                        if self.co not in self.so[self.co.class_type]:
                            self.unhighlight_objects(self.co)
                        self.co = None
                        self.pwindow.destroy()  
                
    ## Menus
        
    def general_menu(self, event):
        x, y = self._start_pos_main_node
        # if the right-click button was pressed, but the position of the 
        # canvas when the button is released hasn't changed, we create
        # the general right-click menu
        if (x, y) == (event.x, event.y):
            GeneralRightClickMenu(event, self)
            
    ## Right-click scroll
    
    def scroll_start(self, event):
        # we record the position of the mouse when right-click is pressed
        # to check, when it is released, if the intent was to drag the canvas
        # or to have access to the right-click menu
        self._start_pos_main_node = event.x, event.y
        self.cvs.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        self.cvs.scan_dragto(event.x, event.y, gain=1)

    ## Zoom / unzoom on the canvas
    
    @adapt_coordinates
    def zoomer(self, event):
        ''' Zoom for window '''
        self._cancel()
        factor = 1.1 if event.delta > 0 else 0.9
        self.diff_y *= factor
        self.NODE_SIZE *= factor
        self.cvs.scale('all', event.x, event.y, factor, factor)
        self.cvs.configure(scrollregion = self.cvs.bbox('all'))
        self.update_nodes_coordinates()
        
    @adapt_coordinates
    def zoomerP(self, event):
        ''' Zoom for Linux '''
        self._cancel()
        self.cvs.scale('all', event.x, event.y, 1.1, 1.1)
        self.cvs.configure(scrollregion = self.cvs.bbox('all'))
        self.update_nodes_coordinates()
        
    @adapt_coordinates
    def zoomerM(self, event):
        ''' Zoom for Linux '''
        self._cancel()
        self.cvs.scale('all', event.x, event.y, 0.9, 0.9)
        self.cvs.configure(scrollregion = self.cvs.bbox('all'))
        self.update_nodes_coordinates()
    
    def update_nodes_coordinates(self):
        # scaling changes the coordinates of the oval, and we update 
        # the corresponding node's coordinates accordingly
        for node in self.ntw.nodes.values():
            new_coords = self.cvs.coords(node.oval[1])
            node.x = (new_coords[0] + new_coords[2]) / 2
            node.y = (new_coords[3] + new_coords[1]) / 2
            self.cvs.coords(node.lid, node.x - 15, node.y + 10)
            for layer in range(1, self.nbl + 1):
                if node.image[layer] or layer == 1:
                    x = node.x - node.imagex / 2
                    y = node.y - (layer - 1) * self.diff_y - node.imagey / 2
                    self.cvs.coords(node.image[layer], x, y)
                    coord = (node.x, node.y, node.x, node.y - (layer - 1) * self.diff_y)
                    self.cvs.coords(node.layer_line, *coord)
            # the oval was also resized while scaling
            node.size = abs(new_coords[0] - new_coords[2])/2 
            for type in self.ntw.link_type:
                for neighbor, t in self.ntw.graph[node.id][type]:
                    layer = 'all' if not self.layered_display else t.layer
                    link_to_coords = self.link_coordinates(node, neighbor, layer)
                    for link in link_to_coords:
                        self.cvs.coords(link.line, *link_to_coords[link])
                        self.update_link_label_coordinates(link)

    ## Object creation
    
    @adapt_coordinates
    def create_node_on_binding(self, event):
        new_node = self.ntw.nf(node_type=self._creation_mode, x=event.x, y=event.y)
        self.create_node(new_node)
    
    def create_node(self, node, layer=1):
        s = self.NODE_SIZE
        curr_image = self.ms.dict_image['default'][node.subtype]
        y = node.y - (layer - 1) * self.diff_y
        tags = (node.subtype, node.class_type, 'object')
        node.image[layer] = self.cvs.create_image(node.x - (node.imagex)/2, 
                y - (node.imagey)/2, image=curr_image, anchor=tk.NW, tags=tags)
        node.oval[layer] = self.cvs.create_oval(node.x-s, y-s, node.x+s, y+s, 
                                outline=node.color, fill=node.color, tags=tags)
        # create/hide the image/the oval depending on the current mode
        self.cvs.itemconfig(node.oval[layer], state=tk.HIDDEN)
        self.object_id_to_object[node.oval[layer]] = node
        self.object_id_to_object[node.image[layer]] = node
        if layer == 1:
            self.create_node_label(node)
            
    @adapt_coordinates
    def start_link(self, event):
        self.drag_item = self.cvs.find_closest(event.x, event.y)[0]
        start_node = self.object_id_to_object[self.drag_item]
        self.temp_line = self.cvs.create_line(start_node.x, start_node.y, 
                        event.x, event.y, arrow=tk.LAST, arrowshape=(6,8,3))
        
    @adapt_coordinates
    def line_creation(self, event):
        # remove the purple highlight of the closest object when creating 
        # a link: the normal system doesn't work because we are in 'B1-Motion'
        # mode and not just 'Motion'
        if self.co:
            self.unhighlight_objects(self.co)
        # node from which the link starts
        start_node = self.object_id_to_object[self.drag_item]
        # create a line to show the link
        self.cvs.coords(self.temp_line, start_node.x, start_node.y, event.x, event.y)
        
    @adapt_coordinates
    def link_creation(self, event, subtype):
        # delete the temporary line
        self.cvs.delete(self.temp_line)
        # node from which the link starts
        start_node = self.object_id_to_object[self.drag_item]
        # node close to the point where the mouse button is released
        self.drag_item = self.cvs.find_closest(event.x, event.y)[0]
        if self.drag_item in self.object_id_to_object: # to avoid labels
            destination_node = self.object_id_to_object[self.drag_item]
            if destination_node.class_type == 'node': # because tag filtering doesn't work !
                # create the link and the associated line
                if start_node != destination_node:
                    new_link = self.ntw.lf(
                                           subtype = subtype,
                                           source = start_node, 
                                           destination = destination_node
                                           )
                    self.create_link(new_link)
    
    def create_link(self, new_link):
        edges = (new_link.source, new_link.destination)
        real_layer = sum(self.display_layer[:(new_link.layer+1)])
        for node in edges:
            # we always have to create the nodes at layer 0, no matter whether
            # the layered display option is activated or not.
            if self.display_layer[new_link.layer] and self.layered_display:
                # we check whether the node image already exist or not, and 
                # create it only if it doesn't.
                if not node.image[real_layer]:
                    self.create_node(node, real_layer)
                # if the link we consider is not the lowest layer
                # and the associated 'layer line' does not yet exist
                # we create it
                if real_layer > 1 and not node.layer_line[real_layer]:
                    coords = (node.x, node.y, node.x, 
                                    node.y - (real_layer - 1) * self.diff_y) 
                    node.layer_line[real_layer] = self.cvs.create_line(
                                *coords, fill='black', width=1, dash=(3,5))
                    self.cvs.tag_lower(node.layer_line[real_layer])
        current_layer = 'all' if not self.layered_display else new_link.layer
        link_to_coords = self.link_coordinates(*edges, layer=current_layer)
        for link in link_to_coords:
            coords = link_to_coords[link]
            if not link.line:
                link.line = self.cvs.create_line(*coords, tags=(link.subtype, 
                        link.type, link.class_type, 'object'), fill=link.color, 
                        width=self.LINK_WIDTH, dash=link.dash, smooth=True,
                        state=tk.NORMAL if self.display_layer[link.layer] else tk.HIDDEN)
            else:
                self.cvs.coords(link.line, *coords)
        self.cvs.tag_lower(new_link.line)
        self.object_id_to_object[new_link.line] = new_link
        self._create_link_label(new_link)
        self.refresh_label(new_link)
    
    def multiple_nodes(self, n, subtype, x, y):
        for node in self.ntw.multiple_nodes(n, subtype):
            node.x = x
            node.y = y
            
    ## Motion
    
    @adapt_coordinates
    def node_motion(self, event):
        # destroy the tip window when moving a node
        self.pwindow.destroy()
        # record the new position
        node = self.object_id_to_object[self.drag_item]
        # layer diff
        merged_dict = node.image.items()
        layer = [l for l, item_id in merged_dict if item_id == self.drag_item].pop()
        diff = (layer - 1) * self.diff_y
        for selected_node in self.so['node']:
            # the main node initial position, the main node current position, 
            # and the other node initial position form a rectangle.
            # we find the position of the fourth vertix.
            x0, y0 = self._start_pos_main_node
            x1, y1 = self._dict_start_position[selected_node]
            selected_node.x = x1 + (event.x - x0)
            selected_node.y = y1 + (event.y + diff - y0)
            self.move_node(selected_node)
        # update coordinates of the node and move it
        node.x, node.y = event.x, event.y + diff
        self.move_node(node)   
                
    def move_node(self, n):
        newx, newy = float(n.x), float(n.y)
        s = self.NODE_SIZE
        for layer in range(1, self.nbl + 1):
            if n.image[layer]:
                y =  newy - (layer - 1) * self.diff_y
                coord_image = (newx - (n.imagex)//2, y - (n.imagey)//2)
                self.cvs.coords(n.image[layer], *coord_image)
                self.cvs.coords(n.oval[layer], newx - s, y - s, newx + s, y + s)
            self.cvs.coords(n.lid, newx - 15, newy + 10)
        
        # move also the virtual line, which length depends on what layer exists
        if self.layered_display:
            for layer in range(1, self.nbl + 1):
                if self.display_layer[layer]:
                    #real_layer = sum(self.display_layer[:(layer + 1)])
                    if n.layer_line[layer]:
                        coord = (newx, newy, newx, newy - (layer - 1) * self.diff_y)
                        self.cvs.coords(n.layer_line[layer], *coord)
    
        # update links coordinates
        for type_link in self.ntw.link_type:
            for neighbor, t in self.ntw.graph[n.id][type_link]:
                layer = 'all' if not self.layered_display else t.layer
                link_to_coords = self.link_coordinates(n, neighbor, layer)
                for link in link_to_coords:
                    self.cvs.coords(link.line, *link_to_coords[link])
                    # update link label coordinates
                    self.update_link_label_coordinates(link)
                    # if there is a link in failure, we need to update the
                    # failure icon by retrieving the middle position of the arc
                    if link in self.ntw.fdtks:
                        mid_x, mid_y = link_to_coords[link][2:4]
                        self.cvs.coords(self.id_fdtks[link], mid_x, mid_y)
                        
    def move_nodes(self, nodes):
        for node in nodes:
            self.move_node(node)
            
    ## Object deletion
                    
    def remove_objects(self, *objects):
        for obj in objects:
            if obj.type not in ('traffic', 'route', 'l2vc', 'l3vc'):
                for AS in list(obj.AS):
                    AS.management.remove_from_AS(obj)
            if obj.class_type == 'node':
                del self.object_id_to_object[obj.oval[1]]
                del self.object_id_to_object[obj.image[1]]
                self.cvs.delete(obj.oval[1], obj.image[1], obj.lid)
                self.remove_objects(*self.ntw.remove_node(obj))
                if self.layered_display:
                    for layer in range(2, self.nbl + 1):
                        self.cvs.delete(
                                    obj.oval[layer], 
                                    obj.image[layer], 
                                    obj.layer_line[layer]
                                    )
            if obj.class_type == 'link':
                # we remove the label of the attached interfaces
                self.cvs.delete(obj.ilid[0], obj.ilid[1])
                # we remove the line as well as the label on the canvas
                self.cvs.delete(obj.line, obj.lid)
                # we remove the id in the 'id to object' dictionnary
                del self.object_id_to_object[obj.line]
                # we remove the associated link in the network model
                self.ntw.remove_link(obj)
                # if the layered display is activate and the link 
                # to delete is not a physical link
                if self.layered_display and obj.layer:
                    for edge in (obj.source, obj.destination):
                        # we check if there still are other links of the same
                        # type (i.e at the same layer) between the edge nodes
                        if not self.ntw.graph[edge.id][obj.type]:
                            # if that's not the case, we delete the upper-layer
                            # projection of the edge nodes, and reset the 
                            # associated 'layer to projection id' dictionnary
                            self.cvs.delete(edge.oval[obj.layer], edge.image[obj.layer])
                            edge.image[obj.layer] = edge.oval[obj.layer] = None
                            # we delete the dashed 'layer line' and reset the
                            # associated 'layer to layer line id' dictionnary
                            self.cvs.delete(edge.layer_line[obj.layer])
                            edge.layer_line[obj.layer] = None
                            
    def erase_graph(self):
        self.object_id_to_object.clear()
        self.unhighlight_all()
        self.so = {'node': set(), 'link': set()}
        self.temp_line = None
        self.drag_item = None
                            
    def erase_all(self):
        self.cvs.delete('all')
        
        for node in self.ntw.nodes.values():
            #TODO dict from keys
            node.oval = {layer: None for layer in range(1, self.nbl + 1)}
            node.image = {layer: None for layer in range(1, self.nbl + 1)}
            node.layer_line = {layer: None for layer in range(1, self.nbl + 1)}
            
        for link_type in self.ntw.link_type:
            for link in self.ntw.pn[link_type].values():
                link.line = None
                            
    ## Selection / Highlight
    
    # 1) Canvas selection process
    
    def start_point_select_objects(self, event):
        x, y = self.cvs.canvasx(event.x), self.cvs.canvasy(event.y)
        # create the temporary line, only if there is nothing below
        # this is to avoid drawing a rectangle when moving a node
        if not self.cvs.find_overlapping(x-1, y-1, x+1, y+1):
            if not self.ctrl:
                self.unhighlight_all()
                self.so = {'node': set(), 'link': set()}
            self._start_position = x, y
            # create the temporary line
            x, y = self._start_position
            self.temp_line_x_top = self.cvs.create_line(x, y, x, y)
            self.temp_line_y_left = self.cvs.create_line(x, y, x, y)
            self.temp_line_y_right = self.cvs.create_line(x, y, x, y)
            self.temp_line_x_bottom = self.cvs.create_line(x, y, x, y)

    @adapt_coordinates
    def rectangle_drawing(self, event):
        # draw the line only if they were created in the first place
        if self._start_position != [None]*2:
            # update the position of the temporary lines
            x0, y0 = self._start_position
            self.cvs.coords(self.temp_line_x_top, x0, y0, event.x, y0)
            self.cvs.coords(self.temp_line_y_left, x0, y0, x0, event.y)
            self.cvs.coords(self.temp_line_y_right, event.x, y0, event.x, event.y)
            self.cvs.coords(self.temp_line_x_bottom, x0, event.y, event.x, event.y)
    
    def change_object_selection(self, event=None):
        self.obj_selection = (self.obj_selection == 'link')*'node' or 'link' 

    @adapt_coordinates
    def end_point_select_nodes(self, event):
        if self._start_position != [None]*2:
            # delete the temporary lines
            self.cvs.delete(self.temp_line_x_top)
            self.cvs.delete(self.temp_line_x_bottom)
            self.cvs.delete(self.temp_line_y_left)
            self.cvs.delete(self.temp_line_y_right)
            # select all nodes enclosed in the rectangle
            start_x, start_y = self._start_position
            for obj in self.cvs.find_enclosed(start_x, start_y, event.x, event.y):
                if obj in self.object_id_to_object:
                    enclosed_obj = self.object_id_to_object[obj]
                    if enclosed_obj.class_type == self.obj_selection:
                        self.highlight_objects(enclosed_obj)
            self._start_position = [None]*2
        
    # 2) Update selected objects and highlight
    def highlight_objects(self, *objects, color='red', dash=False):
        # highlight in red = selection: everything that is highlighted in red
        # is considered selected, and everything that isn't, unselected.
        for obj in objects:
            if color == 'red':
                self.so[obj.class_type].add(obj)
            if obj.class_type == 'node':
                self.cvs.itemconfig(obj.oval, fill=color)
                self.cvs.itemconfig(
                                obj.image[1], 
                                image = self.ms.dict_image[color][obj.subtype]
                                )
            elif obj.class_type == 'link':
                dash = (3, 5) if dash else ()
                self.cvs.itemconfig(obj.line, fill=color, width=5, dash=dash)

                
    def unhighlight_objects(self, *objects):
        for obj in objects:
            self.so[obj.class_type].discard(obj)
            if obj.class_type == 'node':
                self.cvs.itemconfig(obj.oval, fill=obj.color)
                self.cvs.itemconfig(
                                obj.image[1], 
                                image = self.ms.dict_image['default'][obj.subtype]
                                )
            elif obj.class_type == 'link':
                self.cvs.itemconfig(obj.line, fill=obj.color, 
                                        width=self.LINK_WIDTH, dash=obj.dash)  
                
    def unhighlight_all(self):
        self.cvs.delete(self.src_label)
        self.cvs.delete(self.dest_label)
        self.src_label = None
        self.dest_label = None
        for object_type in self.so:
            self.unhighlight_objects(*self.so[object_type])
            
    ## Object labelling
                
    def create_node_label(self, node):
        node.lid = self.cvs.create_text(node.x - 15, node.y + 10, anchor='nw')
        self.cvs.itemconfig(node.lid, fill='blue', tags='label')
        # set the text of the label with refresh label
        self.refresh_label(node)
        
    # refresh the label for one object with the current object label
    def refresh_label(self, obj, label_type=None, itf=False):
        # label_type is None if we simply want to update the label value
        # but not change the type of label displayed.
        if not label_type:
            label_type = self.current_label[obj.type.capitalize()].lower()
        else:
            label_type = label_type.lower()
        # we retrieve the id of the normal label in general, but the interface
        # labels id (two labels) if we update the interfaces labels. 
        label_id = obj.lid if not itf else obj.ilid
        
        # if it is not, it means there is no label to display. 
        # we have one or two labels to reset to an empty string depending 
        # on whether it is the interface labels or another one.
        if label_type == 'none':
            if itf:
                self.cvs.itemconfig(label_id[0], text='')
                self.cvs.itemconfig(label_id[1], text='')
            else:
                self.cvs.itemconfig(label_id, text='')
        elif label_type == 'position':
            text = '({}, {})'.format(obj.x, obj.y)
            self.cvs.itemconfig(label_id, text=text)
        elif label_type == 'coordinates':
            text = '({}, {})'.format(obj.longitude, obj.latitude)
        elif label_type in ('capacity', 'flow', 'cost', 'traffic', 'wctraffic'):
            # retrieve the value of the parameter depending on label type
            valueSD = getattr(obj, label_type + 'SD')
            valueDS = getattr(obj, label_type + 'DS')
            if itf:
                self.cvs.itemconfig(label_id[0], text=valueSD)
                self.cvs.itemconfig(label_id[1], text=valueDS)
            # if it isn't an interface, the label type is necessarily 
            # among traffic and wctraffic: we display the total amount of
            # traffic going over the link (traffic sum of both directions)
            else:
                text = str(valueSD + valueDS)
                self.cvs.itemconfig(label_id, text=text)
        elif itf and label_type in ('name', 'ipaddress'):
            # to display the name of the interface, we retrieve the 'interface'
            # parameters of the corresponding physical link
            valueS = getattr(obj.interfaceS, label_type)
            valueD = getattr(obj.interfaceD, label_type)
            self.cvs.itemconfig(label_id[0], text=valueS)
            self.cvs.itemconfig(label_id[1], text=valueD)
        else:
            self.cvs.itemconfig(label_id, text=getattr(obj, label_type))
            
    # change label and refresh it for all objects
    def refresh_labels(self, type, label=None):
        if label:
            self.current_label[type] = label
        # if we change the interface label, it is actually the physical link we
        # need to retrieve, since that's where we store the interfaces values
        obj_type = 'plink' if type == 'Interface' else type.lower()
        # interface is a boolean that tells the 'refresh_label' function
        # whether we want to update the interface label, or the physical link label,
        # since they have the same name
        itf = type == 'Interface'
        for obj in self.ntw.pn[obj_type].values():
            self.refresh_label(obj, self.current_label[type], itf)
            
    def refresh_all_labels(self):
        for type in self.current_label:
            self.refresh_labels(type)
                        
    def _create_link_label(self, link):
        coeff = self.compute_coeff(link)
        link.lid = self.cvs.create_text(*self.offcenter(coeff, *link.lpos), 
                            anchor='nw', fill='red', tags='label', font='bold')
        # we also create the interface labels, which position is at 1/4
        # of the line between the end point and the middle point
        # source interface label coordinates:
        s = self.offcenter(coeff, *self.if_label(link))
        link.ilid[0] = self.cvs.create_text(*s, anchor='nw', fill='red',
                                                    tags='label', font='bold')
        # destination interface label coordinates:                                                        
        d = self.offcenter(coeff, *self.if_label(link, 'd'))
        link.ilid[1] = self.cvs.create_text(*d, anchor='nw', fill='red', 
                                                    tags='label', font='bold')
        self.refresh_label(link)
                        
    def offcenter(self, coeff, x, y):
        # move the label off-center, so that its position depends on the 
        # slope of the link, and it can be read easily
        return x, y - 30 * (coeff > 0)
        
    def compute_coeff(self, link):
        # compute the slope of the link's line
        try:
            dy = link.destination.y - link.source.y
            dx = link.destination.x - link.source.x
            coeff = dy / dx
        except ZeroDivisionError:
            coeff = 0
        return coeff
        
    def if_label(self, link, end='s'):
        # compute the position of the interface label. Instead of placing the 
        # interface label in the middle of the line between the middle point lpos
        # and the end of the link, we set it at 1/4 (middle of the middle) so 
        # that its placed closer to the link's end.
        mx, my = link.lpos
        if end == 's':
            if_label_x = (mx + link.source.x) / 4 + link.source.x / 2
            if_label_y = (my + link.source.y) / 4 + link.source.y / 2
        else:
            if_label_x = (mx + link.destination.x) / 4 + link.destination.x / 2
            if_label_y = (my + link.destination.y) / 4 + link.destination.y / 2
        return if_label_x, if_label_y
                    
    def update_link_label_coordinates(self, link):
        coeff = self.compute_coeff(link)
        self.cvs.coords(link.lid, *self.offcenter(coeff, *link.lpos))
        self.cvs.coords(link.ilid[0], *self.offcenter(coeff, *self.if_label(link)))
        self.cvs.coords(link.ilid[1], *self.offcenter(coeff, *self.if_label(link, 'd')))
        
    # cancel the graph drawing job
    def _cancel(self):
        if self._job is not None:
            self.cvs.after_cancel(self._job)
            self._job = None

    def link_coordinates(self, source, destination, layer='all'):
        xA, yA, xB, yB = source.x, source.y, destination.x, destination.y
        angle = atan2(yB - yA, xB - xA)
        dict_link_to_coords = {}
        type = layer if layer == 'all' else self.layers[1][layer]
        real_layer = 1 if layer == 'all' else sum(self.display_layer[:(layer+1)])
        for id, link in enumerate(self.ntw.links_between(source, destination, type)):
            d = ((id + 1) // 2) * 30 * (-1)**id
            xC = (xA + xB) / 2 + d * sin(angle)
            yC = (yA + yB) / 2 - d * cos(angle)
            offset = 0 if layer == 'all' else (real_layer - 1) * self.diff_y
            coord = (xA, yA - offset, xC, yC - offset, xB, yB - offset)
            dict_link_to_coords[link] = coord
            link.lpos = (xC, yC - offset)
        return dict_link_to_coords
                
    ## Drawing
    
    # 1) Regular drawing
    def draw_objects(self, objects, random_drawing=True):
        self._cancel()
        for obj in objects:
            if obj.type == 'node':
                if random_drawing:
                    obj.x, obj.y = randint(100,700), randint(100,700)
                if not obj.image[1]:
                    self.create_node(obj)
            else:
                self.create_link(obj)
             
    def draw_all(self, random=True):
        self.erase_all()
        for type in self.ntw.pn:
            self.draw_objects(self.ntw.pn[type].values(), random)
            
    # 2) Force-based drawing
    
    def retrieve_parameters(self):
        entry_value = lambda entry: float(entry.text)
        parameters = list(map(entry_value, self.ms.drawing_menu.entries)) 
        parameters.append(self.ms.drawing_menu.stay_withing_screen_bounds.get())
        return parameters

    def spring_based_drawing(self, nodes):
        if not self._job:
            # reset the number of iterations
            self.drawing_iteration = 0
        else:
            self._cancel()
        self.drawing_iteration += 1
        params = self.retrieve_parameters()
        self.ntw.spring_layout(nodes, *params[:4])
        if not self.drawing_iteration % 5:   
            for node in nodes:
                self.move_node(node)
        self._job = self.cvs.after(1, lambda: self.spring_based_drawing(nodes))
        
    def FR_drawing(self, nodes):
        if not self._job:
            # update the optimal pairwise distance
            self.ms.opd = sqrt(500*500/len(self.ntw.nodes.values()))
            # reset the number of iterations
            self.drawing_iteration = 0
        else:
            self._cancel()
        self.drawing_iteration += 1
        # retrieve the optimal pairwise distance and the screen limit boolean
        params = self.retrieve_parameters()
        self.ntw.fruchterman_reingold_layout(nodes, *params[-2:])
        if not self.drawing_iteration % 5:   
            for node in nodes:
                self.move_node(node)
        self._job = self.cvs.after(1, lambda: self.FR_drawing(nodes))
        
    def bfs_cluster_drawing(self, nodes):
        if not self._job:
            # update the optimal pairwise distance
            self.ms.opd = sqrt(500*500/len(self.ntw.nodes.values()))
            # reset the number of iterations
            self.drawing_iteration = 0
        else:
            self._cancel()
        params = self.retrieve_parameters()
        self.ntw.bfs_spring(nodes, *params[:4])
        for node in nodes:
            self.move_node(node)
        self._job = self.cvs.after(1, lambda: self.bfs_cluster_drawing(nodes))
    
    # 3) Alignment / distribution
    
    def align(self, nodes, horizontal=True):
        # alignment can be either horizontal (horizontal = True) or vertical
        minimum = min(node.y if horizontal else node.x for node in nodes)
        for node in nodes:
            setattr(node, 'y'*horizontal or 'x', minimum)
        self.move_nodes(nodes)
        
    def distribute(self, nodes, horizontal=True):
        # uniformly distribute the nodes between the minimum and
        # the maximum lontitude/latitude of the selection
        minimum = min(node.x if horizontal else node.y for node in nodes)
        maximum = max(node.x if horizontal else node.y for node in nodes)
        # we'll use a sorted list to keep the same order after distribution
        nodes = sorted(nodes, key=lambda n: getattr(n, 'x'*horizontal or 'y'))
        offset = (maximum - minimum)/(len(nodes) - 1)
        for idx, node in enumerate(nodes):
            setattr(node, 'x'*horizontal or 'y', minimum + idx*offset)
        self.move_nodes(nodes)
                
    ## Multi-layer display
                
    def switch_display_mode(self):
        self.layered_display = not self.layered_display
        
        if self.layered_display:
            self.planal_move(50)
            min_y = min(node.y for node in self.ntw.nodes.values())
            max_y = max(node.y for node in self.ntw.nodes.values())
            self.diff_y = (max_y - min_y) // 2 + 200
            
        self.unhighlight_all()
        self.draw_all(False)
        
        return self.layered_display
            
    def planal_move(self, angle=45):
        min_y = min(node.y for node in self.ntw.nodes.values())
        max_y = max(node.y for node in self.ntw.nodes.values())
        
        for node in self.ntw.nodes.values():
            diff_y = abs(node.y - min_y)
            new_y = min_y + diff_y * cos(radians(angle))
            node.y = new_y
            
    ## Failure simulation
    
    def remove_failure(self, plink):
        self.ntw.fdtks.remove(plink)
        icon_id = self.id_fdtks.pop(plink)
        self.cvs.delete(icon_id)
    
    def remove_failures(self):
        self.ntw.fdtks.clear()
        for idx in self.id_fdtks.values():
            self.cvs.delete(idx)
        self.id_fdtks.clear()
    
    def simulate_failure(self, plink):
        self.ntw.fdtks.add(plink)
        source, destination = plink.source, plink.destination
        xA, yA, xB, yB = source.x, source.y, destination.x, destination.y
        id_failure = self.cvs.create_image(
                                        (xA+xB)/2, 
                                        (yA+yB)/2, 
                                        image = self.ms.img_failure
                                        )
        self.id_fdtks[plink] = id_failure
        
    def refresh_failures(self):
        self.id_fdtks.clear()
        for plink in self.ntw.fdtks:
            self.simulate_failure(plink)
            
    ## Display filtering
    
    def display_filter(self, filter):
        filter_sites = set(re.sub(r'\s+', '', filter).split(','))
        for node in self.ntw.nodes.values():
            state = tk.NORMAL if node.sites & filter_sites else tk.HIDDEN
            self.cvs.itemconfig(node.lid, state=state)
            for layer in range(1, self.nbl + 1):
                if node.image[layer]:
                    self.cvs.itemconfig(node.image[layer], state=state)
        for link_type in self.ntw.link_type:
            for link in self.ntw.pn[link_type].values():
                state = tk.NORMAL if link.sites & filter_sites else tk.HIDDEN
                self.cvs.itemconfig(link.line, state=state)
                self.cvs.itemconfig(link.lid, state=state)
            
    ## Refresh display
    
    def refresh(self):
        self.ntw.calculate_all()
        self.refresh_all_labels()
        self.draw_all(False)      
        self.refresh_failures() 
        filter = self.ms.display_menu.filter_entry.text
        if filter:
            self.display_filter(filter)      
            
    ## Other
    
    def add_to_edges(self, AS, *nodes):
        for node in nodes:
            if node not in AS.edges:
                AS.edges.add(node)
                AS.management.listbox_edges.insert(tk.END, obj)
                
    # show/hide display per type of objects
    def show_hide(self, subtype):
        self.display_per_type[subtype] = not self.display_per_type[subtype]
        new_state = tk.NORMAL if self.display_per_type[subtype] else tk.HIDDEN
        if subtype in self.ntw.node_subtype:
            for node in self.ntw.ftr('node', subtype):
                self.cvs.itemconfig(node.lid, state=new_state)
                for layer in range(1, self.nbl + 1):
                    self.cvs.itemconfig(node.image[layer], state=new_state)
                    self.cvs.itemconfig(node.layer_line[layer], state=new_state)
                for link in self.ntw.attached_links(node):
                    # if the display is activated for the link's layer, we 
                    # update the state
                    if self.display_layer[link.layer]:
                        self.cvs.itemconfig(link.line, state=new_state)
                        self.cvs.itemconfig(link.lid, state=new_state)
        else:
            type = subtype_to_type[subtype]
            for link in self.ntw.ftr(type, subtype):
                self.cvs.itemconfig(link.line, state=new_state)
                self.cvs.itemconfig(link.lid, state=new_state)
        return self.display_per_type[subtype]
                
                
class LabelCreation(CustomTopLevel):
            
    def __init__(self, scenario):
        super().__init__()
        self.cs = scenario
        
        # labelframe
        lf_label_creation = Labelframe(self)
        lf_label_creation.text = 'Create a label'
        lf_label_creation.grid(0, 0)

        self.entry_label = Entry(self, width=20)
        
        OK_button = Button(self, width=20)
        OK_button.text = 'OK'
        OK_button.command = self.OK
        
        lf_label_creation.grid(0, 0)
        self.entry_label.grid(0, 0, in_=lf_label_creation)
        OK_button.grid(1, 0, in_=lf_label_creation)

    def OK(self):
        pass
        self.destroy()
        