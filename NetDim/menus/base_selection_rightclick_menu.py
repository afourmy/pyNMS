# NetDim
# Copyright (C) 2017 Antoine Fourmy (contact@netdim.fr)

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
from objects.object_management_window import ObjectManagementWindow, PropertyChanger
from collections import OrderedDict
from objects.interface_window import InterfaceWindow
                                
class BaseSelectionRightClickMenu(tk.Menu):
    def __init__(self, event, scenario, from_scenario=True):
        super().__init__(tearoff=0)
        self.cs = scenario
        
        x, y = self.cs.cvs.canvasx(event.x), self.cs.cvs.canvasy(event.y)

        if from_scenario:
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
            
        # all selected objects
        self.all_so = self.cs.so['node'] | self.cs.so['link'] | self.cs.so['shape']
        
        # useful booleans
        self.no_node = not self.cs.so['node']
        self.no_link = not self.cs.so['link']
        self.no_shape = not self.cs.so['shape']
        self.one_node = len(self.cs.so['node']) == 1
        self.one_link = len(self.cs.so['link']) == 1
                            
        # exactly one object: property window 
        if self.no_shape and len(self.all_so) == 1:
            self.add_command(label='Properties', 
                        command=lambda: self.show_object_properties())
            self.add_separator()
        
        if self.no_shape:
            self.add_command(label='Simulate failure', 
                            command=lambda: self.simulate_failure(*self.all_so))
            self.add_command(label='Remove failure', 
                            command=lambda: self.remove_failure(*self.all_so))
            
            self.add_separator()
            
        # only nodes: 
        if self.no_shape and self.no_link:
            
            # alignment submenu
            self.add_cascade(label='Align nodes', 
                            menu=AlignmentMenu(self.cs, self.cs.so['node']))
            self.add_separator()
            
            # map submenu
            self.add_cascade(label='Map menu', 
                            menu=MapMenu(self.cs, self.cs.so['node']))
            self.add_separator()
            
            # multiple links creation menu
            self.add_command(label='Create multiple links', 
                                command=lambda: self.multiple_links(self.cs))
            self.add_separator()
            
            # only one subtype of nodes
            if self.cs.so['node']:
                for subtype in node_subtype:
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
        if self.no_node and self.no_shape:
            for subtype in link_subtype:
                ftr = lambda o, st=subtype: o.subtype == st
                if self.cs.so['link'] == set(filter(ftr, self.cs.so['link'])):
                    self.add_cascade(label='Change property', 
                                command= lambda: self.change_property(
                                                        self.cs.so['link'],
                                                        subtype
                                                        )
                                    )
                    self.add_separator()
        
        # we allow to delete if the menu was generated from the scenario
        # (and not the treeview which view cannot be easily updated)
        if from_scenario:
            # at least one object: deletion or create AS
            self.add_command(label='Delete', 
                                command=lambda: self.remove_objects())
    
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
    def simulate_failure(self, *objects):
        self.cs.simulate_failure(*objects)
        
    @empty_selection_and_destroy_menu
    def remove_failure(self, *objects):
        self.cs.remove_failure(*objects)
            
    @empty_selection_and_destroy_menu
    def show_object_properties(self):
        so ,= self.all_so
        ObjectManagementWindow(self.cs.ms, so)
        
    @empty_selection_and_destroy_menu
    def change_property(self, objects, subtype):
        objects = set(objects)
        PropertyChanger(self.cs.ms, objects, subtype)
        
    @empty_selection_and_destroy_menu
    def multiple_links(self, scenario):
        mobj.MultipleLinks(scenario, set(self.cs.so['node']))
                