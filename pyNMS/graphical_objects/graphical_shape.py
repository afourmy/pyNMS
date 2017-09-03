from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class GraphicalShape(QGraphicsItem):
    
    class_type = 'shape'

    def mousePressEvent(self, event):
        selection_allowed = self.controller.mode == 'selection'
        shape_selection_allowed = self.view.selection['shape']
        print(selection_allowed, shape_selection_allowed)
        can_be_selected = selection_allowed and shape_selection_allowed
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
            menu = MainNetworkSelectionMenu(self.controller)
            menu.exec_(QCursor.pos())
            self.setFlag(QGraphicsItem.ItemIsSelectable, can_be_selected)
        super().mousePressEvent(event)