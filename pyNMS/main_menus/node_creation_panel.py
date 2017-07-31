from collections import defaultdict, OrderedDict
from objects.objects import *
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

class NodeCreationPanel(QGroupBox):
    
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.setTitle('Node creation')
        self.setMinimumSize(300, 300)
        self.setAcceptDrops(True)
                
        # exit connection lost because of the following lines
        layout = QtWidgets.QGridLayout(self)
        for index, item in enumerate(controller.pixmaps['default'].items()):
            subtype, image = item
            label = QLabel(self)
            label.subtype = subtype
            pixmap = image.scaled(
                                 label.size(), 
                                 Qt.KeepAspectRatio,
                                 Qt.SmoothTransformation
                                 )
            label.setPixmap(pixmap)
            label.show()
            label.setAttribute(Qt.WA_DeleteOnClose)
            layout.addWidget(label, index // 4, index % 4, 1, 1)
            
    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('application/x-dnditemdata'):
            if event.source() == self:
                event.setDropAction(Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()

    dragEnterEvent = dragMoveEvent

    def mousePressEvent(self, event):
        # retrieve the label 
        child = self.childAt(event.pos())
        if not child:
            return
        
        # update the creation mode to the appropriate subtype
        self.controller.creation_mode = child.subtype
        
        pixmap = QPixmap(child.pixmap())
        item_data = QtCore.QByteArray()
        data_stream = QtCore.QDataStream(item_data, QtCore.QIODevice.WriteOnly)
        data_stream << pixmap << QtCore.QPoint(event.pos() - child.pos())

        mime_data = QtCore.QMimeData()
        mime_data.setData('application/x-dnditemdata', item_data)

        drag = QtGui.QDrag(self)
        drag.setMimeData(mime_data)
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos() - child.pos())

        if drag.exec_(Qt.CopyAction | Qt.MoveAction, Qt.CopyAction) == Qt.MoveAction:
            child.close()
        else:
            child.show()
            child.setPixmap(pixmap)