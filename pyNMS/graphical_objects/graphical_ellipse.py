from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class GraphicalEllipse(QGraphicsEllipseItem):
    
    class_type = 'shape'
    subtype = 'rectangle'
    
    def __init__(self, view):
        super().__init__()
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)