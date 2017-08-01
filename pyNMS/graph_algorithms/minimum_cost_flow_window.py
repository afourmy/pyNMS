from miscellaneous.decorators import update_paths
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
        QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QInputDialog, QLabel, QLineEdit, QComboBox, QListWidget, QAbstractItemView)

class MCFlowWindow(QWidget):
    
    algorithms = ('Linear programming', 'Klein')
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle('Minimum-cost flow algorithms')
        
        algorithm = QLabel('Algorithm')        
        self.mcf_list = QComboBox()
        self.mcf_list.addItems(self.algorithms)

        source = QLabel('Source')
        self.source_edit = QLineEdit()
        
        destination = QLabel('Destination')
        self.destination_edit = QLineEdit()
        
        flow = QLabel('Flow')
        self.flow_edit = QLineEdit()
                
        # confirmation button
        button_compute = QPushButton()
        button_compute.setText('Compute')
        button_compute.clicked.connect(self.compute_mcflow)
        
        # position in the grid
        layout = QGridLayout()
        layout.addWidget(algorithm, 0, 0, 1, 1)
        layout.addWidget(self.mcf_list, 0, 1, 1, 1)
        layout.addWidget(source, 1, 0, 1, 1)
        layout.addWidget(self.source_edit, 1, 1, 1, 1)
        layout.addWidget(destination, 2, 0, 1, 1)
        layout.addWidget(self.destination_edit, 2, 1, 1, 1)
        layout.addWidget(flow, 3, 0, 1, 1)
        layout.addWidget(self.flow_edit, 3, 1, 1, 1)
        layout.addWidget(button_compute, 4, 0, 1, 2)
        self.setLayout(layout)
        
    @update_paths(False)
    def compute_mcflow(self):
        source = self.network.nf(name=self.source_edit.text())
        destination = self.network.nf(name=self.destination_edit.text())
        flow = self.flow_entry.text
        algorithm = {
                    'Linear programming': self.network.LP_MCF_formulation,
                    'Klein': lambda: 'to be implemented'
                    }[self.mcf_list.currentText()]
        cost = algorithm(source, destination, flow)   
        print(cost)
        