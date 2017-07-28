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
from graph_generation.multiple_objects import MultipleLinks
from objects.object_management_window import ObjectManagementWindow, PropertyChanger
from PyQt5.QtWidgets import QMenu, QAction
                                
class SelectionMenu(BaseMenu):
    
    def __init__(self, controller):
        super().__init__(controller)
        
        # set containing all selected objects: we convert generators into sets
        # because to know if they are empty or not to build the menu
        self.so = set(self.view.scene.selectedItems())
        self.selected_nodes = set(self.view.selected_nodes())
        self.selected_links = set(self.view.selected_links())
        self.no_node = not self.selected_nodes
        self.no_link = not self.selected_links
        self.no_shape = True
        self.one_object = len(self.so) == 1
        self.one_node = len(self.selected_nodes) == 1
        self.one_link = len(self.selected_links) == 1
        self.one_subtype = False
        
        # exactly one object: property window 
        if self.no_shape and self.one_object == 1:
            properties = QAction('Properties', self)        
            properties.triggered.connect(lambda: self.show_object_properties())
            self.addAction(properties)
            self.addSeparator()
        
        # only nodes: 
        if self.no_shape and self.no_link:
                        
            self.align_action = QAction("Alignment", self)
            align_submenu = QMenu("Alignment", self)
            for method in ('Horizontal alignment', 'Vertical alignment'):
                action = QAction(method, self) 
                action.triggered.connect(lambda _, m=method: self.align(m))
                align_submenu.addAction(action)
            for method in ('Horizontal distribution', 'Vertical distribution'):
                action = QAction(method, self) 
                action.triggered.connect(lambda _, m=method: self.distribute(m))
                align_submenu.addAction(action)
            self.align_action.setMenu(align_submenu)
            
            # multiple links creation menu
            multiple_links = QAction('Create multiple links', self)        
            multiple_links.triggered.connect(self.multiple_links)
            self.addAction(multiple_links)
            self.addSeparator()
            
        change_property = QAction('Change property', self)        
        change_property.triggered.connect(self.change_property)
        self.addAction(change_property)
        self.addSeparator()
        
        # at least one object: deletion and property changer
        delete_objects = QAction('Delete', self)        
        delete_objects.triggered.connect(self.delete_objects)
        self.addAction(delete_objects)
        self.addSeparator()
        
    def graph_drawing(self, drawing):
        self.view.node_selection = self.selected_nodes
        super().graph_drawing(drawing)
        
    def show_object_properties(self):
        obj ,= self.so
        self.properties = ObjectManagementWindow(obj.object, self.controller)
        self.properties.show()
            
    def change_property(self):
        pass
        # objects = set(objects)
        # PropertyChanger(objects, subtype, self.controller)
                
    def delete_objects(self, _):
        self.view.remove_objects(*self.so)
        
    def multiple_links(self):
        self.multiple_links = MultipleLinks(self.selected_nodes, self.controller)
        self.multiple_links.show()
        
    def align(self, method):
        horizontal = method == 'Horizontal alignment'
        self.view.align(self.selected_nodes, horizontal)
        
    def distribute(self, method):
        horizontal = method == 'Horizontal distribution'
        self.view.distribute(self.selected_nodes, horizontal)
                
                        