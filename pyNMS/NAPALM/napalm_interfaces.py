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
    
    napalm_actions = OrderedDict([
    ('Interfaces', 'get_interfaces'),
    ('Interface IP', 'get_interfaces_ip'),
    ('Interfaces counters', 'get_interfaces_counters')
    ])

    @update_paths(True)
    def __init__(self, nodes, controller):
        super().__init__()
        
        # group box to choose an interface
        napalm_management = QGroupBox()
        napalm_management.setTitle('Choose a device and a NAPALM action')
        
        network_devices = QLabel('Network devices')
        action = QLabel('Action')

        self.device_list = QListWidget()
        self.device_list.setSortingEnabled(True)
        self.device_list.itemSelectionChanged.connect(self.properties_update)
        self.device_list.addItems(map(str, nodes))
        
        self.action_list = QListWidget()
        self.action_list.setSortingEnabled(True)
        self.action_list.itemSelectionChanged.connect(self.properties_update)
        self.action_list.addItems(self.napalm_actions)

        napalm_management_layout = QGridLayout()
        napalm_management_layout.addWidget(network_devices, 0, 0)
        napalm_management_layout.addWidget(self.device_list, 1, 0)
        napalm_management_layout.addWidget(action, 0, 1)
        napalm_management_layout.addWidget(self.action_list, 1, 1)
        napalm_management.setLayout(napalm_management_layout)
        
        # group box to display interface properties
        property_management = QGroupBox()
        property_management.setTitle('Properties')
        
        self.object_list = QListWidget()
        self.object_list.setSortingEnabled(True)
        self.object_list.itemSelectionChanged.connect(self.object_update)
        
        self.properties_edit = QTextEdit()
        
        self.property_management_layout = QGridLayout()
        self.property_management_layout.addWidget(self.object_list, 0, 0)
        self.property_management_layout.addWidget(self.properties_edit, 0, 1)
        property_management.setLayout(self.property_management_layout)
        
        # layout for the group boxes
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(napalm_management)
        main_layout.addWidget(property_management)
        self.setLayout(main_layout)
            
    def properties_update(self):
        device = self.device_list.currentItem()
        action = self.action_list.currentItem()
        if device and action:
            device = self.network.nf(name=device.text())
            self.object_list.clear()
            self.object_list.addItems(device.napalm_data[action.text()])
            
    def object_update(self):
        device = self.device_list.currentItem().text()
        action = self.action_list.currentItem().text()
        object = self.object_list.currentItem().text()
        self.properties_edit.clear()
        device = self.network.nf(name=device)
        value = device.napalm_data[action][object]
        self.properties_edit.insertPlainText(pformat(value))
                        
