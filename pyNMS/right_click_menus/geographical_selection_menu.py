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

from collections import OrderedDict
from .selection_menu import SelectionMenu
from PyQt5.QtWidgets import QMenu, QAction
                                
class GeographicalSelectionMenu(SelectionMenu):
    
    def __init__(self, controller):
        super().__init__(controller)
        
        self.map_action = QAction('Geographical menu', self)
        map_submenu = QMenu('Geographical menu', self)
        
        update_geographical_action = QAction(
            'Update geographical coordinates with current position', self) 
        update_geographical_action.triggered.connect(self.update_geographical_coordinates)
        map_submenu.addAction(update_geographical_action)
        
        update_logical_action = QAction(
            'Update logical coordinates with current position', self) 
        update_logical_action.triggered.connect(self.update_logical_coordinates)
        map_submenu.addAction(update_logical_action)
        
        move_to_geographical_action = QAction(
                                'Move to geographical coordinates', self) 
        move_to_geographical_action.triggered.connect(self.move_to_geographical_coordinates)
        map_submenu.addAction(move_to_geographical_action)
        
        move_to_logical_action = QAction(
                                'Move to logical coordinates', self) 
        move_to_logical_action.triggered.connect(self.move_to_logical_coordinates)
        map_submenu.addAction(move_to_logical_action)
            
        self.map_action.setMenu(map_submenu)
        
    def update_geographical_coordinates(self):
        self.view.update_geographical_coordinates(*self.so)
        
    def update_logical_coordinates(self):
        self.view.update_logical_coordinates(*self.so)
        
    def move_to_geographical_coordinates(self):
        self.view.move_to_geographical_coordinates(*self.so)
        
    def move_to_logical_coordinates(self):
        self.view.move_to_logical_coordinates(*self.so)
        