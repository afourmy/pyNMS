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
        so = set(self.view.scene.selectedItems())
        exitAction = QAction('&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(lambda: _)
        self.addAction(exitAction)
        
        self.selected_nodes = set(filter(lambda o: o.Qtype == 'node', so))
        self.selected_links = set(filter(lambda o: o.Qtype == 'link', so))
        self.no_node = not self.selected_nodes
        self.no_link = not self.selected_links

        print(self.selected_nodes, self.selected_links, self.no_node)
        # 
        # # useful booleans
        # self.no_node = not self.view.so['node']
        # self.no_link = not self.view.so['link']
        # self.no_shape = not self.view.so['shape']
        # self.one_node = len(self.view.so['node']) == 1
        # self.one_link = len(self.view.so['link']) == 1
        #                     
        # # exactly one object: property window 
        # if self.no_shape and len(self.all_so) == 1:
        #     self.add_command(label='Properties', 
        #                 command=lambda: self.show_object_properties())
        #     self.add_separator()
        # 
        # if self.no_shape:
        #     self.add_command(label='Simulate failure', 
        #                     command=lambda: self.simulate_failure(*self.all_so))
        #     self.add_command(label='Remove failure', 
        #                     command=lambda: self.remove_failure(*self.all_so))
        #     
        #     self.add_separator()
        #     
        # # only nodes: 
        # if self.no_shape and self.no_link:
        #     
        #     # alignment submenu
        #     self.add_cascade(label='Align nodes', 
        #                     menu=AlignmentMenu(self.view, self.view.so['node']))
        #     self.add_separator()
        #     
        #     # map submenu
        #     self.add_cascade(label='Map menu', 
        #                     menu=MapMenu(self.view, self.view.so['node']))
        #     self.add_separator()
        #     
        #     # multiple links creation menu
        #     self.add_command(label='Create multiple links', 
        #                         command=lambda: self.multiple_links(self.view))
        #     self.add_separator()
        #     
        #     # only one subtype of nodes
        #     if self.view.so['node']:
        #         for subtype in node_subtype:
        #             ftr = lambda o, st=subtype: o.subtype == st
        #             if self.view.so['node'] == set(filter(ftr, self.view.so['node'])):
        #                 self.add_cascade(label='Change property', 
        #                             command= lambda: self.change_property(
        #                                                     self.view.so['node'],
        #                                                     subtype
        #                                                     )
        #                                 )
        #                 self.add_separator()
        #     
        # # only one subtype of link: property changer
        # if self.no_node and self.no_shape:
        #     for subtype in link_subtype:
        #         ftr = lambda o, st=subtype: o.subtype == st
        #         if self.view.so['link'] == set(filter(ftr, self.view.so['link'])):
        #             self.add_cascade(label='Change property', 
        #                         command= lambda: self.change_property(
        #                                                 self.view.so['link'],
        #                                                 subtype
        #                                                 )
        #                             )
        #             self.add_separator()
        # 
        # # we allow to delete if the menu was generated from the view
        # # (and not the treeview which view cannot be easily updated)
        # if from_view:
        #     # at least one object: deletion or create AS
        #     self.add_command(label='Delete', 
        #                         command=lambda: self.remove_objects())
    
    def empty_selection_and_destroy_menu(function):
        def wrapper(self, *others):
            function(self, *others)
            self.view.unhighlight_all()
            self.destroy()
        return wrapper
        
    @empty_selection_and_destroy_menu
    def remove_objects(self):
        self.view.remove_objects(*self.all_so)
                
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
    def change_property(self, objects, subtype):
        objects = set(objects)
        PropertyChanger(objects, subtype, self.controller)
        
    @empty_selection_and_destroy_menu
    def multiple_links(self, view):
        mobj.MultipleLinks(set(self.view.so['node']), self.controller)
                