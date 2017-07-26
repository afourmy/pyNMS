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
from miscellaneous.decorators import update_paths
                                
class BaseMenu(QMenu):
    
    @update_paths(True)
    def __init__(self, controller):
        super().__init__()
                
        self.drawing_action = QAction("Graph drawing algorithms", self)
        drawing_submenu = QMenu("Graph drawing", self)
        for drawing in (
                        'Random drawing', 
                        'Spring-based layout', 
                        'Fruchterman-Reingold layout'
                        ): 
            action = QAction(drawing, self)        
            action.triggered.connect(lambda _, d=drawing: self.graph_drawing(d))
            drawing_submenu.addAction(action)
        self.drawing_action.setMenu(drawing_submenu)
        
    def graph_drawing(self, drawing):
        self.view.random_layout()
        if drawing != 'Random drawing':
            self.view.drawing_algorithm = drawing
            self.view.timer = self.view.startTimer(1)
                        