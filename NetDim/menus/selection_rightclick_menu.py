# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk
from autonomous_system import AS
import ip_networks.configuration as conf
import ip_networks.troubleshooting as ip_ts
import ip_networks.ping as ip_ping
import ip_networks.switching_table as switching_table
import ip_networks.arp_table as arp_table
import ip_networks.routing_table as ip_rt
import ip_networks.bgp_table as ip_bgpt
import graph_generation.multiple_objects as mobj
from .alignment_menu import AlignmentMenu
from objects.object_management_window import PropertyChanger
from collections import OrderedDict
from objects.interface_window import InterfaceWindow
                                
class SelectionRightClickMenu(tk.Menu):
    def __init__(self, event, scenario):
        super().__init__(tearoff=0)
        self.cs = scenario
        
        x, y = self.cs.cvs.canvasx(event.x), self.cs.cvs.canvasy(event.y)

        closest_obj = self.cs.cvs.find_closest(x, y)[0]
        selected_obj = self.cs.object_id_to_object[closest_obj]
        # if the object from which the menu was started does not belong to
        # the current selection, it means the current selection is no longer
        # to be considered, and only the selected objected is considered 
        # as having been selected by the user
                
        if selected_obj not in self.cs.so[selected_obj.class_type]:
            # we empty / unhighlight the selection
            self.cs.unhighlight_all()
            self.cs.highlight_objects(selected_obj)
            
        self.all_so = self.cs.so['node'] | self.cs.so['link']
                            
        # exactly one object: property window 
        if (len(self.cs.so['node']) == 1 and not self.cs.so['link']
            or len(self.cs.so['link']) == 1 and not self.cs.so['node']):
            self.add_command(label='Properties', 
                        command=lambda: self.show_object_properties())
            self.add_separator()
            
        # exacly one node and one physical link: menu for the associated interface
        if len(self.cs.so['node']) == 1 and len(self.cs.so['link']) == 1:
            link ,= self.cs.so['link']
            if link.type == 'plink':
                node ,= self.cs.so['node']
                interface = link('interface', node)
                self.add_command(label='Interface menu', 
                    command=lambda: InterfaceWindow(self.cs.master, interface))
                self.add_separator()
                
        # exactly one node: configuration menu
        if not self.cs.so['link'] and len(self.cs.so['node']) == 1:
            node ,= self.cs.so['node']
            
            self.add_command(label='Configuration', 
                        command=lambda: self.configure(node))
            self.add_command(label='Troubleshooting', 
                        command=lambda: self.troubleshoot(node))
                        
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
                            
            if node.subtype == 'switch':
                menu_tables.add_command(label='Switching table', 
                            command=lambda: self.switching_table(node))
                            
            self.add_cascade(label='Tables', menu=menu_tables)

            self.add_separator()
        
        self.add_command(label='Create AS', 
                            command=lambda: self.create_AS()) 
      
        # at least one AS in the network: add to AS
        if self.cs.ntw.pnAS:
            self.add_command(label='Add to AS', 
                        command=lambda: self.change_AS('add'))
        
        # we compute the set of common AS among all selected objects
        self.common_AS = set(self.cs.ntw.pnAS.values())  
        cmd = lambda o: o.type in ('node', 'plink')
        for obj in filter(cmd, self.all_so):
            self.common_AS &= obj.AS.keys()
            
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
        
        # exactly one physical link: 
        if not self.cs.so['node'] and len(self.cs.so['link']) == 1:
            plink ,= self.cs.so['link']
            # failure simulation menu
            if plink.type == 'plink':
                self.add_command(label='Simulate failure', 
                        command=lambda: self.simulate_failure(plink))
                if plink in self.cs.ntw.fdtks:
                    self.add_command(label='Remove failure', 
                        command=lambda: self.remove_failure(plink))
                        
                # interface menu 
                menu_interfaces = tk.Menu(self, tearoff=0)
                source_if = plink('interface', plink.source)
                menu_interfaces.add_command(label='Source interface', 
                command=lambda: InterfaceWindow(self.cs.master, source_if))
                destination_if = plink('interface', plink.destination)
                menu_interfaces.add_command(label='Destination interface', 
                command=lambda: InterfaceWindow(self.cs.master, destination_if))
                self.add_cascade(label='Interface menu', menu=menu_interfaces)
            
        # only nodes: 
        if not self.cs.so['link']:
            
            # alignment submenu
            self.add_cascade(label='Align nodes', 
                            menu=AlignmentMenu(self.cs, self.cs.so['node']))
            self.add_separator()
            
            # multiple links creation menu
            self.add_command(label='Create multiple links', 
                                command=lambda: self.multiple_links(self.cs))
            self.add_separator()
            
            # only one subtype of nodes
            if self.cs.so['node']:
                for subtype in self.cs.ntw.node_subtype:
                    ftr = lambda o, st=subtype: o.subtype == st
                    if self.cs.so['node'] == set(filter(ftr, self.cs.so['node'])):
                        self.add_cascade(label='Change property', 
                                    command= lambda: self.change_property(
                                                            self.cs.so['node'],
                                                            subtype
                                                            )
                                        )
                        self.add_separator()
            
        # only one subtype of link: property changer
        if not self.cs.so['node'] and self.cs.so['link']:
            for subtype in self.cs.ntw.link_subtype:
                ftr = lambda o, st=subtype: o.subtype == st
                if self.cs.so['link'] == set(filter(ftr, self.cs.so['link'])):
                    self.add_cascade(label='Change property', 
                                command= lambda: self.change_property(
                                                        self.cs.so['link'],
                                                        subtype
                                                        )
                                    )
                    self.add_separator()
                    
        # at least one object: deletion or create AS
        self.add_command(label='Delete', 
                            command=lambda: self.remove_objects())
            
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
        print(self.all_so)
        self.cs.remove_objects(*self.all_so)
        
    @empty_selection_and_destroy_menu
    def change_AS(self, mode):
        AS.ASOperation(self.cs, mode, self.all_so, self.common_AS)
        
    @empty_selection_and_destroy_menu
    def change_area(self, mode):
        AS.AreaOperation(self.cs, mode, self.all_so, self.common_AS)
        
    @empty_selection_and_destroy_menu
    def simulate_failure(self, plink):
        self.cs.simulate_failure(plink)
        
    @empty_selection_and_destroy_menu
    def remove_failure(self, plink):
        self.cs.remove_failure(plink)
        
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
    def bfs(self, nodes):
        self.cs.bfs_cluster_drawing(nodes)
        
    @empty_selection_and_destroy_menu
    def bgp(self, node):
        self.cs.ntw.BGPT_builder(node)
        
    @empty_selection_and_destroy_menu
    def create_AS(self):
        nodes, plinks = set(self.cs.so['node']), set(self.cs.so['link'])
        AS.ASCreation(self.cs, nodes, plinks)
        