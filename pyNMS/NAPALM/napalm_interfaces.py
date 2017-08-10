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
from pprint import pformat
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
        QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QInputDialog, QLabel, QLineEdit, QComboBox, QListWidget, QAbstractItemView, QTabWidget, QTextEdit)

class NapalmInterfaces(QWidget):
    
    napalm_actions = (
    'Interfaces',
    'Interface IP',
    'Interfaces counters',
    )

    @update_paths(True)
    def __init__(self, node, controller):
        super().__init__()
        self.node = node

        action_label = QLabel('Action')
        object_label = QLabel('Object')
        
        self.action_list = QListWidget()
        self.action_list.setSortingEnabled(True)
        self.action_list.itemSelectionChanged.connect(self.text_update)
        self.action_list.addItems(self.napalm_actions)
        
        self.object_list = QListWidget()
        self.object_list.setSortingEnabled(True)
        self.object_list.itemSelectionChanged.connect(self.text_update)
        interfaces = node.napalm_data['Interfaces'] if node.napalm_data else ()
        self.object_list.addItems(interfaces)
        
        self.properties_edit = QTextEdit()
        self.properties_edit.setMinimumSize(300, 300)

        layout = QGridLayout()
        layout.addWidget(object_label, 0, 0)
        layout.addWidget(self.object_list, 1, 0)
        layout.addWidget(action_label, 0, 1)
        layout.addWidget(self.action_list, 1, 1)
        layout.addWidget(self.properties_edit, 2, 0, 1, 2)
        self.setLayout(layout)
            
    def text_update(self):
        action = self.action_list.currentItem()
        object = self.object_list.currentItem()
        if action and object:
            
            self.properties_edit.clear()
            # we display a dictionnary with the following format:
            # property1: value1
            # property2: value2
            
            action, object = action.text(), object.text()
            try:
                value = '\n'.join(
                        '{}: {}'.format(*data)
                        for data in self.node.napalm_data[action][object].items()
                        )
            except KeyError:
                value = ''
                
            self.properties_edit.insertPlainText(value)
                        