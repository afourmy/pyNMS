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
from .napalm_functions import *
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
        QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QInputDialog, QLabel, QLineEdit, QComboBox, QListWidget, QAbstractItemView, QTabWidget, QTextEdit)

class NapalmActions(QWidget):
    
    update_actions = {
    'Ethernet': {'MAC address', 'ARP table'},
    'LLDP': {'LLDP neighbors', 'LLDP neighbors detail'},
    'Interfaces': {'Interfaces', 'Interface IP', 'Interfaces counters', 'Transceivers'},
    'Facts': {'Facts', 'Environment'},
    'Configuration': {'Configuration'},
    'Logging': {'Logging'},
    'NTP': {'NTP servers', 'NTP statistics'},
    'SNMP': {'SNMP'}
    }

    @update_paths(True)
    def __init__(self, napalm_window, node, controller):
        super().__init__()
        self.node = node
        self.napalm_window = napalm_window
        
        update_groupbox = QGroupBox('Update')
        update_groupbox_layout = QGridLayout(update_groupbox)
        
        self.checkboxes = []
        for index, action in enumerate(self.update_actions):
            checkbox = QCheckBox(action)
            checkbox.setChecked(True)
            self.checkboxes.append(checkbox)
            update_groupbox_layout.addWidget(checkbox, index // 2, index % 2)
        
        napalm_update = QPushButton(self)
        napalm_update.setText('Update')
        napalm_update.clicked.connect(self.update)
        update_groupbox_layout.addWidget(napalm_update, 4, 0, 1, 2)
        
        update_groupbox.setLayout(update_groupbox_layout)
        
        config_groupbox = QGroupBox('Configuration')
        config_groupbox_layout = QGridLayout(config_groupbox)
        
        napalm_commit = QPushButton()
        napalm_commit.setText('Commit')
        napalm_commit.clicked.connect(self.commit)
        
        napalm_discard = QPushButton()
        napalm_discard.setText('Discard')
        napalm_discard.clicked.connect(self.discard)
        
        napalm_load_merge = QPushButton()
        napalm_load_merge.setText('Load merge candidate')
        napalm_load_merge.clicked.connect(self.load_merge)
        
        napalm_load_replace = QPushButton()
        napalm_load_replace.setText('Load replace candidate')
        napalm_load_replace.clicked.connect(self.load_replace)
        
        config_groupbox_layout.addWidget(napalm_commit, 0, 0)
        config_groupbox_layout.addWidget(napalm_discard, 0, 1)
        config_groupbox_layout.addWidget(napalm_load_merge, 1, 0)
        config_groupbox_layout.addWidget(napalm_load_replace, 1, 1)
        config_groupbox.setLayout(config_groupbox_layout)
        
        layout = QGridLayout()
        layout.addWidget(update_groupbox, 0, 0)
        layout.addWidget(config_groupbox, 1, 0)
        self.setLayout(layout)
        
    def update(self):
        standalone_napalm_update(self.allowed_actions(), self.node)
        self.napalm_window.update()
        
    def allowed_actions(self):
        update_allowed = set()
        for checkbox in self.checkboxes:
            if checkbox.isChecked():
                update_allowed |= self.update_actions[checkbox.text()]
        return update_allowed
        
    def commit(self):
        napalm_commit(self.node)
        self.napalm_window.configurations_frame.update()
        
    def discard(self):
        napalm_discard(self.node)
        self.napalm_window.configurations_frame.update()
        
    def load_merge(self):
        self.napalm_window.closeEvent(None)
        napalm_load_merge_commit(self.node)
        self.napalm_window.configurations_frame.update()
        
    def load_replace(self):
        self.napalm_window.closeEvent(None)
        napalm_load_replace_commit(self.node)
        self.napalm_window.configurations_frame.update()

                        