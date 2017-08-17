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
            yield link.glink[self]
        
    def draw_objects(self, *objects):
        for obj in objects:
            if obj.class_type == 'node' and self not in obj.gnode:
                GraphicalNetworkNode(self, obj)
            if obj.class_type == 'link' and self not in obj.glink:
                self.draw_objects(obj.source, obj.destination)
                GraphicalLink(self, obj)
        
    def dropEvent(self, event):
        pos = self.mapToScene(event.pos())
        if event.mimeData().hasFormat('application/x-dnditemdata'):
            item_data = event.mimeData().data('application/x-dnditemdata')
            dataStream = QDataStream(item_data, QIODevice.ReadOnly)
            pixmap, offset = QPixmap(), QPoint()
            dataStream >> pixmap >> offset
            new_node = GraphicalNetworkNode(self)
            new_node.setPos(pos - offset)