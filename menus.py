import tkinter as tk
import AS

class RightClickMenu(tk.Menu):
    def __init__(self, event, scenario):
        super().__init__(tearoff=0)
        
        # Add the object from which the menu started to the selected objects
        self.selection = scenario._selected_objects
        x, y = scenario.canvasx(event.x), scenario.canvasy(event.y)
        self.selected_obj = scenario.object_id_to_object[scenario.find_closest(x, y)[0]]
        self.selection[self.selected_obj.class_type].add(self.selected_obj)
        
        # highlight all to add the selected object to the highlight
        scenario.highlight_objects(*scenario._selected_objects["node"]|scenario._selected_objects["link"])
        
        # initialize menu parameters depending on what is selected:
        # only one node
        if(not self.selection["link"] and len(self.selection["node"]) == 1):
            self.add_command(label="Properties", command= lambda: self.show_object_properties(scenario))
            self.add_command(label="Delete node", command= lambda: self.remove_objects(scenario))
            self.add_command(label="Add node to AS", command= lambda: AS.AddToAS(scenario, self.selected_obj))
            if(self.selected_obj.AS):
                self.add_command(label="Manage AS", command= lambda: AS.ManageAS(scenario, self.selected_obj))
        # multiple nodes
        elif(not self.selection["link"]):
            self.add_command(label="Delete nodes", command= lambda: self.remove_objects(scenario))
            self.add_command(label="Create AS", command= lambda: self.create_AS(scenario))
            self.add_command(label="Add nodes to AS", command= lambda: AS.AddToAS(scenario, *self.selection["node"]))
        # only one link
        elif(not self.selection["node"] and len(self.selection["link"]) == 1):
            self.add_command(label="Properties", command= lambda: self.show_object_properties(scenario))
            self.add_command(label="Delete link", command= lambda: self.remove_objects(scenario))
            if(self.selected_obj.AS):
                self.add_command(label="Manage AS", command= lambda: selected_obj.AS.management.deiconify())
                self.add_command(label="Add link to AS", command= lambda: AS.AddToAS(scenario, self.selected_obj))
                self.add_command(label="Remove link from AS", command= lambda: self.remove_links_from_AS(scenario))
        # multiple links
        elif(not self.selection["node"]):
            self.add_command(label="Delete links", command= lambda: self.remove_objects(scenario))
            self.add_command(label="Create AS", command= lambda: self.create_AS(scenario))
            self.add_command(label="Add links to AS", command= lambda: AS.AddToAS(scenario, *self.selection["link"]))
        # links AND nodes
        else:
            self.add_command(label="Delete objects", command= lambda: scenario.remove_objects(scenario))
        # make the menu appear    
        self.tk_popup(event.x_root, event.y_root)
    
    def empty_selection_and_destroy_menu(function):
        def wrapper(self, scenario):
            function(self, scenario)
            scenario._selected_objects = {"node": set(), "link": set()}
            self.destroy()
        return wrapper
        
    @empty_selection_and_destroy_menu
    def remove_objects(self, scenario):
        scenario.remove_objects(*(self.selection["link"] | self.selection["node"]))
        
    def create_AS(self, scenario):
        AS.ASCreation(scenario)
        self.destroy()
    
    @empty_selection_and_destroy_menu
    def show_object_properties(self, scenario):
        selected_obj ,= scenario._selected_objects["node"] | scenario._selected_objects["link"]
        scenario.master.dict_obj_mgmt_window[selected_obj.type].current_obj = selected_obj
        scenario.master.dict_obj_mgmt_window[selected_obj.type].update()
        scenario.master.dict_obj_mgmt_window[selected_obj.type].deiconify()
