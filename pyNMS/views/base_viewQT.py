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
        self.proj = 'mercator'
        self.ratio, self.offset = 1, (0, 0)
        self.scene = QtWidgets.QGraphicsScene(self)
        
        
        self.path_to_shapefile = 'C:/Users/minto/Desktop/pyGISS/shapefiles/World countries.shp'
        for polygon in self.create_polygon():
            self.scene.addItem(polygon)
        self.setScene(self.scene)
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
                    if px == 1e+30:
                        continue
                    qt_polygon.append(QtCore.QPointF(px/10000, py/10000))
                yield QtWidgets.QGraphicsPolygonItem(qt_polygon)

    def wheelEvent(self, event):
        factor = 1.25 if event.angleDelta().y() > 0 else 0.8
        self.scale(factor, factor)
        self.ratio *= float(factor)
        self.offset = (self.offset[0]*factor + event.x()*(1 - factor), 
                       self.offset[1]*factor + event.y()*(1 - factor))
        
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

            newIcon = DragLabel(self)
            # newIcon.setPixmap(pixmap)
            newIcon.move(event.pos() - offset)
            # newIcon.show()
            # newIcon.setAttribute(Qt.WA_DeleteOnClose)

            if event.source() == self:
                event.setDropAction(Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()

    def mousePressEvent(self, event):
        
        # retrieve the label 
        child = self.childAt(event.pos())
        if not child:
            return
            
class DragLabel(QLabel):
    
    def __init__(self, parent):
        super().__init__(parent)
        
        pixmap = QPixmap('C:\\Users\minto\\Desktop\\pyGISS\\node.png')
        pixmap = pixmap.scaled(65, 65, Qt.KeepAspectRatio)
        self.setPixmap(pixmap)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.show()

    def mousePressEvent(self, event):
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()

        super(DragLabel, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self.__mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)
            self.move(newPos)

            self.__mouseMovePos = globalPos

        super(DragLabel, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos 
            if moved.manhattanLength() > 3:
                event.ignore()
                return

        super(DragLabel, self).mouseReleaseEvent(event)