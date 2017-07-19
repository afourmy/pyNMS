from collections import defaultdict, OrderedDict
from objects.objects import *
from os.path import join
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

class NodeCreationMenu(QGroupBox):
    def __init__(self, controller):
        super(NodeCreationMenu, self).__init__(controller)
        self.setTitle('Node creation')

        self.setMinimumSize(300, 300)
        self.setAcceptDrops(True)
                
        # exit connection lost because of the following lines
        layout = QtWidgets.QGridLayout(self)
        for index, image in enumerate(controller.node_subtype_to_pixmap['default'].values()):
            label = QLabel(self)
            label.setPixmap(image.scaled(
                                        label.size(), 
                                        Qt.KeepAspectRatio,
                                        Qt.SmoothTransformation
                                        ))
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

        pixmap = QPixmap(child.pixmap())

        itemData = QtCore.QByteArray()
        dataStream = QtCore.QDataStream(itemData, QtCore.QIODevice.WriteOnly)
        dataStream << pixmap << QtCore.QPoint(event.pos() - child.pos())

        mimeData = QtCore.QMimeData()
        mimeData.setData('application/x-dnditemdata', itemData)

        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos() - child.pos())

        if drag.exec_(Qt.CopyAction | Qt.MoveAction, Qt.CopyAction) == Qt.MoveAction:
            child.close()
        else:
            child.show()
            child.setPixmap(pixmap)