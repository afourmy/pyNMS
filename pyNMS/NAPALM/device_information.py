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

from collections import OrderedDict, defaultdict
from miscellaneous.decorators import update_paths
from napalm_base import get_network_driver
from pprint import pformat
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
        QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QInputDialog, QLabel, QLineEdit, QComboBox, QListWidget, QAbstractItemView, QTabWidget, QTextEdit)
from threading import Thread

class DeviceInformation(QTabWidget):
    
    napalm_actions = OrderedDict([
    ('Facts', 'get_facts'),
    ('Environment', 'get_environment'),
    ('Configuration', 'get_config'),
    ('Interfaces', 'get_interfaces')
    ])
    
    @update_paths(True)
    def __init__(self, nodes, controller):
        super().__init__()
        # driver = get_network_driver('ios')
        self.setMinimumSize(500, 500)
        self.setWindowTitle('NAPALM: device information')
                
        # open all devices with napalm and store napalm data
        self.napalm_data = defaultdict(dict)
        for node in nodes:
            driver = get_network_driver('ios')
            device = driver(
                            hostname = node.ipaddress, 
                            username = 'cisco', 
                            password = 'cisco', 
                            optional_args= {'secret': 'cisco'}
                            )
            device.open()
            for action, function in self.napalm_actions.items():
                self.napalm_data[node.name][action] = getattr(device, function)()
            device.close()
                
        # first tab: the common management window
        common_frame = QWidget(self)
        self.addTab(common_frame, 'Interfaces')

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
        
        # layout for the group box
        common_frame_layout = QVBoxLayout(common_frame)
        common_frame_layout.addWidget(napalm_management)
        common_frame_layout.addWidget(property_management)
            
    def properties_update(self):
        device = self.device_list.currentItem()
        action = self.action_list.currentItem()
        if device and action:
            self.object_list.clear()
            self.object_list.addItems(self.napalm_data[device.text()][action.text()])
            
    def object_update(self):
        device = self.device_list.currentItem().text()
        action = self.action_list.currentItem().text()
        object = self.object_list.currentItem().text()
        self.properties_edit.clear()
        value = self.napalm_data[device][action][object]
        self.properties_edit.insertPlainText(pformat(value, width=1))

    # refresh display
    def refresh_display(self):
        # populate the listbox with all AS objects
        for obj_type in ('link', 'node'):
            self.dict_listbox[obj_type].clear()
            for obj in self.AS.pAS[obj_type]:
                self.dict_listbox[obj_type].addItem(str(obj))
        
    # function to highlight the selected object on the canvas
    def highlight_object(self, obj_type):
        self.AS.view.scene.clearSelection() 
        for selected_item in self.dict_listbox[obj_type].selectedItems():
            obj = self.network.of(name=selected_item.text(), _type=obj_type)
            obj.gobject.setSelected(True)
                        
    # remove the object selected in 'obj_type' listbox from the AS
    def remove_selected(self, obj_type):
        # remove and retrieve the selected object in the listbox
        for selected_item in self.dict_listbox[obj_type].selectedItems():
            # self.dict_listbox[obj_type].removeItem(selected_item)
            # remove it from the AS as well
            so = self.network.of(name=selected_item.text(), _type=obj_type)
            self.AS.remove_from_AS(so)
            row = self.dict_listbox[obj_type].row(selected_item)
            self.dict_listbox[obj_type].takeItem(row)
        

            
