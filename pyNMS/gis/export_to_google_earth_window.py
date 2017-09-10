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
                             QFileDialog,
                             QGridLayout, 
                             QLabel, 
                             QLineEdit, 
                             QPushButton, 
                             QWidget
                             )
try:
    import simplekml
except ImportError:
    warnings.warn('simplekml not installed: export to google earth disabled')

class GoogleEarthExportWindow(QWidget):  

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle('Export to Google Earth')
        
        node_size = QLabel('Node label size')
        self.node_size = QLineEdit('2')
        
        path = 'https://raw.githubusercontent.com/afourmy/pyNMS/master/Icons/default_router.gif'
        self.path_edit = QLineEdit(path)
        
        line_width = QLabel('Line width')
        self.line_width = QLineEdit('2')
        
        path_to_icon = QPushButton('Node icon')
        path_to_icon.clicked.connect(self.choose_path)
        
        export = QPushButton('Export to KML')
        export.clicked.connect(self.kml_export)
        
        layout = QGridLayout()
        layout.addWidget(node_size, 0, 0)
        layout.addWidget(self.node_size, 0, 1)
        layout.addWidget(self.path_edit, 1, 1)
        layout.addWidget(line_width, 2, 0)
        layout.addWidget(self.line_width, 2, 1)
        layout.addWidget(path_to_icon, 1, 0)
        layout.addWidget(export, 3, 0, 1, 2)
        self.setLayout(layout)
        
    @update_paths
    def kml_export(self, _):
        kml = simplekml.Kml()
        
        point_style = simplekml.Style()
        point_style.labelstyle.color = simplekml.Color.blue
        point_style.labelstyle.scale = float(self.node_size.text())
        point_style.iconstyle.icon.href = self.path_edit.text()
        
        for node in self.network.nodes.values():
            point = kml.newpoint(name=node.name, description=node.description)
            point.coords = [(node.longitude, node.latitude)]
            point.style = point_style
            
        line_style = simplekml.Style()
        line_style.linestyle.color = simplekml.Color.red
        line_style.linestyle.width = self.line_width.text()
            
        for link in self.network.pn['plink'].values():
            line = kml.newlinestring(name=link.name, description=link.description) 
            line.coords = [(link.source.longitude, link.source.latitude),
                        (link.destination.longitude, link.destination.latitude)]
            line.style = line_style
            
        filepath = QFileDialog.getSaveFileName(
                                               self, 
                                               'KML export', 
                                               'project', 
                                               '.kml'
                                               )
        selected_file = ''.join(filepath)
        kml.save(selected_file)
        self.close()
        
    def choose_path(self):
        path = 'Choose an icon'
        filepath = ''.join(QFileDialog.getOpenFileName(self, path, path))
        self.path_edit.setText(filepath)
        self.path = filepath