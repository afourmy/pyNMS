# Copyright (C) 2017 Antoine Fourmy <antoine dot fourmy at gmail dot com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from miscellaneous.decorators import update_paths
from pyQT_widgets.Q_console_edit import QConsoleEdit
from PyQt5.QtWidgets import QGridLayout, QPushButton, QWidget
from warnings import warn
try:
    from netmiko import ConnectHandler
except ImportError:
    warn('netmiko not installed')
try:
    from jinja2 import Template
except ImportError:
    warn('jinja2 not installed')

class SendScriptWindow(QWidget):
    
    # this window is a console which content will be convert it into a 
    # jinja2 template before being sent to the device
    
    @update_paths
    def __init__(self, nodes, controller):
        super().__init__()
        self.nodes = nodes
        
        self.setWindowTitle('Send a Jinja2 script')
        self.setMinimumSize(1000, 500)
        
        self.script_content_edit = QConsoleEdit()
        
        send_button = QPushButton('Send script')
        send_button.clicked.connect(self.send_script)
                                        
        layout = QGridLayout()
        layout.addWidget(self.script_content_edit, 0, 0)
        layout.addWidget(send_button, 1, 0)
        self.setLayout(layout)
        
    def send_script(self):
        config = self.script_content_edit.toPlainText()
        for node in self.nodes:
            # log in to the device
            credentials = self.network.get_credentials(node)
            connection_parameters = {
                'device_type': node.operating_system,
                'ip': node.ip_address,
                # credentials to log in to the device
                'username': credentials['username'], 
                'password': credentials['password'], 
                'secret': credentials['enable_password']
            }
            net_connect = ConnectHandler(**connection_parameters)
            
            # turn the script into a Jinja2 template
            j2_config = Template(config).render(**node.__dict__)
            
            # send the script line per line
            for line in j2_config.splitlines():
                print(line)
                net_connect.send_command(line)
                
            # log out
            net_connect.disconnect()
            
                                            