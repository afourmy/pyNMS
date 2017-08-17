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
from views.geographical_view import Map
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
        QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QInputDialog, QLabel, QLineEdit, QComboBox)

class GISParameterWindow(QWidget):  

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle('GIS parameters')
        
        layout = QGridLayout()
        
        # choose the projection and change it
        choose_projection = QLabel('Projection')
        self.projection_list = QComboBox(self)
        self.projection_list.addItems(Map.projections)
        
        # choose the map/nodes ratio
        ratio = QLabel('Map / nodes ratio')
        self.ratio_edit = QLineEdit()
        self.ratio_edit.setText('0.01')
        self.ratio_edit.setMaximumWidth(120)
        
        # cancel button
        draw_map_button = QPushButton()
        draw_map_button.setText('Redraw map')
        draw_map_button.clicked.connect(self.redraw_map)
        
        # position in the grid
        layout.addWidget(choose_projection, 0, 0, 1, 1)
        layout.addWidget(self.projection_list, 0, 1, 1, 1)
        layout.addWidget(ratio, 1, 0, 1, 1)
        layout.addWidget(self.ratio_edit, 1, 1, 1, 1)
        layout.addWidget(draw_map_button, 2, 0, 1, 2)
        self.setLayout(layout)
        
    @update_paths
    def redraw_map(self, _):
        self.view.world_map.ratio = float(self.ratio_edit.text())
        self.view.world_map.proj = self.projection_list.currentText()
        self.view.world_map.redraw_map()
    
        