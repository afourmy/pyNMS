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
from PyQt5.QtWidgets import (
                             QComboBox,
                             QGridLayout, 
                             QLabel, 
                             QLineEdit, 
                             QPushButton, 
                             QWidget, 
                             )

class RWAWindow(QWidget):
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle('Routing and Wavelength Assignment')
        
        scenario_name = QLabel('Scenario name')
        self.scenario_name_edit = QLineEdit()
        
        # confirmation button
        button_graph_transformation = QPushButton()
        button_graph_transformation.setText('Graph transformation')
        button_graph_transformation.clicked.connect(self.transform_graph)
        
        algorithm = QLabel('Algorithm :')        
        self.algorithm_list = QComboBox()
        self.algorithm_list.addItems(('Linear programming', 'Largest degree first'))
                
        button_compute = QPushButton()
        button_compute.setText('Compute')
        button_compute.clicked.connect(self.compute)
        
        # position in the grid
        layout = QGridLayout()
        layout.addWidget(scenario_name, 0, 0, 1, 1)
        layout.addWidget(self.scenario_name_edit, 0, 1, 1, 1)
        layout.addWidget(button_graph_transformation, 1, 0, 1, 2)
        layout.addWidget(algorithm, 2, 0, 1, 1)
        layout.addWidget(self.algorithm_list, 2, 1, 1, 1)
        layout.addWidget(button_compute, 3, 0, 1, 2)
        self.setLayout(layout)
        
    @update_paths(False)
    def transform_graph(self, _):
        name = self.scenario_name_edit.text()
        self.network.RWA_graph_transformation(name)

    @update_paths(False)
    def compute(self, _):
        algorithm = self.algorithm_list.currentText()
        if algorithm == 'Linear programming':
            self.network.LP_RWA_formulation()
        else:
            self.network.largest_degree_first()