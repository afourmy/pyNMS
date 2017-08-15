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
import ip_networks.switching_table as switching_table
import ip_networks.arp_table as arp_table
import ip_networks.routing_table as ip_rt
from sites.site_operations import SiteOperations
from NAPALM.napalm_window import NapalmWindow
from NAPALM.napalm_functions import standalone_napalm_update
from collections import OrderedDict
from objects.interface_window import InterfaceWindow
from subprocess import Popen
                                
class NetworkSelectionMenu(SelectionMenu):
    
    def __init__(self, controller):
        super().__init__(controller)
        
        # exactly one node
        if self.no_link and self.no_shape and self.one_node:
            
            # we retrieve the node
            self.node ,= self.nodes
            
            # configuration + troubleshooting windows
            configuration = QAction('Configuration', self)        
            configuration.triggered.connect(self.configure)
            self.addAction(configuration)
            
            troubleshooting = QAction('Troubleshooting', self)        
            troubleshooting.triggered.connect(self.troubleshoot)
            self.addAction(troubleshooting)
            
            # SSH connection using PuTTY
            ssh_connection = QAction('SSH connection', self)        
            ssh_connection.triggered.connect(self.ssh_connection)
            self.addAction(ssh_connection)
            
            tables = QAction('L2/L3 tables', self)
            tables_submenu = QMenu('L2/L3 tables', self)
            
            if self.node.subtype == 'router':
                
                routing_table = QAction('Routing table', self)        
                routing_table.triggered.connect(self.routing_table)
                tables_submenu.addAction(routing_table)
                
                arp_table = QAction('ARP table', self)        
                arp_table.triggered.connect(self.arp_table)
                tables_submenu.addAction(arp_table)
                
            if self.node.subtype == 'switch':
                
                switching_table = QAction('Switching table', self)        
                switching_table.triggered.connect(self.switching_table)
                tables_submenu.addAction(switching_table)
                
            tables.setMenu(tables_submenu)
            self.addAction(tables)
            self.addSeparator()
        
        # only nodes
        if self.no_shape and self.no_link:
            
            napalm_update = QAction('NAPALM update', self)        
            napalm_update.triggered.connect(self.napalm_update)
            self.addAction(napalm_update)
            
            if self.one_node:
                napalm_data = QAction('NAPALM window', self)        
                napalm_data.triggered.connect(self.napalm_data)
                self.addAction(napalm_data)
            
            self.addSeparator()
            
            # multiple links creation menu
            multiple_links = QAction('Create multiple links', self)        
            multiple_links.triggered.connect(self.multiple_links)
            self.addAction(multiple_links)
            
            self.addSeparator()
        
        if self.no_shape:
            
            simulate_failure = QAction('Simulate failure', self)        
            simulate_failure.triggered.connect(lambda: self.simulate_failure(*self.items))
            self.addAction(simulate_failure)
            
            remove_failure = QAction('Remove failure', self)        
            remove_failure.triggered.connect(lambda: self.remove_failure(*self.items))
            self.addAction(remove_failure)
            
            self.addSeparator()
            
            create_AS = QAction('Create AS', self)        
            create_AS.triggered.connect(self.create_AS)
            self.addAction(create_AS)
            
        # only one link
        if self.no_shape and self.no_node and self.one_link:
            
            # we retrieve the link
            self.link = self.links
            
            interfaces = QAction('Interfaces', self)
            interfaces_submenu = QMenu('Interfaces', self)
            
            source_interface = QAction('Source interface', self)        
            source_interface.triggered.connect(self.source_interface)
            interfaces_submenu.addAction(source_interface)
            
            destination_interface = QAction('Destination interface', self)        
            destination_interface.triggered.connect(self.destination_interface)
            interfaces_submenu.addAction(destination_interface)

            interfaces.setMenu(interfaces_submenu)
            self.addAction(interfaces)
            self.addSeparator()

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
            for obj in filter(cmd, self.items):
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
        
        self.addSeparator()
            
        self.common_sites = set(self.site_network.nodes.values())
        for obj in self.objects:
            self.common_sites &= obj.sites
        
        self.remove_from_site_action = QAction('Remove from site', self)        
        self.remove_from_site_action.triggered.connect(self.remove_from_site)
            
    def configure(self):
        if self.node.subtype == 'router':
            self.config = conf.RouterConfiguration(self.node, self.controller)
        if self.node.subtype == 'switch':
            self.config = conf.SwitchConfiguration(self.node, self.controller)
        self.config.show()
        
    def troubleshoot(self):
        ip_ts.Troubleshooting(self.node, self.controller)
        
    def ssh_connection(self):
        ssh_data = self.controller.ssh_management_window.get()
        ssh_data['IP'] = self.node.ipaddress
        ssh_connection = '{path} -ssh {username}@{IP} -pw {password}'
        connect = Popen(ssh_connection.format(**ssh_data).split())
        
    def routing_table(self):
        self.routing_table = ip_rt.RoutingTable(self.node, self.controller)
        self.routing_table.show()
        
    def switching_table(self):
        self.switching_table = switching_table.SwitchingTable(self.node, self.controller)
        self.switching_table.show()
        
    def arp_table(self):
        self.arp_table = arp_table.ARPTable(self.node, self.controller)
        self.arp_table.show()
        
    ## AS operations: 
    # - add or remove from an AS
    # - add or remove from an area
    # - create an AS
        
    def change_AS(self, mode):
        self.change_AS = AS_operations.ASOperation(mode, self.objects, 
                                            self.common_AS, self.controller)
        self.change_AS.show()
        
    def change_area(self, mode):
        self.change_area = area_operations.AreaOperation(mode, self.objects,
                                            self.common_AS, self.controller)
        self.change_area.show()
        
    def create_AS(self):
        self.create_AS = AS_operations.ASCreation(
                                self.nodes, self.links, self.controller)
        self.create_AS.show()
                
    def simulate_failure(self, *objects):
        self.view.simulate_failure(*objects)
        
    def remove_failure(self, *objects):
        self.view.remove_failure(*objects)
        
    ## NAPALM operations:
    
    def napalm_update(self, _):
        standalone_napalm_update(*self.nodes)
    
    def napalm_data(self, _):
        node ,= self.nodes
        self.napalm_window = NapalmWindow(node, self.controller)
        self.napalm_window.show()
        
    ## Interface
    
    def source_interface(self):
        interface = self.link.interfaceS
        self.interface_window = InterfaceWindow(interface, self.controller)
        self.interface_window.show()
        
    def destination_interface(self):
        interface = self.link.interfaceD
        self.interface_window = InterfaceWindow(interface, self.controller)
        self.interface_window.show()
        
    ## Site operations
    
    def add_to_site(self):
        self.add_window = SiteOperations('add', self.objects, self.all_sites, self.controller)
        self.add_window.show()
        
    ## Multiple links
    
    def multiple_links(self):
        self.multiple_links = MultipleLinks(self.selected_nodes, self.controller)
        self.multiple_links.show()
            