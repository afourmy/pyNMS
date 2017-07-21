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

# class GraphGenerationWindow(QWidget):
#     
#     def __init__(self, controller):
#         super(GraphGenerationWindow, self).__init__()
#         self.controller = controller
#         
#         grid = QGridLayout()
#         grid.addWidget(self.classic_graph_generation(), 0, 0)
#         grid.addWidget(self.complex_graph_generation(), 1, 0)
#         self.setLayout(grid)
# 
#         self.setWindowTitle('Graph generation')
#         self.resize(480, 320)
# 
#     def classic_graph_generation(self):
#         classic_graph_groupbox = QGroupBox('Classic graph generation')
#         layout = QGridLayout(classic_graph_groupbox)
#         for index, graph_type in enumerate(self.classic_graph):
#             button = QPushButton(self)
#             button.clicked.connect(lambda _, g=graph_type: self.graph_dimension(g))
#             image_path = join(self.controller.path_icon, graph_type + '.png')
#             icon = QIcon(image_path)
#             button.setIcon(icon)
#             button.setIconSize(QSize(50, 50))
#             layout.addWidget(button, index // 2, index % 2, 1, 1)
#         return classic_graph_groupbox
# 
#     def complex_graph_generation(self):
#         complex_graph_groupbox = QGroupBox('Complex graph generation')
#         layout = QGridLayout(complex_graph_groupbox)
#         for index, graph_type in enumerate(self.complex_graph):
#             button = QPushButton(self)
#             button.clicked.connect(lambda _, g=graph_type: self.graph_dimension(g))
#             image_path = join(self.controller.path_icon, graph_type + '.png')
#             icon = QIcon(image_path)
#             button.setIcon(icon)
#             button.setIconSize(QSize(50, 50))
#             layout.addWidget(button, index // 2, index % 2, 1, 1)
#         return complex_graph_groupbox
#             
#     def graph_dimension(self, graph_type):
#         self.window = GraphDimensionWindow(graph_type, self.controller)
#         self.window.show()
            
class GraphDrawingWindow(QWidget):
        
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle('Graph drawing algorithms')
        
        layout = QGridLayout()
        self.drawing_algorithm_list = QComboBox(self)
        self.drawing_algorithm_list.addItem('Random drawing')
        
        # confirmation button
        confirmation_button = QPushButton(self)
        confirmation_button.setText('OK')
        confirmation_button.clicked.connect(self.confirm)
        
        # cancel button
        cancel_button = QPushButton(self)
        cancel_button.setText('Cancel')
        
        layout.addWidget(self.drawing_algorithm_list, 0, 0, 1, 2)
            
        layout.addWidget(confirmation_button, 3, 0, 1, 1)
        layout.addWidget(cancel_button, 3, 1, 1, 1)
        self.setLayout(layout)
        
    @update_paths(False)
    def confirm(self, _):
        self.view.random_placement()

        

