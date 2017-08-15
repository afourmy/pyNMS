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
from objects.properties import IP_Address, SubnetMask, MAC_Address
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
        QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QInputDialog, QLabel, QLineEdit, QComboBox)

class InterfaceWindow(QWidget):
    
    interface_properties = (
                            IP_Address, 
                            SubnetMask, 
                            MAC_Address
                            )
                
    @update_paths(True)
    def __init__(self, interface, controller):
        super().__init__()
        self.interface = interface
        self.setWindowTitle('Manage interface properties')
        
        self.dict_global_properties = {}

        # global properties
        global_properties = QGroupBox('Global properties')
        global_properties_layout = QGridLayout(global_properties)
        
        for index, property in enumerate(interface.public_properties):
            label = QLabel(property.pretty_name)
            
            property_edit = QLineEdit()
            property_edit.setText(str(getattr(self.interface, property.name)))
            self.dict_global_properties[property] = property_edit
            
            global_properties_layout.addWidget(label, index + 1, 0, 1, 1)
            global_properties_layout.addWidget(property_edit, index + 1, 1, 1, 1)
            
        if self.interface.AS_properties:
            
            # per-AS properties
            perAS_properties = QGroupBox('Per-AS properties')
            perAS_properties_layout = QGridLayout(global_properties)
            self.dict_perAS_properties = {}
            
            # AS combobox
            self.AS_list = QComboBox()
            self.AS_list.addItems(tuple(self.interface.AS_properties))
            self.AS_list.activated.connect(self.update_AS_properties)
            
            for index, property in enumerate(interface.perAS_properties):
                label = QLabel(property.pretty_name)
                
                property_edit = QLineEdit()
                text = self.interface(self.AS_list.currentText(), property.name)
                property_edit.setText(text)
                self.dict_perAS_properties[property] = property_edit
                
                perAS_properties_layout.addWidget(label, index + 1, 0, 1, 1)
                perAS_properties_layout.addWidget(property_edit, index + 1, 1, 1, 1)

        grid = QGridLayout()
        grid.addWidget(global_properties, 0, 0)
        if self.interface.AS_properties:
            grid.addWidget(perAS_properties_layout, 0, 1)
        self.setLayout(grid)
        
    def update_AS_properties(self, _):
        AS = self.AS_list.currentText()
        for property, line_edit in self.dict_perAS_properties.items():
            line_edit.setText(self.interface(AS, property.name))
            
    def closeEvent(self, _):
        for property, edit in self.dict_global_properties.items():
            value = self.project.objectizer(property.name, edit.text())
            setattr(self.interface, property.name, value)
            
        if self.interface.AS_properties:
            AS = self.AS_list.currentText()
            for property, edit in self.dict_perAS_properties.items():
                value = self.project.objectizer(property.name, edit.text())
                self.interface(AS, property.name, value)
                
        self.close()