from random import randint
from menus.selection_menu import BaseSelectionRightClickMenu
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
        self.selected_items = set()
    
        
    ## Useful functions
    def is_node(self, item):
        return isinstance(item, GraphicalNode)
        
    def is_link(self, item):
        return isinstance(item, GraphicalLink)
        
    ## Zoom system
    
    def wheelEvent(self, event):
        factor = 1.25 if event.angleDelta().y() > 0 else 0.8
        self.scale(factor, factor)
        
    ## Drag & Drop system
    
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
            
    ## Object deletion
    
    def remove_objects(self, *items):
        for item in items:
            obj = item.object
            self.scene.removeItem(item)
            # remove it from all AS it belongs to
            if hasattr(obj, 'AS'):
                for AS in list(obj.AS):
                    AS.management.remove_from_AS(obj)
            # remove it from the scene and the network model
            if self.is_node(item):
                for link in self.network.remove_node(obj):
                    self.remove_objects(link.glink)
            else:
                self.network.remove_link(obj)
            
    ## Mouse bindings

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        # activate rubberband for selection
        # by default, the rubberband is active for both clicks, we have to
        # deactivate it explicitly for the right-click
        if event.buttons() == Qt.LeftButton and self.controller.mode == 'selection':
            self.setDragMode(QGraphicsView.RubberBandDrag)
        else:
            self.setDragMode(QGraphicsView.NoDrag)
        item = self.itemAt(event.pos())
        if self.controller.mode == 'creation':
            if self.is_node(item) and event.buttons() == Qt.LeftButton:
                self.start_node = item
                self.start_position = pos = self.mapToScene(event.pos())
                self.temp_line = QGraphicsLineItem(QLineF(pos, pos))
                self.temp_line.setZValue(2)
                self.scene.addItem(self.temp_line)
        if event.button() == Qt.RightButton:
            self.cursor_pos = event.pos()
        super(BaseView, self).mousePressEvent(event)
            
    def mouseReleaseEvent(self, event):
        item = self.itemAt(event.pos())
        if self.temp_line:
            if self.is_node(item):
                self.end_node = item
                GraphicalLink(self)
            self.scene.removeItem(self.temp_line)
            self.temp_line = None
        elif event.button() == Qt.RightButton:
            # here you do not call super hence the selection won't be cleared
            menu = BaseSelectionRightClickMenu(self.controller)
            menu.exec_(event.globalPos())
        super(BaseView, self).mouseReleaseEvent(event)
        
    def mouseMoveEvent(self, event):
        position = self.mapToScene(event.pos())
        if event.buttons() == Qt.LeftButton and self.temp_line:  
            self.temp_line.setLine(QLineF(self.start_position, position))
        # sliding the scrollbar with the right-click button
        if event.buttons() == Qt.RightButton:
            offset = self.cursor_pos - event.pos()
            self.cursor_pos = event.pos()
            x_value = self.horizontalScrollBar().value() + offset.x()
            y_value = self.verticalScrollBar().value() + offset.y()
            self.horizontalScrollBar().setValue(x_value)
            self.verticalScrollBar().setValue(y_value)
        super(BaseView, self).mouseMoveEvent(event)
        
    ## Drawing functions
        
    def draw_objects(self, objects):
        for obj in objects:
            if obj.class_type == 'node' and not obj.gnode:
                GraphicalNode(self, obj)
            if obj.class_type == 'link' and not obj.glink:
                GraphicalLink(self, obj)
                
    def random_placement(self):
        for node in self.network.nodes.values():
            x, y = randint(0, 1000), randint(0, 1000)
            node.gnode.setPos(x, y)            

   ##       for point in (start, end):
    #         text = self.scene.addSimpleText(
    #             '(%d, %d)' % (point.x(), point.y()))
    #         text.setBrush(Qt.red)
    #         text.setPos(point)

                                
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
        self.object = self.node
        # we retrieve the pixmap based on the subtype to initialize a QGPI
        pixmap = view.controller.node_subtype_to_pixmap['default'][self.node.subtype]
        selection_pixmap = self.controller.node_subtype_to_pixmap['red'][self.node.subtype]
        self.pixmap = pixmap.scaled(
                                    QSize(100, 100), 
                                    Qt.KeepAspectRatio,
                                    Qt.SmoothTransformation
                                    )
        self.selection_pixmap = selection_pixmap.scaled(
                                                        QSize(100, 100), 
                                                        Qt.KeepAspectRatio,
                                                        Qt.SmoothTransformation
                                                        )
        super().__init__(self.pixmap)
        self.node.gnode = self
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges, True)
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
        
    def itemChange(self, change, value):
        if change == self.ItemSelectedHasChanged:
            if self.isSelected():
                self.setPixmap(self.selection_pixmap)
            else:
                self.setPixmap(self.pixmap)
        if change == self.ItemScenePositionHasChanged:
            for link in self.view.network.attached_links(self.node):
                link.glink.update_position()
        return QGraphicsPixmapItem.itemChange(self, change, value)
        
    def mousePressEvent(self, event):
        selection_allowed = self.controller.mode == 'selection'
        self.setFlag(QGraphicsItem.ItemIsSelectable, selection_allowed)
        self.setFlag(QGraphicsItem.ItemIsMovable, selection_allowed)
        # ideally, the menu should be triggered from the mouseReleaseEvent
        # binding, but for QT-related issues, the right-click filter does not
        # work in mouseReleaseEvent
        if event.buttons() == Qt.RightButton:
            menu = BaseSelectionRightClickMenu(self.controller)
            menu.exec_(QCursor.pos())
        super(GraphicalNode, self).mousePressEvent(event)
        
                
class GraphicalLink(QGraphicsLineItem):
    
    def __init__(self, view, link=None):
        super(GraphicalLink, self).__init__()
        self.controller = view.controller
        # self.setFlag(QGraphicsItem.ItemIsSelectable, True)
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
        self.object = self.link
        self.setZValue(2)
        self.update_position()
        view.scene.addItem(self)
        self.link.glink = self
        
    def mousePressEvent(self, event):
        selection_allowed = self.controller.mode == 'selection'
        self.setFlag(QGraphicsItem.ItemIsSelectable, selection_allowed)
        # ideally, the menu should be triggered from the mouseReleaseEvent
        # binding, but for QT-related issues, the right-click filter does not
        # work in mouseReleaseEvent
        if event.buttons() == Qt.RightButton:
            menu = BaseSelectionRightClickMenu(self.controller)
            menu.exec_(QCursor.pos())
        
    def update_position(self):
        start_position = self.source.pos()
        end_position = self.destination.pos()
        self.setLine(QLineF(start_position, end_position))