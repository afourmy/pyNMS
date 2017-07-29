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
from PyQt5.QtWidgets import QWidget, QTextEdit, QGridLayout

class RouterConfiguration(QWidget):
    
    @update_paths(True)
    def __init__(self, node, controller):
        super().__init__()
        self.setWindowTitle('Router configuration')
        self.setMinimumSize(500, 600)
        
        config_edit = QTextEdit()
            
        for conf in self.network.build_router_configuration(node):
            config_edit.insertPlainText(conf + '\n')
            
        layout = QGridLayout()
        layout.addWidget(config_edit, 0, 0, 1, 1)
        self.setLayout(layout)
        
class SwitchConfiguration(QWidget):
    
    @update_paths(True)
    def __init__(self, node, controller):
        super().__init__()
        self.setWindowTitle('Switch configuration')
        self.setMinimumSize(500, 600)
        
        config_edit = QTextEdit()
        
        for conf in self.network.build_switch_configuration(node):
            config_edit.insertPlainText(conf + '\n')
            
        layout = QGridLayout()
        layout.addWidget(config_edit, 0, 0, 1, 1)
        self.setLayout(layout)
        