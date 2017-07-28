from miscellaneous.decorators import update_paths
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
        QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QInputDialog, QLabel, QLineEdit, QComboBox, QListWidget, QAbstractItemView)

class CreateArea(QWidget):
    
    def __init__(self, asm):
        super().__init__()
        self.setWindowTitle('Create area')
        
        area_name = QLabel('Area name')
        area_id = QLabel('Area id')
                
        self.name_edit = QLineEdit()
        self.name_edit.setMaximumWidth(120)
        
        self.id_edit = QLineEdit()
        self.id_edit.setMaximumWidth(120)
        
        # confirmation button
        button_create_area = QPushButton()
        button_create_area.setText('OK')
        button_create_area.clicked.connect(lambda: self.create_area(asm))
        
        # cancel button
        cancel_button = QPushButton()
        cancel_button.setText('Cancel')
        
        # position in the grid
        layout = QGridLayout()
        layout.addWidget(area_name, 0, 0, 1, 1)
        layout.addWidget(self.name_edit, 0, 1, 1, 1)
        layout.addWidget(area_id, 1, 0, 1, 1)
        layout.addWidget(self.id_edit, 1, 1, 1, 1)
        layout.addWidget(button_create_area, 2, 0, 1, 1)
        layout.addWidget(cancel_button, 2, 1, 1, 1)
        self.setLayout(layout)
        
    def create_area(self, asm):
        asm.add_area(self.name_edit.text(), self.id_edit.text())
        self.close()
        
class AreaOperation(QWidget):
    
    # - add objects to an area
    # - remove objects from an area
    
    @update_paths(True)
    def __init__(self, mode, obj, AS=set(), controller=None):
        super().__init__()
        
        title = 'Add to area' if mode == 'add' else 'Remove from area'
        self.setWindowTitle(title)

        values = tuple(map(str, AS))
        
        # list of existing AS
        self.AS_list = QComboBox()
        self.AS_list.addItems(values)
        self.AS_list.activated.connect(self.update_value)
        
        # list of areas
        self.area_list = QComboBox()
        self.update_value()
        
        # confirmation button
        button_area_operation = QPushButton()
        button_area_operation.setText('OK')
        button_area_operation.clicked.connect(lambda: self.area_operation(mode, *obj))
        
        # cancel button
        cancel_button = QPushButton()
        cancel_button.setText('Cancel')
        
        # position in the grid
        layout = QGridLayout()
        layout.addWidget(self.AS_list, 0, 0, 1, 2)
        layout.addWidget(self.area_list, 1, 0, 1, 2)
        layout.addWidget(button_area_operation, 2, 0, 1, 1)
        layout.addWidget(cancel_button, 2, 1, 1, 1)
        self.setLayout(layout)
        
    def update_value(self, index):
        self.area_list.clear()
        selected_AS = self.network.AS_factory(name=self.AS_list.get())
        self.area_list.addItems(tuple(map(str, selected_AS.areas)))
        
    def area_operation(self, mode, *objects):
        selected_AS = self.network.AS_factory(name=self.AS_list.currentText())
        selected_area = self.area_list.currentText()

        if mode == 'add':
            selected_AS.management.add_to_area(selected_area, *objects)
        else:
            selected_AS.management.remove_from_area(selected_area, *objects)
            
        self.close()