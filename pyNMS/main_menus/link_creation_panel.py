from collections import defaultdict, OrderedDict
from objects.objects import *
from os.path import join
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import (
                         QColor, 
                         QDrag, 
                         QPainter, 
                         QPixmap
                         )
from PyQt5.QtWidgets import (
                             QFrame,
                             QToolButton, 
                             QWidget, 
                             QApplication, 
                             QLabel, 
                             QGraphicsPixmapItem,
                             QGroupBox,
                             )

class LinkCreationPanel(QGroupBox):
    
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.setTitle('Link creation')
                
        # exit connection lost because of the following lines
        layout = QtWidgets.QGridLayout(self)
        self.subtype_to_button = {}
        for index, subtype in enumerate(link_subtype):
            if subtype in ('l2vc', 'l3vc'):
                continue
            button = QToolButton(self)
            
            button.setStyleSheet('''QToolButton{ 
                    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                    stop: 0 rgb(230, 230, 250), stop: 1 rgb(230, 230, 250));
                    }''')
            button.clicked.connect(lambda _, s=subtype: self.create_link(s))
            image_path = join(controller.path_icon, subtype + '.png')
            icon = QtGui.QIcon(image_path)
            button.setIcon(icon)
            button.setIconSize(QtCore.QSize(120, 30))
            button.setText(obj_to_name[subtype])
            button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            self.subtype_to_button[subtype] = button
            layout.addWidget(button, index // 2, index % 2, 1, 1)
            
    def create_link(self, subtype):
        for button_subtype, button in self.subtype_to_button.items():
            button.setAutoRaise(subtype == button_subtype)
        self.controller.mode = 'creation'
        self.controller.creation_mode = subtype
