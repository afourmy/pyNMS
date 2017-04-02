# NetDim
# Copyright (C) 2017 Antoine Fourmy (contact@netdim.fr)

from .base_scenario import BaseScenario
from objects.objects import *
from menus.insite_general_rightclick_menu import InSiteGeneralRightClickMenu
from menus.network_selection_rightclick_menu import NetworkSelectionRightClickMenu
from math import cos, sin, atan2, sqrt, radians
from random import randint

def overrider(interface_class):
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider

class InSiteScenario(BaseScenario):

    def __init__(self, site, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.site = site
        self.ns = self.ms.ns
        self.ntw = self.ns.ntw
        
        # add binding for right-click menu 
        self.cvs.tag_bind('object', '<ButtonPress-3>',
                                lambda e: NetworkSelectionRightClickMenu(e, self))
        
        # add binding to exit the insite view, back to the site view
        self.cvs.bind('<space>', self.back_to_site_view)
        
    # upon pressing space, back to the site scenario
    def back_to_site_view(self, _):
        self.ms.view_menu.switch_view('site')
        
    def adapt_coordinates(function):
        def wrapper(self, event, *others):
            event.x, event.y = self.cvs.canvasx(event.x), self.cvs.canvasy(event.y)
            function(self, event, *others)
        return wrapper
        
    def general_menu(self, event):
        x, y = self._start_pos_main_node
        # if the right-click button was pressed, but the position of the 
        # canvas when the button is released hasn't changed, we create
        # the general right-click menu
        if (x, y) == (event.x, event.y):
            InSiteGeneralRightClickMenu(event, self)
                
    @adapt_coordinates
    @overrider(BaseScenario)
    def find_closest_node(self, event):
        # record the item and its location
        self._dict_start_position.clear()
        self.drag_item = self.cvs.find_closest(event.x, event.y)[0]
        # save the initial position to compute the delta for multiple nodes motion
        main_node_selected = self.object_id_to_object[self.drag_item]
        merged_dict = main_node_selected.site_image[self.site].items()
        layer = [l for l, item_id in merged_dict if item_id == self.drag_item].pop()
        diff = layer * self.diff_y
        self._start_pos_main_node = event.x, event.y + diff
        if main_node_selected in self.so['node']:
            # for all selected node (sn), we store the initial position
            for sn in self.so['node']:
                self._dict_start_position[sn] = [
                                            sn.site_coords[self.site][0], 
                                            sn.site_coords[self.site][1] + diff
                                            ]
        else:
            # if ctrl is not pressed, we forget about the old selection, 
            # consider only the newly selected node, and unhighlight everything
            if not self.ctrl:
                self.unhighlight_all()
            self.highlight_objects(main_node_selected)
            # we update the dict of start position
            self._dict_start_position[main_node_selected] = self._start_pos_main_node 
            # we also need to update the highlight to that the old selection
            # is no longer highlighted but the newly selected node is.
            self.highlight_objects(main_node_selected)
            
    @adapt_coordinates
    @overrider(BaseScenario)
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
                                            source.site_coords[self.site][0], 
                                            source.site_coords[self.site][1], 
                                            text = 'S', 
                                            font = font, 
                                            fill = 'yellow'
                                            )
            self.dest_label = self.cvs.create_text(
                                            destination.site_coords[self.site][0], 
                                            destination.site_coords[self.site][1], 
                                            text = 'D', 
                                            font = font, 
                                            fill = 'yellow'
                                            )
        if main_link_selected.type in ('traffic', 'route'):
            if hasattr(main_link_selected, 'path'):
                self.highlight_objects(*main_link_selected.path)
                          
    @overrider(BaseScenario)
    def update_nodes_coordinates(self, factor):
        # scaling changes the coordinates of the oval, and we update 
        # the corresponding node's coordinates accordingly
        for node in self.site.ps['node']:
            new_coords = self.cvs.coords(node.site_oval[self.site][1])
            node.site_coords[self.site][0] = (new_coords[0] + new_coords[2]) / 2
            node.site_coords[self.site][1] = (new_coords[3] + new_coords[1]) / 2
            self.cvs.coords(node.site_lid[self.site], node.site_coords[self.site][0] - 15, node.site_coords[self.site][1] + 10)
            for layer in range(1, self.nbl + 1):
                if node.site_image[self.site][layer] or layer == 1:
                    x = node.site_coords[self.site][0] - node.imagex / 2
                    y = node.site_coords[self.site][1] - (layer - 1) * self.diff_y - node.imagey / 2
                    self.cvs.coords(node.site_image[self.site][layer], x, y)
                    coord = (node.site_coords[self.site][0], node.site_coords[self.site][1], node.site_coords[self.site][0], node.site_coords[self.site][1] - (layer - 1) * self.diff_y)
                    self.cvs.coords(node.site_layer_line[self.site], *coord)
            # the oval was also resized while scaling
            node.site_size[self.site] = abs(new_coords[0] - new_coords[2])/2 
            for type in link_type:
                for neighbor, t in self.ns.ntw.graph[node.id][type]:
                    if t not in self.site.ps['link']:
                        continue
                    layer = 'all' if not self.layered_display else t.layer
                    link_to_coords = self.link_coordinates(node, neighbor, layer)
                    for link in link_to_coords:
                        self.cvs.coords(link.site_line[self.site], *link_to_coords[link])
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
    
    @adapt_coordinates
    @overrider(BaseScenario)
    def create_node_on_binding(self, event):
        # we create the node in both the insite scenario and the network scenario
        # the node will be at its geographical coordinates in the network scenario,
        # and the event coordinates in the insite scenario
        node = self.ns.ntw.nf(
                              node_type = self._creation_mode,
                              longitude = self.site.longitude,
                              latitude = self.site.latitude
                              )
        # since the node is created from within a site, it is immediately 
        # added to the site (and drawn in the insite view at the same time)
        self.site.add_to_site(node)
        node.site_coords[self.site] = [event.x, event.y]
        self.move_node(node)
        # create the node in the network view and move to the site coordinates
        self.ns.create_node(node)
        self.ns.move_to_geographical_coordinates(node)
    
    @overrider(BaseScenario)
    def create_node(self, node, layer=1):
        s = self.node_size
        curr_image = self.ms.dict_image['default'][node.subtype]
        y = node.site_coords[self.site][1] - (layer - 1) * self.diff_y
        tags = (node.subtype, node.class_type, 'object')
        node.site_image[self.site][layer] = self.cvs.create_image(
                            node.site_coords[self.site][0] - (node.imagex)/2, 
                            y - (node.imagey)/2, 
                            image = curr_image, 
                            anchor = 'nw', 
                            tags = tags
                            )
        node.site_oval[self.site][layer] = self.cvs.create_oval(
                            node.site_coords[self.site][0] - s, 
                            y - s, 
                            node.site_coords[self.site][0] + s, 
                            y + s, 
                            outline = node.color, 
                            fill = node.color, 
                            tags = tags
                            )
        # create/hide the image/the oval depending on the current mode
        self.cvs.itemconfig(node.site_oval[self.site][layer], state='hidden')
        self.object_id_to_object[node.site_oval[self.site][layer]] = node
        self.object_id_to_object[node.site_image[self.site][layer]] = node
        if layer == 1:
            self.create_node_label(node)
            
    @adapt_coordinates
    @overrider(BaseScenario)
    def start_link(self, event):
        self.drag_item = self.cvs.find_closest(event.x, event.y)[0]
        start_node = self.object_id_to_object[self.drag_item]
        self.temp_line = self.cvs.create_line(
                                        start_node.site_coords[self.site][0], 
                                        start_node.site_coords[self.site][1], 
                                        event.x, 
                                        event.y, 
                                        arrow = 'last', 
                                        arrowshape = (6,8,3)
                                        )
        
    @adapt_coordinates
    @overrider(BaseScenario)
    def line_creation(self, event):
        # remove the purple highlight of the closest object when creating 
        # a link: the normal system doesn't work because we are in 'B1-Motion'
        # mode and not just 'Motion'
        if self.co:
            self.unhighlight_objects(self.co)
        # node from which the link starts
        start_node = self.object_id_to_object[self.drag_item]
        # create a line to show the link
        self.cvs.coords(
                        self.temp_line, 
                        start_node.site_coords[self.site][0], 
                        start_node.site_coords[self.site][1], 
                        event.x, 
                        event.y
                        )
        
    @adapt_coordinates
    @overrider(BaseScenario)
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
                    new_link = self.ns.ntw.lf(
                                            subtype = subtype,
                                            source = start_node, 
                                            destination = destination_node
                                            )
                    self.site.add_to_site(new_link)
                    # add in the network scenario as well
                    self.ns.create_link(new_link)
                    
    @overrider(BaseScenario)
    def create_link(self, new_link):
        edges = (new_link.source, new_link.destination)
        real_layer = sum(self.display_layer[:(new_link.layer+1)])
        for node in edges:
            # we always have to create the nodes at layer 0, no matter whether
            # the layered display option is activated or not.
            if self.display_layer[new_link.layer] and self.layered_display:
                # we check whether the node image already exist or not, and 
                # create it only if it doesn't.
                if not node.site_image[self.site][real_layer]:
                    self.create_node(node, real_layer)
                # if the link we consider is not the lowest layer
                # and the associated 'layer line' does not yet exist
                # we create it
                if real_layer > 1 and not node.site_layer_line[self.site][real_layer]:
                    coords = (
                              node.site_coords[self.site][0], 
                              node.site_coords[self.site][1], 
                              node.site_coords[self.site][0], 
                              node.site_coords[self.site][1] - (real_layer - 1) * self.diff_y
                              ) 
                    node.site_layer_line[self.site][real_layer] = self.cvs.create_line(
                                        *coords, 
                                        tags = ('line',), 
                                        fill = 'black', 
                                        width = 1, dash = (3,5)
                                        )
                    self.cvs.tag_lower(node.site_layer_line[self.site][real_layer])
        current_layer = 'all' if not self.layered_display else new_link.layer
        link_to_coords = self.link_coordinates(*edges, layer=current_layer)
        for link in link_to_coords:
            coords = link_to_coords[link]
            if not link.site_line[self.site]:
                state = 'normal' if self.display_layer[link.layer] else 'hidden'
                link.site_line[self.site] = self.cvs.create_line(
                                            *coords, 
                                            tags = (
                                                    link.subtype, 
                                                    link.type, 
                                                    link.class_type, 
                                                    'object'
                                                    ), 
                                            fill = link.color, 
                                            width = self.LINK_WIDTH, 
                                            dash = link.dash, 
                                            smooth = True,
                                            state = state
                                            )
            else:
                self.cvs.coords(link.site_line[self.site], *coords)
        self.cvs.tag_lower(new_link.site_line[self.site])
        self.object_id_to_object[new_link.site_line[self.site]] = new_link
        self._create_link_label(new_link)
        self.refresh_label(new_link)
    
    @overrider(BaseScenario)
    def multiple_nodes(self, n, subtype, x, y):
        for node in self.ns.ntw.multiple_nodes(n, subtype):
            node.site_coords[self.site][0] = x
            node.site_coords[self.site][1] = y
            
    ## Motion
    
    @adapt_coordinates
    @overrider(BaseScenario)
    def node_motion(self, event):
        # destroy the tip window when moving a node
        self.pwindow.destroy()
        # record the new position
        node = self.object_id_to_object[self.drag_item]
        # layer diff
        merged_dict = node.site_image[self.site].items()
        layer = [l for l, item_id in merged_dict if item_id == self.drag_item].pop()
        diff = (layer - 1) * self.diff_y
        for selected_node in self.so['node']:
            # the main node initial position, the main node current position, 
            # and the other node initial position form a rectangle.
            # we find the position of the fourth vertix.
            x0, y0 = self._start_pos_main_node
            x1, y1 = self._dict_start_position[selected_node]
            selected_node.site_coords[self.site][0] = x1 + (event.x - x0)
            selected_node.site_coords[self.site][1] = y1 + (event.y + diff - y0)
            self.move_node(selected_node)
          
    @overrider(BaseScenario)
    def move_node(self, n):
        newx, newy = float(n.site_coords[self.site][0]), float(n.site_coords[self.site][1])
        s = self.node_size
        for layer in range(1, self.nbl + 1):
            if n.site_image[self.site][layer]:
                y =  newy - (layer - 1) * self.diff_y
                coord_image = (newx - (n.imagex)//2, y - (n.imagey)//2)
                self.cvs.coords(n.site_image[self.site][layer], *coord_image)
                self.cvs.coords(n.site_oval[self.site][layer], newx - s, y - s, newx + s, y + s)
            self.cvs.coords(n.site_lid[self.site], newx - 15, newy + 10)
            # move the failure icon if need be
            if n in self.ns.ntw.failed_obj:
                self.cvs.coords(self.id_fdtks[n], n.site_coords[self.site][0], n.site_coords[self.site][1])
        
        # move also the virtual line, which length depends on what layer exists
        if self.layered_display:
            for layer in range(1, self.nbl + 1):
                if self.display_layer[layer]:
                    real_layer = sum(self.display_layer[:(layer+1)])
                    if n.site_layer_line[self.site][real_layer]:
                        coord = (newx, newy, newx, newy - (real_layer-1)*self.diff_y)
                        self.cvs.coords(n.site_layer_line[self.site][real_layer], *coord)
    
        # update links coordinates
        for type_link in link_type:
            for neighbor, t in self.ns.ntw.graph[n.id][type_link]:
                if t not in self.site.ps['link']:
                    continue
                layer = 'all' if not self.layered_display else t.layer
                link_to_coords = self.link_coordinates(n, neighbor, layer)
                for link in link_to_coords:
                    self.cvs.coords(link.site_line[self.site], *link_to_coords[link])
                    # update link label coordinates
                    self.update_link_label_coordinates(link)
                    # if there is a link in failure, we need to update the
                    # failure icon by retrieving the middle position of the arc
                    if link in self.ns.ntw.failed_obj:
                        mid_x, mid_y = link_to_coords[link][2:4]
                        self.cvs.coords(self.id_fdtks[link], mid_x, mid_y)
            
    ## Object deletion
    
    @overrider(BaseScenario)
    def remove_objects(self, *objects):
        self.ns.remove_objects(*objects)
                  
    def remove_object_from_insite_view(self, obj):
        if obj.class_type == 'node':
            del self.object_id_to_object[obj.site_oval[self.site][1]]
            del self.object_id_to_object[obj.site_image[self.site][1]]
            self.cvs.delete(
                            obj.site_oval[self.site][1], 
                            obj.site_image[self.site][1], 
                            obj.site_lid[self.site]
                            )
            if self.layered_display:
                for layer in range(2, self.nbl + 1):
                    self.cvs.delete(
                                    obj.site_oval[self.site][layer], 
                                    obj.site_image[self.site][layer], 
                                    obj.site_layer_line[self.site][layer]
                                    )
                                
        elif obj.class_type == 'link':
            # we remove the label of the attached interfaces
            self.cvs.delete(
                            obj.site_ilid[self.site][0], 
                            obj.site_ilid[self.site][1]
                            )
            # we remove the line as well as the label on the canvas
            self.cvs.delete(
                            obj.site_line[self.site], 
                            obj.site_lid[self.site]
                            )
            # we remove the id in the 'id to object' dictionnary
            del self.object_id_to_object[obj.site_line[self.site]]
            # if the layered display is activate and the link 
            # to delete is not a physical link
            if self.layered_display and obj.layer > 1:
                for edge in (obj.source, obj.destination):
                    # we check if there still are other links of the same
                    # type (i.e at the same layer) between the edge nodes
                    if ((not set(self.ns.ntw.graph[edge.id][obj.type]) 
                                & set(self.site.ps['link']))
                                and self.site in edge.site_image
                                ):
                        # if that's not the case, we delete the upper-layer
                        # projection of the edge nodes, and reset the 
                        # associated 'layer to projection id' dictionnary
                        self.cvs.delete(
                                        edge.site_oval[self.site][obj.layer], 
                                        edge.site_image[self.site][obj.layer]
                                        )
                        # edge.site_image[self.site][obj.layer] = edge.site_oval[self.site][obj.layer] = None
                        # we delete the dashed 'layer line' and reset the
                        # associated 'layer to layer line id' dictionnary
                        self.cvs.delete(edge.site_layer_line[self.site][obj.layer])
                        # we delete the edge id in object id to object
                        # del self.object_id_to_object[edge.site_oval[obj.layer]]
                        # del self.object_id_to_object[edge.site_image[obj.layer]]
                        edge.site_layer_line[self.site][obj.layer] = None
                        
        else:
            # object is a shape
            # we remove it from the model and erase it from the canvas
            self.cvs.delete(obj.site_id[self.site])
            del self.object_id_to_object[obj.site_id[self.site]]
            
        # remove the object from selected objects if it was selected
        self.so[obj.class_type].discard(obj)
        self.co = None
                        
        if obj in self.ns.ntw.failed_obj:
            self.remove_failure(obj)
                                          
    @overrider(BaseScenario)
    def erase_all(self):
        self.erase_graph()
        self.cvs.delete('node', 'link', 'line', 'label')
        self.id_fdtks.clear()
        
        for node in self.site.ps['node']:
            node.site_oval[self.site] = dict.fromkeys(range(1, self.nbl + 1), None)
            node.site_image[self.site] = dict.fromkeys(range(1, self.nbl + 1), None)
            node.site_layer_line[self.site] = dict.fromkeys(range(1, self.nbl + 1), None)
            
        for link in self.site.ps['link']:
            link.site_line[self.site] = None
                            
    ## Selection / Highlight
                
    # 2) Update selected objects and highlight
    @overrider(BaseScenario)
    def highlight_objects(self, *objects, color='red', dash=False):
        # highlight in red = selection: everything that is highlighted in red
        # is considered selected, and everything that isn't, unselected.
        for obj in objects:
            if color == 'red':
                self.so[obj.class_type].add(obj)
            if obj.class_type == 'node':
                self.cvs.itemconfig(obj.site_oval[self.site], fill=color)
                self.cvs.itemconfig(
                                    obj.site_image[self.site][1], 
                                    image = self.ms.dict_image[color][obj.subtype]
                                    )
            elif obj.class_type == 'link':
                dash = (3, 5) if dash else ()
                self.cvs.itemconfig(obj.site_line[self.site], fill=color, width=5, dash=dash)
            # object is a shape
            else:
                if obj.subtype == 'label':
                    self.cvs.itemconfig(obj.id, fill=color)
                else:
                    self.cvs.itemconfig(obj.id, outline=color)
                
    @overrider(BaseScenario)
    def unhighlight_objects(self, *objects):
        for obj in objects:
            self.so[obj.class_type].discard(obj)
            if obj.class_type == 'node':
                self.cvs.itemconfig(obj.site_oval[self.site], fill=obj.color)
                self.cvs.itemconfig(
                                obj.site_image[self.site][1], 
                                image = self.ms.dict_image['default'][obj.subtype]
                                )
            elif obj.class_type == 'link':
                self.cvs.itemconfig(obj.site_line[self.site], fill=obj.color, 
                                        width=self.LINK_WIDTH, dash=obj.dash)
            # object is a shape
            else:
                if obj.subtype == 'label':
                    self.cvs.itemconfig(obj.id, fill=obj.color)
                else:
                    self.cvs.itemconfig(obj.id, outline=obj.color)
                            
    ## Object labelling
                
    @overrider(BaseScenario)
    def create_node_label(self, node):
        node.site_lid[self.site] = self.cvs.create_text(
                                node.site_coords[self.site][0] - 15, 
                                node.site_coords[self.site][1] + 10, 
                                anchor = 'nw'
                                )
        self.cvs.itemconfig(node.site_lid[self.site], fill='blue', tags='label')
        # set the text of the label with refresh label
        self.refresh_label(node)
        
    # refresh the label for one object with the current object label
    @overrider(BaseScenario)
    def refresh_label(self, obj, label_type=None, itf=False):
        # label_type is None if we simply want to update the label value
        # but not change the type of label displayed.
        if not label_type:
            label_type = self.current_label[obj.subtype]
        else:
            label_type = label_type.lower()
        # we retrieve the id of the normal label in general, but the interface
        # labels id (two labels) if we update the interfaces labels. 
        label_id = obj.site_lid[self.site] if not itf else obj.site_ilid[self.site]
        
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
            
    # change label and refresh it for all objects
    @overrider(BaseScenario)
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
        # whether we want to update the interface label, or the physical link label,
        # since they have the same name
        itf = type == 'Interface'
        for obj in set(self.ntw.ftr(type, subtype)) & set(self.site.get_obj()):
            self.refresh_label(obj, self.current_label[subtype], itf)
           
    @overrider(BaseScenario)
    def _create_link_label(self, link):
        coeff = self.compute_coeff(link)
        link.site_lid[self.site] = self.cvs.create_text(
                            *self.offcenter(
                                            coeff, 
                                            *link.site_lpos[self.site]
                                            ), 
                            anchor = 'nw', 
                            fill = 'red', 
                            tags = 'label', 
                            font = 'bold'
                            )
        # we also create the interface labels, which position is at 1/4
        # of the line between the end point and the middle point
        # source interface label coordinates:
        s = self.offcenter(coeff, *self.if_label(link))
        link.site_ilid[self.site][0] = self.cvs.create_text(
                            *s, 
                            anchor = 'nw', 
                            fill = 'red',
                            tags = 'label', 
                            font = 'bold'
                            )
        # destination interface label coordinates:                                                        
        d = self.offcenter(coeff, *self.if_label(link, 'd'))
        link.site_ilid[self.site][1] = self.cvs.create_text(
                            *d, 
                            anchor = 'nw', 
                            fill = 'red', 
                            tags = 'label', 
                            font = 'bold'
                            )
        self.refresh_label(link)
                        
    @overrider(BaseScenario)
    def compute_coeff(self, link):
        # compute the slope of the link's line
        try:
            dy = (link.destination.site_coords[self.site][1] 
                            - link.source.site_coords[self.site][1])
            dx = (link.destination.site_coords[self.site][0] 
                            - link.source.site_coords[self.site][0])
            coeff = dy / dx
        except ZeroDivisionError:
            coeff = 0
        return coeff
        
    @overrider(BaseScenario)
    def if_label(self, link, end='s'):
        # compute the position of the interface label. Instead of placing the 
        # interface label in the middle of the line between the middle point lpos
        # and the end of the link, we set it at 1/4 (middle of the middle) so 
        # that its placed closer to the link's end.
        mx, my = link.site_lpos[self.site]
        if end == 's':
            if_label_x = ((mx + link.source.site_coords[self.site][0])/4 
                            + link.source.site_coords[self.site][0]/2)
            if_label_y = ((my + link.source.site_coords[self.site][1])/4 
                            + link.source.site_coords[self.site][1]/2)
        else:
            if_label_x = ((mx + link.destination.site_coords[self.site][0])/4 
                            + link.destination.site_coords[self.site][0]/2)
            if_label_y = ((my + link.destination.site_coords[self.site][1])/4 
                            + link.destination.site_coords[self.site][1]/2)
        return if_label_x, if_label_y
             
    @overrider(BaseScenario)
    def update_link_label_coordinates(self, link):
        coeff = self.compute_coeff(link)
        self.cvs.coords(
                        link.site_lid[self.site], 
                        *self.offcenter(coeff, *link.site_lpos[self.site])
                        )
        self.cvs.coords(
                        link.site_ilid[self.site][0], 
                        *self.offcenter(coeff, *self.if_label(link))
                        )
        self.cvs.coords(
                        link.site_ilid[self.site][1], 
                        *self.offcenter(coeff, *self.if_label(link, 'd'))
                        )

    @overrider(BaseScenario)
    def link_coordinates(self, source, destination, layer='all'):
        xA = source.site_coords[self.site][0]
        yA = source.site_coords[self.site][1]
        xB = destination.site_coords[self.site][0]
        yB = destination.site_coords[self.site][1]
        angle = atan2(yB - yA, xB - xA)
        dict_link_to_coords = {}
        type = layer if layer == 'all' else self.layers[1][layer]
        real_layer = 1 if layer == 'all' else sum(self.display_layer[:(layer+1)])
        for id, link in enumerate(
                    set(self.ns.ntw.links_between(source, destination, type)) 
                    & set(self.site.ps['link'])
                    ):
            d = ((id + 1) // 2) * 30 * (-1)**id
            xC = (xA + xB) / 2 + d * sin(angle)
            yC = (yA + yB) / 2 - d * cos(angle)
            offset = 0 if layer == 'all' else (real_layer - 1) * self.diff_y
            coord = (xA, yA - offset, xC, yC - offset, xB, yB - offset)
            dict_link_to_coords[link] = coord
            link.site_lpos[self.site] = (xC, yC - offset)
        return dict_link_to_coords
                
    ## Drawing
    
    # 1) Regular drawing

    @overrider(BaseScenario)
    def draw_objects(self, objects, random_drawing=True):
        self._cancel()
        for obj in objects:
            if obj.class_type == 'node':
                if random_drawing:
                    obj.site_coords[self.site][0] = randint(100,700)
                    obj.site_coords[self.site][0] = randint(100,700)
                if not obj.site_image[self.site][1]:
                    self.create_node(obj)
            else:
                self.create_link(obj)
            if obj in self.ns.ntw.failed_obj:
                self.simulate_failure(obj)
             
    @overrider(BaseScenario)
    def draw_all(self, random=True, draw_site=False):
        self.erase_all()
        # we draw everything except interface
        for type in ('node', 'link'):
            self.draw_objects(self.site.ps[type], random)
            
    # 3) Alignment / distribution
    
    @overrider(BaseScenario)
    def align(self, nodes, horizontal=True):
        # alignment can be either horizontal (horizontal = True) or vertical
        minimum = min(
                      node.site_coords[self.site][1] if horizontal 
                      else node.site_coords[self.site][0] for node in nodes
                      )
        for node in nodes:
            setattr(node, 'y'*horizontal or 'x', minimum)
        self.move_nodes(nodes)
        
    @overrider(BaseScenario)
    def distribute(self, nodes, horizontal=True):
        # uniformly distribute the nodes between the minimum and
        # the maximum lontitude/latitude of the selection
        minimum = min(
                      node.site_coords[self.site][0] if horizontal 
                      else node.site_coords[self.site][1] for node in nodes
                      )
        maximum = max(
                      node.site_coords[self.site][0] if horizontal 
                      else node.site_coords[self.site][1] for node in nodes
                      )
        # we'll use a sorted list to keep the same order after distribution
        nodes = sorted(nodes, key=lambda n: getattr(n, 'x'*horizontal or 'y'))
        offset = (maximum - minimum)/(len(nodes) - 1)
        for idx, node in enumerate(nodes):
            setattr(node, 'x'*horizontal or 'y', minimum + idx*offset)
        self.move_nodes(nodes)
                
    ## Multi-layer display
                
    @overrider(BaseScenario)
    def switch_display_mode(self):
        self.layered_display = not self.layered_display
        
        if self.layered_display:
            self.planal_move(50)
            min_y = min(node.site_coords[self.site][1] for node in self.site.ps['node'])
            max_y = max(node.site_coords[self.site][1] for node in self.site.ps['node'])
            self.diff_y = (max_y - min_y) // 2 + 200
            
        self.unhighlight_all()
        self.draw_all(False)
        
        return self.layered_display
            
    @overrider(BaseScenario)
    def planal_move(self, angle=45):
        min_y = min(node.site_coords[self.site][1] for node in self.site.ps['node'])
        max_y = max(node.site_coords[self.site][1] for node in self.site.ps['node'])
        
        for node in self.site.ps['node']:
            diff_y = abs(node.site_coords[self.site][1] - min_y)
            new_y = min_y + diff_y * cos(radians(angle))
            node.site_coords[self.site][1] = new_y
            
    ## Failure simulation
    
    @overrider(BaseScenario)
    def simulate_failure(self, *objects):
        for obj in objects:
            if obj in self.id_fdtks:
                continue
            self.ns.ntw.failed_obj.add(obj)
            if obj.class_type == 'link':
                source, destination = obj.source, obj.destination
                xA = source.site_coords[self.site][0]
                yA = source.site_coords[self.site][1]
                xB = destination.site_coords[self.site][0]
                yB = destination.site_coords[self.site][1]
                id_failure = self.cvs.create_image(
                                                (xA+xB)/2, 
                                                (yA+yB)/2, 
                                                image = self.ms.img_failure
                                                )
            else:
                id_failure = self.cvs.create_image(
                                                obj.x, 
                                                obj.y, 
                                                image = self.ms.img_failure
                                                )
                for _, plink in self.ntw.graph[obj.site_id[self.site]]['plink']:
                    self.simulate_failure(plink)
            self.id_fdtks[obj] = id_failure
                        
    ## Other
                
    # show/hide display per type of objects
    @overrider(BaseScenario)
    def show_hide(self, subtype):
        self.display_per_type[subtype] = not self.display_per_type[subtype]
        new_state = 'normal' if self.display_per_type[subtype] else 'hidden'
        if subtype in node_subtype:
            for node in self.ntw.ftr('node', subtype):
                self.cvs.itemconfig(node.site_lid[self.site], state=new_state)
                for layer in range(1, self.nbl + 1):
                    self.cvs.itemconfig(node.site_image[self.site][layer], state=new_state)
                    self.cvs.itemconfig(node.site_layer_line[self.site][layer], state=new_state)
                for link in self.ntw.attached_links(node):
                    # if the display is activated for the link's layer, we 
                    # update the state
                    if self.display_layer[link.layer]:
                        self.cvs.itemconfig(link.site_line[self.site], state=new_state)
                        self.cvs.itemconfig(link.site_lid[self.site], state=new_state)
        else:
            type = subtype_to_type[subtype]
            for link in self.ntw.ftr(type, subtype):
                self.cvs.itemconfig(link.site_line[self.site], state=new_state)
                self.cvs.itemconfig(link.site_lid[self.site], state=new_state)
        return self.display_per_type[subtype]