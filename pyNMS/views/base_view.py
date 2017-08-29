from collections import defaultdict
from graphical_objects.graphical_node import GraphicalNode
from graphical_objects.graphical_link import GraphicalLink
from graphical_objects.graphical_text import GraphicalText
from graphical_objects.graphical_rectangle import GraphicalRectangle
from miscellaneous.decorators import *
from objects.objects import *
from os.path import join
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class BaseView(QGraphicsView):
    
    link_color = {
    'ethernet link': QPen(QColor(0, 0, 255), 3),
    'optical link': QPen(QColor(212, 34, 42), 3),
    'optical channel': QPen(QColor(255, 130, 71), 3),
    'etherchannel': QPen(QColor(207, 34, 138), 3),
    'pseudowire': QPen(QColor(144, 43, 236), 3),
    'BGP peering': QPen(QColor(119, 235, 202), 3),
    'routed traffic': QPen(QColor(3, 139, 132), 3),
    'static traffic': QPen(QColor(0, 210, 0), 3),
    'l3vc': QPen(QColor(100, 100, 100), 3),
    'l2vc': QPen(QColor(200, 200, 200), 3)
    }
    
    selection_pen = QPen(QColor(Qt.red), 3)
        
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setRenderHint(QPainter.Antialiasing)
        # per-subtype display (True -> display, False -> don't display)
        self.display = dict.fromkeys(all_subtypes, True)
        # per-mode selection (nodes, links, shapes)
        self.selection = dict.fromkeys(self.controller.selection_panel.modes, True)
        
    ## Useful functions
    
    def is_node(self, item):
        return isinstance(item, GraphicalNode)
        
    def is_link(self, item):
        return isinstance(item, GraphicalLink)
        
    def get_items(self, objects):
        return map(lambda o: o.gobject[self], objects)
        
    def all_gnodes(self):
        return self.get_items(self.network.all_nodes())
        
    def all_glinks(self):
        return self.get_items(self.network.all_links())
        
    def get_obj(self, graphical_objects):
        return map(lambda gobject: gobject.object, graphical_objects)
        
    def selected_gnodes(self):
        return filter(self.is_node, self.scene.selectedItems())
        
    def selected_nodes(self):
        return self.get_obj(self.selected_gnodes())
        
    def selected_glinks(self):
        return filter(self.is_link, self.scene.selectedItems())
        
    def selected_links(self):
        return self.get_obj(self.selected_glinks())
    
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
            
    ## Mouse bindings

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            # activate rubberband for selection
            # by default, the rubberband is active for both clicks, we have to
            # deactivate it explicitly for the right-click
            if self.controller.mode == 'selection':
                self.setDragMode(QGraphicsView.RubberBandDrag)
            else:
                self.setDragMode(QGraphicsView.NoDrag)
                if self.controller.creation_mode == 'text':
                    text_item = GraphicalText(self)
                    text_item.setTextInteractionFlags(Qt.TextEditorInteraction)
                    text_item.setZValue(11)
                    self.scene.addItem(text_item)
                    text_item.setPos(self.mapToScene(event.pos()))
                elif self.controller.creation_mode == 'rectangle':
                    self.rectangle_item = GraphicalRectangle(self)
                    self.scene.addItem(self.rectangle_item)
                    self.rectangle_item.setZValue(11)
                    self.position = self.mapToScene(event.pos())
                    self.rectangle_item.setRect(self.position.x(), self.position.y(), 0, 0)
        if event.button() == Qt.RightButton:
            # when the right-click button is pressed, we don't know yet whether
            # the user wants to access the general right-click menu or move
            # the view
            # trigger_menu is set to True and will be set to False if the 
            # mouseMoveEvent binding is triggered
            self.trigger_menu = True
            self.cursor_pos = event.pos()
        super(BaseView, self).mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        position = self.mapToScene(event.pos())
        if event.buttons() == Qt.LeftButton:
            if hasattr(self, 'temp_line') and self.temp_line:  
                self.temp_line.setLine(QLineF(self.start_position, position))
            if hasattr(self, 'rectangle_item'):
                width, height = position.x() - self.position.x(), position.y() - self.position.y()
                self.rectangle_item.setRect(self.position.x(), self.position.y(), width, height)
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
            # text = self.scene.addSimpleText(
            #     '(%d, %d)' % (point.x(), point.y()))
            # text.setBrush(Qt.red)
            # text.setPos(point)
