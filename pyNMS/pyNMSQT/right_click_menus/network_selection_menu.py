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
from .selection_menu import SelectionMenu
from autonomous_system import AS
from autonomous_system import AS_operations
from autonomous_system import area_operations
from objects.objects import *
import ip_networks.configuration as conf
import ip_networks.troubleshooting as ip_ts
import ip_networks.ping as ip_ping
import ip_networks.switching_table as switching_table
import ip_networks.arp_table as arp_table
import ip_networks.routing_table as ip_rt
import ip_networks.bgp_table as ip_bgpt
from miscellaneous import site_operations
from collections import OrderedDict
from objects.interface_window import InterfaceWindow
                                
class NetworkSelectionMenu(SelectionMenu):
    
    def __init__(self, controller):
        super().__init__(controller)
        
        if self.no_shape:
            simulate_failure = QAction('&Simulate failure', self)        
            simulate_failure.triggered.connect(lambda: self.simulate_failure(*self.so))
            self.addAction(simulate_failure)
            
            remove_failure = QAction('&Remove failure', self)        
            remove_failure.triggered.connect(lambda: self.remove_failure(*self.so))
            self.addAction(remove_failure)
            self.addSeparator()
            
        if self.no_shape:
            create_AS = QAction('Create AS', self)        
            create_AS.triggered.connect(self.create_AS)
            self.addAction(create_AS)

        # at least one AS in the network: add to AS
        if self.network.pnAS and self.no_shape:
            add_to_AS = QAction('Add to AS', self)        
            add_to_AS.triggered.connect(lambda: self.change_AS('add'))
            self.addAction(add_to_AS)
        
        # we compute the set of common AS among all selected objects
        # providing that no shape were selected
        if self.no_shape:
            
            self.common_AS = set(self.network.pnAS.values())  
            cmd = lambda o: o.object.type in ('node', 'plink')
            for obj in filter(cmd, self.so):
                self.common_AS &= obj.object.AS.keys()
            
            # if at least one common AS: remove from AS or manage AS
            if self.common_AS:
                
                manage_AS = QAction('Manage AS', self)        
                manage_AS.triggered.connect(lambda: self.change_AS('manage'))
                self.addAction(manage_AS)
                
                remove_from_AS = QAction('Remove from AS', self)        
                remove_from_AS.triggered.connect(lambda: self.change_AS('remove'))
                self.addAction(remove_from_AS)
                            
                keep = lambda AS: AS.has_area
                self.common_AS_with_area = set(filter(keep, self.common_AS))
                
                # if there is at least one AS with area among all common AS
                # of the current selection, display the area management menu
                if self.common_AS_with_area:
                    add_to_area = QAction('Add to area', self)        
                    add_to_area.triggered.connect(lambda: self.change_area('add'))
                    self.addAction(add_to_area)
                    
                    remove_from_area = QAction('Remove from area', self)        
                    remove_from_area.triggered.connect(lambda: self.change_area('remove'))
                    self.addAction(remove_from_area)

        if self.no_link and self.no_shape:
            self.addAction(self.align_action)
            
        self.addAction(self.drawing_action)
        
    ## AS operations: 
    # - add or remove from an AS
    # - add or remove from an area
    # - create an AS
        
    def change_AS(self, mode):
        objects = set(self.view.get_obj(self.so))
        self.change_AS = AS_operations.ASOperation(mode, objects, self.common_AS, self.controller)
        self.change_AS.show()
        
    def change_area(self, mode):
        objects = set(self.view.get_obj(self.so))
        self.change_area = area_operations.AreaOperation(mode, self.so, self.common_AS, self.controller)
        self.change_area.show()
        
    def create_AS(self):
        nodes = set(self.view.get_obj(self.selected_nodes))
        plinks = set(self.view.get_obj(self.selected_links))
        self.create_AS = AS_operations.ASCreation(nodes, plinks, self.controller)
        self.create_AS.show()
                
    def simulate_failure(self, *objects):
        self.view.simulate_failure(*objects)
        
    def remove_failure(self, *objects):
        self.view.remove_failure(*objects)
            