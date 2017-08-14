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
from .napalm_functions import *
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
        QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QInputDialog, QLabel, QLineEdit, QComboBox, QListWidget, QAbstractItemView, QTabWidget, QTextEdit)

class NapalmActions(QWidget):

    @update_paths(True)
    def __init__(self, napalm_window, node, controller):
        super().__init__()
        self.node = node
        self.napalm_window = napalm_window
        
        napalm_update = QPushButton(self)
        napalm_update.setText('Update')
        napalm_update.clicked.connect(self.update)
        
        napalm_commit = QPushButton(self)
        napalm_commit.setText('Commit')
        napalm_commit.clicked.connect(self.commit)
        
        napalm_discard = QPushButton(self)
        napalm_discard.setText('Discard')
        napalm_discard.clicked.connect(self.discard)
        
        napalm_load_merge = QPushButton(self)
        napalm_load_merge.setText('Load merge candidate')
        napalm_load_merge.clicked.connect(self.load_merge)
        
        napalm_load_replace = QPushButton(self)
        napalm_load_replace.setText('Load replace candidate')
        napalm_load_replace.clicked.connect(self.load_replace)
        
        layout = QGridLayout()
        layout.addWidget(napalm_update, 0, 0)
        layout.addWidget(napalm_commit, 1, 0)
        layout.addWidget(napalm_discard, 2, 0)
        layout.addWidget(napalm_load_merge, 3, 0)
        layout.addWidget(napalm_load_replace, 4, 0)
        self.setLayout(layout)
        
    def update(self):
        standalone_napalm_update(self.node)
        self.napalm_window.update()
        
    def commit(self):
        napalm_commit(self.node)
        self.napalm_window.update()
        
    def discard(self):
        napalm_discard(self.node)
        self.napalm_window.update()
        
    def load_merge(self):
        self.napalm_window.closeEvent(None)
        napalm_load_merge_commit(self.node)
        self.napalm_window.update()
        
    def load_replace(self):
        self.napalm_window.closeEvent(None)
        napalm_load_replace_commit(self.node)
        self.napalm_window.update()

                        