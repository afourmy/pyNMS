# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk
from autonomous_system import AS
import ip_networks.configuration as ip_conf
import ip_networks.troubleshooting as ip_ts
import ip_networks.ping as ip_ping
import ip_networks.routing_table as ip_rt
import ip_networks.bgp_table as ip_bgpt
import drawing.drawing_options_window
import graph_generation.multiple_objects as mobj
from .alignment_menu import AlignmentMenu
from drawing.drawing_menu import DrawingMenu
from objects.object_management_window import PropertyChanger
from collections import OrderedDict
                                
class SelectionRightClickMenu(tk.Menu):
    def __init__(self, event, scenario):
        super().__init__(tearoff=0)
        self.cs = scenario
        
        x, y = self.cs.canvasx(event.x), self.cs.canvasy(event.y)

        closest_obj = self.cs.find_closest(x, y)[0]
        selected_obj = self.cs.object_id_to_object[closest_obj]
        # if the object from which the menu was started does not belong to
        # the current selection, it means the current selection is no longer
        # to be considered, and only the selected objected is considered 
        # as having been selected by the user
                
        if selected_obj not in self.cs.so[selected_obj.class_type]:
            # we empty / unhighlight the selection
            self.cs.unhighlight_all()
            self.cs.highlight_objects(selected_obj)
            
        self.all_so = self.cs.so["node"] | self.cs.so["link"]
                            
        # exactly one object: property window 
        if len(self.cs.so["node"]) == 1 or len(self.cs.so["link"]) == 1:
            self.add_command(label="Properties", 
                        command=lambda: self.show_object_properties())
                            
            self.add_separator()
                
        # exactly one node: configuration menu
        if not self.cs.so["link"] and len(self.cs.so["node"]) == 1:
            node ,= self.cs.so["node"]
            self.add_command(label="Routing table", 
                        command=lambda: self.routing_table(node))
            self.add_command(label="BGP table", 
                        command=lambda: self.bgp_table(node))
            self.add_command(label="Configuration", 
                        command=lambda: self.configure(node))
            self.add_command(label="Troubleshooting", 
                        command=lambda: self.troubleshoot(node))
            self.add_command(label="Ping", 
                        command=lambda: self.ping(node))
            self.add_separator()
        
        self.add_command(label="Create AS", 
                            command=lambda: self.create_AS()) 
      
        # at least one AS in the network: add to AS
        if self.cs.ntw.pnAS:
            self.add_command(label="Add to AS", 
                        command=lambda: self.change_AS("add"))
        
        # we compute the set of common AS among all selected objects
        self.common_AS = set(self.cs.ntw.pnAS.values())  
        cmd = lambda o: o.type in ("node", "trunk")
        for obj in filter(cmd, self.all_so):
            self.common_AS &= obj.AS.keys()
            
        # if at least one common AS: remove from AS or manage AS
        if self.common_AS:
            self.add_command(label="Remove from AS", 
                        command=lambda: self.change_AS("remove"))
            self.add_command(label="Remove from area", 
                        command=lambda: self.change_AS("remove area"))
            self.add_command(label="Manage AS", 
                        command=lambda: self.change_AS("manage"))
                        
        self.add_separator()
        
        # exactly one trunk: failure simulation menu
        if not self.cs.so["node"] and len(self.cs.so["link"]) == 1:
            trunk ,= self.cs.so["link"]
            if trunk.type == "trunk":
                self.add_command(label="Simulate failure", 
                        command=lambda: self.simulate_failure(trunk))
                if trunk in self.cs.ntw.fdtks:
                    self.add_command(label="Remove failure", 
                        command=lambda: self.remove_failure(trunk))
            
        # only nodes: 
        if not self.cs.so["link"]:
            # drawing submenu
            self.add_cascade(label="Automatic layout", 
                            menu=DrawingMenu(self.cs, self.cs.so["node"]))
            
            # alignment submenu
            self.add_cascade(label="Align nodes", 
                            menu=AlignmentMenu(self.cs, self.cs.so["node"]))
            self.add_separator()
            
            # multiple links creation menu
            self.add_command(label="Create multiple links", 
                                command=lambda: self.multiple_links(self.cs))
            self.add_separator()
            
            # only one subtype of nodes
            if self.cs.so["node"]:
                for subtype in self.cs.ntw.node_subtype:
                    ftr = lambda o, st=subtype: o.subtype == st
                    if self.cs.so["node"] == set(filter(ftr, self.cs.so["node"])):
                        self.add_cascade(label="Change property", 
                                    command= lambda: self.change_property(
                                                            self.cs.so["node"],
                                                            subtype
                                                            )
                                        )
                        self.add_separator()
            
        # only one subtype of link: property changer
        if not self.cs.so["node"] and self.cs.so["link"]:
            for subtype in self.cs.ntw.link_subtype:
                ftr = lambda o, st=subtype: o.subtype == st
                if self.cs.so["link"] == set(filter(ftr, self.cs.so["link"])):
                    self.add_cascade(label="Change property", 
                                command= lambda: self.change_property(
                                                        self.cs.so["link"],
                                                        subtype
                                                        )
                                    )
                    self.add_separator()
                    
        # at least one object: deletion or create AS
        self.add_command(label="Delete", 
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
        AS.ModifyAS(self.cs, mode, self.all_so, self.common_AS)
        
    @empty_selection_and_destroy_menu
    def simulate_failure(self, trunk):
        self.cs.simulate_failure(trunk)
        
    @empty_selection_and_destroy_menu
    def remove_failure(self, trunk):
        self.cs.remove_failure(trunk)
        
    @empty_selection_and_destroy_menu
    def routing_table(self, node):
        ip_rt.RoutingTable(node, self.cs)
        
    @empty_selection_and_destroy_menu
    def bgp_table(self, node):
        ip_bgpt.BGPTable(node, self.cs)
        
    @empty_selection_and_destroy_menu
    def configure(self, node):
        ip_conf.Configuration(node, self.cs)
        
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
        PropertyChanger(self.cs.ms, objects, subtype)
        
    @empty_selection_and_destroy_menu
    def multiple_links(self, scenario):
        mobj.MultipleLinks(scenario, set(self.cs.so["node"]))
        
    @empty_selection_and_destroy_menu
    def bfs(self, nodes):
        self.cs.bfs_cluster_drawing(nodes)
        
    @empty_selection_and_destroy_menu
    def bgp(self, node):
        self.cs.ntw.BGPT_builder(node)
        
    @empty_selection_and_destroy_menu
    def create_AS(self):
        nodes, trunks = set(self.cs.so["node"]), set(self.cs.so["link"])
        AS.ASCreation(self.cs, nodes, trunks)
        