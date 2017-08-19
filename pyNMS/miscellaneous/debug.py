from miscellaneous.decorators import update_paths
from PyQt5.QtWidgets import (
                             QGridLayout, 
                             QTextEdit,
                             QPushButton, 
                             QWidget, 
                             QLabel, 
                             QLineEdit, 
                             QComboBox
                             )

class DebugWindow(QWidget):
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle('Debug')
        
        values = (
                  'Objects',
                  'Nodes',
                  'Physical links',
                  'L2 links',
                  'L3 links',
                  'Traffic links',
                  'Interfaces',
                  'AS',
                  'IP addresses'
                  )
        
        self.debug_list = QComboBox()
        self.debug_list.addItems(values)
        self.debug_list.activated.connect(self.debug)
        self.debug_edit = QLineEdit()
        
        query_button = QPushButton()
        query_button.setText('OK')
        query_button.clicked.connect(self.query_pynms)
        
        self.debug_result = QTextEdit()
        
        # position in the grid
        layout = QGridLayout()
        layout.addWidget(self.debug_list, 0, 0)
        layout.addWidget(self.debug_edit, 0, 1)
        layout.addWidget(query_button, 0, 2)
        layout.addWidget(self.debug_result, 1, 0, 1, 3)
        self.setLayout(layout)
        
    def query_pynms(self, _):
        query = self.debug_edit.text()
        query_result = eval(query)
        self.debug_result.clear()
        self.debug_result.insertPlainText(str(query_result))
        
    @update_paths
    def debug(self, _):
        self.debug_result.clear()
        value = self.debug_list.currentText()
        if value == 'Objects':
            query_result = eval('self.view.object_id_to_object')
        elif value == 'Nodes':
            query_result = eval('self.main_network.nodes')
        elif value == 'Physical links':
            query_result = eval('self.main_network.plinks')
        elif value == 'L2 links':
            query_result = eval('self.main_network.l2links')
        elif value == 'L3 links':
            query_result = eval('self.main_network.l3links')
        elif value == 'Traffic links':
            query_result = eval('self.main_network.traffics')
        elif value == 'Interfaces':
            query_result = eval('self.main_network.interfaces')
        elif value == 'IP addresses':
            query_result = eval('self.main_network.ip_to_oip')
        else:
            query_result = ''
            # for AS, more details
            for AS in self.main_network.pnAS.values():
                query_result += '''AS name: {name}
AS type: {type}
AS id: {id}
AS nodes: {nodes}
AS links: {links}
                '''.format(
                           name = AS.name, 
                           type = AS.AS_type, 
                           id = AS.id,
                           nodes = AS.nodes,
                           links = AS.links
                           )
        self.debug_result.insertPlainText(str(query_result))