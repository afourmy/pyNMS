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

from PyQt5.QtWidgets import QMenu, QAction
from .general_menu import GeneralMenu

class NetworkGeneralMenu(GeneralMenu):
    
    def __init__(self, event, controller):
        super().__init__(event, controller)
                   
        # find networks
        refresh = QAction('&Refresh', self)        
        refresh.triggered.connect(self.refresh)
        self.addAction(refresh)
        self.addSeparator()
        self.addAction(self.drawing_action)
        
    def graph_drawing(self, drawing):
        self.view.node_selection = set(self.view.all_gnodes())
        super().graph_drawing(drawing)

    def remove_all_failures(self):
        self.view.remove_failures()
        
    def refresh(self):
        self.project.refresh()