from collections import defaultdict, OrderedDict
from miscellaneous.decorators import update_paths
from objects.objects import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QSize, QPoint
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

class NetworkNodeCreationPanel(QGroupBox):
    
    mode = 'network'
    
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.setTitle('Node creation')
        self.setMinimumSize(300, 300)
        self.setAcceptDrops(True)
                
        # exit connection lost because of the following lines
        layout = QtWidgets.QGridLayout(self)
        for index, subtype in enumerate(network_node_subtype):
            pixmap = controller.pixmaps['default'][subtype]
            label = QLabel(self)
            label.setMaximumSize(50, 50)
            label.subtype = subtype
            label.setPixmap(pixmap)
            label.setScaledContents(True)
            label.show()
            label.setAttribute(Qt.WA_DeleteOnClose)
            layout.addWidget(label, index // 4, index % 4)
            
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

    @update_paths
    def mousePressEvent(self, event):
        # retrieve the label 
        child = self.childAt(event.pos())
        if not child:
            return
        
        self.controller.mode = 'selection'
        # update the creation mode to the appropriate subtype
        self.controller.creation_mode = child.subtype
        # we change the view if necessary:
        # if it is a site, we switch the site view
        # if it is anything else and we are in the site view, we switch 
        # to the network view
        if child.subtype == 'site':
            self.project.show_site_view()
        else:
            if self.project.view_type == 'site':
                self.project.show_network_view()
        
        pixmap = QPixmap(child.pixmap().scaled(
                                            QSize(50, 50), 
                                            Qt.KeepAspectRatio,
                                            Qt.SmoothTransformation
                                            ))

        mime_data = QtCore.QMimeData()
        mime_data.setData('application/x-dnditemdata', QtCore.QByteArray())

        drag = QtGui.QDrag(self)
        drag.setMimeData(mime_data)
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos() - child.pos() + QPoint(-3, -10))

        if drag.exec_(Qt.CopyAction | Qt.MoveAction, Qt.CopyAction) == Qt.MoveAction:
            child.close()
        else:
            child.show()