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
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
        QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QGraphicsItem)
    
class SelectionPanel(QGroupBox):
    
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.setTitle('Selection')        
        self.modes = ('nodes', 'links', 'shapes')
                        
        layout = QGridLayout(self)
        self.checkboxes = []
        for index, mode in enumerate(self.modes, 1):
            checkbox = QCheckBox(mode.title())
            checkbox.selection_mode = mode
            checkbox.setChecked(True)
            checkbox.clicked.connect(lambda _, m=mode: self.change_selection(m))
            layout.addWidget(checkbox, index, 1, 1, 1)
        self.setLayout(layout)
        
    @update_paths(False)
    def change_selection(self, mode):
        can_be_selected = not self.view.selection[mode]
        for item in {
                    'nodes': self.view.all_gnodes,
                    'links': self.view.all_glinks,
                    'shapes': lambda _: _
                    }[mode]():
            item.setFlag(QGraphicsItem.ItemIsSelectable, can_be_selected)
        self.view.selection[mode] = can_be_selected

        