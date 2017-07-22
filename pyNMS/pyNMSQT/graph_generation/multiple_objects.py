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
from objects.objects import *
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
        QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QInputDialog, QLabel, QLineEdit, QComboBox)

class MultipleNodes(QWidget):  

    @update_paths(True)
    def __init__(self, x, y, controller):
        super().__init__()
        self.x = x
        self.y = y
        self.setWindowTitle('Multiple nodes')
        
        nb_nodes = QLabel('Number of nodes')
        self.nb_nodes_edit = QLineEdit()
        self.nb_nodes_edit.setMaximumWidth(120)
        
        # list of node type
        node_type = QLabel('Type of node')
        self.node_subtype_list = QComboBox(self)
        self.node_subtype_list.addItems(node_name_to_obj)
    
        # confirmation button
        confirmation_button = QPushButton(self)
        confirmation_button.setText('OK')
        confirmation_button.clicked.connect(self.create_nodes)
        
        # cancel button
        cancel_button = QPushButton(self)
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
        
    def create_nodes(self):
        pass
        # self.view.multiple_nodes(
        #                        int(self.entry_nodes.text), 
        #                        name_to_obj[self.node_type_list.text],
        #                        self.x,
        #                        self.y
        #                        )
        # self.view.draw_all(random=False)
        # self.destroy()