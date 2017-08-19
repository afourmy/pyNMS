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

from PyQt5.QtWidgets import (
                             QGridLayout, 
                             QLabel,
                             QLineEdit,
                             QWidget
                             )

class CredentialsWindow(QWidget):  

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle('Default credentials')
        
        layout = QGridLayout()
        
        username = QLabel('Default username')
        self.username_edit = QLineEdit('cisco')
        
        password = QLabel('Default password')
        self.password_edit = QLineEdit('cisco')
        self.password_edit.setEchoMode(QLineEdit.Password)
        
        enable_password = QLabel('Default "Enable" password')
        self.enable_password_edit = QLineEdit('cisco')
        self.enable_password_edit.setEchoMode(QLineEdit.Password)
        
        layout = QGridLayout()
        layout.addWidget(username, 0, 0)
        layout.addWidget(self.username_edit, 0, 1)
        layout.addWidget(password, 1, 0)
        layout.addWidget(self.password_edit, 1, 1)
        layout.addWidget(enable_password, 2, 0)
        layout.addWidget(self.enable_password_edit, 2, 1)
        self.setLayout(layout)
        
    def get_default_credentials(self):
        return {
                'username': self.username_edit.text(),
                'password': self.password_edit.text(),
                'secret': self.enable_password_edit.text()
                }
    
        