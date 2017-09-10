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

from collections import defaultdict, OrderedDict
from objects.objects import *
from os.path import join
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import (
                         QColor, 
                         QDrag, 
                         QPainter, 
                         QPixmap
                         )
from PyQt5.QtWidgets import (
                             QFrame,
                             QPushButton, 
                             QWidget, 
                             QApplication, 
                             QLabel, 
                             QGraphicsPixmapItem,
                             QGroupBox,
                             )

class LinkCreationPanel(QGroupBox):
    
    mode = 'network'
    
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.setTitle('Link creation')
                
        # exit connection lost because of the following lines
        layout = QtWidgets.QGridLayout(self)
        self.subtype_to_button = {}
        for index, subtype in enumerate(link_subtype):
            if subtype in ('l2vc', 'l3vc'):
                continue
            button = QPushButton(self)
            button.setStyleSheet('QPushButton{ background-color: rgb(255, 255, 255);}')
            button.clicked.connect(lambda _, s=subtype: self.create_link(s))
            image_path = join(controller.path_icon, subtype + '.png')
            icon = QtGui.QIcon(image_path)
            button.setIcon(icon)
            button.setIconSize(QtCore.QSize(120, 30))
            button.setFlat(True)
            self.subtype_to_button[subtype] = button
            layout.addWidget(button, index // 2, index % 2, 1, 1)
            
    def create_link(self, subtype):
        for button_subtype, button in self.subtype_to_button.items():
            button.setFlat(subtype != button_subtype)
        self.controller.mode = 'creation'
        self.controller.creation_mode = subtype
