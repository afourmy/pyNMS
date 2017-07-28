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

from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
        QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget)
    
class RoutingPanel(QGroupBox):
    
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.setTitle('Routing')
        self.setMinimumSize(300, 300)
        
        select_all_button = QPushButton()
        select_all_button.setText('Select / Unselect all')
        select_all_button.clicked.connect(self.selection)
        
        self.actions = (
                        'Update AS topology',
                        'Creation of all virtual connections',
                        'Names / addresses interface allocation',
                        'Creation of all ARP / MAC tables',
                        'Creation of all routing tables',
                        'Path finding procedure',
                        'Refresh the display'
                        )
                        
        layout = QGridLayout(self)
        layout.addWidget(select_all_button, 0, 1, 1, 1)
        self.checkboxes = []
        for index, action in enumerate(self.actions, 1):
            checkbox = QCheckBox(action)
            checkbox.setChecked(True)
            self.checkboxes.append(checkbox)
            layout.addWidget(checkbox, index, 1, 1, 1)
        self.setLayout(layout)
        
    def selection(self):
        select_all = not all(map(QCheckBox.isChecked, self.checkboxes))
        for checkbox in self.checkboxes:
            checkbox.setChecked(select_all)

        