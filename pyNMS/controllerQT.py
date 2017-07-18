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
                             QMainWindow, 
                             QApplication,
                             QHBoxLayout,
                             QLabel, 
                             QGraphicsPixmapItem,
                             QGroupBox,
                             QWidget
                             )

class Controller(QMainWindow):
    def __init__(self, path_app):
        super(Controller, self).__init__()
        
        # a QMainWindow needs a central widget for the layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        exitAction = QtWidgets.QAction(QtGui.QIcon('exit24.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)

        toolbar = self.addToolBar('Exit')
        toolbar.addAction(exitAction)

        # initialize all paths
        self.path_app = path_app
        path_parent = abspath(join(path_app, pardir))
        self.path_icon = join(path_parent, 'Icons')
        self.path_workspace = join(path_parent, 'Workspace')
        self.path_shapefiles = join(path_parent, 'Shapefiles')
        
        # create all pixmap images for node subtypes
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
        # self.edit = QtWidgets.QLineEdit(self)
        # self.edit.setReadOnly(True)
        # self.button = QtWidgets.QToolButton(self)
        # self.button.setText('...')
        # self.button.clicked.connect(self.open_file)

        layout = QHBoxLayout(central_widget)
        layout.addWidget(self.node_creation_menu) 
        layout.addWidget(self.viewer)
        # layout.addWidget(self.edit, 1, 1, 1, 1)
        # layout.addWidget(self.button, 1, 2, 1, 1)
        

    # def open_file(self):
    #     path = QtWidgets.QFileDialog.getOpenFileName(
    #         self, 'Choose Image', self.edit.text())
    #     if path:
    #         self.edit.setText(path)
    #         self.viewer.setPhoto(QtGui.QPixmap(path))