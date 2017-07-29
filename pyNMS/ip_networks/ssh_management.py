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

from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
        QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QInputDialog, QLabel, QLineEdit, QComboBox, QListWidget, QAbstractItemView, QFileDialog)

class SSHManagementWindow(QWidget):
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle('SSH connection management')
        
        username = QLabel('Username')
        self.username_edit = QLineEdit()
        # self.username_edit.setMaximumWidth(120)
        self.username_edit.setText('cisco')
        
        password = QLabel('Password')
        self.password_edit = QLineEdit()
        # self.password_edit.setMaximumWidth(120)
        self.password_edit.setText('cisco')
    
        path_to_putty = QPushButton()
        path_to_putty.setText('Path to PuTTY')
        path_to_putty.clicked.connect(self.choose_path)
        
        self.path_edit = QLineEdit()
        # self.path_edit.setMaximumWidth(120)
        self.path_edit.setText('C:/Users/minto/Desktop/Apps/putty.exe')
        
        layout = QGridLayout()
        layout.addWidget(username, 0, 0, 1, 1)
        layout.addWidget(self.username_edit, 0, 1, 1, 1)
        layout.addWidget(password, 1, 0, 1, 2)
        layout.addWidget(self.password_edit, 1, 1, 1, 1)
        layout.addWidget(path_to_putty, 2, 0, 1, 2)
        layout.addWidget(self.path_edit, 3, 0, 1, 2)
        self.setLayout(layout)

    def choose_path(self):
        path = 'Path to PuTTY'
        filepath = ''.join(QFileDialog.getOpenFileName(self, path, path))
        self.path_edit.setText(filepath)
        self.path = filepath
        
    def get(self):
        return {
                'username': self.username_edit.text(),
                'password': self.password_edit.text(),
                'path': self.path_edit.text()
                }
        