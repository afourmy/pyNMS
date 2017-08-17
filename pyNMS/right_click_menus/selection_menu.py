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
from objects.object_management_window import ObjectManagementWindow
from objects.property_changer import PropertyChanger
from PyQt5.QtWidgets import QMenu, QAction
                                
class SelectionMenu(BaseMenu):
    
    def __init__(self, controller):
        super().__init__(controller)
        
        # set containing all selected objects: we convert generators into sets
        # because to know if they are empty or not to build the menu
        self.items = set(self.view.scene.selectedItems())
        self.objects = set(self.view.get_obj(self.items))
        self.gnodes = set(self.view.selected_nodes())
        self.nodes = set(self.view.get_obj(self.gnodes))
        self.glinks = set(self.view.selected_links())
        self.links = set(self.view.get_obj(self.glinks))
        self.no_node = not self.gnodes
        self.no_link = not self.glinks
        self.no_shape = True
        self.one_object = len(self.items) == 1
        self.one_node = len(self.gnodes) == 1
        self.one_link = len(self.glinks) == 1
        self.one_subtype = len(set(map(lambda obj: obj.subtype, self.objects))) == 1
        
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
            self.addSeparator()
            
        if self.one_subtype:
            self.subtype ,= set(map(lambda obj: obj.subtype, self.objects))
            change_property = QAction('Change property', self)        
            change_property.triggered.connect(self.change_property)
            self.addAction(change_property)
            self.addSeparator()
        
        delete_objects = QAction('Delete', self)        
        delete_objects.triggered.connect(self.delete_objects)
        self.addAction(delete_objects)
        self.addSeparator()
        
    def graph_drawing(self, drawing):
        self.view.node_selection = self.gnodes or self.view.all_gnodes()
        super().graph_drawing(drawing)
        
    def show_object_properties(self):
        obj ,= self.objects
        self.properties = ObjectManagementWindow(obj, self.controller)
        self.properties.show()
            
    def change_property(self):
        self.property_changer = PropertyChanger(self.objects, self.subtype, self.controller)
        self.property_changer.show()
                
    def delete_objects(self, _):
        self.view.remove_objects(*self.items)
        
    def align(self, method):
        horizontal = method == 'Horizontal alignment'
        self.view.align(self.gnodes, horizontal)
        
    def distribute(self, method):
        horizontal = method == 'Horizontal distribution'
        self.view.distribute(self.gnodes, horizontal)
                
                        