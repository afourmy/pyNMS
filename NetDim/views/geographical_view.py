# NetDim (contact@netdim.fr)

import numpy as np
import warnings
from os.path import join
from tkinter import filedialog
from .base_view import BaseView
from math import *
from miscellaneous.decorators import update_coordinates, overrider
try:
    import shapefile as shp
    import shapely.geometry as sgeo
except ImportError:
    warnings.warn('SHP librairies missing: map import disabled')

class GeographicalView(BaseView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # initialize the map 
        self.world_map = Map(self)
            
    def switch_binding(self, mode): 
        super(GeographicalView, self).switch_binding(self.mode)
            
    # set the map object at the bottom of the stack
    def lower_map(self):
        for map_obj in self.world_map.map_ids:
            self.cvs.tag_lower(map_obj)
        self.cvs.tag_lower(self.world_map.oval_id)
        
    @update_coordinates
    def move_sphere(self, event):
        coords = self.world_map.from_points((event.x, event.y), dosphere=1)
        if coords and self.world_map.is_spherical():
            self.world_map.center = coords
            self.world_map.change_projection(self.world_map.mode)
                        
    @update_coordinates
    @overrider(BaseView)
    def create_node_on_binding(self, event, subtype):
        node = self.network.nf(node_type=subtype, x=event.x, y=event.y)
        # update logical and geographical coordinates
        lon, lat = self.world_map.to_geographical_coordinates(node.x, node.y)
        node.longitude, node.latitude = lon, lat
        node.logical_x, node.logical_y = node.x, node.y
        self.create_node(node)
      
    @overrider(BaseView)
    def create_node(self, node, layer=1):
        super(GeographicalView, self).create_node(node, layer)
        # if the node wasn't created from the binding (e.g import or graph
        # generation), its canvas coordinates are initialized at (0, 0). 
        # we draw the node in the middle of the canvas for the user to see them
        if not node.x and not node.y:
            # node.x, node.y = self.world_map.to_points([[node.longitude, node.latitude]], 1)
            node.x, node.y = self.world_map.view_center()

    @overrider(BaseView)
    def create_link(self, new_link):
        # create the link
        super(GeographicalView, self).create_link(new_link)
        # the link is now at the bottom of the stack after calling tag_lower
        # if the map is activated, we need to lower all map objects to be 
        # able to see the link
        self.lower_map()
            
    ## Map Menu
    
    def update_geographical_coordinates(self, *nodes):
        for node in nodes:
            node.longitude, node.latitude = self.world_map.get_geographical_coordinates(node.x, node.y)
            
    def update_logical_coordinates(self, *nodes):
        for node in nodes:
            node.logical_x, node.logical_y = node.x, node.y 
            
    def move_to_geographical_coordinates(self, *nodes):
        if not nodes:
            nodes = self.network.pn['node'].values()
        for node in nodes:
            node.x, node.y = self.world_map.to_points([[node.longitude, node.latitude]], 1)
        self.move_nodes(nodes)
        
    def move_to_logical_coordinates(self, *nodes):
        if not nodes:
            nodes = self.network.pn['node'].values()
        for node in nodes:
            node.x, node.y = node.logical_x, node.logical_y
        self.move_nodes(nodes)
        
    def delete_map(self):
        for idx in self.world_map.map_ids:
            self.cvs.delete(idx)
        
    ## Geographical projection menu
    
    def change_projection(self, projection):
        self.world_map.change_projection(projection)
        self.lower_map()
    
    @update_coordinates
    @overrider(BaseView)
    def zoomer(self, event):
        ''' Zoom for window '''
        self.cancel()
        factor = 1.2 if event.delta > 0 else 0.8
        self.diff_y *= factor
        self.node_size *= factor
        self.cvs.scale('all', 0, 0, factor, factor)
        self.world_map.scale_map(factor, event)
        self.update_nodes_coordinates(factor)
    #     
    # @update_coordinates
    # @overrider(BaseView)
    # def zoomerP(self, event):
    #     # zoom in (unix)
    #     self.cancel()
    #     self.diff_y *= 1.2
    #     self.node_size *= 1.2
    #     self.world_map.scale_map(1.2)
    #     self.update_nodes_coordinates(1.2)
    #     
    # @update_coordinates
    # @overrider(BaseView)
    # def zoomerM(self, event):
    #     # zoom out (unix)
    #     self.cancel()
    #     self.diff_y *= 0.8
    #     self.node_size *= 0.8
    #     self.world_map.scale_map(0.8)
    #     self.update_nodes_coordinates(0.8)
        
    ## Import of shapefile
    
    def import_shapefile(self, filepath=None):
                
        filepath = filedialog.askopenfilenames(
                        initialdir = join(self.controller.path_workspace, 'map'),
                        title = 'Import SHP map', 
                        filetypes = (
                        ('shp files','*.shp'),
                        ('all files','*.*')
                        ))
        
        # no error when closing the window
        if not filepath: 
            return
        else: 
            self.filepath ,= filepath
            
        self.world_map.load_polygon(*self.yield_polygons())
        
        for idx in self.world_map.map_ids:
            self.cvs.tag_lower(idx)
        self.cvs.tag_lower(self.world_map.oval_id)
        
    def yield_polygons(self):
        
        # shapefile with all countries
        sf = shp.Reader(self.filepath)
        
        shapes = sf.shapes()
        
        for shape in shapes:
            shape = sgeo.shape(shape)
            
            if shape.geom_type == 'MultiPolygon':
                yield from shape
            else:
                yield shape
                
from pyproj import Proj
        
class Map():

    projections = {
    'mercator': Proj(init="epsg:3395"),
    'spherical': Proj('+proj=ortho +lat_0=49 +lon_0=7')
    }
    
    def __init__(self, view):
        self.cvs = view.cvs
        self.map_ids = set()
        self.projection = 'mercator'
        # set containing all polygons to redraw the map with another projection
        self.polygons = []
        self.change_projection()

    def scale_map(self, ratio, event):
        self.scale *= float(ratio)

    def change_projection(self, centerof=None):
        # initialize the scale
        self.scale = 1
        # self.scale_map(center=False)
        # self.draw_sphere()
        for id in self.map_ids:
            self.cvs.delete(id)
        self.draw_water()
        for coords in self.polygons:
            self.draw_map(coords)
        self.cvs.tag_lower(self.oval_id)
            
        

    def draw_water(self):
        self.cvs.delete('water')
        if self.projection == 'mercator':
            x0, y0 = self.to_projected_coordinates([[-180, 85]])
            x1, y1 = self.to_projected_coordinates([[180, -85]])
            self.oval_id = self.cvs.create_rectangle(
                                                    0,
                                                    0,
                                                    0, 
                                                    0,
                                                    outline = 'black', 
                                                    fill = 'deep sky blue', 
                                                    tags = ('water')
                                                    )
        # if self.is_spherical():
        #     R = 180/pi*self.scale
        #     vx, vy = self.scale_x*self.scale, self.scale_y*self.scale
        #     self.oval_id = self.cvs.create_oval(
        #                                         vx/2 - R, 
        #                                         vy/2 - R, 
        #                                         vx/2 + R, 
        #                                         vy/2 + R,
        #                                         outline = 'black', 
        #                                         fill = 'deep sky blue', 
        #                                         tags = ('water')
        #                                         )
        
    def draw_map(self, coords):
        points = self.to_projected_coordinates(coords)
        obj_id = self.cvs.create_polygon(
                                         points, 
                                         fill = 'medium sea green', 
                                         outline = 'black', 
                                         tags=('land',)
                                         )
        self.map_ids.add(obj_id)
                                
    def load_polygon(self, *polygons):
        for polygon in polygons:
            coords = self.shape_to_coords(str(polygon))
            try:
                self.load_map(coords)
            except ValueError as e:
                print(str(e))
                
    def view_center(self):
        return (sum(self.cvs.xview())/2, sum(self.cvs.yview())/2)
                
    def load_map(self, polygon_coords):
        self.polygons.append(polygon_coords)
        self.draw_map(polygon_coords)
            
    def shape_to_coords(self, shape):
        try:
            keep = lambda x: x.isdigit() or x in '- .'
            coords = ''.join(filter(keep, str(shape))).split(' ')[1:]
            return [(eval(a[:10]), eval(b[:10])) for a, b in zip(coords[0::2], coords[1::2])]
        except (ValueError, SyntaxError) as e:
            print(str(e))

    def to_projected_coordinates(self, coords):
        points = []
        for longitude, latitude in coords:
            px, py = self.projections[self.projection](longitude, latitude)
            points += [px, -py]
        return points

    def to_geographical_coordinates(self, x, y):
        px, py = x/self.scale, -y/self.scale
        lon, lat = self.projections[self.projection](px, py, inverse=True)
        print(lon, lat)
        return lon, lat
