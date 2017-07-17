from collections import defaultdict, OrderedDict
from objects.objects import *
from os.path import abspath, join, pardir
from main_menus import node_creation_menuQT
from views import base_viewQT
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

class Controller(QWidget):
    def __init__(self, path_app):
        super(Controller, self).__init__()

        # initialize all paths
        self.path_app = path_app
        path_parent = abspath(join(path_app, pardir))
        self.path_icon = join(path_parent, 'Icons')
        self.path_workspace = join(path_parent, 'Workspace')
        self.path_shapefiles = join(path_parent, 'Shapefiles')
        
        self.node_subtype_to_pixmap = defaultdict(OrderedDict)
        for color in ('default', 'red', 'purple'):
            for subtype in node_subtype:
                path = join(self.path_icon, ''.join((
                                                    color, 
                                                    '_', 
                                                    subtype, 
                                                    '.gif'
                                                    )))
                self.node_subtype_to_pixmap[color][subtype] = QPixmap(path)
        
        # node creation menu
        self.node_creation_menu = node_creation_menuQT.NodeCreationMenu(self)
        
        self.viewer = base_viewQT.BaseView(self)
        self.edit = QtWidgets.QLineEdit(self)
        self.edit.setReadOnly(True)
        self.button = QtWidgets.QToolButton(self)
        self.button.setText('...')
        self.button.clicked.connect(self.open_file)
        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(self.viewer, 0, 1, 1, 2)
        layout.addWidget(self.edit, 1, 1, 1, 1)
        layout.addWidget(self.button, 1, 2, 1, 1)
        layout.addWidget(self.node_creation_menu, 0, 0, 1, 1) 

    def open_file(self):
        path = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Choose Image', self.edit.text())
        if path:
            self.edit.setText(path)
            self.viewer.setPhoto(QtGui.QPixmap(path))