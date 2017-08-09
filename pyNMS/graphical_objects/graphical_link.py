from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from right_click_menus.internal_site_selection_menu import InternalSiteSelectionMenu
from right_click_menus.main_network_selection_menu import MainNetworkSelectionMenu

class GraphicalLink(QGraphicsLineItem):
    
    def __init__(self, view, link=None):
        super().__init__()
        self.view = view
        self.controller = view.controller
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        # source and destination graphic nodes
        if link:
            self.link = link
            self.source = link.source.gnode[view]
            self.destination = link.destination.gnode[view]
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
        self.link.glink[view] = self.link.gobject[view] = self
        
    def mousePressEvent(self, event):
        selection_allowed = self.controller.mode == 'selection'
        self.setFlag(QGraphicsItem.ItemIsSelectable, selection_allowed)
        # ideally, the menu should be triggered from the mouseReleaseEvent
        # binding, but for QT-related issues, the right-click filter does not
        # work in mouseReleaseEvent
        if event.buttons() == Qt.RightButton:
            menu = {
                    'main': MainNetworkSelectionMenu,
                    'internal': InternalSiteSelectionMenu,
                    }[self.view.subtype](self.controller)
            menu.exec_(QCursor.pos())
            
    def itemChange(self, change, value):
        if change == self.ItemSelectedHasChanged:
            if self.isSelected():
                self.setPen(self.view.selection_pen)
            else:
                self.setPen(self.view.link_color[self.link.subtype])
        return QGraphicsLineItem.itemChange(self, change, value)
        
    def update_position(self):
        start_position = self.source.pos()
        end_position = self.destination.pos()
        self.setLine(QLineF(start_position, end_position))