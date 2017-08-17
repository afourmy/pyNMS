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

from miscellaneous.decorators import update_paths
from objects.objects import node_name_to_obj
from pyQT_widgets.Q_object_combo_box import QObjectComboBox
from PyQt5.QtWidgets import (
                             QGridLayout, 
                             QPushButton, 
                             QWidget, 
                             QLabel, 
                             QLineEdit
                             )

class MultipleNodes(QWidget):  

    def __init__(self, x, y, controller):
        super().__init__()
        self.controller = controller
        self.x, self.y = x, y
        self.setWindowTitle('Multiple nodes')
        
        nb_nodes = QLabel('Number of nodes')
        self.nb_nodes_edit = QLineEdit()
        self.nb_nodes_edit.setMaximumWidth(120)
        
        # list of node type
        node_type = QLabel('Type of node')
        self.node_subtype_list = QObjectComboBox()
        self.node_subtype_list.addItems(node_name_to_obj)
    
        # confirmation button
        confirmation_button = QPushButton()
        confirmation_button.setText('OK')
        confirmation_button.clicked.connect(self.create_nodes)
        
        # cancel button
        cancel_button = QPushButton()
        cancel_button.setText('Cancel')
        
        # position in the grid
        layout = QGridLayout()
        layout.addWidget(nb_nodes, 0, 0, 1, 1)
        layout.addWidget(self.nb_nodes_edit, 0, 1, 1, 1)
        layout.addWidget(node_type, 1, 0, 1, 1)
        layout.addWidget(self.node_subtype_list, 1, 1, 1, 1)
        layout.addWidget(confirmation_button, 2, 0, 1, 1)
        layout.addWidget(cancel_button, 2, 1, 1, 1)
        self.setLayout(layout)
        
    @update_paths
    def create_nodes(self, _):
        nb_nodes = int(self.nb_nodes_edit.text())
        subtype = node_name_to_obj[self.node_subtype_list.currentText()]
        self.view.draw_objects(*self.network.multiple_nodes(nb_nodes, subtype))
        self.close()
        