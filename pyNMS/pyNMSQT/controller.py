from collections import defaultdict, OrderedDict
from objects.objects import *
from os.path import abspath, join, pardir
from main_menus import node_creation_menu, link_creation_menu
from project import Project
from views import base_view
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import (
                         QColor, 
                         QIcon,
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
        
        # initialize all paths
        self.path_app = path_app
        path_parent = abspath(join(path_app, pardir))
        self.path_icon = join(path_parent, 'Icons')
        self.path_workspace = join(path_parent, 'Workspace')
        self.path_shapefiles = join(path_parent, 'Shapefiles')
        
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
        export_project.triggered.connect(self.export_project)
        
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
        
        selection_icon = QIcon(join(self.path_icon, 'motion.png'))
        selection_mode = QAction(selection_icon, 'Selection mode', self)
        selection_mode.setShortcut('Ctrl+S')
        selection_mode.setStatusTip('Switch to selection mode')
        selection_mode.triggered.connect(self.switch_to_selection_mode)
        
        network_view_icon = QIcon(join(self.path_icon, 'network_view.png'))
        network_view = QAction(network_view_icon, 'Network view', self)
        network_view.setShortcut('Ctrl+N')
        network_view.setStatusTip('Switch to network view')
        network_view.triggered.connect(lambda: self.switch_view('network'))
        
        site_view_icon = QIcon(join(self.path_icon, 'site_view.png'))
        site_view = QAction(site_view_icon, 'Site view', self)
        site_view.setShortcut('Ctrl+N')
        site_view.setStatusTip('Switch to site view')
        site_view.triggered.connect(lambda: self.switch_view('site'))

        toolbar = self.addToolBar('')
        toolbar.resize(1500, 1500)
        toolbar.setIconSize(QtCore.QSize(70, 70))
        toolbar.addAction(selection_mode)
        toolbar.addSeparator()
        toolbar.addAction(network_view)
        toolbar.addAction(site_view)
        
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
                
        # associate a project name to a Project object
        self.dict_project = {}
        # project counter
        self.cpt_project = 0
        
        ## notebook containing all menus
        notebook_menu = QTabWidget(self)
        
        # first tab: the creation menu
        creation_menu = QWidget(notebook_menu)
        notebook_menu.addTab(creation_menu, 'Creation')
        
        # node creation menu
        self.node_creation_menu = node_creation_menu.NodeCreationMenu(self)
        self.link_creation_menu = link_creation_menu.LinkCreationMenu(self)
        
        # layout of the creation menu
        creation_menu_layout = QVBoxLayout(creation_menu)
        creation_menu_layout.addWidget(self.node_creation_menu)
        creation_menu_layout.addWidget(self.link_creation_menu)
        
        ## notebook containing all projects
        self.notebook_project = QTabWidget(self)
        
        # first project
        self.add_project()

        layout = QHBoxLayout(central_widget)
        layout.addWidget(notebook_menu) 
        layout.addWidget(self.notebook_project)
        
        # mode (creation of links or selection of objects)
        # since the drag & drop system for node creation does not interfere 
        # with the selection process, nodes can be created in selection mode
        # OTOH, creating links will automatically switch the mode to creation
        self.mode = 'selection'
        # creation mode (node subtype or link subtype)
        self.creation_mode = 'router'
        
    def add_project(self, name=None):
        self.cpt_project += 1
        if not name:
            name = ' '.join(('project', str(self.cpt_project)))
        new_project = Project(self, name)
        self.notebook_project.addTab(new_project, name)
        self.dict_project[name] = new_project
        return new_project
        
    def switch_to_selection_mode(self):
        self.mode = 'selection'
        
    def switch_view(self, view_mode):
        self.current_project.switch_view(view_mode)

    def close(self):
        pass

    def export_project(self):
        self.current_project.export_project()
        
    def import_project(self):
        pass