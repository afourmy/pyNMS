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

from .AS import AS_subtypes
from miscellaneous.decorators import update_paths
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
        QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QInputDialog, QLabel, QLineEdit, QComboBox, QListWidget, QAbstractItemView)

class ASCreation(QWidget):  

    @update_paths(True)
    def __init__(self, nodes, links, controller):
        super().__init__()
        self.controller = controller
        self.nodes = nodes
        self.links = links
        self.setWindowTitle('Create AS')
        
        # AS type
        AS_type = QLabel('Type')
        self.AS_type_list = QComboBox()
        self.AS_type_list.addItems(AS_subtypes)
        
        # AS name
        AS_name = QLabel('Name')
        self.name_edit = QLineEdit()
        self.name_edit.setMaximumWidth(120)
        
        # AS ID
        AS_id = QLabel('ID')
        self.id_edit = QLineEdit()
        self.id_edit.setMaximumWidth(120)
        
        # confirmation button
        button_create_AS = QPushButton()
        button_create_AS.setText('Create AS')
        button_create_AS.clicked.connect(self.create_AS)
        
        # cancel button
        cancel_button = QPushButton()
        cancel_button.setText('Cancel')
        
        # position in the grid
        layout = QGridLayout()
        layout.addWidget(AS_type, 0, 0, 1, 1)
        layout.addWidget(self.AS_type_list, 0, 1, 1, 1)
        layout.addWidget(AS_name, 1, 0, 1, 1)
        layout.addWidget(self.name_edit, 1, 1, 1, 1)
        layout.addWidget(AS_id, 2, 0, 1, 1)
        layout.addWidget(self.id_edit, 2, 1, 1, 1)
        layout.addWidget(button_create_AS, 3, 0, 1, 1)
        layout.addWidget(cancel_button, 3, 1, 1, 1)
        self.setLayout(layout)
        
    def create_AS(self):
        # automatic initialization of the AS id in case it is empty
        id = self.id_edit.text()
        id = int(id) if id else len(self.network.pnAS) + 1
        new_AS = self.network.AS_factory(
                                         self.AS_type_list.currentText(), 
                                         self.name_edit.text(), 
                                         id,
                                         self.links, 
                                         self.nodes
                                         )
        self.close()
        
class ASOperation(QWidget):
    
    # - add objects to an AS
    # - remove objects from an AS
    # - enter the AS management window
    
    @update_paths(True)
    def __init__(self, mode, obj, AS=set(), controller=None):
        super().__init__()
        
        title = {
        'add': 'Add to AS',
        'remove': 'Remove from AS',
        'manage': 'Manage AS'
        }[mode]
        
        self.setWindowTitle(title)
        
        if mode == 'add':
            # all AS are proposed 
            values = tuple(map(str, self.network.pnAS))
        else:
            # only the common AS among all selected objects
            values = tuple(map(str, AS))
        
        # list of existing AS
        self.AS_list = QComboBox()
        self.AS_list.addItems(values)
        
        # confirmation button
        button_AS_operation = QPushButton()
        button_AS_operation.setText('OK')
        button_AS_operation.clicked.connect(lambda: self.as_operation(mode, *obj))
        
        # cancel button
        cancel_button = QPushButton()
        cancel_button.setText('Cancel')
        
        # position in the grid
        layout = QGridLayout()
        layout.addWidget(self.AS_list, 0, 0, 1, 2)
        layout.addWidget(button_AS_operation, 1, 0, 1, 1)
        layout.addWidget(cancel_button, 1, 1, 1, 1)
        self.setLayout(layout)
        
    def as_operation(self, mode, *objects):
        selected_AS = self.network.AS_factory(name=self.AS_list.currentText())

        if mode == 'add':
            selected_AS.management.add_to_AS(*objects)
        elif mode == 'remove':
            selected_AS.management.remove_from_AS(*objects)
        else:
            selected_AS.management.show()
            
        self.close()
            