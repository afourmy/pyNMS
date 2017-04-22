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
            filepath ,= filepath
            self.world_map.create_map(filepath)
        
        # *self.world_map.yield_polygons(filepath)
        
        # for idx in self.world_map.map_ids:
        #     self.cvs.tag_lower(idx)
        # self.cvs.tag_lower(self.world_map.oval_id)
                
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
        # set containing all polygons 
        # used to redraw the map upon changing the projection
        self.polygons = []
        self.scale = 1
        # indicates whether a map is currently displayed or not
        self.display = False
        
    def create_map(self, filepath):
        self.land_coordinates = self.yield_lands(filepath)
        self.draw_map()
        
    def draw_map(self):
        # first, delete the existing map objects
        self.cvs.delete('land', 'water')
        # draw the water
        self.draw_water()
        # loop over the polygons in the shapefile
        for land in self.land_coordinates:
            try:
                # draw the land on the canvas
                self.draw_land(land)
            except ValueError as e:
                print(str(e))
        self.display = True
                
    def yield_lands(self, filepath):        
        # read the shapefile
        sf = shp.Reader(filepath)       
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

    def change_projection(self, projection):
        # reset the scale to 1
        self.scale = 1
        # update the projection
        self.projection = projection
        # draw the map
        self.draw_map()
        for id in self.map_ids:
            self.cvs.delete(id)
        self.draw_water()
        for coords in self.polygons:
            self.draw_map(coords)
        self.cvs.tag_lower(self.water_id)
        
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
            (cx, cy) ,= self.to_projected_coordinates((7, 49))
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
        try:
            keep = lambda x: x.isdigit() or x in '- .'
            coords = ''.join(filter(keep, str(shape))).split(' ')[1:]
            return [(eval(a[:10]), eval(b[:10])) for a, b in zip(coords[0::2], coords[1::2])]
        except (ValueError, SyntaxError) as e:
            print(str(e))
            
    # set the map object at the bottom of the stack
    def lower_map(self):
        for map_obj in self.map_ids:
            self.cvs.tag_lower(map_obj)
        self.cvs.tag_lower(self.water_id)
                                
    def view_center(self):
        return (sum(self.cvs.xview())/2, sum(self.cvs.yview())/2)

    def to_projected_coordinates(self, *coords):
        # points = []
        for longitude, latitude in coords:
            px, py = self.projections[self.projection](longitude, latitude)
            yield (px, -py)
        # return points

    def to_geographical_coordinates(self, x, y):
        px, py = x/self.scale, -y/self.scale
        lon, lat = self.projections[self.projection](px, py, inverse=True)
        return lon, lat
