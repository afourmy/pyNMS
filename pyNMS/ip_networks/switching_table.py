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

class SwitchingTable(QWidget):
    
    @update_paths(True)
    def __init__(self, node, controller):
        super().__init__()
        self.setWindowTitle('Switching table')
        self.setMinimumSize(600, 800)
        
        config_edit = QConsoleEdit()

        introduction = '''
                            Mac Address Table
----------------------------------------------------------------------------
                    Vlan    |    Mac Address    |    Type    |    Ports\n\n'''
        
        config_edit.insertPlainText(introduction)
                
        switching_table = sorted(node.st.items(), key=itemgetter(0))
        for mac_address, outgoing_interface in switching_table:
            line = ('All', mac_address, 'DYNAMIC', str(outgoing_interface), '\n')
            config_edit.insertPlainText(16*" " + (8*" ").join(line))
            
        layout = QGridLayout()
        layout.addWidget(config_edit, 0, 0, 1, 1)
        self.setLayout(layout)