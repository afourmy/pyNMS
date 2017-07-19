from collections import defaultdict, OrderedDict
from objects.objects import *
from os.path import abspath, join, pardir
from main_menus import node_creation_menu, link_creation_menu
from views import base_view
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import (
                         QColor, 
                         QDrag, 
                         QPainter, 
                         QPixmap
                         )
from PyQt5.QtWidgets import (
                             QAction,
                             QFrame,
                             QFileDialog,
                             QPushButton, 
                             QMainWindow, 
                             QApplication,
                             QHBoxLayout,
                             QVBoxLayout,
                             QLabel, 
                             QGraphicsPixmapItem,
                             QGroupBox,
                             QTabWidget,
                             QWidget
                             )

class Controller(QMainWindow):
    def __init__(self, path_app):
        super(Controller, self).__init__()
        
        # a QMainWindow needs a central widget for the layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        new_project = QAction('Add project', self)
        new_project.setStatusTip('Create a new project')
        new_project.triggered.connect(self.close)
        
        delete_project = QAction('Delete project', self)
        delete_project.setStatusTip('Delete the current project')
        delete_project.triggered.connect(self.close)
        
        import_project = QAction('Import project', self)
        import_project.setStatusTip('Import a project')
        import_project.triggered.connect(self.import_project)
        
        export_project = QAction('Export project', self)
        export_project.setStatusTip('Export the current project')
        export_project.triggered.connect(self.close)
        
        quit_pynms = QAction('Quit', self)
        quit_pynms.setShortcut('Ctrl+Q')
        quit_pynms.setStatusTip('Close pyNMS')
        quit_pynms.triggered.connect(self.close)

        menu_bar = self.menuBar()
        main_menu = menu_bar.addMenu('File')
        main_menu.addAction(new_project)
        main_menu.addAction(delete_project)
        main_menu.addSeparator()
        main_menu.addAction(import_project)
        main_menu.addAction(export_project)
        main_menu.addSeparator()
        main_menu.addAction(quit_pynms)

        self.statusBar()

        toolbar = self.addToolBar('Exit')
        toolbar.addAction(quit_pynms)

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
        
        tab_menu = QTabWidget(self)
        
        # first tab: the creation menu
        creation_menu = QWidget(tab_menu)
        tab_menu.addTab(creation_menu, 'Creation menu')
        # node creation menu
        self.node_creation_menu = node_creation_menu.NodeCreationMenu(self)
        self.link_creation_menu = link_creation_menu.LinkCreationMenu(self)
        
        # layout of the creation menu
        creation_menu_layout = QVBoxLayout(creation_menu)
        creation_menu_layout.addWidget(self.node_creation_menu)
        creation_menu_layout.addWidget(self.link_creation_menu)
        
        self.viewer = base_view.BaseView(self)


        layout = QHBoxLayout(central_widget)
        layout.addWidget(tab_menu) 
        layout.addWidget(self.viewer)

    def close(self):
        pass

    def import_project(self):
        path = QFileDialog.getOpenFileName(
                                           self, 
                                           'Import project', 
                                           'Choose a project to import'
                                           )