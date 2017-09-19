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
from objects.objects import node_subtype, link_class
from os.path import join
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
    
    github_path = 'https://raw.githubusercontent.com/afourmy/pyNMS/master/Icons'

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle('Export to Google Earth')
        
        node_size = QLabel('Node label size')
        self.node_size = QLineEdit('1')
        
        line_width = QLabel('Line width')
        self.line_width = QLineEdit('1')
        
        export = QPushButton('Export to KML')
        export.clicked.connect(self.kml_export)
        
        self.styles = {}
        for subtype in node_subtype:
            point_style = simplekml.Style()
            point_style.labelstyle.color = simplekml.Color.blue
            path_icon = join(self.github_path, 'default_{}.gif'.format(subtype))
            point_style.iconstyle.icon.href = path_icon
            self.styles[subtype] = point_style
            
        for subtype, cls in link_class.items():
            line_style = simplekml.Style()
            # we convert the RGB color to a KML color, 
            # i.e #RRGGBB to #AABBGGRR
            kml_color = "#ff{0:02x}{1:02x}{2:02x}".format(*cls.color[::-1])
            print(kml_color)
            line_style.linestyle.color = kml_color
            self.styles[subtype] = line_style
            
        layout = QGridLayout()
        layout.addWidget(node_size, 0, 0)
        layout.addWidget(self.node_size, 0, 1)
        layout.addWidget(line_width, 2, 0)
        layout.addWidget(self.line_width, 2, 1)
        layout.addWidget(export, 3, 0, 1, 2)
        self.setLayout(layout)
        
    @update_paths
    def kml_export(self, _):
        kml = simplekml.Kml()
                
        for node in self.network.nodes.values():
            point = kml.newpoint(name=node.name, description=node.description)
            point.coords = [(node.longitude, node.latitude)]
            point.style = self.styles[node.subtype]
            point.style.labelstyle.scale = float(self.node_size.text())
            
        for link in self.network.all_links():
            line = kml.newlinestring(name=link.name, description=link.description) 
            line.coords = [(link.source.longitude, link.source.latitude),
                        (link.destination.longitude, link.destination.latitude)]
            line.style = self.styles[link.subtype]
            line.style.linestyle.width = self.line_width.text() 
            
        filepath = QFileDialog.getSaveFileName(
                                               self, 
                                               'KML export', 
                                               'project', 
                                               '.kml'
                                               )
        selected_file = ''.join(filepath)
        kml.save(selected_file)
        self.close()
