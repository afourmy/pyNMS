# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk
import AS
import config
import drawing_options_window

class DrawingMenu(tk.Menu):
    
    def __init__(self, scenario, nodes):
        super().__init__(tearoff=0)
        
        cmds = {
        "Random": lambda: scenario.draw_objects(nodes, True),
        "FBA": lambda: scenario.spring_based_drawing(scenario.master, nodes),
        "Both": lambda: self.both(scenario, nodes)
        }
    
        self.add_command(label="Random layout", command=cmds["Random"])
        self.add_command(label="Force-based layout", command=cmds["FBA"])
        self.add_command(label="Both", command=cmds["Both"])
                                            
    def both(self, scenario, nodes):
        scenario.draw_objects(nodes, True)
        scenario.spring_based_drawing(scenario.master, nodes)
                                
class RightClickMenu(tk.Menu):
    def __init__(self, event, scenario):
        super().__init__(tearoff=0)
        
        x, y = scenario.canvasx(event.x), scenario.canvasy(event.y)

        closest_obj = scenario.find_closest(x, y)[0]
        selected_obj = scenario.object_id_to_object[closest_obj]
        # if the object from which the menu was started does not belong to
        # the current selection, it means the current selection is no longer
        # to be considered, and only the selected objected is considered 
        # as having been selected by the user
        if selected_obj not in scenario.so[selected_obj.class_type]:
            scenario.so = {"node": set(), "link": set()}
            scenario.so[selected_obj.class_type].add(selected_obj)
            # we also have to unhighlight the current selection 
            scenario.unhighlight_all()
        self.all_so = scenario.so["node"] | scenario.so["link"]
        
        # highlight all to add the selected object to the highlight
        scenario.highlight_objects(*self.all_so)
                            
        # exactly one object: property window 
        if len(scenario.so["node"]) == 1 or len(scenario.so["link"]) == 1:
            self.add_command(label="Properties", 
                        command=lambda: self.show_object_properties(scenario))
                            
            self.add_separator()
                            
        # only nodes: drawing submenu
        if not scenario.so["link"]:
            self.add_cascade(label="Drawing", 
                            menu=DrawingMenu(scenario, scenario.so["node"]))
            self.add_separator()
                
        # exactly one node: configuration menu
        if not scenario.so["link"] and len(scenario.so["node"]) == 1:
            node ,= scenario.so["node"]
            self.add_command(label="Configuration", 
                        command=lambda: self.configure(node, scenario))
                        
            self.add_separator()
        
        self.add_command(label="Create AS", 
                            command=lambda: self.create_AS(scenario)) 
      
        # at least one AS in the network: add to AS
        if scenario.ntw.pnAS:
            self.add_command(label="Add to AS", 
                        command=lambda: self.change_AS(scenario, "add"))
        
        # we compute the set of common AS among all selected objects
        self.common_AS = set(scenario.ntw.pnAS.values())  
        cmd = lambda o: o.network_type in ("node", "trunk")      
        for obj in filter(cmd, self.all_so):
            self.common_AS &= obj.AS.keys()
            
        # if at least one common AS: remove from AS or manage AS
        if self.common_AS:
            self.add_command(label="Remove from AS", 
                        command=lambda: self.change_AS(scenario, "remove"))
            self.add_command(label="Remove from area", 
                        command=lambda: self.change_AS(scenario, "remove area"))
            self.add_command(label="Manage AS", 
                        command=lambda: self.change_AS(scenario, "manage"))
                        
        self.add_separator()
        
        # exactly one trunk: failure simulation menu
        if not scenario.so["node"] and len(scenario.so["link"]) == 1:
            trunk ,= scenario.so["link"]
            if trunk.network_type == "trunk" and trunk.AS:
                self.add_command(label="Simulate failure", 
                        command=lambda: self.simulate_failure(trunk, scenario))
                    
            self.add_separator()
                    
        # at least one object: deletion or create AS
        self.add_command(label="Delete", 
                            command=lambda: self.remove_objects(scenario))
            
        # make the menu appear    
        self.tk_popup(event.x_root, event.y_root)
    
    def empty_selection_and_destroy_menu(function):
        def wrapper(self, scenario, *others):
            function(self, scenario, *others)
            scenario.so = {"node": set(), "link": set()}
            self.destroy()
        return wrapper
        
    @empty_selection_and_destroy_menu
    def remove_objects(self, scenario):
        scenario.remove_objects(*self.all_so)
        
    @empty_selection_and_destroy_menu
    def change_AS(self, scenario, mode):
        AS.ModifyAS(scenario, mode, self.all_so, self.common_AS)
        
    @empty_selection_and_destroy_menu
    def create_AS(self, scenario):
        AS.ASCreation(scenario, scenario.so)
        
    @empty_selection_and_destroy_menu
    def simulate_failure(self, trunk, scenario):
        scenario.simulate_failure(trunk)
        
    @empty_selection_and_destroy_menu
    def configure(self, node, scenario):
        config.Configuration(node, scenario)
    
    @empty_selection_and_destroy_menu
    def show_object_properties(self, scenario):
        so ,= self.all_so
        scenario.master.dict_obj_mgmt_window[so.subtype].current_obj = so
        scenario.master.dict_obj_mgmt_window[so.subtype].update()
        scenario.master.dict_obj_mgmt_window[so.subtype].deiconify()
        
class GeneralRightClickMenu(tk.Menu):
    def __init__(self, event, scenario):
        super().__init__(tearoff=0)
        
        # drawing mode selection
        nodes = scenario.ntw.pn["node"].values()
        self.add_cascade(label="Drawing", menu=DrawingMenu(scenario, nodes))
        
        # stop drawing entry
        self.add_command(label="Stop drawing", command=lambda: scenario._cancel())
        
        # remove all failures if there is at least one
        if any(AS.management.failed_trunk for AS in scenario.ntw.pnAS.values()):
            self.add_separator()
            self.add_command(label="Remove all failures", 
                    command=lambda: self.remove_all_failures(scenario))
                    
        # make the menu appear    
        self.tk_popup(event.x_root, event.y_root)

    def remove_all_failures(self, scenario):
        scenario.remove_failures()
        self.destroy()