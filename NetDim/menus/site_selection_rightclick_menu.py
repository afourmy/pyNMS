# NetDim
# Copyright (C) 2017 Antoine Fourmy (contact@netdim.fr)
# Released under the GNU General Public License GPLv3

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
from miscellaneous import site_operations
from .alignment_menu import AlignmentMenu
from .map_menu import MapMenu
from objects.object_management_window import PropertyChanger
from collections import OrderedDict
from objects.interface_window import InterfaceWindow
from .base_selection_rightclick_menu import BaseSelectionRightClickMenu
                                
class SiteSelectionRightClickMenu(BaseSelectionRightClickMenu):
    def __init__(self, event, scenario, from_scenario=True):
        super().__init__(event, scenario, from_scenario)
        self.cs = scenario
            
        # exacly one node and one physical link: menu for the associated interface
        if self.one_node and self.one_link:
            link ,= self.cs.so['link']
            if link.type == 'plink':
                node ,= self.cs.so['node']
                interface = link('interface', node)
                self.add_command(label='Interface menu', 
                    command=lambda: InterfaceWindow(self.cs.master, interface))
                self.add_separator()
                
        # exactly one node: configuration menu
        if self.no_link and self.no_shape and self.one_node:
            node ,= self.cs.so['node']
            
            self.add_command(label='Enter site', 
                        command=lambda: self.enter_site(node))
            self.add_separator()
            
        # make the menu appear    
        self.tk_popup(event.x_root, event.y_root)
    
    def empty_selection_and_destroy_menu(function):
        def wrapper(self, *others):
            function(self, *others)
            self.cs.unhighlight_all()
            self.destroy()
        return wrapper
        
    @empty_selection_and_destroy_menu
    def remove_objects(self):
        self.cs.remove_objects(*self.all_so)
        
    @empty_selection_and_destroy_menu
    def change_AS(self, mode):
        AS.ASOperation(self.cs, mode, self.all_so, self.common_AS)
        
    @empty_selection_and_destroy_menu
    def change_area(self, mode):
        AS.AreaOperation(self.cs, mode, self.all_so, self.common_AS)
        
    @empty_selection_and_destroy_menu
    def simulate_failure(self, *objects):
        self.cs.simulate_failure(*objects)
        
    @empty_selection_and_destroy_menu
    def remove_failure(self, *objects):
        self.cs.remove_failure(*objects)
        
    @empty_selection_and_destroy_menu
    def arp_table(self, node):
        arp_table.ARPTable(node, self.cs)
        
    @empty_selection_and_destroy_menu
    def switching_table(self, node):
        switching_table.SwitchingTable(node, self.cs)
        
    @empty_selection_and_destroy_menu
    def routing_table(self, node):
        ip_rt.RoutingTable(node, self.cs)
        
    @empty_selection_and_destroy_menu
    def bgp_table(self, node):
        ip_bgpt.BGPTable(node, self.cs)
        
    @empty_selection_and_destroy_menu
    def configure(self, node):
        if node.subtype == 'router':
            conf.RouterConfiguration(node, self.cs)
        if node.subtype == 'switch':
            conf.SwitchConfiguration(node, self.cs)
        
    @empty_selection_and_destroy_menu
    def troubleshoot(self, node):
        ip_ts.Troubleshooting(node, self.cs)
        
    @empty_selection_and_destroy_menu
    def connection(self, node):
        ssh_data = self.cs.ms.ssh_management_window.get()
        ssh_data['IP'] = node.ipaddress
        ssh_connection = '{path} -ssh {username}@{IP} -pw {password}'
        os.system(ssh_connection.format(**ssh_data))
        
    @empty_selection_and_destroy_menu
    def ping(self, node):
        ip_ping.Ping(node, self.cs)
    
    @empty_selection_and_destroy_menu
    def show_object_properties(self):
        so ,= self.all_so
        self.cs.master.dict_obj_mgmt_window[so.subtype].current_obj = so
        self.cs.master.dict_obj_mgmt_window[so.subtype].update()
        self.cs.master.dict_obj_mgmt_window[so.subtype].deiconify()
        
    @empty_selection_and_destroy_menu
    def change_property(self, objects, subtype):
        objects = set(objects)
        PropertyChanger(self.cs.ms, objects, subtype)
        
    @empty_selection_and_destroy_menu
    def multiple_links(self, scenario):
        mobj.MultipleLinks(scenario, set(self.cs.so['node']))
        
    @empty_selection_and_destroy_menu
    def enter_site(self, site):
        self.cs.ms.view_menu.enter_site(site)
        
    @empty_selection_and_destroy_menu
    def add_to_site(self):
        site_operations.SiteOperations(self.cs, 'add', self.all_so)
        
    @empty_selection_and_destroy_menu
    def remove_from_site(self):
        site_operations.SiteOperations(self.cs, 'remove', self.all_so, 
                                                            self.common_sites)
        
    @empty_selection_and_destroy_menu
    def bgp(self, node):
        self.cs.ntw.BGPT_builder(node)
        
    @empty_selection_and_destroy_menu
    def create_AS(self):
        nodes, plinks = set(self.cs.so['node']), set(self.cs.so['link'])
        AS.ASCreation(self.cs, nodes, plinks)
        