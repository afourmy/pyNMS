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
from operator import itemgetter
from pyQT_widgets.Q_console_edit import QConsoleEdit
from PyQt5.QtWidgets import QWidget, QGridLayout

class ARPTable(QWidget):
    
    @update_paths(True)
    def __init__(self, node, controller):
        super().__init__()
        self.setWindowTitle('ARP table')
        self.setMinimumSize(600, 800)
        
        config_edit = QConsoleEdit()

        introduction = '''
                    Address Resolution Protocol Table
----------------------------------------------------------------------------
         Address     |     Hardware Addr     |     Type     |     Interface\n\n'''
        
        config_edit.insertPlainText(introduction)

        arp_table = sorted(node.arpt.items(), key=itemgetter(0))
        for oip, (mac_addr, outgoing_interface) in arp_table:
            line = (oip.ip_addr, mac_addr, 'ARPA', str(outgoing_interface), '\n')
            config_edit.insertPlainText(8*" " + (9*" ").join(line))
            
        layout = QGridLayout()
        layout.addWidget(config_edit, 0, 0, 1, 1)
        self.setLayout(layout)