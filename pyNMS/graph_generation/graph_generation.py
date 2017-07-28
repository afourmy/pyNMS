#!/usr/bin/env python

from miscellaneous.decorators import update_paths
from objects.objects import *
from os.path import join
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import (
                         QIcon,
                         QColor, 
                         QDrag, 
                         QPainter, 
                         QPixmap
                         )
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
        QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QInputDialog, QLabel, QLineEdit, QComboBox)

class GraphGenerationWindow(QWidget):
    
    classic_graph = ('ring', 'tree', 'star', 'full-mesh')
    complex_graph = ('square-tiling', 'hypercube', 'kneser', 'petersen')
    
    def __init__(self, controller):
        super(GraphGenerationWindow, self).__init__()
        self.controller = controller
        
        grid = QGridLayout()
        grid.addWidget(self.classic_graph_generation(), 0, 0)
        grid.addWidget(self.complex_graph_generation(), 1, 0)
        self.setLayout(grid)

        self.setWindowTitle('Graph generation')
        self.resize(480, 320)

    def classic_graph_generation(self):
        classic_graph_groupbox = QGroupBox('Classic graph generation')
        layout = QGridLayout(classic_graph_groupbox)
        for index, graph_type in enumerate(self.classic_graph):
            button = QPushButton()
            button.clicked.connect(lambda _, g=graph_type: self.graph_dimension(g))
            image_path = join(self.controller.path_icon, graph_type + '.png')
            icon = QIcon(image_path)
            button.setIcon(icon)
            button.setIconSize(QSize(50, 50))
            layout.addWidget(button, index // 2, index % 2, 1, 1)
        return classic_graph_groupbox

    def complex_graph_generation(self):
        complex_graph_groupbox = QGroupBox('Complex graph generation')
        layout = QGridLayout(complex_graph_groupbox)
        for index, graph_type in enumerate(self.complex_graph):
            button = QPushButton()
            button.clicked.connect(lambda _, g=graph_type: self.graph_dimension(g))
            image_path = join(self.controller.path_icon, graph_type + '.png')
            icon = QIcon(image_path)
            button.setIcon(icon)
            button.setIconSize(QSize(50, 50))
            layout.addWidget(button, index // 2, index % 2, 1, 1)
        return complex_graph_groupbox
            
    def graph_dimension(self, graph_type):
        self.window = GraphDimensionWindow(graph_type, self.controller)
        self.window.show()
            
class GraphDimensionWindow(QWidget):
        
    def __init__(self, graph_type, controller):
        super().__init__()
        self.controller = controller
        self.graph_type = graph_type
        self.setWindowTitle('Graph generation')
        
        layout = QGridLayout()
        self.node_subtype_list = QComboBox(self)
        self.node_subtype_list.addItems(node_name_to_obj)
        
        number_of_nodes = QLabel('Nodes')
        self.nodes_edit = QLineEdit()
        self.nodes_edit.setMaximumWidth(120)
        
        if graph_type in ('kneser', 'petersen'):
            number_of_subset = QLabel('Subsets')
            self.subset_edit = QLineEdit()
            self.subset_edit.setMaximumWidth(120)
        
        # confirmation button
        confirmation_button = QPushButton(self)
        confirmation_button.setText('OK')
        confirmation_button.clicked.connect(self.confirm)
        
        # cancel button
        cancel_button = QPushButton()
        cancel_button.setText('Cancel')
        
        layout.addWidget(self.node_subtype_list, 0, 0, 1, 2)
        layout.addWidget(number_of_nodes, 1, 0, 1, 1)
        layout.addWidget(self.nodes_edit, 1, 1, 1, 1)
        
        if graph_type in ('kneser', 'petersen'):
            layout.addWidget(number_of_subset, 2, 0, 1, 1)
            layout.addWidget(self.subset_edit, 2, 1, 1, 1)
            
        layout.addWidget(confirmation_button, 3, 0, 1, 1)
        layout.addWidget(cancel_button, 3, 1, 1, 1)
        self.setLayout(layout)
        
    @update_paths(False)
    def confirm(self, _):
        nodes = int(self.nodes_edit.text())
        subtype = node_name_to_obj[self.node_subtype_list.currentText()]
        if self.graph_type in ('kneser', 'petersen'):
            subset = int(self.subset_edit.text())
            function = {
            'kneser': self.network.kneser,
            'petersen': self.network.petersen
            }[self.graph_type]
            function(nodes, subset, subtype)
        else:
            function = {
            'star': self.network.star,
            'ring': self.network.ring,
            'full-mesh': self.network.full_mesh,
            'tree': self.network.tree,
            'square-tiling': self.network.square_tiling,
            'hypercube': self.network.hypercube,
            }[self.graph_type]
            self.view.draw_objects(function(nodes, subtype))
        self.close()
        # we close the graph generation window as well, as we usually don't 
        # need to create two graph in a row
        self.controller.graph_generation_window.hide()
