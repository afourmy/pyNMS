from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from right_click_menus.network_selection_menu import NetworkSelectionMenu
from right_click_menus.internal_site_selection_menu import InternalSiteSelectionMenu

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
        self.node.gnode[view] = self.node.gobject[view] = self
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
                link.glink[self.view].update_position()
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
            if self.view.subtype == 'main':
                menu = NetworkSelectionMenu(self.controller)
            elif self.view.subtype == 'internal':
                menu = InternalSiteSelectionMenu(self.controller)
            menu.exec_(QCursor.pos())
        super(GraphicalNode, self).mousePressEvent(event)