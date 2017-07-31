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
                             QPushButton, 
                             QWidget, 
                             QApplication, 
                             QLabel, 
                             QGraphicsPixmapItem,
                             QGroupBox,
                             )

class NodeDisplayPanel(QGroupBox):
    
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.setTitle('Node display')
        self.setMinimumSize(300, 300)
                
        # exit connection lost because of the following lines
        layout = QtWidgets.QGridLayout(self)
        for index, subtype in enumerate(node_subtype):
            button = QPushButton(self)
            print(subtype)
            # button.clicked.connect(lambda _, s=subtype: self.create_link(s))
            image_path = join(controller.path_icon, 'default_{}.gif'.format(subtype))
            icon = QtGui.QIcon(image_path)
            button.setIcon(icon)
            button.setIconSize(QtCore.QSize(50, 50))
            layout.addWidget(button, index // 4, index % 4, 1, 1)
            