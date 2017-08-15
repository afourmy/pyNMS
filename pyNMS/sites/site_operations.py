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
        QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QInputDialog, QLabel, QLineEdit, QComboBox, QListWidget, QAbstractItemView)

class SiteOperations(QWidget):
    
    # add objects to a site, or remove objects from a site
    
    @update_paths(True)
    def __init__(self, mode, objects, sites, controller):
        super().__init__()
        
        title = {
                'add': 'Add to site',
                'remove': 'Remove from site'
                }[mode]
        
        self.setWindowTitle(title)
        
        # list of sites
        self.site_list = QComboBox()
        self.site_list.addItems(tuple(map(str, sites)))
        
        # confirmation button
        button_OK = QPushButton()
        button_OK.setText('OK')
        button_OK.clicked.connect(lambda: self.site_operation(mode, *objects))

        # position in the grid
        layout = QGridLayout()
        layout.addWidget(self.site_list, 0, 0)
        layout.addWidget(button_OK, 1, 0)
        self.setLayout(layout)
        
    def site_operation(self, mode, *objects):
        site_id = self.site_network.name_to_id[self.site_list.currentText()]
        selected_site = self.site_network.pn['node'][site_id]

        if mode == 'add':
            selected_site.view.add_to_site(*objects)
        elif mode == 'remove': 
            selected_site.view.remove_from_site(*objects)
            
        self.close()