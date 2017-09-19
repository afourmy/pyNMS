# Copyright (C) 2017 Antoine Fourmy <antoine dot fourmy at gmail dot com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from collections import defaultdict, OrderedDict
from objects.objects import *
from os.path import abspath, join, pardir
from graph_algorithms.shortest_path_window import ShortestPathWindow
from graph_algorithms.maximum_flow_window import MaximumFlowWindow
from graph_algorithms.disjoint_sp_window import DisjointSPWindow
from graph_algorithms.minimum_cost_flow_window import MCFlowWindow
from graph_algorithms.rwa_window import RWAWindow
from graph_generation.graph_generation_window import GraphGenerationWindow
from gis.gis_parameter_window import GISParameterWindow
from gis.export_to_google_earth_window import GoogleEarthExportWindow
from miscellaneous.graph_drawing import *
from miscellaneous.credentials_window import CredentialsWindow
from miscellaneous.search_window import SearchWindow
from miscellaneous.style_window import StyleWindow
from miscellaneous.debug import DebugWindow
from miscellaneous.decorators import update_paths
from main_menus import (
                        network_node_creation_panel,
                        internal_node_creation_panel,
                        link_creation_panel,
                        node_display_panel,
                        link_display_panel,
                        routing_panel,
                        selection_panel,
                        site_panel
                        )
from project import Project
from subprocess import Popen
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
    def __init__(self, path_app, test=False):
        super().__init__()
        self.test = test
        # for the update_paths decorator to work
        self.controller = self
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(212, 212, 212))
        self.setPalette(palette)
        
        # initialize all paths
        self.path_app = path_app
        path_parent = abspath(join(path_app, pardir))
        self.path_apps = join(path_parent, 'Apps')
        self.path_icon = join(path_parent, 'Icons')
        self.path_shapefiles = join(path_parent, 'Shapefiles')
        self.path_test = join(path_parent, 'Tests')
        self.path_workspace = join(path_parent, 'Workspace')
        
        # set the icon
        self.setWindowIcon(QIcon(join(self.path_icon, 'pynms_icon.gif')))
        
        # a QMainWindow needs a central widget for the layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        ## permanent windows
        
        self.graph_generation_window = GraphGenerationWindow(self)
        self.spring_layout_parameters_window = SpringLayoutParametersWindow(self)
        self.gis_parameter_window = GISParameterWindow(self)
        self.google_earth_export_window = GoogleEarthExportWindow(self)
        self.search_window = SearchWindow(self)
        self.style_window = StyleWindow()
        self.debug_window = DebugWindow(self)
        self.credentials_window = CredentialsWindow(self)
        
        # Graph algorithm windows
        self.shortest_path_window = ShortestPathWindow(self)   
        self.maximum_flow_window = MaximumFlowWindow(self)
        self.disjoint_sp_window = DisjointSPWindow(self)
        self.mcf_window = MCFlowWindow(self)
        self.rwa_window = RWAWindow(self)
        
        ## Menu bar
        menu_bar = self.menuBar()
        
        add_project = QAction('Add project', self)
        add_project.setStatusTip('Create a new project')
        add_project.triggered.connect(self.add_project)
        
        delete_project = QAction('Delete project', self)
        delete_project.setStatusTip('Delete the current project')
        delete_project.triggered.connect(self.delete_project)
        
        excel_import = QAction('Excel import', self)
        excel_import.setStatusTip('Import a project (Excel format)')
        excel_import.triggered.connect(self.excel_import)
        
        excel_export = QAction('Excel export', self)
        excel_export.setStatusTip('Export the current project (Excel format)')
        excel_export.triggered.connect(self.excel_export)
        
        yaml_import = QAction('YAML import', self)
        yaml_import.setStatusTip('Import a project (YAML format)')
        yaml_import.triggered.connect(self.yaml_import)
        
        yaml_export = QAction('YAML export', self)
        yaml_export.setStatusTip('Export the current project (YAML format)')
        yaml_export.triggered.connect(self.yaml_export)
        
        debug_pynms = QAction('Debug', self)
        debug_pynms.setShortcut('Ctrl+D')
        debug_pynms.setStatusTip('Debug')
        debug_pynms.triggered.connect(self.debug)
        
        quit_pynms = QAction('Quit', self)
        quit_pynms.setShortcut('Ctrl+Q')
        quit_pynms.setStatusTip('Close pyNMS')
        quit_pynms.triggered.connect(self.close)

        main_menu = menu_bar.addMenu('File')
        main_menu.addAction(add_project)
        main_menu.addAction(delete_project)
        main_menu.addSeparator()
        main_menu.addAction(excel_import)
        main_menu.addAction(excel_export)
        main_menu.addSeparator()
        main_menu.addAction(yaml_import)
        main_menu.addAction(yaml_export)
        main_menu.addSeparator()
        main_menu.addAction(debug_pynms)
        main_menu.addAction(quit_pynms)
        
        edit_style = QAction('Styles', self)
        edit_style.setStatusTip('Choose a style for the GUI')
        edit_style.triggered.connect(lambda: self.style_window.show())
        
        main_menu = menu_bar.addMenu('Edit')
        main_menu.addAction(edit_style)
        
        spring_parameters = QAction('Spring layout parameters', self)
        spring_parameters.setStatusTip('Spring layout parameters')
        spring_parameters.triggered.connect(lambda: self.spring_layout_parameters_window.show())
        
        drawing_menu = menu_bar.addMenu('Drawing parameters')
        drawing_menu.addAction(spring_parameters)
        
        show_hide_map = QAction('Show / Hide', self)
        show_hide_map.setStatusTip('Show / Hide map')
        show_hide_map.triggered.connect(self.show_hide_map)
        
        delete_map = QAction('Delete the map', self)
        delete_map.setStatusTip('Delete the map')
        delete_map.triggered.connect(self.delete_map)
        
        modify_map = QAction('Modify map', self)
        modify_map.setStatusTip('Modify map')
        modify_map.triggered.connect(lambda: self.gis_parameter_window.show())
        
        gis_parameters_menu = menu_bar.addMenu('GIS parameters')
        gis_parameters_menu.addAction(show_hide_map)
        gis_parameters_menu.addAction(delete_map)
        gis_parameters_menu.addAction(modify_map)
        
        default_credentials = QAction('Defaut credentials', self)
        default_credentials.setStatusTip('Default username and password')
        default_credentials.triggered.connect(lambda: self.credentials_window.show())
        
        connectivity_menu = menu_bar.addMenu('Connectivity')
        connectivity_menu.addAction(default_credentials)
        
        SP_window = QAction('Shortest path', self)
        SP_window.setStatusTip('Shortest path')
        SP_window.triggered.connect(lambda: self.shortest_path_window.show())
        
        MF_window = QAction('Maximum flow', self)
        MF_window.setStatusTip('Maximum flow')
        MF_window.triggered.connect(lambda: self.maximum_flow_window.show())
        
        DSP_window = QAction('Disjoint shortest paths', self)
        DSP_window.setStatusTip('Disjoint shortest paths')
        DSP_window.triggered.connect(lambda: self.disjoint_sp_window.show())
        
        MCF_window = QAction('Minimum-cost flow', self)
        MCF_window.setStatusTip('Minimum-cost flow')
        MCF_window.triggered.connect(lambda: self.mcf_window.show())
        
        RWA_window = QAction('Routing and wavelength assignment', self)
        RWA_window.setStatusTip('Routing and wavelength assignment')
        RWA_window.triggered.connect(lambda: self.rwa_window.show())
        
        algorithm_menu = menu_bar.addMenu('Advanced algorithms')
        algorithm_menu.addAction(SP_window)
        algorithm_menu.addAction(MF_window)
        algorithm_menu.addAction(DSP_window)
        algorithm_menu.addAction(MCF_window)
        algorithm_menu.addAction(RWA_window)

        ## Status bar
        
        self.statusBar()
        
        new_project_icon = QIcon(join(self.path_icon, 'new_project.png'))
        new_project = QAction(new_project_icon, 'New project', self)
        new_project.setStatusTip('Create a new project')
        new_project.triggered.connect(self.add_project)
        
        shapefile_import_icon = QIcon(join(self.path_icon, 'shapefile_import.png'))
        shapefile_import = QAction(shapefile_import_icon, 'Shapefile import', self)
        shapefile_import.setStatusTip('Import a shapefile (.shp)')
        shapefile_import.triggered.connect(self.shapefile_import)
        
        kml_export_icon = QIcon(join(self.path_icon, 'kml_export.png'))
        kml_export = QAction(kml_export_icon, 'Export to Google Earth', self)
        kml_export.setStatusTip('Export project to Google Earth (.kml)')
        kml_export.triggered.connect(self.kml_export)
        
        selection_icon = QIcon(join(self.path_icon, 'selection.png'))
        selection_mode = QAction(selection_icon, 'Selection mode', self)
        selection_mode.setStatusTip('Switch to selection mode')
        selection_mode.triggered.connect(self.switch_to_selection_mode)
        
        rectangle_icon = QIcon(join(self.path_icon, 'rectangle.png'))
        rectangle = QAction(rectangle_icon, 'Draw a rectangle', self)
        rectangle.setStatusTip('Draw a rectangle')
        rectangle.triggered.connect(self.rectangle)
        
        ellipse_icon = QIcon(join(self.path_icon, 'ellipse.png'))
        ellipse = QAction(ellipse_icon, 'Draw an ellipse', self)
        ellipse.setStatusTip('Draw an ellipse')
        ellipse.triggered.connect(self.ellipse)
        
        add_note_icon = QIcon(join(self.path_icon, 'add_note.png'))
        add_note = QAction(add_note_icon, 'Add note', self)
        add_note.setStatusTip('Add a note')
        add_note.triggered.connect(self.add_note)
        
        network_view_icon = QIcon(join(self.path_icon, 'network_view.png'))
        network_view = QAction(network_view_icon, 'Network view', self)
        network_view.setStatusTip('Switch to network view')
        network_view.triggered.connect(self.show_network_view)
        
        site_view_icon = QIcon(join(self.path_icon, 'site_view.png'))
        site_view = QAction(site_view_icon, 'Site view', self)
        site_view.setStatusTip('Switch to site view')
        site_view.triggered.connect(self.show_site_view)
        
        parent_view_icon = QIcon(join(self.path_icon, 'parent_view.png'))
        parent_view = QAction(parent_view_icon, 'Parent view', self)
        parent_view.setStatusTip('Go back to the parent view')
        parent_view.triggered.connect(self.show_parent_view)
        
        graph_generation_icon = QIcon(join(self.path_icon, 'ring.png'))
        graph_generation = QAction(graph_generation_icon, 'Graph generation', self)
        graph_generation.setShortcut('Ctrl+G')
        graph_generation.setStatusTip('Generate a graph')
        graph_generation.triggered.connect(lambda: self.graph_generation_window.show())
        
        stop_drawing_icon = QIcon(join(self.path_icon, 'stop.png'))
        stop_drawing = QAction(stop_drawing_icon, 'Stop drawing', self)
        stop_drawing.setStatusTip('Stop the graph drawing algorithm')
        stop_drawing.triggered.connect(lambda: self.stop_drawing())
        
        refresh_icon = QIcon(join(self.path_icon, 'refresh.png'))
        refresh = QAction(refresh_icon, 'Calculate all', self)
        refresh.setStatusTip('Calculate all (routing options + refresh display)')
        refresh.triggered.connect(self.refresh)
        
        search_icon = QIcon(join(self.path_icon, 'search.png'))
        search = QAction(search_icon, 'Search', self)
        search.setShortcut('Ctrl+F')
        search.setStatusTip('Search objects per property value')
        search.triggered.connect(lambda: self.search_window.show())
        
        zoom_in_icon = QIcon(join(self.path_icon, 'zoom_in.png'))
        zoom_in = QAction(zoom_in_icon, 'Zoom in', self)
        zoom_in.setStatusTip('Zoom in')
        zoom_in.triggered.connect(self.zoom_in)
        
        zoom_out_icon = QIcon(join(self.path_icon, 'zoom_out.png'))
        zoom_out = QAction(zoom_out_icon, 'Zoom out', self)
        zoom_out.setStatusTip('Zoom out')
        zoom_out.triggered.connect(self.zoom_out)
        
        search_icon = QIcon(join(self.path_icon, 'connection.png'))
        search = QAction(search_icon, 'SSH connection', self)
        search.setShortcut('Tab')
        search.setStatusTip('Start an SSH connection to the selected device')
        search.triggered.connect(self.ssh_connection)
        
        toolbar = self.addToolBar('')
        toolbar.resize(1500, 1500)
        toolbar.setIconSize(QtCore.QSize(70, 70))
        toolbar.addAction(new_project)
        toolbar.addSeparator()
        toolbar.addAction(shapefile_import)
        toolbar.addAction(kml_export)
        toolbar.addSeparator()
        toolbar.addAction(selection_mode)
        toolbar.addAction(rectangle)
        toolbar.addAction(ellipse)
        toolbar.addAction(add_note)
        toolbar.addSeparator()
        toolbar.addAction(network_view)
        toolbar.addAction(site_view)
        toolbar.addAction(parent_view)
        toolbar.addSeparator()
        toolbar.addAction(graph_generation)
        toolbar.addAction(stop_drawing)
        toolbar.addSeparator()
        toolbar.addAction(refresh)
        toolbar.addSeparator()
        toolbar.addAction(search)
        toolbar.addSeparator()
        toolbar.addAction(zoom_in)
        toolbar.addAction(zoom_out)
        
        # create all pixmap images for node subtypes
        self.pixmaps = defaultdict(OrderedDict)
        # rescaled pixmap used on the canvas to display graphical objects
        self.gpixmaps = defaultdict(OrderedDict)
        for color in ('default', 'red', 'purple'):
            for subtype in node_subtype:
                if test:
                    path = ''
                elif subtype in ('shelf', 'port', 'card'):
                    path = join(self.path_icon, ''.join((color, '_', subtype, '.png')))
                else:
                    path = join(self.path_icon, ''.join((color, '_', subtype, '.gif')))
                self.pixmaps[color][subtype] = QPixmap(path)
                self.gpixmaps[color][subtype] = QPixmap(path).scaled(
                                                        QSize(100, 100), 
                                                        Qt.KeepAspectRatio,
                                                        Qt.SmoothTransformation
                                                        )
                
        # associate a project name to a Project object
        self.dict_project = {}
        # project counter
        self.cpt_project = 0
        
        ## notebook containing all menus
        notebook_menu = QTabWidget(self)
        notebook_menu.setFixedSize(350, 800)
        
        # first tab: the creation menu
        creation_menu = QWidget(notebook_menu)
        notebook_menu.addTab(creation_menu, 'Creation')
        
        # creation menus
        network_node_creation_menu = network_node_creation_panel.NetworkNodeCreationPanel(self)
        link_creation_menu = link_creation_panel.LinkCreationPanel(self)
        
        # panel for the internal node view
        internal_node_creation_menu = internal_node_creation_panel.InternalNodeCreationPanel(self)
        # panel for the site view
        site_menu = site_panel.SitePanel(self)
        
        # layout of the creation menu
        self.creation_menu_layout = QGridLayout(creation_menu)
        self.creation_menu_layout.addWidget(network_node_creation_menu, 0, 0)
        self.creation_menu_layout.addWidget(link_creation_menu, 1, 0)
        self.creation_menu_layout.addWidget(internal_node_creation_menu, 0, 0)
        self.creation_menu_layout.addWidget(site_menu, 0, 0)
        
        # second tab: the display menu
        display_menu = QWidget(notebook_menu)
        notebook_menu.addTab(display_menu, 'Display')
        
        # display menus
        self.node_display_menu = node_display_panel.NodeDisplayPanel(self)
        self.link_display_menu = link_display_panel.LinkDisplayPanel(self)
        
        display_menu_layout = QVBoxLayout(display_menu)
        display_menu_layout.addWidget(self.node_display_menu)
        display_menu_layout.addWidget(self.link_display_menu)
        
        # third tab: the options menu
        options_menu = QWidget(notebook_menu)
        notebook_menu.addTab(options_menu, 'Options')
        
        # options panel
        self.routing_panel = routing_panel.RoutingPanel(self)
        self.selection_panel = selection_panel.SelectionPanel(self)
        
        options_menu_layout = QGridLayout(options_menu)
        options_menu_layout.addWidget(self.selection_panel, 0, 0, 1, 2)
        options_menu_layout.addWidget(self.routing_panel, 2, 0, 3, 1)
        
        # display the menu for the network mode
        self.change_menu('network')
        
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
        
    @update_paths
    def shapefile_import(self, _):
        filepath = QFileDialog.getOpenFileName(
                                                self, 
                                                'Import shapefile', 
                                                'Choose a shapefile to import'
                                                )[0]
        if filepath:
            self.view.world_map.shapefile = filepath
            self.view.world_map.redraw_map()
        
    def kml_export(self):
        self.google_earth_export_window.show()
        
    ## function to change the menu depending on the current mode
    def change_menu(self, mode):
        for index in range(self.creation_menu_layout.count()):
            widget = self.creation_menu_layout.itemAt(index).widget()
            widget.setHidden(widget.mode != mode)
        
    def delete_project(self):
        pass
        
    def excel_import(self):
        self.current_project.excel_import()
        
    def excel_export(self):
        self.current_project.excel_export()
        
    def yaml_import(self):
        self.current_project.yaml_import()
        
    def yaml_export(self):
        self.current_project.yaml_export()
        
    @update_paths
    def stop_drawing(self):
        self.view.stop_timer()
        
    def switch_to_selection_mode(self):
        self.mode = 'selection'
        self.creation_mode = None
        
    def show_network_view(self):
        self.current_project.show_network_view()
        
    def show_site_view(self):
        self.current_project.show_site_view()
        
    @update_paths
    def show_parent_view(self, _):
        self.current_project.show_parent_view()
        
    def generate_graph(self):
        self.current_project.generate_graph()
        
    def debug(self):
        self.debug_window.show()
        
    @update_paths
    def show_hide_map(self, _):
        self.view.world_map.show_hide_map()
        
    @update_paths
    def delete_map(self, _):
        self.view.world_map.delete_map()
        
    def refresh(self):
        self.current_project.refresh()
        
    def add_note(self):
        self.mode = 'creation'
        self.creation_mode = 'text'
        
    def rectangle(self):
        self.mode = 'creation'
        self.creation_mode = 'rectangle'
        
    def ellipse(self):
        self.mode = 'creation'
        self.creation_mode = 'ellipse'
        
    @update_paths
    def zoom_in(self):
        self.view.zoom_in()
        
    @update_paths
    def zoom_out(self):
        self.view.zoom_out()
        
    @update_paths
    def ssh_connection(self, _):
        selection = list(self.view.scene.selectedItems())
        if len(selection) == 1 and self.view.is_node(selection[0]):
            gnode ,= selection
            credentials = self.network.get_credentials(gnode.node)
            command = '{path} -ssh {username}@{ip_address} -pw {password}'
            connect = Popen(command.format(**credentials).split())