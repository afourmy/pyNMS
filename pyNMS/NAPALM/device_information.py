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

from napalm_base import get_network_driver
from .napalm_interfaces import NapalmInterfaces
from .napalm_configurations import NapalmConfigurations
from .napalm_general import NapalmGeneral
from pprint import pformat
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
        QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QInputDialog, QLabel, QLineEdit, QComboBox, QListWidget, QAbstractItemView, QTabWidget, QTextEdit)
from threading import Thread

class DeviceInformation(QTabWidget):
    
    def __init__(self, node, controller):
        super().__init__()
        self.node = node
        self.setMinimumSize(600, 600)
        self.setWindowTitle('NAPALM: device information')
        
        if len(node.napalm_data) > 1:
            # first tab: general information (facts + environment)
            general_frame = NapalmGeneral(node, controller)
            self.addTab(general_frame, 'General')
                                    
            # second tab: the interfaces
            interfaces_frame = NapalmInterfaces(node, controller)
            self.addTab(interfaces_frame, 'Interfaces')
        
        # third tab: the configurations
        self.configurations_frame = NapalmConfigurations(node, controller)
        self.addTab(self.configurations_frame, 'Configurations')
        
    def closeEvent(self, _):
        candidate = self.configurations_frame.candidate_edit.toPlainText()
        if 'Configuration' not in self.node.napalm_data:
            self.node.napalm_data['Configuration'] = {}
        self.node.napalm_data['Configuration']['candidate'] = candidate
