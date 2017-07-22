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

import os
from PyQt5.QtWidgets import QMenu, QAction
from autonomous_system import AS
from objects.objects import *
import ip_networks.configuration as conf
import ip_networks.troubleshooting as ip_ts
import ip_networks.ping as ip_ping
import ip_networks.switching_table as switching_table
import ip_networks.arp_table as arp_table
import ip_networks.routing_table as ip_rt
import ip_networks.bgp_table as ip_bgpt
import graph_generation.multiple_objects as mobj
from pythonic_tkinter.preconfigured_widgets import Menu
from miscellaneous import site_operations
from .alignment_menu import AlignmentMenu
from .map_menu import MapMenu
from objects.object_management_window import ObjectManagementWindow, PropertyChanger
from collections import OrderedDict
from objects.interface_window import InterfaceWindow
from miscellaneous.decorators import *
                                
class BaseSelectionRightClickMenu(QMenu):
    
    @update_paths(True)
    def __init__(self, controller):
        super().__init__()
        
        # set containing all selected objects
        self.so = set(self.view.scene.selectedItems())
        self.selected_nodes = set(filter(self.view.is_node, self.so))
        self.selected_links = set(filter(self.view.is_link, self.so))
        self.no_node = not self.selected_nodes
        self.no_link = not self.selected_links
        self.no_shape = True
        self.one_object = len(self.so) == 1
        self.one_node = len(self.selected_nodes) == 1
        self.one_link = len(self.selected_links) == 1
        self.one_subtype = False
               
        # exactly one object: property window 
        if self.no_shape and self.one_object == 1:
            properties = QAction('&Properties', self)        
            properties.triggered.connect(lambda: lambda: self.show_object_properties())
            self.addAction(properties)
            self.addSeparator()
        
        if self.no_shape:
            simulate_failure = QAction('&Simulate failure', self)        
            simulate_failure.triggered.connect(lambda: self.simulate_failure(*self.so))
            self.addAction(simulate_failure)
            remove_failure = QAction('&Remove failure', self)        
            remove_failure.triggered.connect(lambda: self.remove_failure(*self.so))
            self.addAction(remove_failure)
            self.addSeparator()
            
        # only nodes: 
        if self.no_shape and self.no_link:
            
            # alignment submenu
            align_nodes = QAction('&Align nodes', self)        
            align_nodes.triggered.connect(self.align)
            self.addAction(align_nodes)
            self.addSeparator()
            
            # map submenu
            # map_menu = QAction('&Map menu', self)        
            # map_menu.triggered.connect(MapMenu(self.view, self.selected_nodes))
            # self.addAction(map_menu)
            # self.addSeparator()
            
            # multiple links creation menu
            multiple_links = QAction('&Create multiple links', self)        
            multiple_links.triggered.connect(lambda: self.multiple_links(self.view))
            self.addAction(multiple_links)
            self.addSeparator()

        change_property = QAction('&Change property', self)        
        change_property.triggered.connect(self.change_property)
        self.addAction(change_property)
        self.addSeparator()
        
        # at least one object: deletion and property changer
        delete_objects = QAction('&Delete', self)        
        delete_objects.triggered.connect(self.delete_objects)
        self.addAction(delete_objects)
        self.addSeparator()
        
    def change_property(self):
        pass
        # objects = set(objects)
        # PropertyChanger(objects, subtype, self.controller)
        
    def align(self):
        AlignmentMenu(self.view, self.selected_nodes)
        
    def delete_objects(self, _):
        self.view.remove_objects(*self.so)
                
    @empty_selection_and_destroy_menu
    def simulate_failure(self, *objects):
        self.view.simulate_failure(*objects)
        
    @empty_selection_and_destroy_menu
    def remove_failure(self, *objects):
        self.view.remove_failure(*objects)
            
    @empty_selection_and_destroy_menu
    def show_object_properties(self):
        so ,= self.all_so
        ObjectManagementWindow(so, self.controller)
        
    @empty_selection_and_destroy_menu
    def multiple_links(self, view):
        mobj.MultipleLinks(set(self.view.so['node']), self.controller)
                