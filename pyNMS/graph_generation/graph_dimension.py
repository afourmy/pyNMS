from miscellaneous.decorators import update_paths
from objects.objects import *
from os.path import join
from pyQT_widgets.Q_object_combo_box import QObjectComboBox
from PyQt5.QtWidgets import (
                             QGridLayout, 
                             QWidget, 
                             QLabel, 
                             QLineEdit, 
                             QPushButton
                             )

class GraphDimensionWindow(QWidget):
        
    def __init__(self, graph_type, controller):
        super().__init__()
        self.controller = controller
        self.graph_type = graph_type
        self.setWindowTitle('Graph generation')
        
        layout = QGridLayout()
        self.node_subtype_list = QObjectComboBox()
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
        
        layout.addWidget(self.node_subtype_list, 0, 0, 1, 2)
        layout.addWidget(number_of_nodes, 1, 0, 1, 1)
        layout.addWidget(self.nodes_edit, 1, 1, 1, 1)
        if graph_type in ('kneser', 'petersen'):
            layout.addWidget(number_of_subset, 2, 0, 1, 1)
            layout.addWidget(self.subset_edit, 2, 1, 1, 1)
        layout.addWidget(confirmation_button, 3, 0, 1, 2)
        self.setLayout(layout)
        
    @update_paths(False)
    def confirm(self, _):
        nodes = int(self.nodes_edit.text()) - 1
        subtype = node_name_to_obj[self.node_subtype_list.currentText()]
        if self.graph_type in ('kneser', 'petersen'):
            subset = int(self.subset_edit.text())
            function = {
            'kneser': self.network.kneser,
            'petersen': self.network.petersen
            }[self.graph_type]
            objects = function(nodes, subset, subtype)
        else:
            function = {
            'star': self.network.star,
            'ring': self.network.ring,
            'full-mesh': self.network.full_mesh,
            'tree': self.network.tree,
            'square-tiling': self.network.square_tiling,
            'hypercube': self.network.hypercube,
            }[self.graph_type]
            objects = function(nodes, subtype)
        self.view.draw_objects(*objects)
        self.close()
        # we close the graph generation window as well, as we usually don't 
        # need to create two graphs in a row
        self.controller.graph_generation_window.hide()