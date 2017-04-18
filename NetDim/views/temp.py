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
        self.world_map.create_meridians()
        self.world_map.center_map([[7, 49]])
            
    def switch_binding(self): 
        super(GeographicalView, self).switch_binding()
        
        # if self._mode == 'motion':
        #     self.cvs.tag_bind('water', '<ButtonPress-1>', self.move_sphere, add='+')
        #     self.cvs.tag_bind('Area', '<ButtonPress-1>', self.move_sphere, add='+')
            
    # set the map object at the bottom of the stack
    def lower_map(self):
        for map_obj in self.world_map.map_ids:
            self.cvs.tag_lower(map_obj)
        if self.world_map.is_spherical():
            self.cvs.tag_lower(self.world_map.oval_id)
        
    @update_coordinates
    def move_sphere(self, event):
        coords = self.world_map.from_points((event.x, event.y), dosphere=1)
        if coords and self.world_map.is_spherical():
            self.world_map.center = coords
            self.world_map.change_projection(self.world_map.mode)
                        
    @update_coordinates
    @overrider(BaseView)
    def create_node_on_binding(self, event):
        node = self.network.nf(node_type=self._creation_mode, x=event.x, y=event.y)
        # update logical and geographical coordinates
        lon, lat = self.world_map.get_geographical_coordinates(node.x, node.y)
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
            node.x, node.y = self.world_map.to_points([[node.longitude, node.latitude]])
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
    
    def change_projection(self, mode):
        self.world_map.change_projection(mode)
        self.lower_map()
    
    @update_coordinates
    @overrider(BaseView)
    def zoomer(self, event):
        ''' Zoom for window '''
        self.cancel()
        factor = 1.2 if event.delta > 0 else 0.8
        self.diff_y *= factor
        self.node_size *= factor
        self.world_map.scale_map(ratio=factor)
        self.update_nodes_coordinates(factor)
        
    @update_coordinates
    @overrider(BaseView)
    def zoomerP(self, event):
        # zoom in (unix)
        self.cancel()
        self.diff_y *= 1.2
        self.node_size *= 1.2
        self.world_map.scale_map(ratio=1.2)
        self.update_nodes_coordinates(1.2)
        
    @update_coordinates
    @overrider(BaseView)
    def zoomerM(self, event):
        # zoom out (unix)
        self.cancel()
        self.diff_y *= 0.8
        self.node_size *= 0.8
        self.world_map.scale_map(ratio=0.8)
        self.update_nodes_coordinates(0.8)
        
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
        
class Map():

    delta = 3600.0
    halfX = 648000.0
    mflood = []
    lonlat = []
    map_temp = {}
    
    def __init__(self, view, viewx=500, viewy=250):
        self.viewx, self.viewy = viewx, viewy
        self.cvs = view.cvs
        self.map_ids = set()
        self.scale = 0.05
        self.mode = 'mercator'
        self.change_projection(self.mode)

    def scale_map(self, ratio=1, center=True):
        # instead of remembering the center before zooming, it would be better
        # to zoom according to where the mouse is located
        self.cx = (self.cvs.xview()[0] + self.cvs.xview()[1])/2
        self.cy = (self.cvs.yview()[0] + self.cvs.yview()[1])/2
        # calc ratio of current and previous scale
        self.scale *= float(ratio)
        # update scrollregion and scale
        self.cvs['scrollregion'] = (
                                    0, 
                                    0, 
                                    self.scale_x*self.scale, 
                                    self.scale_y*self.scale
                                    )
        self.cvs.scale('all', 0, 0, ratio, ratio)
        if center:
            self.center_point()
        
    def get_geographical_coordinates(self, x, y):
        return self.from_points([x, y], dosphere=1)

    def create_meridians(self):
        x = -180
        for x in range(-180, 181, 30):
            lon = []
            for y in range(-90, 91, 30):
                lon += [[x, y]]
            self.lonlat.append(list(lon))
        for y in range(-90, 91, 30):
            centerof = [-180, y]
            lat = [centerof]
            for x in range(-180, 181, 30):
                lat += [[x, y]]
                self.lonlat.append(list(lat))
                label = centerof = None
                lat.pop(0)
                
    def draw_meridians(self):
        for coords in self.lonlat:
            coords = self.to_points(coords)
            if not coords:
                return
            if len(coords) < 4:
                coords = coords * 2
            obj_id = self.cvs.create_line(coords, fill='black', tags=('meridians',), smooth=True)
        
    def load_map(self, data):
        for row in data:
            self.mflood.append(row)
            self.draw_map(row)

    def center_point(self, x=None, y=None):
        # current view
        scrollX = self.cvs.xview()
        scrollY = self.cvs.yview()
        if x and y:
            # center by point
            moveX = x/(self.scale_x*self.scale) - (scrollX[1] - scrollX[0])/2.0
            moveY = y/(self.scale_y*self.scale) - (scrollY[1] - scrollY[0])/2.0
        else:
            # visible center
            moveX = self.cx - (scrollX[1] - scrollX[0]) / 2.0
            moveY = self.cy - (scrollY[1] - scrollY[0]) / 2.0
        self.cvs.xview('moveto', moveX)
        self.cvs.yview('moveto', moveY)

    def change_projection(self, mode='linear'):

        self.scale_x = self.viewx*self.delta
        if mode in ('linear', 'mercator'):
            self.scale_y = self.viewy*self.delta
        else:
            self.scale_y = self.to_mercator(90.0)*self.delta*self.viewy/90
            
        self.halfX = self.scale_x/2
        self.halfY = self.scale_y/2
        self.center = self.center_of()
        self.mode = mode
        self.scale_map(center=False)
        self.draw_sphere()
        for id in self.map_ids:
            self.cvs.delete(id)
        self.cvs.delete('meridians')

        for coords in self.mflood:
            self.draw_map(coords)
            
        self.create_meridians()
        self.draw_meridians()
        self.center_map([[7, 49]])

    def center_map(self, centerof=[[0,0]]):
        pts = self.to_points(centerof)
        if pts:
            self.center_point(*pts)

    def draw_sphere(self):
        self.cvs.delete('water')
        if self.is_spherical():
            R = 180/pi*self.delta*self.scale
            vx, vy = self.scale_x*self.scale, self.scale_y*self.scale
            self.oval_id = self.cvs.create_oval(
                                                vx/2 - R, 
                                                vy/2 - R, 
                                                vx/2 + R, 
                                                vy/2 + R,
                                                outline = 'black', 
                                                fill = '#40A4DF', 
                                                tags = ('water')
                                                )
        
    def draw_map(self, coords):
        points = self.to_points(coords)
        if not points:
            return
        if len(points) < 4:
            points = points * 2
        obj_id = self.cvs.create_polygon(
                                         points, 
                                         fill = 'green', 
                                         outline = 'black', 
                                         tags=('Area',)
                                         )
        self.map_ids.add(obj_id)
                                
    def load_polygon(self, *polygons):
        for polygon in polygons:
            coords = self.shape_to_coords(str(polygon))
            try:
                self.load_map([coords])
            except ValueError as e:
                print(str(e))
            
    def shape_to_coords(self, shape):
        try:
            keep = lambda x: x.isdigit() or x in '- .'
            coords = ''.join(filter(keep, str(shape))).split(' ')[1:]
            coords = [(eval(a[:10]), eval(b[:10])) for a, b in zip(coords[0::2], coords[1::2])]
        except (ValueError, SyntaxError) as e:
            print(str(e))
        return coords

    def is_spherical(self):
        return self.mode == 'globe'

    def center_of(self):
        return self.from_points(self.view_center())

    def view_center(self):
        cx = (self.scale_x*self.scale*x for x in self.cvs.xview())
        cy = (self.scale_y*self.scale*y for y in self.cvs.yview())
        return [[sum(cx)/2, sum(cy)/2]]

    def to_points(self, coords=[]):
        points = []
        for x, y in coords:
            x, y = float(x), -y
            if self.mode == 'mercator':
                y = self.to_mercator(float(y))
            if self.mode == 'globe':
                tmp = self.to_sphere([x, y])
                if not tmp:
                    continue
                x, y = tmp
            _x = x * self.delta + self.halfX 
            _y = y * self.delta + self.halfY
            points += [_x * self.scale, _y * self.scale]
        return points

    def from_points(self, points, dosphere=0):
        b, coords = 0, []
        x, y = points[0]
        x = (x / self.scale - self.halfX) / self.delta
        y = -(y / self.scale - self.halfY) / self.delta
        if self.mode == 'mercator':
            y = self.from_mercator(y)
        return [[x, y]]

    def to_mercator(self, y):
        # latitude in mercator projection
        if abs(y) > 84: 
            y = 84*np.sign(y)
        return degrees(log(tan(radians(y)/2 + atan(1))))

    def from_mercator(self, y):
        # latitude from mercator projection
        return degrees(2*(atan(e**(radians(y))) - atan(1)))

    def to_sphere(self, coords):
        x, y, cx, cy = [radians(float(x)) for x in coords + self.center[0]]
        cx += pi
        if sin(y) * sin(cy) - cos(y)*cos(cy)*cos(cx - x) > 0:
            return [
                    degrees(cos(y)*sin(cx - x)),
                    degrees(-sin(y)*cos(cy) - sin(cy)*cos(y)*cos(cx - x))
                    ]

    def from_sphere(self, coords):
        # internal
        asinz = lambda x: asin([x, ([-1.0, 1.0][x > 1.0])][abs(x) > 1.0])
        adjust_lon = lambda x: [(x - ([1, -1][x < 0] * 2.0 * pi)), x][abs( x ) < pi]
        EPSLN = 1.0e-10
        # args
        centerof = self.center or [[0, 0]]
        x, y, center_x, center_y = [radians(float(x)) for x in coords + centerof]
        rh = sqrt(x * x + y * y) + EPSLN
        if rh > 1:
            return []
        sin_p14 = sin(center_y)
        cos_p14 = cos(center_y)
        z = asinz(rh/1)
        lon = center_x
        if abs(rh) <= EPSLN :
            lat = center_y
        lat = asinz(cos(z)*sin_p14 + (y*sin(z)*cos_p14)/rh)
        con = abs(center_y) - pi/2
        if abs(con) <= EPSLN:
            if center_y >= EPSLN:
                lon = adjust_lon(center_x + atan2(x, y))
            else:
                lon = adjust_lon(center_x - atan2(-x, y))
        con = cos(z) - sin_p14*sin(lat)
        if abs(con) >= EPSLN or abs(x) >= EPSLN:
            lon = adjust_lon(center_x + atan2((x*sin(z)*cos_p14), (con*rh)));
        x = degrees(lon)
        y = degrees(lat)
        return [x, y]

    def distance(self, coords):
        # length of the great circle between two points (km)
        x, y, x1, y1 = [radians(x) for x in coords[0] + coords[1]]
        return 6378.136 * acos(cos(y)*cos(y1)*cos(x - x1) + sin(y)*sin(y1))

