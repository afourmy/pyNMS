from .geographical_view import GeographicalView
from .network_view import NetworkView
from graphical_objects.graphical_network_node import GraphicalNetworkNode
from graphical_objects.graphical_link import GraphicalLink
from math import sqrt
from networks import main_network
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from random import randint

class MainNetworkView(GeographicalView, NetworkView):
    
    subtype = 'main'

    def __init__(self, controller):
        self.network = main_network.MainNetwork(self)
        super().__init__(controller)
        
    # given a graphical node, retrieves all attached graphical links    
    def attached_glinks(self, gnode):
        for link in self.network.attached_links(gnode.node):
            if 'vc' in link.subtype:
                continue
            yield link.glink[self]
        
    def draw_objects(self, *objects):
        for obj in objects:
            if obj.class_type == 'node' and self not in obj.gnode:
                GraphicalNetworkNode(self, obj)
            if obj.class_type == 'link' and self not in obj.glink:
                if 'vc' in obj.subtype:
                    continue
                self.draw_objects(obj.source, obj.destination)
                GraphicalLink(self, obj)
        
    def dropEvent(self, event):
        pos = self.mapToScene(event.pos())
        geo_pos = self.world_map.to_geographical_coordinates(pos.x(), pos.y())
        if event.mimeData().hasFormat('application/x-dnditemdata'):
            new_gnode = GraphicalNetworkNode(self)
            new_gnode.setPos(pos)
            # update the nodes coordinates at creation
            new_gnode.node.longitude, new_gnode.node.latitude = geo_pos