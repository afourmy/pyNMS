import re
from math import *    

# Tk color by RGB
rgb = lambda r, g, b: '#%02x%02x%02x' % (r, g, b)

class Map():
    """Main class."""
    # Public
    mopt = {
        '.Mainland':    {'cls': 'Polygon', 'fg': rgb(135,159,103), 'bg': rgb(135,159,103)},
        '.Water':       {'cls': 'Polygon', 'fg': rgb(90,140,190), 'bg': rgb(90,140,190)},
        '.Latitude':    {'cls': 'Line', 'fg': rgb(164,164,164), 'anchor': 'sw'},
        '.Longtitude':  {'cls': 'Line', 'fg': rgb(164,164,164), 'anchor': 'nw'},
        'Area':         {'cls': 'Polygon', 'fg': rgb(0,130,200), 'bg': ''},
    }
    
    delta = 3600.0
    halfX = 648000.0
    ylimit = 84
    mflood = []

    map_temp = {}
    
    def __init__(self, parent, **kw):
        # set of all map ids
        self.map_ids = set()
        self.scale = 0.05
        self.parent = parent
        self.dw = self.parent.cvs
        self.bg = kw.get('bg')
        self.viewportx = kw.get('viewportx', 360+180)
        self.viewporty = kw.get('viewporty', 180+90)
        self.mode = 'linear'
        self.change_projection(self.mode)

    def scale_map(self, ratio=1, docenter=1):
        """Change scale according previous value. Also Slider callback.
        DOCENTER (opt.) center when scaling {1 (default)|0}."""
        # remember visible center for center_point
        self.map_temp['center_x'] = (self.dw.xview()[0] + self.dw.xview()[1]) / 2.0
        self.map_temp['center_y'] = (self.dw.yview()[0] + self.dw.yview()[1]) / 2.0
        # calc ratio of current and previous scale
        self.scale *= float(ratio)
        # scale and center with ratio, show labels by new scale
        self.dw['scrollregion'] = (0, 0, self.scaleX * self.scale, self.scaleY * self.scale)
        self.dw.scale('all', 0, 0, ratio, ratio)
        if docenter:
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
        """Return meridians coords."""
        lonlat = []
        # X
        x = -180
        for x in range(-180, 181, 30):
            lon = []
            for y in range(-90, 91, 30):
                lon += [[x, y]]
            lonlat += [('.Longtitude', list(lon))]
        for y in range(-90, 91, 30):
            centerof = [-180, y]
            lat = [centerof]
            for x in range(-180, 181, 30):
                lat += [[x, y]]
                lonlat += [('.Latitude', list(lat))]
                label = centerof = None
                lat.pop(0)
        return lonlat
        
    def load_map(self, data=(), docenter=0):
        """Display objects. Use draw_map.
        DATA (opt.) list of list as (
            0 layer name from mopt,
            1 tag of object (unique within layer),
            2 string of coords as "((x1,y1),...,(xn,yn))"  (in degrees)"""
        for idx, row in enumerate(data):
            _row = dict([[i, x] for i, x in enumerate(row) if not x == None])
            ftype = _row[0]
            coords = _row[1]
            # save in mflood label, coords..
            self.mflood.append((coords, ftype))
            # draw object
            self.draw_map(coords, ftype)

    def center_point(self, x=None, y=None):
        # current view
        scrollX = self.dw.xview()
        scrollY = self.dw.yview()
        if x and y:
            # center by point
            moveX = x/(self.scaleX*self.scale) - (scrollX[1] - scrollX[0])/2.0
            moveY = y/(self.scaleY*self.scale) - (scrollY[1] - scrollY[0])/2.0
        else:
            # visible center
            moveX = self.map_temp['center_x'] - (scrollX[1] - scrollX[0]) / 2.0
            moveY = self.map_temp['center_y'] - (scrollY[1] - scrollY[0]) / 2.0
        self.dw.xview('moveto', moveX)
        self.dw.yview('moveto', moveY)

    def change_projection(self, mode='linear', centerof=None):
        mcenterof = []
        if not self.mode == mode:
            mcenterof = self.map_temp['centerof'] = (centerof or self.center_of())
        if mode == 'linear':   # linear
            self.scaleX = self.viewportx * self.delta
            self.scaleY = self.viewporty * self.delta
        elif 'mode' == 'mercator':    # mercator
            self.scaleX = self.viewportx * self.delta
            self.scaleY = self.to_mercator(90.0) * self.delta * self.viewporty/90.0
        else: # mode is globe
            self.scaleX = self.viewportx * self.delta
            self.scaleY = self.viewporty * self.delta
        self.halfX = self.scaleX / 2.0
        self.halfY = self.scaleY / 2.0
        self.mode = mode
        self.scale_map(docenter=0)
        self.draw_boundaries()
        for id in self.map_ids:
            self.dw.delete(id)

        for coords, ftype in self.mflood:
            self.draw_map(coords, ftype)
            
        if mcenterof:
            self.centerCarta(mcenterof)

    def centerCarta(self, centerof=[[0,0]]):
        """Center map by point.
        CENTEROF list of point coords [[x,y]] (in degrees)."""
        pts = self.to_points(centerof, doscale=1)
        if pts:
            self.center_point(*pts)

    def draw_boundaries(self):
        """Draw Sphere radii bounds."""
        self.dw.delete('sphereBounds')
        if self.is_spherical():
            radii = 180 / pi * self.delta * self.scale
            vx, vy = self.scaleX * self.scale, self.scaleY * self.scale
            self.oval_id = self.dw.create_oval(
                                vx/2.0 - radii, 
                                vy/2.0 - radii, 
                                vx/2.0 + radii, 
                                vy/2.0 + radii,
                                outline=self.mopt['.Latitude']['fg'], 
                                fill=self.mopt['.Water']['bg'], 
                                tags=('water', 'sphereBounds')
                                )

    def draw_map(self, coords, ftype):
        # interpolate coords for Globe projection
        _coords = []
        if self.is_spherical():
            for i in range(len(coords) - 1):
                _coords += self.interpolation(coords[i:i + 2])
        if not _coords:
            _coords = coords

        points = self.to_points(_coords, doscale=1)
        
        if not points:
            return

        if self.mopt[ftype]['cls'] in ('Line'):
            if len(points) < 4:
                points = points * 2
            obj_id = self.dw.create_line(points, fill='black', 
                                dash=self.mopt[ftype].get('dash'), smooth=self.mopt[ftype].get('smooth'), 
                                width=self.mopt[ftype].get('width', 1), tags=(ftype,))
        else: 
            # polygon
            if len(points) < 4:
                points = points * 2
            obj_id = self.dw.create_polygon(points, fill='green', outline='black', tags=(ftype,))
        self.map_ids.add(obj_id)
                                
    def load_shp_file(self, data=(), docenter=0):
        # display WKT-objects. Use loadCarta.
        _data = []
        for row in data:
            _row = dict([[i, x] for i, x in enumerate(row)])
            try:
                tp, e = self.from_WKT(_row[1])
            except: 
                return
            for i2, coords2 in enumerate(e):
                for i, coords in enumerate(coords2):
                    _data += [('Area', coords)]
        if _data:
            self.load_map(_data, docenter)
            
    def from_WKT(self, wkt):
        # wkt-string -> list of coords

        r = '(-?\\d+\\.?\\d*)[ \t]+[ \t]*(-?\\d+\\.?\\d*)'
        r1 = '((?:POLYGON|MULTIPOLYGON)[^a-zA-Z]+)'

        wkt = wkt.replace("(", "[").replace(")", "]")
        tp = wkt[:wkt.find(" ")]

        try:
            e = eval(re.sub(r, '[\\1,\\2]', wkt[wkt.find("["):]))
        except: 
            return


        if tp == 'POLYGON':
            return tp, [e]
        if tp == 'MULTIPOLYGON':
            return tp, e

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
        return [self.scaleX, self.scaleY]

    def viewsizeOf(self):
        """Return rect. of visible area (in points)."""
        left, right = [self.scaleX * self.scale * x for x in self.dw.xview()]
        top, bottom = [self.scaleY * self.scale * y for y in self.dw.yview()]
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
        """Return list of two `points` for Spherical projection.
        COORDS coords list [x,y] (in degrees)."""
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
        z = asinz( rh / 1 )
        sinz = sin( z )
        cosz = cos( z )
        lon = center_x
        if ( abs(rh) <= EPSLN ):
            lat = center_y
        lat = asinz( cosz * sin_p14 + (y * sinz * cos_p14) / rh )
        con = abs(center_y) - pi / 2.0
        if ( abs(con) <= EPSLN ):
            if ( center_y >= EPSLN ):
                lon = adjust_lon( center_x + atan2(x, y) )
            else:
                lon = adjust_lon( center_x - atan2(-x, y) )
        con = cosz - sin_p14 * sin(lat)
        if ((abs(con) >= EPSLN) or (abs(x) >= EPSLN)):
            lon = adjust_lon(center_x + atan2((x * sinz * cos_p14), (con * rh)));
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
