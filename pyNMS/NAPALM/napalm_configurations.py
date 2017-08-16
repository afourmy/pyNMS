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
from pyQT_widgets.Q_console_edit import QConsoleEdit
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
        QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QInputDialog, QLabel, QLineEdit, QComboBox, QListWidget, QAbstractItemView, QTabWidget, QTextEdit)

class NapalmConfigurations(QTabWidget):

    @update_paths(True)
    def __init__(self, node, controller):
        super().__init__()
        self.node = node
        self.config_edit = {}
        
        for config in ('running', 'startup', 'candidate', 'compare'):
            text_edit = QConsoleEdit()
            self.config_edit[config] = text_edit
            self.addTab(text_edit, '{} config'.format(config.title()))
                
    def update(self):
        for config in ('running', 'startup', 'candidate', 'compare'):
            self.config_edit[config].clear()
            value = self.node.napalm_data['Configuration'][config]
            self.config_edit[config].insertPlainText(value)
                        