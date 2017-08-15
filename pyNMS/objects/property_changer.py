from objects.objects import object_properties
from objects.properties import pretty_name_to_class
from miscellaneous.decorators import update_paths
from PyQt5.QtWidgets import (
                             QCheckBox, 
                             QComboBox,
                             QGridLayout, 
                             QGroupBox,
                             QPushButton,
                             QWidget, 
                             QLineEdit
                             )
                
class PropertyChanger(QWidget):
                                 
    @update_paths(True)
    def __init__(self, objects, type, controller):
        super().__init__()
        
        # list of properties
        self.property_list = QComboBox()
        self.property_list.addItems(map(str, object_properties[type]))
                            
        self.value_edit = QLineEdit()

        confirmation_button = QPushButton()
        confirmation_button.setText('OK')
        confirmation_button.clicked.connect(lambda: self.confirm(objects))
                                       
        # position in the grid
        layout = QGridLayout()
        layout.addWidget(self.property_list, 0, 0)
        layout.addWidget(self.value_edit, 1, 0)
        layout.addWidget(confirmation_button, 2, 0)
        self.setLayout(layout)
        
    def confirm(self, objects):
        selected_property = pretty_name_to_class[self.property_list.currentText()]
        str_value = self.value_edit.text()
        value = self.network.prop_to_type[selected_property.name](str_value)
        for object in objects:
            setattr(object, selected_property.name, value)
        self.close()