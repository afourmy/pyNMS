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

import re
from objects.objects import *
from miscellaneous.decorators import update_paths
from PyQt5.QtWidgets import (
                             QCheckBox, 
                             QComboBox,
                             QGridLayout, 
                             QGroupBox,
                             QPushButton,
                             QWidget, 
                             QLineEdit
                             )

class SearchWindow(QWidget):
    
    # Find all objects which property fits a given value
    # -------------
    # ComboBox: list of all subtypes of objects
    # ComboBox: list of all properties of the subtype
    # CheckBox: whether the search is regex-based or not
    # LineEdit: value 
    # PushButton: confirmation
    # -------------
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle('Search window')
        self.setMinimumSize(300, 200)
        
        self.subtypes_list = QComboBox()
        self.subtypes_list.addItems(name_to_obj)
        self.subtypes_list.activated.connect(self.update_properties)
        
        self.property_list = QComboBox()
        self.checkbox_regex = QCheckBox('Regex search')
        self.entry_search = QLineEdit()
        
        button_OK = QPushButton()
        button_OK.setText('OK')
        button_OK.clicked.connect(self.search)
        
        # position in the grid
        layout = QGridLayout()
        layout.addWidget(self.subtypes_list, 0, 0, 1, 2)
        layout.addWidget(self.property_list, 1, 0, 1, 2)
        layout.addWidget(self.checkbox_regex, 2, 0, 1, 1)
        layout.addWidget(self.entry_search, 3, 0, 1, 1)
        layout.addWidget(button_OK, 4, 0, 1, 1)
        self.setLayout(layout)
        
        # update property with first value of the list
        self.update_properties()
        
    def update_properties(self):
        subtype = self.subtypes_list.currentText()
        print(subtype)
        properties = object_properties[name_to_obj[subtype]]
        properties = tuple(p.name for p in properties)
        self.property_list.clear()
        self.property_list.addItems(properties)
        
    @update_paths(False)
    def search(self, _):
        self.view.scene.clearSelection()
        subtype = name_to_obj[self.subtypes_list.currentText()]
        property = name_to_prop[self.property_list.currentText()]
        type = subtype_to_type[subtype]
        input = self.entry_search.text()
        for obj in self.network.ftr(type, subtype):
            value = getattr(obj, property)
            if not self.checkbox_regex.isChecked():
                converted_input = self.project.objectizer(property, input)
                if value == converted_input:
                    obj.gobject.setSelected(True)
            else:
                if re.search(str(input), str(value)):
                    obj.gobject.setSelected(True)
                
        