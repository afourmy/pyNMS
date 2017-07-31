from collections import defaultdict
from random import randint
from math import sqrt
from right_click_menus.network_selection_menu import NetworkSelectionMenu
from right_click_menus.network_general_menu import NetworkGeneralMenu
from miscellaneous.graph_drawing import SpringLayoutParametersWindow
from miscellaneous.decorators import *
from objects.objects import *
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
        
    def __init__(self, name, controller):
        super(BaseView, self).__init__(controller)
        self.name = name
        self.controller = controller
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setRenderHint(QPainter.Antialiasing)
        
        # temporary line displayed at link creation
        self.temp_line = None
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
    
    #TODO add icon in the toolbar
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
        item = self.itemAt(event.pos())
        if self.controller.mode == 'creation':
            if self.is_node(item) and event.buttons() == Qt.LeftButton:
                self.start_node = item
                self.start_position = pos = self.mapToScene(event.pos())
                self.temp_line = QGraphicsLineItem(QLineF(pos, pos))
                self.temp_line.setZValue(2)
                self.scene.addItem(self.temp_line)
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
        if self.temp_line:
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
        if event.buttons() == Qt.LeftButton and self.temp_line:  
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
                
    def random_layout(self):
        for gnode in self.node_selection:
            x, y = randint(0, 1000), randint(0, 1000)
            gnode.setPos(x, y)  
            
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
            
    ## Force-directed layout algorithms
    
    def distance(self, p, q): 
        return sqrt(p*p + q*q)
    
    ## 1) Eades algorithm (spring layout)
    
    # We use the following constants:
    # - k is the spring constant (stiffness of the spring)
    # - L0 is the equilibrium length
    # - cf is the Coulomb factor (repulsive force factor)
    # - sf is the speed factor
    
    def coulomb_force(self, dx, dy, distance, cf):
        c = distance and cf/distance**3
        return (-c*dx, -c*dy)
        
    def hooke_force(self, dx, dy, distance, L0, k):
        const = distance and k*(distance - L0)/distance
        return (const*dx, const*dy)
            
    def spring_layout(self, cf, k, sf, L0):
        for nodeA in self.node_selection:
            Fx = Fy = 0
            neighbors = set(map(lambda n: n.gnode, self.network.neighbors(nodeA.node, 'plink')))
            for nodeB in self.node_selection | neighbors:
                if nodeA != nodeB:
                    dx, dy = nodeB.x - nodeA.x, nodeB.y - nodeA.y
                    distance = self.distance(dx, dy)
                    F_hooke = (0,)*2
                    if self.network.is_connected(nodeA.node, nodeB.node, 'plink'):
                        F_hooke = self.hooke_force(dx, dy, distance, L0, k)
                    F_coulomb = self.coulomb_force(dx, dy, distance, cf)
                    Fx += F_hooke[0] + F_coulomb[0]
                    Fy += F_hooke[1] + F_coulomb[1]
            nodeA.vx = max(-100, min(100, 0.5 * nodeA.vx + 0.2 * Fx))
            nodeA.vy = max(-100, min(100, 0.5 * nodeA.vy + 0.2 * Fy))
    
        for node in self.node_selection:
            node.x, node.y = node.x + node.vx*sf, node.y + node.vy*sf
            
    ## 2) Fruchterman-Reingold algorithm
    
    def fa(self, d, k):
        return (d**2)/k
    
    def fr(self, d, k):
        return -(k**2)/d
        
    def fruchterman_reingold_layout(self, limit=False, opd=0):
        t = 1
        if not opd:
            try:
                opd = sqrt(500*500/len(self.node_selection))
            except ZeroDivisionError:
                return
        for nodeA in self.node_selection:
            nodeA.vx, nodeA.vy = 0, 0
            for nodeB in self.node_selection:
                if nodeA != nodeB:
                    dx, dy = nodeA.x - nodeB.x, nodeA.y - nodeB.y
                    distance = self.distance(dx, dy)
                    if distance:
                        nodeA.vx += (dx*opd**2)/distance**2
                        nodeA.vy += (dy*opd**2)/distance**2
                    
        for link in self.network.plinks.values():
            source, destination = link.source.gnode, link.destination.gnode
            dx, dy = source.x - destination.x, source.y - destination.y
            distance = self.distance(dx, dy)
            if distance:
                link.source.gnode.vx -= distance*dx/opd
                link.source.gnode.vy -= distance*dy/opd
                link.destination.gnode.vx += distance*dx/opd
                link.destination.gnode.vy += distance*dy/opd
            
        for node in self.node_selection:
            distance = self.distance(node.vx, node.vy)
            node.x += node.vx/sqrt(distance)
            node.y += node.vy/sqrt(distance)
            
        t *= 0.95
        
    def igraph_test(self):
        pass
        #TODO later: networkx + igraph drawing algorithms
        # import igraph
        # g = igraph.Graph.Tree(127, 2)
        # b = igraph.BoundingBox(0, 0, 1000, 1000)
        # layout = g.layout("kamada_kawai")
        # for row in layout:
        #     print(row)
        
    def timerEvent(self, event):
        if self.drawing_algorithm =='Spring-based layout':
            parameters = self.controller.spring_layout_parameters_window.get_values()
            self.spring_layout(*parameters)
        else:
            self.fruchterman_reingold_layout()

    def stop_timer(self):
        self.killTimer(self.timer)
        
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
        pixmap = view.controller.pixmaps['default'][self.node.subtype]
        selection_pixmap = self.controller.pixmaps['red'][self.node.subtype]
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
        self.node.gnode = self.node.gobject = self
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setOffset(
                       QPointF(
                               -self.boundingRect().width()/2, 
                               -self.boundingRect().height()/2
                               )
                       )
        self.setZValue(10)
        self.view.scene.addItem(self)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        # node speed for graph drawing algorithms
        self.vx = self.vy = 0
        
    @property
    def x(self):
        return super().x()
        
    @property
    def y(self):
        return super().y()
        
    @x.setter
    def x(self, x):
        self.setPos(x, self.y)
        
    @y.setter
    def y(self, y):
        self.setPos(self.x, y)
        
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
            self.setSelected(True)
            menu = NetworkSelectionMenu(self.controller)
            menu.exec_(QCursor.pos())
        super(GraphicalNode, self).mousePressEvent(event)
        
                
class GraphicalLink(QGraphicsLineItem):
    
    def __init__(self, view, link=None):
        super().__init__()
        self.controller = view.controller
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
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
        self.setPen(view.link_color[self.link.subtype])
        self.update_position()
        view.scene.addItem(self)
        self.link.glink = self.link.gobject = self
        
    def mousePressEvent(self, event):
        selection_allowed = self.controller.mode == 'selection'
        self.setFlag(QGraphicsItem.ItemIsSelectable, selection_allowed)
        # ideally, the menu should be triggered from the mouseReleaseEvent
        # binding, but for QT-related issues, the right-click filter does not
        # work in mouseReleaseEvent
        if event.buttons() == Qt.RightButton:
            menu = NetworkSelectionMenu(self.controller)
            menu.exec_(QCursor.pos())
        
    def update_position(self):
        start_position = self.source.pos()
        end_position = self.destination.pos()
        self.setLine(QLineF(start_position, end_position))