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

            new_node = GraphicalNode(pixmap, self)
            new_node.setPos(pos - offset)

    def mousePressEvent(self, event):
        # activate rubberband for selection
        # by default, the rubberband is active for both clicks, we have to
        # deactivate it explicitly for the right-click
        if event.buttons() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.RubberBandDrag)
        if event.buttons() == Qt.RightButton:
            self.setDragMode(QGraphicsView.NoDrag)
        item = self.itemAt(event.pos())
        if type(item) == GraphicalNode and event.buttons() == Qt.RightButton:
            self.start_node = item
            self.start_position = pos = self.mapToScene(event.pos())
            self.temp_line = QGraphicsLineItem(QLineF(pos, pos))
            self.temp_line.setZValue(1)
            self.scene.addItem(self.temp_line)
        super(BaseView, self).mousePressEvent(event)
            
    def mouseReleaseEvent(self, event):
        item = self.itemAt(event.pos())
        if isinstance(item, GraphicalNode) and self.temp_line:
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

   ##       for point in (start, end):
    #         text = self.scene.addSimpleText(
    #             '(%d, %d)' % (point.x(), point.y()))
    #         text.setBrush(Qt.red)
    #         text.setPos(point)
    


        #     self.setCursor(Qt.ArrowCursor)

            
    def mouseMoveEvent(self, event):
        position = self.mapToScene(event.pos())
        if event.buttons() == Qt.RightButton and self.temp_line:  
            self.temp_line.setLine(QLineF(self.start_position, position))

        super(BaseView, self).mouseMoveEvent(event)
                                
class GraphicalNode(QGraphicsPixmapItem):
    
    def __init__(self, pixmap, view):
        super().__init__(pixmap)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setOffset(QPointF(-self.boundingRect().width()/2, -self.boundingRect().height()/2))
        self.setZValue(3)
        self.view = view
        self.node = self.view.network.nf()
        self.view.scene.addItem(self)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        
    def mouseMoveEvent(self, event):
        for item in self.view.scene.selectedItems():
            if isinstance(item, GraphicalNode):
                for link in self.view.network.attached_links(item.node):
                    link.glink.update_position()
        super(GraphicalNode, self).mouseMoveEvent(event)
        
class GraphicalLink(QGraphicsLineItem):
    
    def __init__(self, view):
        super(GraphicalLink, self).__init__()
        # source and destination graphic nodes
        self.destination = view.end_node
        self.source = view.start_node
        self.setZValue(5)
        self.update_position()
        view.scene.addItem(self)

        self.link = view.network.lf(
                                    source = self.source.node, 
                                    destination = self.destination.node
                                    )
        self.link.glink = self
        
    def update_position(self):
        # # start / end positions of the link
        start_position = self.source.pos()
        end_position = self.destination.pos()
        self.setLine(QLineF(start_position, end_position))