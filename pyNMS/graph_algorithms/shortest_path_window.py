from miscellaneous.decorators import update_paths
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
        QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QInputDialog, QLabel, QLineEdit, QComboBox, QListWidget, QAbstractItemView)

class ShortestPathWindow(QWidget):
    
    algorithms = (
    'Constrained A*',
    'Bellman-Ford algorithm', 
    'Floyd-Warshall algorithm',
    'Linear programming'
    )
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle('Shortest path algorithms')
        
        algorithm = QLabel('Algorithm')        
        self.sp_list = QComboBox()
        self.sp_list.addItems(self.algorithms)

        source = QLabel('Source')
        self.source_edit = QLineEdit()
        
        destination = QLabel('Destination')
        self.destination_edit = QLineEdit()
                
        # confirmation button
        button_compute = QPushButton()
        button_compute.setText('Compute')
        button_compute.clicked.connect(self.compute_sp)
        
        # position in the grid
        layout = QGridLayout()
        layout.addWidget(algorithm, 0, 0, 1, 1)
        layout.addWidget(self.sp_list, 0, 1, 1, 1)
        layout.addWidget(source, 1, 0, 1, 1)
        layout.addWidget(self.source_edit, 1, 1, 1, 1)
        layout.addWidget(destination, 2, 0, 1, 1)
        layout.addWidget(self.destination_edit, 2, 1, 1, 1)
        layout.addWidget(button_compute, 3, 0, 1, 2)
        self.setLayout(layout)
        
    @update_paths(False)
    def compute_sp(self):
        source = self.network.nf(name=self.source_edit.text())
        destination = self.network.nf(name=self.destination_edit.text())
        algorithm = {
                    'Constrained A*': self.network.A_star,
                    'Bellman-Ford algorithm': self.network.bellman_ford,
                    'Floyd-Warshall algorithm': self.network.floyd_warshall,
                    'Linear programming': self.network.LP_SP_formulation
                    }[self.sp_list.currentText()]
        nodes, physical_links = algorithm(source, destination)
        self.view.select(*(nodes + physical_links))