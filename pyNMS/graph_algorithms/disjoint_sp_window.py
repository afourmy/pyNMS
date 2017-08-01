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

class DisjointSPWindow(QWidget):
    
    algorithms = (
    'Constrained A*', 
    'Bhandari algorithm', 
    'Suurbale algorithm', 
    'Linear programming'
    )
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle('Disjoint shortest paths algorithms')
        
        algorithm = QLabel('Algorithm')        
        self.dsp_list = QComboBox()
        self.dsp_list.addItems(self.algorithms)

        source = QLabel('Source')
        self.source_edit = QLineEdit()
        
        destination = QLabel('Destination')
        self.destination_edit = QLineEdit()
        
        number_of_paths = QLabel('Number of paths')
        self.number_of_paths_edit = QLineEdit()
                
        # confirmation button
        button_compute = QPushButton()
        button_compute.setText('Compute')
        button_compute.clicked.connect(self.compute_dsp)
        
        # position in the grid
        layout = QGridLayout()
        layout.addWidget(algorithm, 0, 0, 1, 1)
        layout.addWidget(self.dsp_list, 0, 1, 1, 1)
        layout.addWidget(source, 1, 0, 1, 1)
        layout.addWidget(self.source_edit, 1, 1, 1, 1)
        layout.addWidget(destination, 2, 0, 1, 1)
        layout.addWidget(self.destination_edit, 2, 1, 1, 1)
        layout.addWidget(number_of_paths, 3, 0, 1, 1)
        layout.addWidget(self.number_of_paths_edit, 3, 1, 1, 1)
        layout.addWidget(button_compute, 4, 0, 1, 2)
        self.setLayout(layout)
        
    @update_paths(False)
    def compute_dsp(self, _):
        source = self.network.nf(name=self.source_edit.text())
        destination = self.network.nf(name=self.destination_edit.text())
        algorithm = {
                    'Constrained A*': self.network.A_star_shortest_pair,
                    'Bhandari algorithm': self.network.bhandari,
                    'Suurbale algorithm': self.network.suurbale,
                    'Linear programming': lambda: 'to repair'
                    }[self.dsp_list.currentText()]
        nodes, physical_links = algorithm(source, destination)
        self.view.select(*(nodes + physical_links))