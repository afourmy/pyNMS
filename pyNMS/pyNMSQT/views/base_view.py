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
        
        # call the selection function when the selection changes
        self.scene.selectionChanged.connect(self.change_selection)
        
    def change_selection(self):
        pass
        
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
            dataStream = QDataStream(item_data, QIODevice.ReadOnly)
            pixmap, offset = QPixmap(), QPoint()
            dataStream >> pixmap >> offset
            new_node = GraphicalNode(self)
            new_node.setPos(pos - offset)

    def mousePressEvent(self, event):
        # activate rubberband for selection
        # by default, the rubberband is active for both clicks, we have to
        # deactivate it explicitly for the right-click
        if event.buttons() == Qt.LeftButton and self.controller.mode == 'selection':
            self.setDragMode(QGraphicsView.RubberBandDrag)
        else:
            self.setDragMode(QGraphicsView.NoDrag)
        item = self.itemAt(event.pos())
        if self.controller.mode == 'creation':
            if type(item) == GraphicalNode and event.buttons() == Qt.LeftButton:
                self.start_node = item
                self.start_position = pos = self.mapToScene(event.pos())
                self.temp_line = QGraphicsLineItem(QLineF(pos, pos))
                self.temp_line.setZValue(2)
                self.scene.addItem(self.temp_line)
        super(BaseView, self).mousePressEvent(event)
            
    def mouseReleaseEvent(self, event):
        item = self.itemAt(event.pos())
        if self.temp_line:
            if isinstance(item, GraphicalNode):
                self.end_node = item
                GraphicalLink(self)
            self.scene.removeItem(self.temp_line)
            self.temp_line = None
        elif event.button() == Qt.RightButton:
            # here you do not call super hence the selection won't be cleared
            menu = QMenu(self)
            exitAction = QAction('&Exit', self)        
            exitAction.setShortcut('Ctrl+Q')
            exitAction.triggered.connect(lambda: _)
            menu.addAction(exitAction)
            menu.exec_(event.globalPos())
        super(BaseView, self).mouseReleaseEvent(event)
        
    def draw_objects(self, objects):
        for obj in objects:
            if obj.class_type == 'node' and not obj.gnode:
                print(obj, type(obj))
                GraphicalNode(self, obj)
            if obj.class_type == 'link' and not obj.glink:
                    GraphicalLink(self, obj)
            
        

   ##       for point in (start, end):
    #         text = self.scene.addSimpleText(
    #             '(%d, %d)' % (point.x(), point.y()))
    #         text.setBrush(Qt.red)
    #         text.setPos(point)
    


        #     self.setCursor(Qt.ArrowCursor)

            
    def mouseMoveEvent(self, event):
        position = self.mapToScene(event.pos())
        if event.buttons() == Qt.LeftButton and self.temp_line:  
            self.temp_line.setLine(QLineF(self.start_position, position))

        super(BaseView, self).mouseMoveEvent(event)
                                
class GraphicalNode(QGraphicsPixmapItem):
    
    def __init__(self, view, node=None):
        self.view = view
        self.controller = view.controller
        # if node is not defined, it means the node is created with the 
        # drag & drop system, which implies that: 
        # - the subtype is the value of creation_mode
        # the node object does not yet exist: it must be created
        if not node:
            subtype = self.controller.creation_mode
            self.node = self.view.network.nf(subtype=subtype)
        else:
            self.node = node
        # we retrieve the pixmap based on the subtype to initialize a QGPI
        pixmap = view.controller.node_subtype_to_pixmap['default'][self.node.subtype]
        pixmap = pixmap.scaled(
                        QSize(100, 100), 
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                        )
        super().__init__(pixmap)
        self.node.gnode = self
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setOffset(
                       QPointF(
                               -self.boundingRect().width()/2, 
                               -self.boundingRect().height()/2
                               )
                       )
        self.setZValue(3)
        self.view.scene.addItem(self)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        # if node:
        #     self.setPos(QPoint(0, 0))
        
    def mousePressEvent(self, event):
        selection_allowed = self.controller.mode == 'selection'
        self.setFlag(QGraphicsItem.ItemIsSelectable, selection_allowed)
        self.setFlag(QGraphicsItem.ItemIsMovable, selection_allowed)
        super(GraphicalNode, self).mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        for item in self.view.scene.selectedItems():
            if isinstance(item, GraphicalNode):
                for link in self.view.network.attached_links(item.node):
                    link.glink.update_position()
        super(GraphicalNode, self).mouseMoveEvent(event)
        
class GraphicalLink(QGraphicsLineItem):
    
    def __init__(self, view, link=None):
        super(GraphicalLink, self).__init__()
        # source and destination graphic nodes
        if link:
            self.link = link
            self.source = link.source.gnode
            self.destination = link.destination.gnode
        else:
            self.destination = view.end_node
            self.source = view.start_node
            self.link = view.network.lf(
                                        subtype = view.controller.creation_mode,
                                        source = self.source.node, 
                                        destination = self.destination.node
                                        )
        self.setZValue(2)
        self.update_position()
        view.scene.addItem(self)
        self.link.glink = self
        
    def update_position(self):
        start_position = self.source.pos()
        end_position = self.destination.pos()
        self.setLine(QLineF(start_position, end_position))