from graphical_objects.graphical_shape import GraphicalShape
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class GraphicalRectangle(QGraphicsRectItem, GraphicalShape):
    
    class_type = 'shape'
    subtype = 'rectangle'
    
    def __init__(self, view):
        super().__init__()
        self.view = view
        self.controller = view.controller
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
