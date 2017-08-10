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
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
        QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QInputDialog, QLabel, QLineEdit, QComboBox, QListWidget, QAbstractItemView, QTabWidget, QTextEdit)

class NapalmGeneral(QWidget):
    
    # Facts and environment

    @update_paths(True)
    def __init__(self, node, controller):
        super().__init__()
        self.node = node

        action_label = QLabel('Action')
        object_label = QLabel('Object')
        
        self.general_list = QListWidget()
        self.general_list.setSortingEnabled(True)
        self.general_list.itemSelectionChanged.connect(self.info_update)
        infos = ['Facts'] + list(node.napalm_data['Environment'])
        self.general_list.addItems(infos)
        
        self.action_list = QListWidget()
        self.action_list.setSortingEnabled(True)
        self.action_list.itemSelectionChanged.connect(self.action_update)
        
        self.properties_edit = QTextEdit()
        self.properties_edit.setMinimumSize(300, 300)

        layout = QGridLayout()
        layout.addWidget(object_label, 0, 0)
        layout.addWidget(self.general_list, 1, 0)
        layout.addWidget(action_label, 0, 1)
        layout.addWidget(self.action_list, 1, 1)
        layout.addWidget(self.properties_edit, 2, 0, 1, 2)
        self.setLayout(layout)
            
    def info_update(self):
        self.properties_edit.clear()
        info = self.general_list.currentItem().text()
        
        if info == 'Facts':
            value = '\n'.join(
                    '{}: {}'.format(*data)
                    for data in self.node.napalm_data['Facts'].items()
                    )
            self.properties_edit.insertPlainText(value)
        else:
            self.action_list.clear()
            values = map(str, self.node.napalm_data['Environment'][info])
            self.action_list.addItems(values)
            
    def action_update(self):
        self.properties_edit.clear()
        action = self.action_list.currentItem()
        if action:
            info = self.general_list.currentItem().text()
            action_dict = self.node.napalm_data['Environment'][info][action.text()]
            try:
                value = '\n'.join(
                        '{}: {}'.format(*data)
                        for data in action_dict.items()
                        )
            except KeyError:
                value = ''
            self.properties_edit.insertPlainText(value)
                        