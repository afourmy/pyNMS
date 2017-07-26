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

from .base_menu import BaseMenu
from PyQt5.QtWidgets import QMenu, QAction
from graph_generation.multiple_objects import MultipleNodes
                                
class GeneralMenu(BaseMenu):
    
    def __init__(self, controller):
        super().__init__(controller)
    
        # multiple nodes creation
        multiple_nodes = QAction('&Multiple nodes', self)        
        multiple_nodes.triggered.connect(lambda: self.multiple_nodes(event))
        self.addAction(multiple_nodes)
        
        # remove all failures if there is at least one
        if self.network.failed_obj:
            remove_failures = QAction('&Remove all failures', self)        
            remove_failures.triggered.connect(self.remove_all_failures)
            self.addAction(remove_failures)
            self.addSeparator()
    
    def multiple_nodes(self, event):
        self.window = MultipleNodes(event.x(), event.y(), self.controller)
        self.window.show()
                        