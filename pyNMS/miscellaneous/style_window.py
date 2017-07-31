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

from PyQt5.QtWidgets import (
                             QApplication, 
                             QCheckBox, 
                             QGridLayout, 
                             QWidget, 
                             QLabel, 
                             QComboBox, 
                             QStyleFactory
                             )

class StyleWindow(QWidget):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Styles')
        
        self.original_palette = QApplication.palette()
        
        styles = QLabel('Styles :')
        self.style_list = QComboBox()
        self.style_list.addItems(QStyleFactory.keys())
        self.style_list.setCurrentIndex(3)
        self.style_list.activated[str].connect(self.change_style)
        
        self.standard_palette = QCheckBox("Standard palette")
        self.standard_palette.setChecked(False)
        self.standard_palette.toggled.connect(self.change_palette)
        
        self.change_style('Fusion')
        
        grid = QGridLayout()
        grid.addWidget(styles, 0, 0, 1, 1)
        grid.addWidget(self.style_list, 0, 1, 1, 1)
        grid.addWidget(self.standard_palette, 1, 0, 1, 2)
        self.setLayout(grid)
        
    def change_style(self, name):
        QApplication.setStyle(QStyleFactory.create(name))
        self.change_palette()

    def change_palette(self):
        if self.standard_palette.isChecked():
            QApplication.setPalette(QApplication.style().standardPalette())
        else:
            QApplication.setPalette(self.original_palette)
