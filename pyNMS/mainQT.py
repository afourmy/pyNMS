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

import sys
from inspect import stack
from os.path import abspath, dirname, join, pardir

# prevent python from writing *.pyc files / __pycache__ folders
sys.dont_write_bytecode = True

path_app = dirname(abspath(stack()[0][1]))

if path_app not in sys.path:
    sys.path.append(path_app)
    
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


class PhotoViewer(QtWidgets.QGraphicsView):
    
    projections = {
    'mercator': pyproj.Proj(init='epsg:3395'),
    'spherical': pyproj.Proj('+proj=ortho +lon_0=28 +lat_0=47')
    }
    
    def __init__(self, parent):
        super(PhotoViewer, self).__init__(parent)
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
        
    # def mousePressEvent(self, event):
    #     print(*self.to_geographical_coordinates(event.x(), event.y()))
        
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

            newIcon = QLabel(self)
            newIcon.setPixmap(pixmap)
            newIcon.move(event.pos() - offset)
            newIcon.show()
            newIcon.setAttribute(Qt.WA_DeleteOnClose)

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


class Controller(QWidget):
    def __init__(self, path_app):
        super(Controller, self).__init__()

        # initialize all paths
        self.path_app = path_app
        path_parent = abspath(join(path_app, pardir))
        self.path_icon = join(path_parent, 'Icons')
        self.path_workspace = join(path_parent, 'Workspace')
        self.path_shapefiles = join(path_parent, 'Shapefiles')
        
        # node creation menu
        self.node_creation_menu = NodeCreationMenu(self)
        
        self.viewer = PhotoViewer(self)
        self.edit = QtWidgets.QLineEdit(self)
        self.edit.setReadOnly(True)
        self.button = QtWidgets.QToolButton(self)
        self.button.setText('...')
        self.button.clicked.connect(self.handleOpen)
        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(self.viewer, 0, 1, 1, 2)
        layout.addWidget(self.edit, 1, 1, 1, 1)
        layout.addWidget(self.button, 1, 2, 1, 1)
        layout.addWidget(self.node_creation_menu, 0, 0, 1, 1) 

    def handleOpen(self):
        path = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Choose Image', self.edit.text())
        if path:
            self.edit.setText(path)
            self.viewer.setPhoto(QtGui.QPixmap(path))
            
class NodeCreationMenu(QGroupBox):
    def __init__(self, controller):
        super(NodeCreationMenu, self).__init__(controller)
        self.setTitle('Node creation')

        self.setMinimumSize(300, 300)
        self.setAcceptDrops(True)

        node_subtype_to_pixmap = defaultdict(OrderedDict)
        for color in ('default', 'red', 'purple'):
            for subtype in node_subtype:
                path = join(controller.path_icon, ''.join((
                                                            color, 
                                                            '_', 
                                                            subtype, 
                                                            '.gif'
                                                            )))
                node_subtype_to_pixmap[color][subtype] = QPixmap(path)
                
        # exit connection lost because of the following lines
        layout = QtWidgets.QGridLayout(self)
        for index, image in enumerate(node_subtype_to_pixmap['default'].values()):
            label = QLabel(self)
            label.setPixmap(image.scaled(
                                        label.size(), 
                                        Qt.KeepAspectRatio,
                                        Qt.SmoothTransformation
                                        ))
            label.show()
            label.setAttribute(Qt.WA_DeleteOnClose)
            layout.addWidget(label, index // 4, index % 4, 1, 1)
            
    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('application/x-dnditemdata'):
            if event.source() == self:
                event.setDropAction(Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()

    dragEnterEvent = dragMoveEvent

    def mousePressEvent(self, event):
        
        # retrieve the label 
        child = self.childAt(event.pos())
        if not child:
            return

        pixmap = QPixmap(child.pixmap())

        itemData = QtCore.QByteArray()
        dataStream = QtCore.QDataStream(itemData, QtCore.QIODevice.WriteOnly)
        dataStream << pixmap << QtCore.QPoint(event.pos() - child.pos())

        mimeData = QtCore.QMimeData()
        mimeData.setData('application/x-dnditemdata', itemData)

        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos() - child.pos())

        if drag.exec_(Qt.CopyAction | Qt.MoveAction, Qt.CopyAction) == Qt.MoveAction:
            child.close()
        else:
            child.show()
            child.setPixmap(pixmap)

if str.__eq__(__name__, '__main__'):
    app = QApplication(sys.argv)
    controller = Controller(path_app)
    controller.setGeometry(100, 100, 1500, 800)
    controller.show()
    sys.exit(app.exec_())