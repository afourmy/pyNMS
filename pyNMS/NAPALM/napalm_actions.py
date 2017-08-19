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
from PyQt5.QtWidgets import (
                             QCheckBox,
                             QGridLayout, 
                             QGroupBox,
                             QPushButton, 
                             QWidget
                             )

class NapalmActions(QWidget):
    
    update_actions = {
    'Ethernet': {'MAC address', 'ARP table'},
    'LLDP': {'LLDP neighbors', 'LLDP neighbors detail'},
    'Interfaces': {'Interfaces', 'Interface IP', 'Interfaces counters', 'Transceivers'},
    'Facts': {'Facts', 'Environment'},
    'Configuration': {'Configuration'},
    'Logging': {'Logging'},
    'NTP': {'NTP servers', 'NTP statistics'},
    'SNMP': {'SNMP'},
    'BGP': set(),
    'Probes': set()
    }

    @update_paths
    def __init__(self, napalm_window, node, credentials, controller):
        super().__init__()
        self.node = node
        self.napalm_window = napalm_window
        self.credentials = credentials
        
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
        update_groupbox_layout.addWidget(napalm_update, 5, 0, 1, 2)
        
        update_groupbox.setLayout(update_groupbox_layout)
        
        config_groupbox = QGroupBox('Configuration')
        config_groupbox_layout = QGridLayout(config_groupbox)
        
        napalm_commit = QPushButton('Commit')
        napalm_commit.clicked.connect(self.commit)
        
        napalm_discard = QPushButton('Discard')
        napalm_discard.clicked.connect(self.discard)
        
        self.automatic_commit = QCheckBox('Commit after loading candidate')

        napalm_load_merge = QPushButton('Load merge candidate')
        napalm_load_merge.clicked.connect(self.load_merge)
        
        napalm_load_replace = QPushButton('Load replace candidate')
        napalm_load_replace.clicked.connect(self.load_replace)
        
        napalm_rollback = QPushButton('Rollback')
        napalm_rollback.clicked.connect(self.rollback)
        
        config_groupbox_layout.addWidget(napalm_commit, 0, 0)
        config_groupbox_layout.addWidget(napalm_discard, 0, 1)
        config_groupbox_layout.addWidget(self.automatic_commit, 1, 0, 1, 2)
        config_groupbox_layout.addWidget(napalm_load_merge, 2, 0)
        config_groupbox_layout.addWidget(napalm_load_replace, 2, 1)
        config_groupbox_layout.addWidget(napalm_rollback, 3, 0, 1, 2)
        config_groupbox.setLayout(config_groupbox_layout)
        
        layout = QGridLayout()
        layout.addWidget(update_groupbox, 0, 0)
        layout.addWidget(config_groupbox, 1, 0)
        self.setLayout(layout)
        
    def update(self):
        standalone_napalm_update(self.credentials, self.allowed_actions(), self.node)
        self.napalm_window.update()
        
    def allowed_actions(self):
        update_allowed = set()
        for checkbox in self.checkboxes:
            if checkbox.isChecked():
                update_allowed |= self.update_actions[checkbox.text()]
        return update_allowed
        
    def commit(self):
        napalm_commit(self.credentials, self.node)
        self.napalm_window.configurations_frame.update()
        
    def discard(self):
        napalm_discard(self.credentials, self.node)
        self.napalm_window.configurations_frame.update()
        
    def load_merge(self):
        self.napalm_window.closeEvent(None)
        if self.automatic_commit.isChecked():
            napalm_load_merge_commit(self.credentials, self.node)
        else:
            napalm_load_merge(self.credentials, self.node)
        self.napalm_window.configurations_frame.update()
        
    def load_replace(self):
        self.napalm_window.closeEvent(None)
        if self.automatic_commit.isChecked():
            napalm_load_replace_commit(self.credentials, self.node)
        else:
            napalm_load_replace(self.credentials, self.node)
        self.napalm_window.configurations_frame.update()
        
    def rollback(self):
        napalm_rollback(self.credentials, self.node)
        self.napalm_window.configurations_frame.update()

                        