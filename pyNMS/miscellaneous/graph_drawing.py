#!/usr/bin/env python

from miscellaneous.decorators import update_paths
from objects.objects import *
from os.path import join
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import (
                         QIcon,
                         QColor, 
                         QDrag, 
                         QPainter, 
                         QPixmap
                         )
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
        QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QInputDialog, QLabel, QLineEdit, QComboBox)

class SpringLayoutParametersWindow(QWidget):
    
    spring_parameters = OrderedDict([
    ('Coulomb factor', 10000),
    ('Spring stiffness', 0.5),
    ('Speed factor', 3),
    ('Equilibrium length', 8)
    ])
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle('Spring layout parameters')
        self.resize(480, 320)
        
        grid = QGridLayout()
        spring_groupbox = QGroupBox('Spring layout parameters')
        layout = QGridLayout(spring_groupbox)
        self.line_edits = []
        for index, (parameter, value) in enumerate(self.spring_parameters.items()):
            label = QLabel(parameter)
            line_edit = QLineEdit()
            line_edit.setText(str(value))
            line_edit.setMaximumWidth(120)
            self.line_edits.append(line_edit)
            layout.addWidget(label, index, 0, 1, 1)
            layout.addWidget(line_edit, index, 1, 1, 1)
        grid.addWidget(spring_groupbox, 0, 0, 1, 1)
        self.setLayout(grid)
        
    def get_values(self):
        return (float(line_edit.text()) for line_edit in self.line_edits)
