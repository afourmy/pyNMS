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
    from pyproj import Proj
except ImportError:
    warnings.warn('SHP librairies missing: map import disabled')

class GeographicalView(BaseView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # initialize the map 
        self.world_map = Map(self)
            
    def switch_binding(self, mode): 
        super(GeographicalView, self).switch_binding(self.mode)
        
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
            node.x, node.y = self.canvas_center()

    @overrider(BaseView)
    def create_link(self, new_link):
        # create the link
        super(GeographicalView, self).create_link(new_link)
        # the link is now at the bottom of the stack after calling tag_lower
        # if the map is activated, we need to lower all map objects to be 
        # able to see the link
        self.world_map.lower_map()
            
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
        
    ## Geographical projection menu
    
    @update_coordinates
    @overrider(BaseView)
    def zoomer(self, event):
        ''' Zoom for window '''
        self.cancel()
        factor = 1.2 if event.delta > 0 else 0.8
        self.diff_y *= factor
        self.node_size *= factor
        self.cvs.scale('all', event.x, event.y, factor, factor)
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
            self.world_map.shapefile ,= filepath
            self.world_map.draw_map()
        
class Map():

    projections = {
    'mercator': Proj(init="epsg:3395"),
    'spherical': Proj('+proj=ortho +lat_0=47 +lon_0=28')
    }
    
    def __init__(self, view):
        self.cvs = view.cvs
        self.map_ids = set()
        self.projection = 'mercator'
        # set containing all polygons 
        # used to redraw the map upon changing the projection
        self.land_coordinates = []
        self.scale = 1
        self.offset = (0, 0)
        self.active = False
        
    def draw_map(self):
        # first, delete the existing map objects
        self.delete_map()
        # draw the water
        self.draw_water()
        # loop over the polygons in the shapefile
        for land in self.yield_lands():
            self.draw_land(land)
        self.active = True
                
    def yield_lands(self):        
        # read the shapefile
        sf = shp.Reader(self.shapefile)       
        # retrieve the shapes it contains (polygons or multipolygons) 
        shapes = sf.shapes() 
        for shape in shapes:
            # make it a shapely shape
            shape = sgeo.shape(shape)
            # if it is a multipolygon, yield the polygons it is composed of
            if shape.geom_type == 'MultiPolygon':
                yield from map(self.shape_to_coords, shape)
            # else yield the polygon itself
            else:
                yield self.shape_to_coords(shape)

    def scale_map(self, ratio, event):
        self.scale *= float(ratio)
        offset_x, offset_y = self.offset
        self.offset = (
                       offset_x*ratio + event.x*(1 - ratio), 
                       offset_y*ratio + event.y*(1 - ratio)
                       )

    def change_projection(self, projection):
        # reset the scale to 1 and the offset to 0
        self.scale = 1
        self.offset = (0, 0)
        # update the projection
        self.projection = projection
        # draw the map
        self.draw_map()
        
    def draw_land(self, land):
        # create the polygon the canvas
        obj_id = self.cvs.create_polygon(
                                         *self.to_projected_coordinates(*land), 
                                         fill = 'green3', 
                                         outline = 'black', 
                                         tags = ('land',)
                                         )
        self.map_ids.add(obj_id)

    def draw_water(self):
        if self.projection == 'mercator':
            (x0, y0) ,= self.to_projected_coordinates((-180, 84))
            (x1, y1) ,= self.to_projected_coordinates((180, -84))
            self.water_id = self.cvs.create_rectangle(
                                                    x1,
                                                    y1,
                                                    x0, 
                                                    y0,
                                                    outline = 'black', 
                                                    fill = 'deep sky blue', 
                                                    tags = ('water',)
                                                    )
        if self.projection == 'spherical':
            (cx, cy) ,= self.to_projected_coordinates((28, 47))
            self.water_id = self.cvs.create_oval(
                                                cx - 6378000,
                                                cy - 6378000,
                                                cx + 6378000, 
                                                cy + 6378000,
                                                outline = 'black', 
                                                fill = 'deep sky blue', 
                                                tags = ('water',)
                                                )
                
    def shape_to_coords(self, shape):
        # convert a stringified shape to a list of coordinates
        keep = lambda x: x.isdigit() or x in '- .'
        coords = ''.join(filter(keep, str(shape))).split(' ')[1:]
        for longitude, latitude in zip(coords[0::2], coords[1::2]):
            yield eval(longitude[:10]), eval(latitude[:10])
            
    # set the map object at the bottom of the stack
    def lower_map(self):
        if self.active:
            for map_obj in self.map_ids:
                self.cvs.tag_lower(map_obj)
            self.cvs.tag_lower(self.water_id)
        
    def delete_map(self):
        self.cvs.delete('land', 'water')

    def to_projected_coordinates(self, *coords):
        for longitude, latitude in coords:
            px, py = self.projections[self.projection](longitude, latitude)
            yield px, -py
        
    def to_geographical_coordinates(self, x, y):
        offset_x, offset_y = self.offset
        px, py = (x - offset_x)/self.scale, (offset_y - y)/self.scale
        lon, lat = self.projections[self.projection](px, py, inverse=True)
        return lon, lat
