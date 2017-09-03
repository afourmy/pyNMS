from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from right_click_menus.internal_site_selection_menu import InternalSiteSelectionMenu
from right_click_menus.main_network_selection_menu import MainNetworkSelectionMenu
from right_click_menus.site_selection_menu import SiteSelectionMenu

class GraphicalNode(QGraphicsPixmapItem):
    
    def __init__(self, view, node=None):
        self.view = view
        self.controller = view.controller
        # if node is not defined, it means the node is created with the 
        # drag & drop system, which implies that: 
        # - the subtype is the value of creation_mode
        # - the node object does not yet exist: it must be created
        if not node:
            subtype = self.controller.creation_mode
            self.node = self.view.network.nf(subtype=subtype)
        else:
            self.node = node
        self.object = self.node
        # we retrieve the pixmap based on the subtype to initialize a QGPI
        self.pixmap = self.controller.gpixmaps['default'][self.node.subtype]
        self.selection_pixmap = self.controller.gpixmaps['red'][self.node.subtype]
        super().__init__(self.pixmap)
        self.node.gnode[view] = self.node.gobject[view] = self
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, view.selection['node'])
        self.setFlag(QGraphicsItem.ItemIsMovable, view.selection['node'])
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
        # initialize the label
        self.label = self.view.scene.addSimpleText('')
        self.label.setZValue(15)
        
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
        if change == self.ItemPositionHasChanged:
            # when the node is created, the ItemPositionHasChanged is triggered:
            # we create the label
            if not hasattr(self, 'label'):
                self.label = self.view.scene.addSimpleText('')
                self.label.setZValue(15)
            self.label.setPos(self.pos() + QPoint(-20, 40))
        return QGraphicsPixmapItem.itemChange(self, change, value)
        
    def mousePressEvent(self, event):
        selection_allowed = self.controller.mode == 'selection'
        node_selection_allowed = self.view.selection['node']
        can_be_selected = selection_allowed and node_selection_allowed
        self.setFlag(QGraphicsItem.ItemIsSelectable, can_be_selected)
        self.setFlag(QGraphicsItem.ItemIsMovable, can_be_selected)
        # ideally, the menu should be triggered from the mouseReleaseEvent
        # binding, but for QT-related issues, the right-click filter does not
        # work in mouseReleaseEvent
        if event.buttons() == Qt.RightButton:
            # we set the item selectability to True, no matter what the actual
            # selection mode is, because we want the user to be able to trigger
            # the right-click menu at all times
            # eventually, we will rollback this change if needed depending on 
            # the selection mode
            self.setFlag(QGraphicsItem.ItemIsSelectable, True)
            self.setSelected(True)
            menu = {
                    'main': MainNetworkSelectionMenu,
                    'insite': InternalSiteSelectionMenu,
                    'site': SiteSelectionMenu
                    }[self.view.subtype](self.controller)
            menu.exec_(QCursor.pos())
            self.setFlag(QGraphicsItem.ItemIsSelectable, can_be_selected)
        super(GraphicalNode, self).mousePressEvent(event)
        
    def self_destruction(self):
        self.view.scene.removeItem(self.label)
        self.view.scene.removeItem(self)