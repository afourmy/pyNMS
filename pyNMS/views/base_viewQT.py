import pyproj
import shapefile
import shapely.geometry
import sys
from collections import defaultdict, OrderedDict
from objects.objects import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import (
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

class BaseView(QtWidgets.QGraphicsView):
    
    projections = {
    'mercator': pyproj.Proj(init='epsg:3395'),
    'spherical': pyproj.Proj('+proj=ortho +lon_0=28 +lat_0=47')
    }
    
    def __init__(self, parent):
        super(BaseView, self).__init__(parent)
        self.proj = 'spherical'
        self.ratio, self.offset = 1/10000, (0, 0)
        self.scene = QtWidgets.QGraphicsScene(self)
        self.temp_line = None
        self.start_pos = None
        self.setScene(self.scene)
        
        self.path_to_shapefile = 'C:/Users/minto/Desktop/pyGISS/shapefiles/World countries.shp'
        for polygon in self.create_polygon():
            self.scene.addItem(polygon)
        
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        
        earth = QtWidgets.QGraphicsEllipseItem(0, 0, 500, 500)
        self.scene.addItem(earth)
        
    def to_geographical_coordinates(self, x, y):
        px, py = (x - self.offset[0])/self.ratio, (self.offset[1] - y)/self.ratio
        return self.projections[self.proj](px, py, inverse=True)
        
    def to_canvas_coordinates(self, longitude, latitude):
        px, py = self.projections[self.proj](longitude, latitude)
        return px*self.ratio + self.offset[0], -py*self.ratio + self.offset[1]

    def create_polygon(self):
        sf = shapefile.Reader(self.path_to_shapefile)       
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
                    if px == 1e+26:
                        continue
                    qt_polygon.append(QtCore.QPointF(px, py))
                yield QtWidgets.QGraphicsPolygonItem(qt_polygon)

    def wheelEvent(self, event):
        factor = 1.25 if event.angleDelta().y() > 0 else 0.8
        self.scale(factor, factor)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/x-dnditemdata'):
            if event.source() == self:
                event.setDropAction(Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()

    dragMoveEvent = dragEnterEvent

    def dropEvent(self, event):
        if event.mimeData().hasFormat('application/x-dnditemdata'):
            itemData = event.mimeData().data('application/x-dnditemdata')
            dataStream = QtCore.QDataStream(itemData, QtCore.QIODevice.ReadOnly)

            pixmap = QPixmap()
            offset = QtCore.QPoint()
            dataStream >> pixmap >> offset

            newIcon = GraphicNode(pixmap, self)
            newIcon.setPos(event.pos())

    def mousePressEvent(self, event):
        pos = self.mapToScene(event.pos())
        print(self.to_geographical_coordinates(pos.x(), pos.y()))
        super(BaseView, self).mousePressEvent(event)
            
    # def mouseReleaseEvent(self, event):

   ##       for point in (start, end):
    #         text = self.scene.addSimpleText(
    #             '(%d, %d)' % (point.x(), point.y()))
    #         text.setBrush(QtCore.Qt.red)
    #         text.setPos(point)
            
    def mouseMoveEvent(self, event):
        currPos = self.mapToScene(event.pos())
        if event.buttons() == Qt.RightButton and self.temp_line:  
            self.temp_line.setLine(QtCore.QLineF(self.start, currPos))
            
        super(BaseView, self).mouseMoveEvent(event)

       ##   super(GraphicNode, self).mouseMoveEvent(event)
            
class Link(QtWidgets.QGraphicsLineItem):
    def __init__(self, qline):
        QtWidgets.QGraphicsLineItem.__init__(self, qline)
            
class GraphicNode(QtWidgets.QGraphicsPixmapItem):
    
    def __init__(self, pixmap, view):
        super().__init__(pixmap)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        
        self.view = view
        self.view.scene.addItem(self)
        
    def mousePressEvent(self, event):
        if event.buttons() == Qt.RightButton:
            self.view.start = pos = self.mapToScene(event.pos())
            self.view.temp_line = QGraphicsLineItem(QtCore.QLineF(pos, pos))
            self.view.scene.addItem(self.view.temp_line)
        super(GraphicNode, self).mousePressEvent(event)

        
class GraphicLink(QGraphicsLineItem):
    
    def __init__(self, source, destination):
        super(GraphicLink, self).__init__()
        self.source = source
        self.destination = destination
        print(self.source)