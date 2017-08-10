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
from pprint import pformat
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
        QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QInputDialog, QLabel, QLineEdit, QComboBox, QListWidget, QAbstractItemView, QTabWidget, QTextEdit)
from threading import Thread

class DeviceInformation(QTabWidget):
    
    def __init__(self, nodes, controller):
        super().__init__()
        self.setMinimumSize(500, 500)
        self.setWindowTitle('NAPALM: device information')
        
        # excluse nodes that haven't been NAPALM-updated
        nodes = filter(lambda node: node.napalm_data, nodes)
                                
        # first tab: the common management window
        interfaces_frame = NapalmInterfaces(nodes, controller)
        self.addTab(interfaces_frame, 'Interfaces')
