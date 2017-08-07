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

from graphical_objects.graphical_site import GraphicalSite
from .geographical_view import GeographicalView
from miscellaneous.decorators import overrider
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from networks import site_network

class SiteView(GeographicalView):

    def __init__(self, *args, **kwargs):
        self.network = site_network.SiteNetwork(self)
        super().__init__(*args, **kwargs)
        
    def draw_objects(self, sites):
        for site in sites:
            if not site.gnode:
                GraphicalSite(self, obj)
                
    def dropEvent(self, event):
        pos = self.mapToScene(event.pos())
        if event.mimeData().hasFormat('application/x-dnditemdata'):
            item_data = event.mimeData().data('application/x-dnditemdata')
            dataStream = QDataStream(item_data, QIODevice.ReadOnly)
            pixmap, offset = QPixmap(), QPoint()
            dataStream >> pixmap >> offset
            new_node = GraphicalSite(self)
            new_node.setPos(pos - offset)
