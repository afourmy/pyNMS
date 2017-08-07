# from .insite_view import InSiteView
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from right_click_menus.network_selection_menu import NetworkSelectionMenu

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
        
class GraphicalSite(GraphicalNode):
    
    def __init__(self, view, node=None):
        super().__init__(view, node)
        self.site_view = InSiteView(site, self.controller)
                
class GraphicalLink(QGraphicsLineItem):
    
    def __init__(self, view, link=None):
        super().__init__()
        self.controller = view.controller
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
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