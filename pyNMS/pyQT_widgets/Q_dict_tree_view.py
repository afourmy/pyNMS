from PyQt5.QtWidgets import QTreeView
from PyQt5.QtGui import QStandardItem, QStandardItemModel

class QDictTreeView(QTreeView):
    
    def __init__(self, data=None):
        super().__init__()
        self.header().hide()
        self.root_model = QStandardItemModel()
        self.setModel(self.root_model)
        if data:
            self.populate_tree(data)

    def populate_tree(self, children, parent=None):
        if not parent:
            parent = self.root_model.invisibleRootItem()
        for child in sorted(children):
            child_item = QStandardItem(child)
            parent.appendRow(child_item)
            if isinstance(children, dict) and bool(list(children)):
                self.populate_tree(children[child], child_item)
                