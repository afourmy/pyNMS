# NetDim (contact@netdim.fr)

import re
from os.path import join
from tkinter import filedialog
from .base_scenario import BaseScenario
from math import *
from miscellaneous.decorators import update_coordinates, overrider
try:
    import shapefile as shp
    import shapely.geometry as sgeo
except ImportError:
    warnings.warn('SHP librairies missing: map import disabled')

class GeoScenario(BaseScenario):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # map 
        self.world_map = Map(self)
        self.world_map.change_projection('mercator')
        self.world_map.create_meridians()
        self.world_map.center_map([[7, 49]])
            
    def switch_binding(self): 
        super(GeoScenario, self).switch_binding()
        
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
            self.world_map.map_temp['centerof'] = coords
            self.world_map.change_projection(self.world_map.mode)
                        
    @update_coordinates
    @overrider(BaseScenario)
    def create_node_on_binding(self, event):
        node = self.network.nf(node_type=self._creation_mode, x=event.x, y=event.y)
        # update logical and geographical coordinates
        lon, lat = self.world_map.get_geographical_coordinates(node.x, node.y)
        node.longitude, node.latitude = lon, lat
        node.logical_x, node.logical_y = node.x, node.y
        self.create_node(node)
      
    @overrider(BaseScenario)
    def create_node(self, node, layer=1):
        super(GeoScenario, self).create_node(node, layer)
        # if the node wasn't created from the binding (e.g import or graph
        # generation), its canvas coordinates are initialized at (0, 0). 
        # we draw the node in the middle of the canvas for the user to see them
        if not node.x and not node.y:
            # node.x, node.y = self.world_map.to_points([[node.longitude, node.latitude]], 1)
            node.x, node.y = self.world_map.view_center()

    @overrider(BaseScenario)
    def create_link(self, new_link):
        # create the link
        super(GeoScenario, self).create_link(new_link)
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
    
    def change_projection(self, mode):
        self.world_map.change_projection(mode)
        self.lower_map()
    
    @update_coordinates
    @overrider(BaseScenario)
    def zoomer(self, event):
        ''' Zoom for window '''
        self.cancel()
        factor = 1.2 if event.delta > 0 else 0.8
        self.diff_y *= factor
        self.node_size *= factor
        self.world_map.scale_map(ratio=factor)
        self.update_nodes_coordinates(factor)
        
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
    ylimit = 84
    mflood = []
    lonlat = []
    map_temp = {}
    
    def __init__(self, scenario, viewx=500, viewy=250):
        self.viewx, self.viewy = viewx, viewy
        # scenario canvas
        self.cvs = scenario.cvs
        # self.map_obj
        # set of all canvas ids
        self.map_ids = set()
        self.scale = 0.05
        self.mode = 'linear'
        self.change_projection(self.mode)

    def scale_map(self, ratio=1, center=True):
        # instead of remembering the center before zooming, it would be better
        # to zoom according to where the mouse is located
        self.map_temp['center_x'] = (self.cvs.xview()[0] + self.cvs.xview()[1])/2
        self.map_temp['center_y'] = (self.cvs.yview()[0] + self.cvs.yview()[1])/2
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
        # move figure part
        coords = self.from_points([x, y], dosphere=1)
        if coords and hasattr(self, 'coords'):
            coords = self.coords[2] + coords
            self.coords[0] = self.distance(coords)
            self.draw_map(coords, 'CurrFigure')
            self.draw_map([coords[1]], 'CurrFigure')
        # calc and show coords under cursor
        coords = self.from_points((x, y), dosphere=1) or [(0, 0)]
        return coords[0][0], coords[0][1]

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
            coords = self.convert_coords(coords)
            if not coords:
                return
            if len(coords) < 4:
                coords = coords * 2
            obj_id = self.cvs.create_line(coords, fill='black', tags=('meridians',))
        
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
            moveX = self.map_temp['center_x'] - (scrollX[1] - scrollX[0]) / 2.0
            moveY = self.map_temp['center_y'] - (scrollY[1] - scrollY[0]) / 2.0
        self.cvs.xview('moveto', moveX)
        self.cvs.yview('moveto', moveY)

    def change_projection(self, mode='linear', centerof=None):
        mcenterof = []
        if not self.mode == mode:
            mcenterof = self.map_temp['centerof'] = (centerof or self.center_of())
        self.scale_x = self.viewx*self.delta
        if mode in ('linear', 'mercator'):
            self.scale_y = self.viewy*self.delta
        else:
            self.scale_y = self.to_mercator(90.0)*self.delta*self.viewy/90
            
        self.halfX = self.scale_x/2
        self.halfY = self.scale_y/2
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

            
        if mcenterof:
            self.center_map(mcenterof)

    def center_map(self, centerof=[[0,0]]):
        pts = self.to_points(centerof, doscale=1)
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

    def convert_coords(self, coords):
        # interpolate coords for Globe projection
        _coords = []
        if self.is_spherical():
            for i in range(len(coords) - 1):
                _coords += self.interpolation(coords[i:i+2])
        if not _coords:
            _coords = coords
        coords = self.to_points(_coords, doscale=1)
        
        return coords
        
    def draw_map(self, coords):
        points = self.convert_coords(coords)
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
        """Return centerof [[x,y]] (in degrees)."""
        if self.is_spherical():
            return self.map_temp.get('centerof', [[0,0]])
        else:
            return self.from_points(self.view_center())

    def sizeOf(self):
        """Return viewport size as [width, height] disregarding scale (in points)."""
        return [self.scale_x, self.scale_y]

    def viewsizeOf(self):
        """Return rect. of visible area (in points)."""
        left, right = [self.scale_x * self.scale * x for x in self.cvs.xview()]
        top, bottom = [self.scale_y * self.scale * y for y in self.cvs.yview()]
        return [left, top, right, bottom]

    def view_center(self):
        """Return center of visible area (in points)."""
        rect = self.viewsizeOf()
        return [ (rect[0] + rect[2]) / 2.0,
                 (rect[1] + rect[3]) / 2.0 ]

    def to_points(self, coords=[], doscale=0):
        points = []
        centerof = self.from_points(self.view_center())
        for x, y in coords:
            if self.mode in ('linear', 'mercator'):
                x = float(x)
                y = [self.to_mercator(float(y)), float(y)][self.mode != 'mercator']
                x, y = self.rotate_z([x, y], centerof)
                y = -y
            else:
                # self.mode is 'globe':
                tmp = self.to_sphere([x, y])
                if not tmp:
                    continue
                x, y = self.rotate_z(tmp)
            _x = x * self.delta + self.halfX 
            _y = y * self.delta + self.halfY
            if doscale:
                points += [_x * self.scale, _y * self.scale]
            else:
                points += [_x, _y]
        return points

    def from_points(self, points=[], dorotatez=1, dosphere=0):
        b, coords = 0, []
        center_x, center_y = self.view_center()
        for point in points:
            if not b:
                x, center_x = [(point / self.scale - self.halfX) / self.delta for point in [point, center_x]]
            else:
                y, center_y = [-(point / self.scale - self.halfY) / self.delta for point in [point, center_y]]
                if self.is_spherical() and dosphere:
                    if dorotatez:
                        x, y = self.rotate_z([x, y])
                    _coords = self.from_sphere([x, y])
                    if _coords:
                        coords += [_coords]
                else:
                    if dorotatez:
                        x, y = self.rotate_z([x, y], [[center_x, center_y]], reverse=1)
                    y = [self.from_mercator(y), y][self.mode != 'mercator']
                    coords += [[x, y]]
            b = not b
        return coords

    def to_mercator(self, y, ylimit=None):
        # latitude in mercator projection

        if not ylimit:
            ylimit = self.ylimit
        if abs(y) > ylimit:
            return self.to_mercator([-1, 1][y > 0] * ylimit)
        else:
            return degrees(log(tan(radians(y) / 2.0 + atan(1))))

    def from_mercator(self, y):
        # latitude from mercator projection
        return degrees(2*(atan(e**(radians(y))) - atan(1)))

    def to_sphere(self, coords):
        self.map_temp['centerof'] = centerof = self.map_temp.get('centerof', [[0,0]])
        x, y, center_x, center_y = [radians(float(x)) for x in coords + centerof[0]]
        center_x += pi
        if (sin(y) * sin(center_y) - cos(y) * cos(center_y) * cos(center_x - x)) > 0:
            return [ degrees(cos(y) * sin(center_x - x)),
                     degrees(-sin(y) * cos(center_y) - sin(center_y) * cos(y) * cos(center_x - x)) ]

    def from_sphere(self, coords):
        # internal
        asinz = lambda x: asin([x, ([-1.0, 1.0][x > 1.0])][abs(x) > 1.0])
        adjust_lon = lambda x: [(x - ([1, -1][x < 0] * 2.0 * pi)), x][abs( x ) < pi]
        EPSLN = 1.0e-10
        # args
        centerof = self.map_temp.get('centerof', [[0,0]])
        x, y, center_x, center_y = [radians(float(x)) for x in coords + centerof[0]]
        #a = 1
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

    def rotate_z(self, coords, centerof=[[0,0]], reverse=0):
        roll = self.map_temp.get('z_angle', 0)
        if roll:
            x, y, center_x, center_y = coords + centerof[0]
            roll = radians(roll)
            if reverse: 
                roll = -roll
            r = sqrt((center_x - x)*(center_x - x) + (y - center_y) * (y - center_y))
            if r:
                a = acos((center_x - x) / r)
                if ( y < center_y ): a = 2.0 * pi - a
                coords = [ center_x - r * cos(roll + a),
                           center_y + r * sin(roll + a) ]
        return coords

    def distance(self, coords):
        """Return the length of the great circle between two points (in km).
        COORDS points list [[x,y],[x1,y1]] (in degrees)."""
        x, y, x1, y1 = [radians(x) for x in coords[0] + coords[1]]
        return 6378.136 * acos(cos(y)*cos(y1)*cos(x - x1) + sin(y)*sin(y1))

    def interpolation(self, coords, scalestep=500):
        """Return list of coords as interpol. of two points [[x,y],[x1,y1]].
        COORDS points list [[x,y],[x1,y1]] (in degrees).
        SCALESTEP step (in km)."""
        x, y, x1, y1 = coords[0] + coords[1]
        scalestep = int(self.distance(coords) / scalestep)
        if not scalestep:
            return coords
        scale_dx = (x1 - x) / scalestep
        scale_dy = (y1 - y) / scalestep
        _x, _y = x, y
        interpol_pts = [[_x, _y]]
        for i in range(scalestep):
            _x += scale_dx
            _y += scale_dy
            interpol_pts += [[_x, _y]]
        return interpol_pts
