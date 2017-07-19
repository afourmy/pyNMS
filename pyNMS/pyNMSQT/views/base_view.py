import pyproj
import shapefile
import shapely.geometry
import sys
from collections import defaultdict, OrderedDict
from miscellaneous.decorators import *
from objects.objects import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class BaseView(QGraphicsView):
    
    projections = {
    'mercator': pyproj.Proj(init='epsg:3395'),
    'spherical': pyproj.Proj('+proj=ortho +lon_0=28 +lat_0=47')
    }
    
    def __init__(self, name, controller):
        super(BaseView, self).__init__(controller)
        self.name = name
        self.controller = controller
        self.scene = QGraphicsScene(self)
        self.temp_line = None
        self.start_pos = None
        self.setScene(self.scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setRenderHint(QPainter.Antialiasing)
        # activate rubberband for selection
        self.setDragMode(QGraphicsView.RubberBandDrag)
        # call the selection function when the selection changes
        self.scene.selectionChanged.connect(self.change_selection)
        
    def change_selection(self):
        for item in self.scene.selectedItems():
            print(item)
        
    def wheelEvent(self, event):
        factor = 1.25 if event.angleDelta().y() > 0 else 0.8
        self.scale(factor, factor)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/x-dnditemdata'):
            event.acceptProposedAction()

    dragMoveEvent = dragEnterEvent

    def dropEvent(self, event):
        pos = self.mapToScene(event.pos())
        if event.mimeData().hasFormat('application/x-dnditemdata'):
            item_data = event.mimeData().data('application/x-dnditemdata')
            dataStream = QtCore.QDataStream(item_data, QtCore.QIODevice.ReadOnly)
            pixmap, offset = QPixmap(), QtCore.QPoint()
            dataStream >> pixmap >> offset

            new_node = GraphicalNode(pixmap, self)
            new_node.setPos(pos - offset)

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if type(item) == GraphicalNode and event.buttons() == Qt.RightButton:
            self.start_node = item
            self.start_position = pos = self.mapToScene(event.pos())
            self.temp_line = QGraphicsLineItem(QtCore.QLineF(pos, pos))
            self.temp_line.setZValue(1)
            self.scene.addItem(self.temp_line)
            

        super(BaseView, self).mousePressEvent(event)
            
    def mouseReleaseEvent(self, event):
        item = self.itemAt(event.pos())
        print(isinstance(item, GraphicalNode), event.buttons() == Qt.RightButton)
        if (isinstance(item, GraphicalNode) and self.temp_line):
            self.end_node = item
            GraphicalLink(self)
        self.scene.removeItem(self.temp_line)
        self.temp_line = None
        if event.button() == Qt.RightButton:
            # here you do not call super hence the selection won't be cleared
            menu = QMenu(self)
            exitAction = QAction('&Exit', self)        
            exitAction.setShortcut('Ctrl+Q')
            exitAction.triggered.connect(lambda: _)
            menu.addAction(exitAction)
            menu.exec_(event.globalPos())
        super(BaseView, self).mouseReleaseEvent(event)

   ##       for point in (start, end):
    #         text = self.scene.addSimpleText(
    #             '(%d, %d)' % (point.x(), point.y()))
    #         text.setBrush(QtCore.Qt.red)
    #         text.setPos(point)
    

        # for item in self.scene().selectedItems():
        #     if isinstance(item, NodeItem):
        #         item.mouseRelease()

       ##   # If the left  mouse button is not still pressed TOGETHER with the SHIFT key and neither is the middle button
        # # this means the user is no longer trying to drag the view
        # if self._dragging and not (event.buttons() == QtCore.Qt.LeftButton and event.modifiers() == QtCore.Qt.ShiftModifier) and not event.buttons() & QtCore.Qt.MidButton:
        #     self._dragging = False
        #     self.setCursor(QtCore.Qt.ArrowCursor)
        # else:
        #     item = self.itemAt(event.pos())
        #     if item is not None and not event.modifiers() & QtCore.Qt.ControlModifier:
        #         item.setSelected(True)
        #     super().mouseReleaseEvent(eve
            
    def mouseMoveEvent(self, event):
        position = self.mapToScene(event.pos())
        if event.buttons() == Qt.RightButton and self.temp_line:  
            self.temp_line.setLine(QtCore.QLineF(self.start_position, position))

        super(BaseView, self).mouseMoveEvent(event)
                    
class Link(QGraphicsLineItem):
    def __init__(self, qline):
        QGraphicsLineItem.__init__(self, qline)
            
class GraphicalNode(QGraphicsPixmapItem):
    
    def __init__(self, pixmap, view):
        super().__init__(pixmap)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setZValue(3)
        self.view = view
        self.node = self.view.network.nf()
        self.view.scene.addItem(self)
        
    def mousePressEvent(self, event):
        super(GraphicalNode, self).mousePressEvent(event)
    #     
    # def mouseReleaseEvent(self, event):
    #     super(GraphicalNode, self).mouseReleaseEvent(event)
        
class GraphicalLink(QGraphicsLineItem):
    
    def __init__(self, view):
        # source and destination graphic nodes
        self.destination = view.end_node
        self.source = view.start_node
        print(self.source, self.destination)
        
        # # start / end positions of the link
        start_position = self.source.pos()
        end_position = self.destination.pos()

        super(GraphicalLink, self).__init__(QtCore.QLineF(start_position, end_position))
        self.setZValue(5)
        view.scene.addItem(self)
        
        self.link = view.network.lf(
                                    source = self.source.node, 
                                    destination = self.destination.node
                                    )
        print(self.source, self.destination)