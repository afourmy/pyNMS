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

class LinkCreationMenu(QGroupBox):
    
    def __init__(self, controller):
        super(LinkCreationMenu, self).__init__(controller)
        self.setTitle('Link creation')
                
        # exit connection lost because of the following lines
        layout = QtWidgets.QGridLayout(self)
        for index, subtype in enumerate(link_subtype):
            if subtype in ('l2vc', 'l3vc'):
                continue
            button = QPushButton(self)
            image_path = join(controller.path_icon, subtype + '.png')
            icon = QtGui.QIcon(image_path)
            button.setIcon(icon)
            button.setIconSize(QtCore.QSize(120, 30))
            button.setStyleSheet("background-color: lavender");
            layout.addWidget(button, index // 2, index % 2, 1, 1)

    def mousePressEvent(self, event):
        
        # retrieve the label 
        child = self.childAt(event.pos())
        if not child:
            return
