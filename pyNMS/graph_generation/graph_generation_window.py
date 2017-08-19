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

from objects.objects import *
from os.path import join
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from .graph_dimension import GraphDimensionWindow
from PyQt5.QtWidgets import (
                             QGridLayout, 
                             QGroupBox, 
                             QWidget, 
                             QLabel, 
                             QLineEdit, 
                             QComboBox,
                             QPushButton
                             )

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
            layout.addWidget(button, index // 2, index % 2)
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
            layout.addWidget(button, index // 2, index % 2)
        return complex_graph_groupbox
            
    def graph_dimension(self, graph_type):
        self.window = GraphDimensionWindow(graph_type, self.controller)
        self.window.show()
            