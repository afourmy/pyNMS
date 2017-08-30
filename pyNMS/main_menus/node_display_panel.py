from miscellaneous.decorators import update_paths
from objects.objects import *
from os.path import join
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import (
                         QColor,
                         QCursor, 
                         QDrag,
                         QIcon, 
                         QPainter, 
                         QPixmap
                         )
from PyQt5.QtWidgets import (
                             QAction,
                             QFrame,
                             QPushButton, 
                             QWidget, 
                             QApplication, 
                             QLabel, 
                             QMenu,
                             QGraphicsPixmapItem,
                             QGroupBox,
                             )
                             
class MenuPushButton(QPushButton):
    
    def __init__(self, controller, subtype):
        super().__init__()
        self.controller = controller
        self.subtype = subtype
    
    def mousePressEvent(self, event):
        if event.buttons() == Qt.RightButton:
            menu = QMenu(self)
            
            no_label = QAction('No label', self)
            no_label.triggered.connect(lambda _: self.change_label(None))
            menu.addAction(no_label)
            
            for property in subtype_labels[self.subtype]:
                action = QAction(str(property), self)
                action.triggered.connect(lambda _, p=property: self.change_label(p))
                menu.addAction(action)
            menu.exec_(QCursor.pos())
        super().mousePressEvent(event)
        
    @update_paths
    def change_label(self, property):
        self.view.refresh_label(self.subtype, property)

class NodeDisplayPanel(QGroupBox):
    
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.setTitle('Node display')
        self.setMinimumSize(300, 300)
                
        # exit connection lost because of the following lines
        layout = QtWidgets.QGridLayout(self)
        self.buttons = {}
        for index, subtype in enumerate(node_subtype):
            button = MenuPushButton(controller, subtype)
            button.clicked.connect(lambda _, s=subtype: self.change_display(s))
            image_path = join(controller.path_icon, 'default_{}.gif'.format(subtype))
            button.setIcon(QIcon(image_path))
            button.setIconSize(QtCore.QSize(50, 50))
            self.buttons[subtype] = button
            layout.addWidget(button, index // 4, index % 4, 1, 1)
            
    @update_paths
    def change_display(self, subtype):
        self.view.per_subtype_display(subtype)        
            