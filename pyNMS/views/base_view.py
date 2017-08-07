from collections import defaultdict
from .graphical_items import *
from right_click_menus.network_general_menu import NetworkGeneralMenu
from miscellaneous.decorators import *
from objects.objects import *
from os.path import join
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class BaseView(QGraphicsView):
    
    link_color = {
    'ethernet link': QPen(QColor(0, 0, 255), 3),
    'optical link': QPen(QColor(207, 34, 138), 3),
    'optical channel': QPen(QColor(93, 188, 210), 3),
    'etherchannel': QPen(QColor(212, 34, 42), 3),
    'pseudowire': QPen(QColor(144, 43, 236), 3),
    'BGP peering': QPen(QColor(119, 235, 202), 3),
    'routed traffic': QPen(QColor(3, 139, 132), 3),
    'static traffic': QPen(QColor(0, 210, 0), 3)
    }
        
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setRenderHint(QPainter.Antialiasing)
        # per-subtype display (True -> display, False -> don't display)
        self.display = dict.fromkeys(all_subtypes, True)
        
    ## Useful functions
    
    def is_node(self, item):
        return isinstance(item, GraphicalNode)
        
    def is_link(self, item):
        return isinstance(item, GraphicalLink)
        
    def get_items(self, objects):
        return map(lambda n: n.gobject, objects)
        
    def all_gnodes(self):
        return self.get_items(self.network.nodes.values())
        
    def get_obj(self, graphical_objects):
        return map(lambda gobject: gobject.object, graphical_objects)
        
    def selected_nodes(self):
        return filter(self.is_node, self.scene.selectedItems())
        
    def selected_links(self):
        return filter(self.is_link, self.scene.selectedItems())
    
    def filter(self, type, *subtypes):
        return self.get_items(self.network.ftr(type, *subtypes))
        
    ## Zoom system

    def zoom_in(self):
        self.scale(1.25, 1.25)
        
    def zoom_out(self):
        self.scale(1/1.25, 1/1.25)
        
    def wheelEvent(self, event):
        self.zoom_in() if event.angleDelta().y() > 0 else self.zoom_out()
        
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
        if event.button() == Qt.RightButton:
            # when the right-click button is pressed, we don't know yet whether
            # the user wants to access the general right-click menu or move
            # the view
            # trigger_menu is set to True and will be set to False if the 
            # mouseMoveEvent binding is triggered
            self.trigger_menu = True
            self.cursor_pos = event.pos()
        super(BaseView, self).mousePressEvent(event)
            
    def mouseReleaseEvent(self, event):
        item = self.itemAt(event.pos())
        if hasattr(self, 'temp_line') and self.temp_line:
            if self.is_node(item):
                self.end_node = item
                GraphicalLink(self)
                # we made the start node unselectable and unmovable to enable
                # the creation of links, in the press binding of GraphicalNode: 
                # we revert this change at link creation
                self.start_node.setFlag(QGraphicsItem.ItemIsSelectable, True)
                self.start_node.setFlag(QGraphicsItem.ItemIsMovable, True)
            self.scene.removeItem(self.temp_line)
            self.temp_line = None
        if event.button() == Qt.RightButton and self.trigger_menu:
            if not self.is_node(item) and not self.is_link(item): 
                menu = NetworkGeneralMenu(event, self.controller)
                menu.exec_(event.globalPos())
        super(BaseView, self).mouseReleaseEvent(event)
        
    def mouseMoveEvent(self, event):
        position = self.mapToScene(event.pos())
        if event.buttons() == Qt.LeftButton:
            if hasattr(self, 'temp_line') and self.temp_line:  
                self.temp_line.setLine(QLineF(self.start_position, position))
        # sliding the scrollbar with the right-click button
        if event.buttons() == Qt.RightButton:
            self.trigger_menu = False
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
            
    ## Alignment and distribution functions
    
    def align(self, nodes, horizontal=True):
        # alignment can be either horizontal (h is True) or vertical
        minimum = min(node.y if horizontal else node.x for node in nodes)
        for node in nodes:
            setattr(node, 'y'*horizontal or 'x', minimum)
            
    def distribute(self, nodes, horizontal=True):
        # uniformly distribute the nodes between the minimum and
        # the maximum lontitude/latitude of the selection
        minimum = min(node.x if horizontal else node.y for node in nodes)
        maximum = max(node.x if horizontal else node.y for node in nodes)
        # we'll use a sorted list to keep the same order after distribution
        nodes = sorted(nodes, key=lambda n: getattr(n, 'x'*horizontal or 'y'))
        offset = (maximum - minimum)/(len(nodes) - 1)
        for idx, node in enumerate(nodes):
            setattr(node, 'x'*horizontal or 'y', minimum + idx*offset)
            
    ## Selection of objects
    
    def select(self, *objects):
        for obj in objects:
            obj.setSelected(True)
        
    ## Change display
    
    def per_subtype_display(self, subtype):
        self.display[subtype] = not self.display[subtype]
        type = subtype_to_type[subtype]
        for item in self.filter(type, subtype):
            item.show() if self.display[subtype] else item.hide()
    
    def refresh_display(self):
        pass

   ##       for point in (start, end):
    #         text = self.scene.addSimpleText(
    #             '(%d, %d)' % (point.x(), point.y()))
    #         text.setBrush(Qt.red)
    #         text.setPos(point)
