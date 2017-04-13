# NetDim (contact@netdim.fr)

import os
import tkinter as tk
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
from automation.send_script import SendScript
from miscellaneous import site_operations
from .alignment_menu import AlignmentMenu
from .map_menu import MapMenu
from objects.object_management_window import PropertyChanger
from collections import OrderedDict
from objects.interface_window import InterfaceWindow
from .base_selection_rightclick_menu import BaseSelectionRightClickMenu
                                
class NetworkSelectionRightClickMenu(BaseSelectionRightClickMenu):
    def __init__(self, event, controller, from_scenario=True):
        super().__init__(event, controller, from_scenario)
            
        # exacly one node and one physical link: menu for the associated interface
        if self.one_node and self.one_link:
            link ,= self.scenario.so['link']
            if link.type == 'plink':
                node ,= self.scenario.so['node']
                interface = link('interface', node)
                self.add_command(label='Interface menu', 
                    command=lambda: InterfaceWindow(self.controller, interface))
                self.add_separator()
                
        # exactly one node: configuration menu
        if self.no_link and self.no_shape and self.one_node:
            node ,= self.scenario.so['node']
            
            self.add_command(label='Configuration', 
                        command=lambda: self.configure(node))
            self.add_command(label='Troubleshooting', 
                        command=lambda: self.troubleshoot(node))
                        
            self.add_separator()
            
            self.add_command(label='SSH connection', 
                        command=lambda: self.connection(node))
                        
            # tables menu 
            menu_tables = tk.Menu(self, tearoff=0)
                        
            if node.subtype == 'router':
                menu_tables.add_command(label='Routing table', 
                            command=lambda: self.routing_table(node))
                menu_tables.add_command(label='BGP table', 
                            command=lambda: self.bgp_table(node))
                menu_tables.add_command(label='ARP table', 
                                command=lambda: self.arp_table(node))
                self.add_command(label='Ping', 
                            command=lambda: self.ping(node))
                self.add_cascade(label='Tables', menu=menu_tables)
                            
            if node.subtype == 'switch':
                menu_tables.add_command(label='Switching table', 
                            command=lambda: self.switching_table(node))
                self.add_cascade(label='Tables', menu=menu_tables)

            self.add_separator()
            
        # only nodes: procedure to send a script to all selected devices
        if self.no_shape and self.no_link:
            self.add_command(label='Send a script', 
                        command=lambda: self.send_script(self.all_so))
                        
            self.add_separator()
        
        if self.no_shape:
            self.add_command(label='Create AS', 
                            command=lambda: self.create_AS()) 
      
        # at least one AS in the network: add to AS
        if self.network.pnAS and self.no_shape:
            self.add_command(label='Add to AS', 
                        command=lambda: self.change_AS('add'))
        
        # we compute the set of common AS among all selected objects
        # providing that no shape were selected
        if self.no_shape:
            self.common_AS = set(self.network.pnAS.values())  
            cmd = lambda o: o.type in ('node', 'plink')
            for obj in filter(cmd, self.all_so):
                self.common_AS &= obj.AS.keys()
                
            self.common_sites = set(self.network.ftr('node', 'site'))
            for obj in self.all_so:
                self.common_sites &= obj.sites
            
        # if at least one common AS: remove from AS or manage AS
            if self.common_AS:
                self.add_command(label='Manage AS', 
                            command=lambda: self.change_AS('manage'))
                self.add_command(label='Remove from AS', 
                            command=lambda: self.change_AS('remove'))
                            
                keep = lambda AS: AS.has_area
                self.common_AS_with_area = set(filter(keep, self.common_AS))
                
                # if there is at least one AS with area among all common AS
                # of the current selection, display the area management menu
                if self.common_AS_with_area:
                    self.add_command(label='Add to area', 
                                command=lambda: self.change_area('add'))
                    self.add_command(label='Remove from area', 
                                command=lambda: self.change_area('remove'))
                        
                self.add_separator()
            
            if set(self.site_network.nodes.values()):
                self.add_command(label='Add to site', command=self.add_to_site)
                
                if self.common_sites:
                    self.add_command(label='Remove from site', 
                                                command=self.remove_from_site)  
                self.add_separator()
        
        # exactly one physical link: 
        if self.no_node and self.no_shape and self.one_link:
            plink ,= self.scenario.so['link']
            # failure simulation menu
            if plink.type == 'plink':                        
                # interface menu 
                menu_interfaces = tk.Menu(self, tearoff=0)
                source_if = plink('interface', plink.source)
                menu_interfaces.add_command(label='Source interface', 
                command=lambda: InterfaceWindow(self.controller, source_if))
                destination_if = plink('interface', plink.destination)
                menu_interfaces.add_command(label='Destination interface', 
                command=lambda: InterfaceWindow(self.controller, destination_if))
                self.add_cascade(label='Interface menu', menu=menu_interfaces)
            
        # make the menu appear    
        self.tk_popup(event.x_root, event.y_root)
    
    def empty_selection_and_destroy_menu(function):
        def wrapper(self, *others):
            function(self, *others)
            self.scenario.unhighlight_all()
            self.destroy()
        return wrapper
        
    @empty_selection_and_destroy_menu
    def remove_objects(self):
        self.scenario.remove_objects(*self.all_so)
        
    @empty_selection_and_destroy_menu
    def change_AS(self, mode):
        AS.ASOperation(self.scenario, mode, self.all_so, self.common_AS)
        
    @empty_selection_and_destroy_menu
    def change_area(self, mode):
        AS.AreaOperation(self.scenario, mode, self.all_so, self.common_AS)
        
    @empty_selection_and_destroy_menu
    def simulate_failure(self, *objects):
        self.scenario.simulate_failure(*objects)
        
    @empty_selection_and_destroy_menu
    def remove_failure(self, *objects):
        self.scenario.remove_failure(*objects)
        
    @empty_selection_and_destroy_menu
    def arp_table(self, node):
        arp_table.ARPTable(node, self.scenario)
        
    @empty_selection_and_destroy_menu
    def switching_table(self, node):
        switching_table.SwitchingTable(node, self.scenario)
        
    @empty_selection_and_destroy_menu
    def routing_table(self, node):
        ip_rt.RoutingTable(node, self.scenario)
        
    @empty_selection_and_destroy_menu
    def bgp_table(self, node):
        ip_bgpt.BGPTable(node, self.scenario)
        
    @empty_selection_and_destroy_menu
    def configure(self, node):
        if node.subtype == 'router':
            conf.RouterConfiguration(node, self.scenario)
        if node.subtype == 'switch':
            conf.SwitchConfiguration(node, self.scenario)
        
    @empty_selection_and_destroy_menu
    def troubleshoot(self, node):
        ip_ts.Troubleshooting(node, self.scenario)
        
    @empty_selection_and_destroy_menu
    def send_script(self, nodes):
        SendScript(self.scenario, nodes)
        
    @empty_selection_and_destroy_menu
    def connection(self, node):
        ssh_data = self.controller.ssh_management_window.get()
        ssh_data['IP'] = node.ipaddress
        ssh_connection = '{path} -ssh {username}@{IP} -pw {password}'
        os.system(ssh_connection.format(**ssh_data))
        
    @empty_selection_and_destroy_menu
    def ping(self, node):
        ip_ping.Ping(node, self.scenario)
        
    @empty_selection_and_destroy_menu
    def enter_site(self, site):
        self.controller.view_menu.enter_site(site)
        
    @empty_selection_and_destroy_menu
    def add_to_site(self):
        site_operations.SiteOperations(self.scenario, 'add', self.all_so)
        
    @empty_selection_and_destroy_menu
    def remove_from_site(self):
        site_operations.SiteOperations(self.scenario, 'remove', self.all_so, 
                                                            self.common_sites)
        
    @empty_selection_and_destroy_menu
    def bgp(self, node):
        self.network.BGPT_builder(node)
        
    @empty_selection_and_destroy_menu
    def create_AS(self):
        nodes, plinks = set(self.scenario.so['node']), set(self.scenario.so['link'])
        AS.ASCreation(self.scenario, nodes, plinks)
        