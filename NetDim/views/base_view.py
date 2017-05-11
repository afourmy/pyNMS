# NetDim (contact@netdim.fr)

import tkinter as tk
import re
from os.path import join
from pythonic_tkinter.preconfigured_widgets import *
from objects.objects import *
from .shape_drawing import *
from random import randint, choice
from math import cos, sin, atan2, sqrt, radians
from miscellaneous.decorators import *

class BaseView(CustomFrame):
    
    def __init__(self, name, controller):
        # path update
        self.controller = controller
        self.project = controller.current_project
        
        super().__init__(self.project.gf)
        self.name = name
    
        self.object_id_to_object = {}

        self.cvs = BindingCanvas(
                        self, 
                        bg = '#FFFFFF', 
                        width = 1300, 
                        height = 800,
                        )
                             
        hbar = Scrollbar(self, orient='horizontal')
        hbar.pack(side='bottom', fill='x')
        hbar.config(command=self.cvs.xview)
        
        vbar = Scrollbar(self, orient='vertical')
        vbar.pack(side='right', fill='y')
        vbar.config(command=self.cvs.yview)
        
        self.cvs.config(width=1300, height=800)
        self.cvs.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.cvs.pack(side='left', expand=1, fill='both')
        
        # erase the map if one was created before
        self.update()
        # job running or not (e.g drawing)
        self._job = None
        # number of iteration of the graph layout algorithm
        self.drawing_iteration = 0
            
        # default link width and node size
        self.link_width = 5
        self.node_size = 8
        
        # default label display
        # None means that no label is displayed: it is the default setting
        self.current_label = dict.fromkeys(object_properties, 'None')
        
        # creation mode, object type, and associated bindings
        self.start_position = [None]*2
        self._object_type = 'plink'
        self.drag_item = None
        self.temp_line = None
        
        # used to move several node at once
        self.start_pos_main_node = [None]*2
        self.dict_start_position = {}
        
        # the default mode is motion
        self.mode = 'motion'
        # the default creation mode is router
        self.creation_mode = 'router'
        # the default shape creation mode is text
        self.shape_creation_mode = 'text'
        
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
        self.display_per_type = dict.fromkeys(all_subtypes, True)
        
        # indexes of the failure icons: dictionnary that bins
        # physical links item to the id of the associated icon
        self.id_fdtks = {}
        
        # list of currently selected object ('so')
        self.so = defaultdict(set)
        
        # source / destination indicators when a link is selected
        self.src_label = None
        self.dest_label = None
        
        # window properties upon hovering over an object
        self.pwindow = None
        
        # we also keep track of the closest object for the motion function
        self.co = None
        
        ## persistent bindings (remain available in both modes)
                
        # zoom and unzoom on windows
        window_zoom_binding = Binding(self.cvs)
        window_zoom_binding.event = '<MouseWheel>'
        window_zoom_binding.command = self.zoomer
        window_zoom_binding.bind()
        
        # zoom and unzoom on unix
        unix_zoom_in_binding = Binding(self.cvs)
        unix_zoom_in_binding.event = '<Button-4>'
        unix_zoom_in_binding.command = self.zoomerP
        unix_zoom_in_binding.bind()
        
        unix_zoom_out_binding = Binding(self.cvs)
        unix_zoom_out_binding.event = '<Button-5>'
        unix_zoom_out_binding.command = self.zoomerM
        unix_zoom_out_binding.bind()
        
        # use the right-click to move the background
        scroll_start_binding = Binding(self.cvs)
        scroll_start_binding.event = '<ButtonPress-3>'
        scroll_start_binding.command = self.scroll_start
        scroll_start_binding.bind()
        
        scroll_motion_binding = Binding(self.cvs)
        scroll_motion_binding.event = '<B3-Motion>'
        scroll_motion_binding.command = self.scroll_move
        scroll_motion_binding.bind()
        
        general_menu_binding = Binding(self.cvs)
        general_menu_binding.event = '<ButtonRelease-3>'
        general_menu_binding.command = self.general_menu
        general_menu_binding.bind()
        
        # drag and drop binding
        # enter is triggered when the left-button of the mouse is released
        drag_and_drop_binding = Binding(self.cvs, add='+')
        drag_and_drop_binding.event = '<Enter>'
        drag_and_drop_binding.command = self.dnd_node_creation
        drag_and_drop_binding.bind()
        
        # window and highlight when hovering over an object
        hovering_object_binding = Binding(self.cvs)
        hovering_object_binding.event = '<Motion>'
        hovering_object_binding.command = self.motion
        hovering_object_binding.bind()
        
        # highlight the path of a route/traffic link with left-click
        closest_route_binding = Binding(self.cvs, 'optical channel')
        closest_route_binding.event = '<ButtonPress-1>'
        closest_route_binding.command = lambda _: 42
        closest_route_binding.bind()
        
        # use Ctrl+F to search for an object
        search_binding = Binding(self.cvs)
        search_binding.event = '<Control-Key-f>'
        search_binding.command = lambda e: controller.search_window.deiconify()
        search_binding.bind()
        
        # add nodes to a current selection by pressing control
        self.ctrl = False
        def change_ctrl(value):
            self.ctrl = value
            
        press_ctrl_binding = Binding(self.cvs)
        press_ctrl_binding.event = '<Control-KeyPress>'
        press_ctrl_binding.command = lambda _: change_ctrl(True)
        press_ctrl_binding.bind()
            
        release_ctrl_binding = Binding(self.cvs)
        release_ctrl_binding.event = '<Control-KeyRelease>'
        release_ctrl_binding.command = lambda _: change_ctrl(False)
        release_ctrl_binding.bind()
        
        # display/undisplay a layer by pressing the associated number
        for layer in range(1, self.nbl + 1):
            layer_display_binding = Binding(self.cvs)
            layer_display_binding.event = str(layer)
            layer_display_binding.command = lambda _, l=layer: self.invert_layer_display(l)
            layer_display_binding.bind()
            
        ## non-persistent bindings: 
        
        self.non_persistent_bindings = defaultdict(set)
        
        # 1) bindings used for selection mode
                
        # 1.A) selection bindings
        closest_node_binding = Binding(self.cvs, 'node', add='+')
        closest_node_binding.event = '<Button-1>'
        closest_node_binding.command = self.find_closest_node
        self.non_persistent_bindings['selection'].add(closest_node_binding)
        
        closest_link_binding = Binding(self.cvs, 'link', add='+')
        closest_link_binding.event = '<Button-1>'
        closest_link_binding.command = self.find_closest_link
        self.non_persistent_bindings['selection'].add(closest_link_binding)
        
        closest_shape_binding = Binding(self.cvs, 'shape', add='+')
        closest_shape_binding.event = '<Button-1>'
        closest_shape_binding.command = self.find_closest_shape
        self.non_persistent_bindings['selection'].add(closest_shape_binding)
        
        start_selection_binding = Binding(self.cvs, add='+')
        start_selection_binding.event = '<ButtonPress-1>'
        start_selection_binding.command = self.start_point_select_objects
        self.non_persistent_bindings['selection'].add(start_selection_binding)
        
        rectangle_drawing_binding = Binding(self.cvs)
        rectangle_drawing_binding.event = '<B1-Motion>'
        rectangle_drawing_binding.command = self.rectangle_drawing
        self.non_persistent_bindings['selection'].add(rectangle_drawing_binding)
        
        end_selection_binding = Binding(self.cvs, add='+')
        end_selection_binding.event = '<ButtonRelease-1>'
        end_selection_binding.command = self.end_point_select_nodes
        self.non_persistent_bindings['selection'].add(end_selection_binding)
        
        # set the focus on the canvas when clicking on it
        # allows for the keyboard binding to work properly
        focus_binding = Binding(self.cvs, add='+')
        focus_binding.event = '<ButtonPress-1>'
        focus_binding.command = lambda _: self.cvs.focus_set()
        self.non_persistent_bindings['selection'].add(focus_binding)
        
        # 1.B) motion bindings
        
        node_motion_binding = Binding(self.cvs, 'node')
        node_motion_binding.event = '<B1-Motion>'
        node_motion_binding.command = self.node_motion
        self.non_persistent_bindings['selection'].add(node_motion_binding)
        
        shape_motion_binding = Binding(self.cvs, 'shape')
        shape_motion_binding.event = '<B1-Motion>'
        shape_motion_binding.command = self.shape_motion
        self.non_persistent_bindings['selection'].add(shape_motion_binding)
        
        # 2) binding used for creation
                
        # 2.A) shape creation: rectangle
        start_rectangle_binding = Binding(self.cvs)
        start_rectangle_binding.event = '<ButtonPress-1>'
        start_rectangle_binding.command = self.start_drawing_rectangle
        self.non_persistent_bindings['rectangle'].add(start_rectangle_binding)
        
        draw_rectangle_binding = Binding(self.cvs)
        draw_rectangle_binding.event = '<B1-Motion>'
        draw_rectangle_binding.command = self.draw_rectangle
        self.non_persistent_bindings['rectangle'].add(draw_rectangle_binding)
        
        create_rectangle_binding = Binding(self.cvs)
        create_rectangle_binding.event = '<ButtonRelease-1>'
        create_rectangle_binding.command = self.create_rectangle
        self.non_persistent_bindings['rectangle'].add(draw_rectangle_binding)
        
        # 2.B) shape creation: oval
        start_oval_binding = Binding(self.cvs)
        start_oval_binding.event = '<ButtonPress-1>'
        start_oval_binding.command = self.start_drawing_oval
        self.non_persistent_bindings['oval'].add(start_oval_binding)
        
        draw_oval_binding = Binding(self.cvs)
        draw_oval_binding.event = '<B1-Motion>'
        draw_oval_binding.command = self.draw_oval
        self.non_persistent_bindings['oval'].add(draw_oval_binding)
        
        create_oval_binding = Binding(self.cvs)
        create_oval_binding.event = '<ButtonRelease-1>'
        create_oval_binding.command = self.create_oval
        self.non_persistent_bindings['oval'].add(draw_oval_binding)
        
        # 2.C) shape creation: label
        create_label_binding = Binding(self.cvs)
        create_label_binding.event = '<ButtonPress-1>'
        create_label_binding.command = self.create_label
        self.non_persistent_bindings['text'].add(create_label_binding)
        
        # 2.D) link creation
        start_link_binding = Binding(self.cvs, 'node', add='+')
        start_link_binding.event = '<ButtonPress-1>'
        start_link_binding.command = self.start_link
        self.non_persistent_bindings['link'].add(start_link_binding)
        
        draw_link_binding = Binding(self.cvs, 'node', add='+')
        draw_link_binding.event = '<B1-Motion>'
        draw_link_binding.command = self.line_creation
        self.non_persistent_bindings['link'].add(draw_link_binding)
        
        create_link_binding = Binding(self.cvs, 'node', add='+')
        create_link_binding.event = '<ButtonRelease-1>'
        create_link_binding.command = self.link_creation
        self.non_persistent_bindings['link'].add(create_link_binding)
                
        # initialize other bindings depending on the mode
        self.switch_binding('selection')
            
    ## Bindings
    
    @update_coordinates
    def create_node_on_binding(self, event, subtype):
        node = self.network.nf(
                               node_type = subtype, 
                               x = event.x, 
                               y = event.y
                               )
        self.create_node(node)
        # update logical coordinates
        node.logical_x, node.logical_y = node.x, node.y
    
    def dnd_node_creation(self, event):
        if self.controller.dnd:
            self.create_node_on_binding(event, self.controller.dnd)
            self.controller.dnd = False
        
    def switch_binding(self, mode):   
        # if there were selected nodes, so that they don't remain highlighted
        self.unhighlight_all()
        
        if mode == 'motion':
            # unbind unecessary bindings
            self.cvs.unbind('<Button 1>')
            self.cvs.unbind('<B1-Motion>')
            self.cvs.unbind('<ButtonRelease-1>')
            self.cvs.tag_unbind('link', '<Button-1>')
            self.cvs.tag_unbind('node', '<Button-1>')
            self.cvs.tag_unbind('shape', '<Button-1>')
            self.cvs.tag_unbind('node', '<B1-Motion>')
            self.cvs.tag_unbind('shape', '<B1-Motion>')
            self.cvs.tag_unbind('node', '<ButtonRelease-1>')
            
            self.cvs.binds(*self.non_persistent_bindings['selection'])
            
        else:
            # unbind unecessary bindings
            self.cvs.unbind('<Button-1>')
            self.cvs.unbind('<ButtonPress-1>')
            self.cvs.unbind('<ButtonRelease-1>')
            self.cvs.unbind('<ButtonMotion-1>')
            self.cvs.tag_unbind('node', '<Button-1>')
            self.cvs.tag_unbind('link', '<Button-1>')
            self.cvs.tag_unbind('Area', '<ButtonPress-1>')
            
            if self.creation_mode in ('rectangle', 'oval', 'text'):
                self.cvs.binds(*self.non_persistent_bindings[self.creation_mode])
            else:
                self.cvs.binds(*self.non_persistent_bindings['link'])
                
    ## Drawing modes
    
    @update_coordinates
    def start_drawing_oval(self, event):
        x, y = event.x, event.y
        self.start_position = x, y
        self.oval = self.cvs.create_oval(x, y, x, y, tags=('shape', 'object'))
        self.cvs.tag_lower(self.oval)
        
    @update_coordinates
    def draw_oval(self, event):
        # draw the line only if they were created in the first place
        if self.start_position != [None]*2:
            # update the position of the temporary lines
            x0, y0 = self.start_position
            self.cvs.coords(self.oval, event.x, event.y, x0, y0)
        
    def create_oval(self, event):
        oval = Oval(self.oval, event.x, event.y)
        self.start_position = [None]*2
        self.object_id_to_object[self.oval] = oval
    
    @update_coordinates
    def start_drawing_rectangle(self, event):
        x, y = event.x, event.y
        self.start_position = x, y
        self.rectangle = self.cvs.create_rectangle(x, y, x, y, 
                                                    tags=('shape', 'object'))
        self.cvs.tag_lower(self.rectangle)
        
    @update_coordinates
    def draw_rectangle(self, event):
        # draw the line only if they were created in the first place
        if self.start_position != [None]*2:
            # update the position of the temporary lines
            x0, y0 = self.start_position
            self.cvs.coords(self.rectangle, event.x, event.y, x0, y0)
        
    def create_rectangle(self, event):
        rectangle = Rectangle(self.rectangle, event.x, event.y)
        self.start_position = [None]*2
        self.object_id_to_object[self.rectangle] = rectangle
                  
    @update_coordinates
    def create_label(self, event):
        LabelCreation(self, event.x, event.y)
        
    def invert_layer_display(self, layer):
        self.display_layer[layer] = not self.display_layer[layer]
        self.draw_all(False)
            
    @update_coordinates
    def closest_route_path(self, event):
        self.unhighlight_all()
        route = self.object_id_to_object[self.cvs.find_closest(event.x, event.y)[0]]
        self.highlight_route(route)
            
    def highlight_route(self, route):
        self.highlight_objects(*route.path)
                
    @update_coordinates
    def find_closest_node(self, event):
        # record the item and its location
        self.dict_start_position.clear()
        self.drag_item = self.cvs.find_closest(event.x, event.y)[0]
        # save the initial position to compute the delta for multiple nodes motion
        main_node_selected = self.object_id_to_object[self.drag_item]
        merged_dict = main_node_selected.image.items()
        layer = [l for l, item_id in merged_dict if item_id == self.drag_item].pop()
        diff = layer * self.diff_y
        self.start_pos_main_node = event.x, event.y + diff
        if main_node_selected in self.so['node']:
            # for all selected node (sn), we store the initial position
            for sn in self.so['node']:
                self.dict_start_position[sn] = [sn.x, sn.y + diff]
        else:
            # if ctrl is not pressed, we forget about the old selection, 
            # consider only the newly selected node, and unhighlight everything
            if not self.ctrl:
                self.unhighlight_all()
            self.highlight_objects(main_node_selected)
            # we update the dict of start position
            self.dict_start_position[main_node_selected] = self.start_pos_main_node 
            # we also need to update the highlight to that the old selection
            # is no longer highlighted but the newly selected node is.
            self.highlight_objects(main_node_selected)
            
    @update_coordinates
    def find_closest_link(self, event):
        closest_link = self.cvs.find_closest(event.x, event.y)[0]
        main_link_selected = self.object_id_to_object[closest_link]
        if not self.ctrl:
            self.unhighlight_all()
        self.highlight_objects(main_link_selected)
        source = main_link_selected.source
        destination = main_link_selected.destination
        if not self.src_label:
            font = ("Purisa", '12', 'bold')
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
                
    @update_coordinates
    def find_closest_shape(self, event):
        self.dict_start_position.clear()
        self.drag_item = self.cvs.find_closest(event.x, event.y)[0]
        main_shape_selected = self.object_id_to_object[self.drag_item]
        self.start_pos_main_node = event.x, event.y
        if main_shape_selected in self.so['shape']:
            # for all selected shapes, we store the initial position
            for ss in self.so['shape']:
                self.dict_start_position[ss] = [ss.x, ss.y]
        else:
            # if ctrl is not pressed, we forget about the old selection, 
            # consider only the newly selected node, and unhighlight everything
            if not self.ctrl:
                self.unhighlight_all()
            self.highlight_objects(main_shape_selected)
            # we update the dict of start position
            x, y = main_shape_selected.x, main_shape_selected.y
            self.dict_start_position[main_shape_selected] = [x, y]
        self.highlight_objects(main_shape_selected)
    
    @update_coordinates
    def motion(self, event):
        x, y = event.x, event.y
        # if there is at least one object on the canvas
        if self.cvs.find_closest(x, y):
            # we retrieve it
            co_id = self.cvs.find_closest(x, y)[0]
            if co_id in self.object_id_to_object:
                co = self.object_id_to_object[co_id]
                if co.class_type == 'shape':
                    return
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
                                         prop_to_name[property] 
                                         + ' : ' + str(getattr(co, property)) 
                                         + ' ' for property in 
                                         box_properties[co.subtype]
                                         )
                        x0, y0 = self.controller.winfo_x() + 250, self.controller.winfo_y() + 75
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
                    else:
                        if self.pwindow:
                            self.pwindow.destroy()
            else:
                if self.co:

                    if self.co not in self.so[self.co.class_type]:
                        self.unhighlight_objects(self.co)
                    self.co = None
                    if self.pwindow:
                        self.pwindow.destroy()
            
    ## Right-click scroll
    
    def scroll_start(self, event):
        # we record the position of the mouse when right-click is pressed
        # to check, when it is released, if the intent was to drag the canvas
        # or to have access to the right-click menu
        self.start_pos_main_node = event.x, event.y
        self.cvs.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        self.cvs.scan_dragto(event.x, event.y, gain=1)

    ## Zoom / unzoom on the canvas
    
    @update_coordinates
    def zoomer(self, event):
        # zoom in / zoom out (windows)
        self.cancel()
        factor = 1.2 if event.delta > 0 else 0.8
        self.diff_y *= factor
        self.node_size *= factor
        self.cvs.scale('all', event.x, event.y, factor, factor)
        self.cvs.configure(scrollregion=self.cvs.bbox('all'))
        self.update_nodes_coordinates(factor)
        
    @update_coordinates
    def zoomerP(self, event):
        # zoom in (unix)
        self.cancel()
        self.diff_y *= 1.2
        self.node_size *= 1.2
        self.cvs.scale('all', event.x, event.y, 1.2, 1.2)
        self.cvs.configure(scrollregion=self.cvs.bbox('all'))
        self.update_nodes_coordinates(1.2)
        
    @update_coordinates
    def zoomerM(self, event):
        # zoom out (unix)
        self.cancel()
        self.diff_y *= 0.8
        self.node_size *= 0.8
        self.cvs.scale('all', event.x, event.y, 0.8, 0.8)
        self.cvs.configure(scrollregion=self.cvs.bbox('all'))
        self.update_nodes_coordinates(0.8)
    
    def update_nodes_coordinates(self, factor):
        # scaling changes the coordinates of the oval, and we update 
        # the corresponding node's coordinates accordingly
        for node in self.network.nodes.values():
            new_coords = self.cvs.coords(node.oval[1])
            node.logical_x *= factor
            node.logical_y *= factor
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
            for type in link_type:
                for neighbor, t in self.network.graph[node.id][type]:
                    layer = 'all' if not self.layered_display else t.layer
                    link_to_coords = self.link_coordinates(node, neighbor, layer)
                    for link in link_to_coords:
                        self.cvs.coords(link.line, *link_to_coords[link])
                        self.update_link_label_coordinates(link)
        # update rectangles and ovals coordinates as well
        ftr = lambda obj: obj.subtype in ('oval', 'rectangle')
        for shape in filter(ftr, self.object_id_to_object.values()):
            new_coords = self.cvs.coords(shape.id)
            shape.x, shape.y = new_coords[2:4]
        # resize label shapes
        label_only = lambda obj: obj.subtype == 'label'
        for label in filter(label_only, self.object_id_to_object.values()):
            label.size *= factor
            font = self.cvs.itemcget(label.id, 'font').split()
            font[1] = int(label.size)
            self.cvs.itemconfigure(label.id, font=font)

    ## Object creation
    
    def create_node(self, node, layer=1):
        s = self.node_size
        curr_image = self.controller.dict_image['default'][node.subtype]
        y = node.y - (layer - 1) * self.diff_y
        tags = (node.subtype, node.class_type, 'object')
        node.image[layer] = self.cvs.create_image(node.x - (node.imagex)/2, 
                y - (node.imagey)/2, image=curr_image, anchor='nw', tags=tags)
        node.oval[layer] = self.cvs.create_oval(node.x-s, y-s, node.x+s, y+s, 
                                outline=node.color, fill=node.color, tags=tags)
        # create/hide the image/the oval depending on the current mode
        self.cvs.itemconfig(node.oval[layer], state='hidden')
        self.object_id_to_object[node.oval[layer]] = node
        self.object_id_to_object[node.image[layer]] = node
        if layer == 1:
            self.create_node_label(node)
            
    @update_coordinates
    def start_link(self, event):
        self.drag_item = self.cvs.find_closest(event.x, event.y)[0]
        start_node = self.object_id_to_object[self.drag_item]
        self.temp_line = self.cvs.create_line(start_node.x, start_node.y, 
                        event.x, event.y, arrow=tk.LAST, arrowshape=(6,8,3))
        
    @update_coordinates
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
        
    @update_coordinates
    def link_creation(self, event):
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
                    new_link = self.network.lf(
                                           subtype = self.creation_mode,
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
            #TODO we don't if layer 0 is deactivaited
            if self.display_layer[new_link.layer] and self.layered_display:
                # we check whether the node image already exist or not, and 
                # create it only if it doesn't.
                if not node.image[real_layer]:
                    self.create_node(node, real_layer)
                # if the link we consider is not the lowest layer
                # and the associated 'layer line' does not yet exist
                # we create it
                if real_layer > 1 and not node.layer_line[real_layer]:
                    coords = (
                              node.x, 
                              node.y, 
                              node.x, 
                              node.y - (real_layer - 1)*self.diff_y
                              ) 
                    node.layer_line[real_layer] = self.cvs.create_line(
                                                    tags = ('line',), 
                                                    *coords, 
                                                    fill = 'black', 
                                                    width = 1, 
                                                    dash = (3,5)
                                                    )
                    self.cvs.tag_lower(node.layer_line[real_layer])
        current_layer = 'all' if not self.layered_display else new_link.layer
        link_to_coords = self.link_coordinates(*edges, layer=current_layer)
        for link in link_to_coords:
            coords = link_to_coords[link]
            if not link.line:
                link.line = self.cvs.create_line(
                        *coords, 
                        tags = (
                                link.subtype, 
                                link.type, 
                                link.class_type, 
                                'object'
                                ), 
                        fill = link.color, 
                        width = self.link_width, 
                        dash = link.dash, 
                        smooth = True,
                        state = 'normal' if self.display_layer[link.layer] else 'hidden'
                        )
            else:
                self.cvs.coords(link.line, *coords)
        self.cvs.tag_lower(new_link.line)
        self.object_id_to_object[new_link.line] = new_link
        self._create_link_label(new_link)
        self.refresh_label(new_link)
    
    def multiple_nodes(self, n, subtype, x, y):
        for node in self.network.multiple_nodes(n, subtype):
            node.x = x
            node.y = y
            
    ## Motion
    
    @update_coordinates
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
            x0, y0 = self.start_pos_main_node
            x1, y1 = self.dict_start_position[selected_node]
            selected_node.x = x1 + (event.x - x0)
            selected_node.y = y1 + (event.y + diff - y0)
            self.move_node(selected_node)
        
    @update_coordinates
    def shape_motion(self, event):
        shape = self.object_id_to_object[self.drag_item]
        for ss in self.so['shape']:
            self.move_shape(ss, event)
        
    def move_shape(self, shape, event):
        x0, y0 = self.start_pos_main_node
        x1, y1 = self.dict_start_position[shape]
        dx, dy = x1 - x0, y1 - y0
        if shape.subtype == 'label':
            self.cvs.coords(shape.id, dx + event.x, dy + event.y)
            shape.x, shape.y = dx + event.x, dy + event.y
        else:
            coords = self.cvs.coords(shape.id)
            initial = coords[2:]
            shape.x, shape.y = initial
            self.cvs.coords(
                            shape.id, 
                            coords[0] + dx + event.x - initial[0], 
                            coords[1] + dy + event.y - initial[1],
                            dx + event.x,
                            dy + event.y
                            )
            
                
    def move_node(self, n):
        newx, newy = float(n.x), float(n.y)
        s = self.node_size
        for layer in range(1, self.nbl + 1):
            if n.image[layer]:
                y =  newy - (layer - 1) * self.diff_y
                coord_image = (newx - (n.imagex)//2, y - (n.imagey)//2)
                self.cvs.coords(n.image[layer], *coord_image)
                self.cvs.coords(n.oval[layer], newx - s, y - s, newx + s, y + s)
            self.cvs.coords(n.lid, newx - 15, newy + 10)
            # move the failure icon if need be
            if n in self.network.failed_obj:
                self.cvs.coords(self.id_fdtks[n], n.x, n.y)
        
        # move also the virtual line, which length depends on what layer exists
        if self.layered_display:
            for layer in range(1, self.nbl + 1):
                if self.display_layer[layer]:
                    real_layer = sum(self.display_layer[:(layer+1)])
                    if n.layer_line[real_layer]:
                        coord = (newx, newy, newx, newy - (real_layer-1)*self.diff_y)
                        self.cvs.coords(n.layer_line[real_layer], *coord)
    
        # update links coordinates
        for type_link in link_type:
            for neighbor, t in self.network.graph[n.id][type_link]:
                layer = 'all' if not self.layered_display else t.layer
                link_to_coords = self.link_coordinates(n, neighbor, layer)
                for link in link_to_coords:
                    self.cvs.coords(link.line, *link_to_coords[link])
                    # update link label coordinates
                    self.update_link_label_coordinates(link)
                    # if there is a link in failure, we need to update the
                    # failure icon by retrieving the middle position of the arc
                    if link in self.network.failed_obj:
                        mid_x, mid_y = link_to_coords[link][2:4]
                        self.cvs.coords(self.id_fdtks[link], mid_x, mid_y)
                        
    def move_nodes(self, nodes):
        for node in nodes:
            self.move_node(node)
            
    ## Object deletion
                    
    def remove_objects(self, *objects):
        for obj in objects:

            # FIRST, remove the object from all sites it belongs to 
            for site in set(obj.sites):
                site.view.remove_object_from_insite_view(obj)
                site.remove_from_site(obj)
                
            if hasattr(obj, 'AS'):
                for AS in list(obj.AS):
                    AS.management.remove_from_AS(obj)
                    
            if obj.class_type == 'node':
                del self.object_id_to_object[obj.oval[1]]
                del self.object_id_to_object[obj.image[1]]
                self.cvs.delete(obj.oval[1], obj.image[1], obj.lid)
                self.remove_objects(*self.network.remove_node(obj))
                if self.layered_display:
                    for layer in range(2, self.nbl + 1):
                        self.cvs.delete(
                                        obj.oval[layer], 
                                        obj.image[layer], 
                                        obj.layer_line[layer]
                                        )
                                    
            elif obj.class_type == 'link':
                # in case both nodes and links are selected, a link may have 
                # been deleted from a node deletion: we check it hasn't been
                # deleted yet
                if obj.line not in self.object_id_to_object:
                    continue
                # we remove the label of the attached interfaces
                self.cvs.delete(obj.ilid[0], obj.ilid[1])
                # we remove the line as well as the label on the canvas
                self.cvs.delete(obj.line, obj.lid)
                # we remove the id in the 'id to object' dictionnary
                del self.object_id_to_object[obj.line]
                # we remove the associated link in the network model
                self.network.remove_link(obj)
                # if the layered display is activate and the link 
                # to delete is not a physical link
                if self.layered_display and obj.layer > 1:
                    for edge in (obj.source, obj.destination):
                        # we check if there still are other links of the same
                        # type (i.e at the same layer) between the edge nodes
                        if not self.network.graph[edge.id][obj.type]:
                            # if that's not the case, we delete the upper-layer
                            # projection of the edge nodes, and reset the 
                            # associated 'layer to projection id' dictionnary
                            self.cvs.delete(edge.oval[obj.layer], edge.image[obj.layer])
                            # edge.image[obj.layer] = edge.oval[obj.layer] = None
                            # we delete the dashed 'layer line' and reset the
                            # associated 'layer to layer line id' dictionnary
                            self.cvs.delete(edge.layer_line[obj.layer])
                            # we delete the edge id in object id to object
                            del self.object_id_to_object[edge.oval[obj.layer]]
                            del self.object_id_to_object[edge.image[obj.layer]]
                            edge.layer_line[obj.layer] = None
            else:
                # object is a shape
                # we remove it from the model and erase it from the canvas
                self.cvs.delete(obj.id)
                del self.object_id_to_object[obj.id]
                
            if obj in self.network.failed_obj:
                self.remove_failure(obj)
                            
    def erase_graph(self):
        self.object_id_to_object.clear()
        self.unhighlight_all()
        self.so.clear()
        self.temp_line = None
        self.drag_item = None
                            
    def erase_all(self):
        self.erase_graph()
        self.cvs.delete('node', 'link', 'line', 'label')
        self.id_fdtks.clear()
        
        for node in self.network.nodes.values():
            for image in ('oval', 'image', 'layer_line'):
                setattr(node, image, dict.fromkeys(range(1, self.nbl + 1), None))
            
        for type in link_type:
            for link in self.network.pn[type].values():
                link.line = None
                            
    ## Selection / Highlight
    
    # 1) Canvas selection process
    
    def start_point_select_objects(self, event):
        x, y = self.cvs.canvasx(event.x), self.cvs.canvasy(event.y)
        # create the temporary line, only if there is nothing below
        # this is to avoid drawing a rectangle when moving a node
        below = self.cvs.find_overlapping(x-1, y-1, x+1, y+1)
        tags_below = ''.join(''.join(self.cvs.itemcget(id, 'tags')) for id in below)
        # if no object is below the selection process can start
        if 'object' not in tags_below:
            if not self.ctrl:
                self.unhighlight_all()
                self.so.clear()
            self.start_position = x, y
            # create the temporary line
            x, y = self.start_position
            self.temp_rectangle = self.cvs.create_rectangle(x, y, x, y)
            self.cvs.tag_raise(self.temp_rectangle)

    @update_coordinates
    def rectangle_drawing(self, event):
        # draw the line only if they were created in the first place
        if self.start_position != [None]*2:
            # update the position of the temporary lines
            x0, y0 = self.start_position
            self.cvs.coords(self.temp_rectangle, x0, y0, event.x, event.y)
    
    @update_coordinates
    def end_point_select_nodes(self, event):
        selection_mode = self.controller.creation_menu.selection_mode
        allowed = tuple(mode for mode, v in selection_mode.items() if v.get())
        if self.start_position != [None]*2:
            # delete the temporary lines
            self.cvs.delete(self.temp_rectangle)
            # select all nodes enclosed in the rectangle
            start_x, start_y = self.start_position
            for obj in self.cvs.find_enclosed(start_x, start_y, event.x, event.y):
                if obj in self.object_id_to_object:
                    enclosed_obj = self.object_id_to_object[obj]
                    if enclosed_obj.class_type in allowed:
                        self.highlight_objects(enclosed_obj)
            self.start_position = [None]*2
        
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
                                    image = self.controller.dict_image[color][obj.subtype]
                                    )
            elif obj.class_type == 'link':
                dash = (3, 5) if dash else ()
                self.cvs.itemconfig(obj.line, fill=color, width=5, dash=dash)
            # object is a shape
            else:
                if obj.subtype == 'label':
                    self.cvs.itemconfig(obj.id, fill=color)
                else:
                    self.cvs.itemconfig(obj.id, outline=color)
                
    def unhighlight_objects(self, *objects):
        for obj in objects:
            self.so[obj.class_type].discard(obj)
            if obj.class_type == 'node':
                self.cvs.itemconfig(obj.oval, fill=obj.color)
                self.cvs.itemconfig(
                                obj.image[1], 
                                image = self.controller.dict_image['default'][obj.subtype]
                                )
            elif obj.class_type == 'link':
                self.cvs.itemconfig(obj.line, fill=obj.color, 
                                        width=self.link_width, dash=obj.dash)
            # object is a shape
            else:
                if obj.subtype == 'label':
                    self.cvs.itemconfig(obj.id, fill=obj.color)
                else:
                    self.cvs.itemconfig(obj.id, outline=obj.color)
                
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
        
    def refresh_label(self, obj, label_type=None, itf=False):
        # label_type is None if we simply want to update the label value
        # but not change the type of label displayed.
        if not label_type:
            label_type = self.current_label[obj.subtype]
        # we retrieve the id of the normal label in general, but the interface
        # labels id (two labels) if we update the interfaces labels. 
        label_id = obj.lid if not itf else obj.ilid
        # if it is not, it means there is no label to display. 
        # we have one or two labels to reset to an empty string depending 
        # on whether it is the interface labels or another one.
        if label_type == 'None':
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
        elif label_type in ('capacity', 'flow', 'traffic', 'wctraffic'):
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
        elif itf and label_type in ('name', 'ipaddress', 'cost'):
            # to display the name of the interface, we retrieve the 'interface'
            # parameters of the corresponding physical link
            # or if it is the cost and there is a single AS, we retrieve the
            # AS interface cost
            if label_type == 'cost':
                if len(obj.interfaceS.AS_properties) == 1:
                    AS ,= obj.interfaceS.AS_properties
                    valueS = obj.interfaceS(AS, 'cost')
                    valueD = obj.interfaceD(AS, 'cost')
            else:
                valueS = getattr(obj.interfaceS, label_type)
                valueD = getattr(obj.interfaceD, label_type)
            self.cvs.itemconfig(label_id[0], text=valueS)
            self.cvs.itemconfig(label_id[1], text=valueD)
        else:
            self.cvs.itemconfig(label_id, text=getattr(obj, label_type))
            
    # two functions to refresh label: type and subtype
    # refreshing a type means refreshing all subtypes of that type
    # refresh the label for one object with the current object label
    
    def refresh_subtype_labels(self, subtype, label=False):
        # by default, this function simply refreshes all labels:
        # label defaults to False
        if label:
            self.current_label[subtype] = label
        type = subtype_to_type[subtype]
        # if we change the interface label, it is actually the physical link we
        # need to retrieve, since that's where we store the interfaces values
        obj_type = 'plink' if type == 'Interface' else type.lower()
        # interface is a boolean that tells the 'refresh_label' function
        # whether we want to update the interface label, or the physical 
        # link label, since they have the same name
        itf = type == 'interface'
        #TODO: ilid should be associated with the interface, not with the link
        if itf:
            type = 'plink'
            subtype = subtype.split()[0] + ' link'
            self.current_label[subtype] = label
        for obj in self.network.ftr(type, subtype):
            self.refresh_label(obj, self.current_label[subtype], itf)
    
    def refresh_type_labels(self, type, label=None):
        for subtype in type_to_subtype[type]:
            self.refresh_subtype_labels(subtype, label)
            
    def refresh_all_labels(self):
        for subtype in object_properties:
            self.refresh_subtype_labels(subtype)
                        
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
    def cancel(self):
        if self._job is not None:
            self.cvs.after_cancel(self._job)
            self._job = None

    def link_coordinates(self, source, destination, layer='all'):
        xA, yA, xB, yB = source.x, source.y, destination.x, destination.y
        angle = atan2(yB - yA, xB - xA)
        dict_link_to_coords = {}
        type = layer if layer == 'all' else self.layers[1][layer]
        real_layer = 1 if layer == 'all' else sum(self.display_layer[:(layer+1)])
        for id, link in enumerate(self.network.links_between(source, destination, type)):
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
    def draw_objects(self, objects, random=True):
        self.cancel()
        for obj in objects:
            if obj.class_type == 'node':
                if random:
                    obj.x = randint(int(obj.x) - 500, int(obj.x) + 500)
                    obj.y = randint(int(obj.y) - 500, int(obj.y) + 500)
                if not obj.image[1]:
                    self.create_node(obj)
            else:
                self.create_link(obj)
            if obj in self.network.failed_obj:
                self.simulate_failure(obj)
             
    def draw_all(self, random=True):
        self.erase_all()
        # we draw everything except interface
        for type in set(self.network.pn) - {'interface'}:
            self.draw_objects(self.network.pn[type].values(), random)
            
    # 2) Force-based drawing
    
    ## Distance functions
    
    def distance(self, p, q): 
        return sqrt(p*p + q*q)
        
    def haversine_distance(self, s, d):
        ''' Earth distance between two nodes '''
        coord = (s.longitude, s.latitude, d.longitude, d.latitude)
        # decimal degrees to radians conversion
        lon_s, lat_s, lon_d, lat_d = map(radians, coord)
    
        delta_lon = lon_d - lon_s 
        delta_lat = lat_d - lat_s 
        a = sin(delta_lat/2)**2 + cos(lat_s)*cos(lat_d)*sin(delta_lon/2)**2
        c = 2*asin(sqrt(a)) 
        # radius of earth (km)
        r = 6371 
        return c*r
 
    ## Force-directed layout algorithms
    
    ## 1) Eades algorithm 
    
    # We use the following constants:
    # - k is the spring constant (stiffness of the spring)
    # - L0 is the equilibrium length
    # - cf is the Coulomb factor (repulsive force factor)
    # - sf is the speed factor
    
    def coulomb_force(self, dx, dy, dist, cf):
        c = dist and cf/dist**3
        return (-c*dx, -c*dy)
        
    def hooke_force(self, dx, dy, dist, L0, k):
        const = dist and k*(dist - L0)/dist
        return (const*dx, const*dy)
            
    def spring_layout(self, nodes, cf, k, sf, L0, v_nodes=set()):
        nodes = set(nodes)
        for nodeA in nodes:
            Fx = Fy = 0
            for nodeB in nodes | v_nodes | set(self.network.neighbors(nodeA, 'plink')):
                if nodeA != nodeB:
                    dx, dy = nodeB.x - nodeA.x, nodeB.y - nodeA.y
                    dist = self.distance(dx, dy)
                    F_hooke = (0,)*2
                    if self.network.is_connected(nodeA, nodeB, 'plink'):
                        F_hooke = self.hooke_force(dx, dy, dist, L0, k)
                    F_coulomb = self.coulomb_force(dx, dy, dist, cf)
                    Fx += F_hooke[0] + F_coulomb[0] * nodeB.virtual_factor
                    Fy += F_hooke[1] + F_coulomb[1] * nodeB.virtual_factor
            nodeA.vx = max(-100, min(100, 0.5 * nodeA.vx + 0.2 * Fx))
            nodeA.vy = max(-100, min(100, 0.5 * nodeA.vy + 0.2 * Fy))
    
        for node in nodes:
            node.x += round(node.vx * sf)
            node.y += round(node.vy * sf)
            
    ## 2) Fruchterman-Reingold algorithms
    
    def fa(self, d, k):
        return (d**2)/k
    
    def fr(self, d, k):
        return -(k**2)/d
        
    def fruchterman_reingold_layout(self, nodes, limit, opd=0):
        t = 1
        if not opd:
            opd = sqrt(1200*700/len(self.network.plinks))
        opd /= 3
        for nA in nodes:
            nA.vx, nA.vy = 0, 0
            for nB in nodes:
                if nA != nB:
                    deltax = nA.x - nB.x
                    deltay = nA.y - nB.y
                    dist = self.distance(deltax, deltay)
                    if dist:
                        nA.vx += deltax * opd**2 / dist**2
                        nA.vy += deltay * opd**2 / dist**2
                    
        for l in self.network.plinks.values():
            deltax = l.source.x - l.destination.x
            deltay = l.source.y - l.destination.y
            dist = self.distance(deltax, deltay)
            if dist:
                l.source.vx -= dist * deltax / opd
                l.source.vy -= dist * deltay / opd
                l.destination.vx += dist * deltax / opd
                l.destination.vy += dist * deltay / opd
            
        for n in nodes:
            d = self.distance(n.vx, n.vy)
            n.x += n.vx / sqrt(d)
            n.y += n.vy / sqrt(d)
            if limit:
                n.x = min(800, max(0, n.x))
                n.y = min(800, max(0, n.y))
            
        t *= 0.95
        
    ## 3) BFS-clusterization spring-based algorithm
    
    def bfs_cluster(self, source, visited, stop=30):
        node_number = 0
        cluster = set()
        frontier = {source}
        while frontier and node_number < stop:
            temp = frontier
            frontier = set()
            for node in temp:
                for neighbor, _ in self.network.graph[node.id]['plink']:
                    if node not in visited:
                        frontier.add(neighbor)
                        node_number += 1
                cluster.add(node)
        return frontier, cluster
        
    def create_virtual_nodes(self, cluster, nb):
        n = len(cluster)
        mean_value = lambda axe: sum(getattr(node, axe) for node in cluster)
        x_mean, y_mean = mean_value('x')/n , mean_value('y')/n
        virtual_node = self.network.nf(name = 'vn' + str(nb), node_type = 'cloud')
        virtual_node.x, virtual_node.y = x_mean, y_mean
        virtual_node.virtual_factor = n
        return virtual_node
    
    def bfs_spring(self, nodes, cf, k, sf, L0, vlinks, size=40, iterations=3):
        nodes = set(nodes)
        source = choice(list(nodes))
        # all nodes one step ahead of the already drawn area
        overall_frontier = {source}
        # all nodes which location has already been set
        seen = set(self.network.nodes.values()) - nodes
        # virtuals nodes are the centers of previously clusterized area:
        # they are not connected to any another node, but are equivalent to a
        # coulomb forces of all cluster nodes
        virtual_nodes = set()
        # dict to associate a virtual node to its frontier
        # knowing this association will later allow us to create links
        # between virtual nodes before applying a spring algorithm to virtual
        # nodes
        vnode_to_frontier = {}
        # dict to keep track of all virtual node <-> cluster association
        # this allows us to recompute all cluster nodes position after 
        # applying the spring algorithm on virtual nodes
        vnode_to_cluster = {}
        # number of cluster
        nb_cluster = 0
        # total number of nodes
        n = len(self.network.nodes)
        while overall_frontier:
            new_source = overall_frontier.pop()
            new_frontier, new_cluster = self.bfs_cluster(new_source, seen, size)
            nb_cluster += 1
            overall_frontier |= new_frontier
            seen |= new_cluster
            overall_frontier -= seen
            i = 0
            for i in range(iterations):
                self.spring_layout(new_cluster, cf, k, sf, L0, virtual_nodes)
            new_vnode = self.create_virtual_nodes(new_cluster, nb_cluster)
            vnode_to_cluster[new_vnode] = new_cluster
            vnode_to_frontier[new_vnode] = new_frontier
            virtual_nodes |= {new_vnode}
        
        if vlinks:
            # we create virtual links between virtual nodes, whenever needed
            for vnodeA in virtual_nodes:
                for vnodeB in virtual_nodes:
                    if vnode_to_cluster[vnodeA] & vnode_to_frontier[vnodeB]:
                        self.network.lf(source=vnodeA, destination=vnodeB)
        
        # we then apply a spring algorithm on the virtual nodes only
        # we first store the initial position to compute the difference 
        # with the position after the algorithm has been executed
        # we then move all clusters nodes by the same difference
        initial_position = {}
        for vnode in virtual_nodes:
            initial_position[vnode] = (vnode.x, vnode.y)
        for i in range(iterations):
            self.spring_layout(virtual_nodes, cf, k, sf, L0)
        for vnode, cluster in vnode_to_cluster.items():
            x0, y0 = initial_position[vnode]
            dx, dy = vnode.x - x0, vnode.y - y0
            for node in cluster:
                node.x, node.y = node.x + dx, node.y + dy
                        
        for node in virtual_nodes:
            for link in self.network.remove_node(node):
                self.network.remove_link(link)
    
    def retrieve_parameters(self, algorithm):
        entry_value = lambda entry: float(entry.text)
        parameters = []
        if algorithm in ('Spring-based layout', 'BFS-clusterization layout'):
            parameters += list(map(entry_value, self.controller.drawing_menu.entries))
        if algorithm == 'Fructhermann-Reingold layout':
            bound_limit = self.controller.drawing_menu.stay_withing_screen_bounds.get()
            parameters.append(bound_limit)
        if algorithm == 'BFS-clusterization layout':
            vlinks = self.controller.drawing_menu.virtual_links.get()
            parameters.append(vlinks)
        return parameters

    def spring_based_drawing(self, nodes):
        if not self._job:
            # reset the number of iterations
            self.drawing_iteration = 0
        else:
            self.cancel()
        self.drawing_iteration += 1
        params = self.retrieve_parameters('Spring-based layout')
        self.spring_layout(nodes, *params)
        if not self.drawing_iteration % 5:   
            for node in nodes:
                self.move_node(node)
        self._job = self.cvs.after(1, lambda: self.spring_based_drawing(nodes))
        
    def FR_drawing(self, nodes):
        if not self._job:
            # update the optimal pairwise distance
            self.controller.opd = sqrt(500*500/len(self.network.nodes))
            # reset the number of iterations
            self.drawing_iteration = 0
        else:
            self.cancel()
        self.drawing_iteration += 1
        # retrieve the optimal pairwise distance and the screen limit boolean
        params = self.retrieve_parameters('Fructhermann-Reingold layout')
        self.fruchterman_reingold_layout(nodes, *params)
        if not self.drawing_iteration % 5:   
            for node in nodes:
                self.move_node(node)
        self._job = self.cvs.after(1, lambda: self.FR_drawing(nodes))
        
    def bfs_cluster_drawing(self, nodes):
        if not self._job:
            # update the optimal pairwise distance
            self.controller.opd = sqrt(500*500/len(self.network.nodes))
            # reset the number of iterations
            self.drawing_iteration = 0
        else:
            self.cancel()
        params = self.retrieve_parameters('BFS-clusterization layout')
        self.bfs_spring(nodes, *params)
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
            min_y = min(node.y for node in self.network.nodes.values())
            max_y = max(node.y for node in self.network.nodes.values())
            self.diff_y = (max_y - min_y) // 2 + 200
            
        self.unhighlight_all()
        self.draw_all(False)
        
        return self.layered_display
            
    def planal_move(self, angle=45):
        min_y = min(node.y for node in self.network.nodes.values())
        max_y = max(node.y for node in self.network.nodes.values())
        
        for node in self.network.nodes.values():
            diff_y = abs(node.y - min_y)
            new_y = min_y + diff_y * cos(radians(angle))
            node.y = new_y
            
    ## Failure simulation
    
    def remove_failure(self, *objects):
        for obj in objects:
            self.network.failed_obj.remove(obj)
            icon_id = self.id_fdtks.pop(obj)
            self.cvs.delete(icon_id)
    
    def remove_failures(self):
        self.network.failed_obj.clear()
        for idx in self.id_fdtks.values():
            self.cvs.delete(idx)
        self.id_fdtks.clear()
    
    def simulate_failure(self, *objects):
        for obj in objects:
            if obj in self.id_fdtks:
                continue
            self.network.failed_obj.add(obj)
            if obj.class_type == 'link':
                source, destination = obj.source, obj.destination
                xA, yA, xB, yB = source.x, source.y, destination.x, destination.y
                id_failure = self.cvs.create_image(
                                                (xA+xB)/2, 
                                                (yA+yB)/2, 
                                                image = self.controller.img_failure
                                                )
            else:
                id_failure = self.cvs.create_image(
                                                obj.x, 
                                                obj.y, 
                                                image = self.controller.img_failure
                                                )
                for _, plink in self.network.graph[obj.id]['plink']:
                    self.simulate_failure(plink)
            self.id_fdtks[obj] = id_failure
            
    ## Display filtering
    
    def display_filter(self, filter):
        filter_sites = set(re.sub(r'\s+', '', filter).split(','))
        for node in self.network.nodes.values():
            state = 'normal' if node.sites & filter_sites else 'hidden'
            self.cvs.itemconfig(node.lid, state=state)
            for layer in range(1, self.nbl + 1):
                if node.image[layer]:
                    self.cvs.itemconfig(node.image[layer], state=state)
        for link_type in link_type:
            for link in self.network.pn[link_type].values():
                state = 'normal' if link.sites & filter_sites else 'hidden'
                self.cvs.itemconfig(link.line, state=state)
                self.cvs.itemconfig(link.lid, state=state)
            
    ## Refresh display
    
    def refresh_display(self):
        # remove selections as the red highlight will go away anyway
        self.so.clear()
        self.refresh_all_labels()     
        # self.refresh_failures() 
        # filter = self.controller.display_menu.filter_entry.text
        # if filter:
        #     self.display_filter(filter)   
        for AS in self.network.pnAS.values():
            AS.management.refresh_display()
            
    ## Other
    
    def add_to_edges(self, AS, *nodes):
        for node in nodes:
            if node not in AS.edges:
                AS.edges.add(node)
                AS.management.listbox_edges.insert('end', obj)
                
    # show/hide display per type of objects
    def show_hide(self, subtype):
        self.display_per_type[subtype] = not self.display_per_type[subtype]
        new_state = 'normal' if self.display_per_type[subtype] else 'hidden'
        if subtype in node_subtype:
            for node in self.network.ftr('node', subtype):
                self.cvs.itemconfig(node.lid, state=new_state)
                for layer in range(1, self.nbl + 1):
                    self.cvs.itemconfig(node.image[layer], state=new_state)
                    self.cvs.itemconfig(node.layer_line[layer], state=new_state)
                for link in self.network.attached_links(node):
                    # if the display is activated for the link's layer, we 
                    # update the state
                    if self.display_layer[link.layer]:
                        self.cvs.itemconfig(link.line, state=new_state)
                        self.cvs.itemconfig(link.lid, state=new_state)
        else:
            type = subtype_to_type[subtype]
            for link in self.network.ftr(type, subtype):
                self.cvs.itemconfig(link.line, state=new_state)
                self.cvs.itemconfig(link.lid, state=new_state)
        return self.display_per_type[subtype]
        
    def canvas_center(self):
        x = (self.cvs.xview()[0] + self.cvs.xview()[1]) / 2
        y = (self.cvs.yview()[0] + self.cvs.yview()[1]) / 2
        return x, y
                