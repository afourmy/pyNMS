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
from .napalm_functions import napalm_ping, napalm_traceroute, str_dict
from pyQT_widgets.Q_console_edit import QConsoleEdit
from PyQt5.QtWidgets import (
                             QGridLayout, 
                             QGroupBox,
                             QLabel, 
                             QLineEdit, 
                             QPushButton, 
                             QWidget
                             )

class NapalmTroubleshoot(QWidget):
    
    default_parameters = {
    'source': ('', 'Source'), 
    'ttl': (255, 'TTL'), 
    'timeout': (2, 'Timeout'), 
    'vrf': ('', 'VRF'),
    'size' : (100, 'Size'), 
    'count': (5, 'Count')
    } 

    def __init__(self, napalm_window, node, credentials):
        super().__init__()
        self.napalm_window = napalm_window
        self.node = node
        self.credentials = credentials
        
        destination = QLabel('Destination')
        destination_edit = QLineEdit()
        
        parameters_groupbox = QGroupBox('Ping / Traceroute')
        parameters_groupbox_layout = QGridLayout(parameters_groupbox)
        
        self.dict_line_edit = {'destination': destination_edit}
        for index, (parameter, info) in enumerate(self.default_parameters.items()):
            value, pretty_name = info
            label = QLabel(pretty_name)
            label.setMinimumWidth(200)
            line_edit = QLineEdit(str(value))
            # line_edit.setMaximumWidth(200)
            self.dict_line_edit[parameter] = line_edit
            y = 2*bool(index // 3)
            parameters_groupbox_layout.addWidget(label, index % 3, y)
            parameters_groupbox_layout.addWidget(line_edit, index % 3, y + 1)
        
        napalm_ping = QPushButton('Ping')
        napalm_ping.clicked.connect(self.ping)
        parameters_groupbox_layout.addWidget(napalm_ping, 7, 0, 1, 2)
        
        napalm_traceroute = QPushButton('Traceroute')
        napalm_traceroute.clicked.connect(self.traceroute)
        parameters_groupbox_layout.addWidget(napalm_traceroute, 7, 2, 1, 2)
        
        parameters_groupbox.setLayout(parameters_groupbox_layout)
        
        result_groupbox = QGroupBox('Result')
        result_groupbox_layout = QGridLayout(result_groupbox)
        self.console = QConsoleEdit()
        result_groupbox_layout.addWidget(self.console, 0, 0)
        
        layout = QGridLayout()
        layout.addWidget(destination, 0, 0)
        layout.addWidget(destination_edit, 0, 1)
        layout.addWidget(parameters_groupbox, 1, 0, 1, 2)
        layout.addWidget(result_groupbox, 2, 0, 1, 2)
        self.setLayout(layout)
        
    def get_parameters(self, traceroute=True):
        parameters = {}
        for parameter, line_edit in self.dict_line_edit.items():
            # the traceroute function does not need the following parameters
            if traceroute and parameter in ('size', 'count'):
                continue
            value = line_edit.text()
            if parameter in ('ttl', 'timeout', 'size', 'count'):
                value = int(value)
            parameters[parameter] = value
        return parameters
        
    def traceroute(self):
        self.console.clear()
        output = napalm_traceroute(self.credentials, self.node, **self.get_parameters())
        self.console.insertPlainText(str_dict(output))
        
    def ping(self):
        self.console.clear()
        output = napalm_ping(self.credentials, self.node, **self.get_parameters(False))
        self.console.insertPlainText(str_dict(output))
                        