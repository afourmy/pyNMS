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
        QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QInputDialog, QLabel, QLineEdit, QComboBox, QListWidget, QAbstractItemView)

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
        self.node_subtype_list = QComboBox()
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
        
    @update_paths(False)
    def create_nodes(self, _):
        nb_nodes = int(self.nb_nodes_edit.text())
        subtype = node_name_to_obj[self.node_subtype_list.currentText()]
        self.view.draw_objects(self.network.multiple_nodes(nb_nodes, subtype))
        self.close()
        
class MultipleLinks(QWidget):  

    @update_paths(True)
    def __init__(self, nodes, controller):
        super().__init__()
        self.controller = controller
        self.sources = self.view.get_obj(nodes)
        print(self.sources)
        self.setWindowTitle('Multiple links')
        
        link_type = QLabel('Type of link')
        self.link_subtype_list = QComboBox()
        self.link_subtype_list.addItems(link_name_to_obj)
        
        destinations = QLabel('Destination nodes')
        self.destination_list = QListWidget()
        self.destination_list.addItems(map(str, self.network.nodes.values()))
        self.destination_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        confirmation_button = QPushButton()
        confirmation_button.setText('OK')
        confirmation_button.clicked.connect(self.create_links)
        
        cancel_button = QPushButton()
        cancel_button.setText('Cancel')
        
        layout = QGridLayout()
        layout.addWidget(link_type, 0, 0, 1, 2)
        layout.addWidget(self.link_subtype_list, 1, 0, 1, 2)
        layout.addWidget(destinations, 2, 0, 1, 2)
        layout.addWidget(self.destination_list, 3, 0, 1, 2)
        layout.addWidget(confirmation_button, 4, 0, 1, 1)
        layout.addWidget(cancel_button, 4, 1, 1, 1)
        self.setLayout(layout)
        
    def create_links(self):
        selection = map(lambda s: s.text(), self.destination_list.selectedItems())
        destinations = set(self.network.convert_nodes(selection))
        self.view.draw_objects(self.network.multiple_links(self.sources, destinations))