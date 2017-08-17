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

from collections import OrderedDict
from miscellaneous.decorators import update_paths
from .napalm_functions import str_dict
from pyQT_widgets.Q_console_edit import QConsoleEdit
from PyQt5.QtWidgets import (
                             QGridLayout, 
                             QLabel, 
                             QListWidget,
                             QWidget
                             )

class NapalmInterfaces(QWidget):
    
    napalm_actions = (
    'Interfaces',
    'Interface IP',
    'Interfaces counters',
    )

    @update_paths
    def __init__(self, node, controller):
        super().__init__()
        self.node = node

        action_label = QLabel('Action')
        object_label = QLabel('Object')
        
        self.object_list = QListWidget()
        self.object_list.setSortingEnabled(True)
        self.object_list.itemSelectionChanged.connect(self.text_update)        
        
        self.action_list = QListWidget()
        self.action_list.setSortingEnabled(True)
        self.action_list.itemSelectionChanged.connect(self.text_update)
        self.action_list.addItems(self.napalm_actions)
        
        self.properties_edit = QConsoleEdit()
        self.properties_edit.setMinimumSize(300, 300)

        layout = QGridLayout()
        layout.addWidget(object_label, 0, 0)
        layout.addWidget(self.object_list, 1, 0)
        layout.addWidget(action_label, 0, 1)
        layout.addWidget(self.action_list, 1, 1)
        layout.addWidget(self.properties_edit, 2, 0, 1, 2)
        self.setLayout(layout)
        
    def update(self):
        self.object_list.clear()
        if 'Interfaces' in self.node.napalm_data:
            self.object_list.addItems(self.node.napalm_data['Interfaces'])
            
    def text_update(self):
        action = self.action_list.currentItem()
        object = self.object_list.currentItem()
        
        if action and object:
            self.properties_edit.clear()
            # we display a dictionnary with the following format:
            # property1: value1
            # property2: value2
            
            action, object = action.text(), object.text()
            value = str_dict(self.node.napalm_data[action][object])                
            self.properties_edit.insertPlainText(value)
                        