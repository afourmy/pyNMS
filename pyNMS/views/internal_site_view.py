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

from graphical_objects.graphical_network_node import GraphicalNetworkNode
from graphical_objects.graphical_link import GraphicalLink
from .network_view import NetworkView
from miscellaneous.decorators import update_paths
from networks.base_network import BaseNetwork
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class InternalSiteView(NetworkView):
    
    subtype = 'internal'

    def __init__(self, gsite, controller):
        self.network = controller.current_project.network_view.network
        self.gsite = gsite
        self.site = self.gsite.node
        self.site.view = self
        super().__init__(controller)
        controller.current_project.hlayout.addWidget(self)
        self.hide()
        
        # dictionnary that associates an object to its in-site graphical self
        self.gobj = {}
        
    # given a graphical node, retrieves all attached graphical links   
    # providing that they belong to the site 
    def attached_glinks(self, gnode):
        for link in self.network.attached_links(gnode.node):
            if link in self.site.ps['link']:
                yield link.glink[self]
                
    def add_to_site(self, *objects):
        for obj in objects:
            if obj not in self.site.ps[obj.class_type]:
                self.site.add_to_site(obj)
                if obj.class_type == 'node':
                    self.gobj[obj] = GraphicalNetworkNode(self, obj)
                elif obj.class_type == 'link':
                    self.add_to_site(obj.source, obj.destination)
                    self.gobj[obj] = GraphicalLink(self, obj)
        
    def remove_from_site(self, *objects):
        for obj in objects:
            if obj not in self.site.ps[obj.class_type]:
                continue
            item = self.gobj.pop(obj)
            self.site.remove_from_site(obj)
            self.scene.removeItem(item)
            # remove it from the scene and the network model
            if self.is_node(item):
                for glink in self.attached_glinks(item):
                    self.remove_from_site(glink.link)
        
    @update_paths
    def dropEvent(self, event):
        pos = self.mapToScene(event.pos())
        if event.mimeData().hasFormat('application/x-dnditemdata'):
            item_data = event.mimeData().data('application/x-dnditemdata')
            dataStream = QDataStream(item_data, QIODevice.ReadOnly)
            pixmap, offset = QPixmap(), QPoint()
            dataStream >> pixmap >> offset
            network_gnode = GraphicalNetworkNode(self.network_view)
            new_node = GraphicalNetworkNode(self, network_gnode.node)
            new_node.setPos(pos - offset)
            
    def mouseReleaseEvent(self, event):
        item = self.itemAt(event.pos())
        if hasattr(self, 'temp_line') and self.temp_line:
            if self.is_node(item):
                self.end_node = item
                network_glink = GraphicalLink(self.network_view)
                new_link = GraphicalLink(self, network_glink.link)
                # we made the start node unselectable and unmovable to enable
                # the creation of links, in the press binding of GraphicalNode: 
                # we revert this change at link creation
                self.start_node.setFlag(QGraphicsItem.ItemIsSelectable, True)
                self.start_node.setFlag(QGraphicsItem.ItemIsMovable, True)
            self.scene.removeItem(self.temp_line)
            self.temp_line = None
        if event.button() == Qt.RightButton and self.trigger_menu:
            if not self.is_node(item) and not self.is_link(item): 
                menu = NetworkGeneralMenu(event, self.controller)
                menu.exec_(event.globalPos())
        super(InternalSiteView, self).mouseReleaseEvent(event)
            
        