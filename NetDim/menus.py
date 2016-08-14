# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk
import AS
import configuration
import troubleshooting
import ping
import routing_table
import drawing_options_window
from object_management_window import PropertyChanger
                                
class RightClickMenu(tk.Menu):
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
            self.cs.so = {"node": set(), "link": set()}
            self.cs.so[selected_obj.class_type].add(selected_obj)
            # we also have to unhighlight the current selection 
            self.cs.unhighlight_all()
        self.all_so = self.cs.so["node"] | self.cs.so["link"]
        
        # highlight all to add the selected object to the highlight
        self.cs.highlight_objects(*self.all_so)
                            
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
            self.add_cascade(label="Drawing", 
                            menu=DrawingMenu(self.cs, self.cs.so["node"]))
            self.add_separator()
            
            # only one subtype of nodes
            for subtype in self.cs.ntw.node_type:
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
        if not self.cs.so["node"]:
            for subtype in self.cs.ntw.trunk_type + self.cs.ntw.link_type[1:]:
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
            self.cs.so = {"node": set(), "link": set()}
            self.cs.unhighlight_all()
            self.destroy()
        return wrapper
        
    @empty_selection_and_destroy_menu
    def remove_objects(self):
        self.cs.remove_objects(*self.all_so)
        
    @empty_selection_and_destroy_menu
    def change_AS(self, mode):
        AS.ModifyAS(self.cs, mode, self.all_so, self.common_AS)
        
    @empty_selection_and_destroy_menu
    def create_AS(self):
        AS.ASCreation(self.cs, self.cs.so)
        
    @empty_selection_and_destroy_menu
    def simulate_failure(self, trunk):
        self.cs.simulate_failure(trunk)
        
    @empty_selection_and_destroy_menu
    def remove_failure(self, trunk):
        self.cs.remove_failure(trunk)
        
    @empty_selection_and_destroy_menu
    def routing_table(self, node):
        routing_table.RoutingTable(node, self.cs)
        
    @empty_selection_and_destroy_menu
    def configure(self, node):
        configuration.Configuration(node, self.cs)
        
    @empty_selection_and_destroy_menu
    def troubleshoot(self, node):
        troubleshooting.Troubleshooting(node, self.cs)
        
    @empty_selection_and_destroy_menu
    def ping(self, node):
        ping.Ping(node, self.cs)
    
    @empty_selection_and_destroy_menu
    def show_object_properties(self):
        so ,= self.all_so
        self.cs.master.dict_obj_mgmt_window[so.subtype].current_obj = so
        self.cs.master.dict_obj_mgmt_window[so.subtype].update()
        self.cs.master.dict_obj_mgmt_window[so.subtype].deiconify()
        
    @empty_selection_and_destroy_menu
    def change_property(self, objects, subtype):
        PropertyChanger(self.cs.ms, objects, subtype)
        
class GeneralRightClickMenu(tk.Menu):
    def __init__(self, event, scenario):
        super().__init__(tearoff=0)
        self.cs = scenario
        
        # drawing mode selection
        nodes = self.cs.ntw.pn["node"].values()
        self.add_cascade(label="Drawing", menu=DrawingMenu(self.cs, nodes))
        
        # stop drawing entry
        self.add_command(label="Stop drawing", command=lambda: self.cs._cancel())
        
        # remove all failures if there is at least one
        if self.cs.ntw.fdtks:
            self.add_separator()
            self.add_command(label="Remove all failures",
                    command=lambda: self.remove_all_failures())
                    
        # make the menu appear    
        self.tk_popup(event.x_root, event.y_root)

    def remove_all_failures(self):
        self.cs.remove_failures()
        self.destroy()
        
class DrawingMenu(tk.Menu):
    
    def __init__(self, scenario, nodes):
        super().__init__(tearoff=0)
        self.cs = scenario
        
        cmds = {
        "Random": lambda: scenario.draw_objects(nodes, True),
        "FBA": lambda: scenario.automatic_drawing(nodes),
        "Both": lambda: self.both(nodes)
        }
    
        self.add_command(label="Random layout", command=cmds["Random"])
        self.add_command(label="Force-based layout", command=cmds["FBA"])
        self.add_command(label="Both", command=cmds["Both"])
                                            
    def both(self, nodes):
        self.cs.draw_objects(nodes, True)
        self.cs.automatic_drawing(nodes)