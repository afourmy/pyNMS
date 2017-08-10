# Copyright (C) 2017 Antoine Fourmy <antoine dot fourmy at gmail dot com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import warnings
from collections import OrderedDict
from os.path import join
from .base_view import BaseView
from math import *
from miscellaneous.decorators import overrider
try:
    import shapefile
    import shapely.geometry
    from pyproj import Proj
except ImportError:
    warnings.warn('SHP librairies missing: map import disabled')
    
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import (
                         QBrush,
                         QColor, 
                         QDrag, 
                         QPainter, 
                         QPixmap
                         )
from PyQt5.QtWidgets import (
                             QFrame,
                             QPushButton, 
                             QWidget, 
                             QApplication, 
                             QLabel, 
                             QGraphicsItem,
                             QGraphicsLineItem,
                             QGraphicsPixmapItem,
                             QGroupBox,
                             )

class GeographicalView(BaseView):

    def __init__(self, controller):
        super().__init__(controller)
        
        # initialize the map 
        self.world_map = Map(self)
                            
    def update_geographical_coordinates(self, *gnodes):
        for gnode in gnodes:
            lon, lat = self.world_map.to_geographical_coordinates(gnode.x, gnode.y)
            gnode.node.longitude, gnode.node.latitude = lon, lat
            
    def update_logical_coordinates(self, *gnodes):
        for gnode in gnodes:
            gnode.node.logical_x, gnode.node.logical_y = gnode.x, gnode.y 
            
    def move_to_geographical_coordinates(self, *gnodes):
        if not gnodes:
            gnodes = self.all_gnodes()
        for gnode in gnodes:
            gnode.x, gnode.y = self.world_map.to_canvas_coordinates(
                                    gnode.node.longitude, 
                                    gnode.node.latitude
                                    )
        
    def move_to_logical_coordinates(self, *gnodes):
        if not gnodes:
            gnodes = self.all_gnodes()
        for gnode in gnodes:
            gnode.x, gnode.y = gnode.node.logical_x, gnode.node.logical_y
        
    def haversine_distance(self, s, d):
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
                
class Map():

    projections = OrderedDict([
    ('spherical', Proj('+proj=ortho +lat_0=47 +lon_0=28')),
    ('mercator', Proj(init='epsg:3395')),
    ('wgs84', Proj(init='epsg:3857')),
    ('3035', Proj("+init=EPSG:3035")),
    ('3947', Proj("+init=EPSG:3947"))
    ])
    
    def __init__(self, view):
        self.view = view
        self.proj = 'spherical'
        self.ratio, self.offset = 1/100, (0, 0)
        self.shapefile = join(self.view.controller.path_shapefiles, 'World countries.shp')
        self.display = True
        
        # brush for water and lands
        self.water_brush = QBrush(QColor(64, 164, 223))
        self.land_brush = QBrush(QColor(52, 165, 111))
        
        # draw the map 
        self.polygons = self.view.scene.createItemGroup(self.draw_polygons())
        self.draw_water()
        
    def to_geographical_coordinates(self, x, y):
        px, py = (x - self.offset[0])/self.ratio, (self.offset[1] - y)/self.ratio
        return self.projections[self.proj](px, py, inverse=True)
        
    def to_canvas_coordinates(self, longitude, latitude):
        px, py = self.projections[self.proj](longitude, latitude)
        return px*self.ratio + self.offset[0], -py*self.ratio + self.offset[1]
                
    def draw_water(self):
        if self.proj == 'spherical':
            # draw the planet
            cx, cy = self.to_canvas_coordinates(28, 47)
            R = 6371000*self.ratio
            earth_water = QtWidgets.QGraphicsEllipseItem(cx - R, cy - R, 2*R, 2*R)
            earth_water.setZValue(0)
            earth_water.setBrush(self.water_brush)
            self.polygons.addToGroup(earth_water)
        else:
            pass
            
    def draw_polygons(self):
        sf = shapefile.Reader(self.shapefile)       
        polygons = sf.shapes() 
        for polygon in polygons:
            # convert shapefile geometries into shapely geometries
            # to extract the polygons of a multipolygon
            polygon = shapely.geometry.shape(polygon)
            # if it is a polygon, we use a list to make it iterable
            if polygon.geom_type == 'Polygon':
                polygon = [polygon]
            for land in polygon:
                qt_polygon = QtGui.QPolygonF() 
                land = str(land)[10:-2].replace(', ', ',').replace(' ', ',')
                coords = land.replace('(', '').replace(')', '').split(',')
                for lon, lat in zip(coords[0::2], coords[1::2]):
                    px, py = self.to_canvas_coordinates(lon, lat)
                    if px > 1e+10:
                        continue
                    qt_polygon.append(QtCore.QPointF(px, py))
                polygon_item = QtWidgets.QGraphicsPolygonItem(qt_polygon)
                polygon_item.setBrush(self.land_brush)
                polygon_item.setZValue(1)
                yield polygon_item
                
    def show_hide_map(self):
        self.display = not self.display
        self.polygons.show() if self.display else self.polygons.hide()
        
    def delete_map(self):
        self.view.scene.removeItem(self.polygons)
            
    def redraw_map(self):
        self.delete_map()
        self.polygons = self.view.scene.createItemGroup(self.draw_polygons())
        self.draw_water()
