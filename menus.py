import tkinter as tk
import AS

class RightClickMenu(tk.Menu):
    def __init__(self, event, scenario):
        super().__init__(tearoff=0)
        
        # Add the object from which the menu started to the selected objects
        self.selection = scenario._selected_objects
        x, y = scenario.canvasx(event.x), scenario.canvasy(event.y)
        selected_obj = scenario.object_id_to_object[scenario.find_closest(x, y)[0]]
        self.selection[selected_obj.class_type].add(selected_obj)
        
        # initialize menu parameters depending on what is selected:
        # only one node
        if(not self.selection["link"] and len(self.selection["node"]) == 1):
            self.add_command(label="Properties", command= lambda: self.show_node_properties(scenario))
            self.add_command(label="Delete node", command= lambda: self.delete(scenario))
        # multiple nodes
        elif(not self.selection["link"]):
            self.add_command(label="Delete nodes", command= lambda: self.delete(scenario))
        # only one link
        elif(not self.selection["node"] and len(self.selection["link"]) == 1):
            self.add_command(label="Properties", command= lambda: self.show_link_properties(scenario))
            self.add_command(label="Delete link", command= lambda: self.remove_objects(scenario))
            selected_link ,= self.selection["link"]
            if(selected_link.AS):
                self.add_command(label="Manage AS", command= lambda: selected_link.AS.management.deiconify())
                self.add_command(label="Remove link from AS", command= lambda: self.remove_links_from_AS(scenario))
        # more than one link
        elif(not self.selection["node"]):
            self.add_command(label="Delete links", command= lambda: scenario.remove_objects(scenario))
            self.add_command(label="Create AS", command= lambda: self.create_AS(scenario))
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
        
    @empty_selection_and_destroy_menu
    def remove_links_from_AS(self, scenario):
        scenario.remove_links_from_AS(*self.selection["link"])
    
    @empty_selection_and_destroy_menu
    def remove_nodes_from_AS(self, scenario):
        # TODO a window must pop-up with the list of domain the node belongs to
        pass
        
    @empty_selection_and_destroy_menu
    def create_AS(self, scenario):
        AS.ASCreation(scenario)
    
    @empty_selection_and_destroy_menu
    def show_node_properties(self, scenario):
        scenario.master.node_management_window.update()
        scenario.master.node_management_window.deiconify()

    @empty_selection_and_destroy_menu
    def show_link_properties(self, scenario):
        scenario.master.link_management_window.update()
        scenario.master.link_management_window.deiconify()
        
# TODO les rights click menu ne doivent pas être généré une seule fois à l'init d'un scenario
# TODO ils doivent être générer à chaque click droit pour que leur contenu dépende de ce qui est 
# TODO selectionner

class RightClickMenuRoute(tk.Menu):
    def __init__(self, scenario):
        super().__init__(tearoff=0)
        self.current_route = None
        self.add_command(label="Properties", command= lambda: self.show_properties(scenario))
        self.add_command(label="Delete route", command= lambda: self.delete_route(scenario))
        
    def show_properties(self, scenario):
        scenario.master.path_finding_window.select_route()
        scenario.master.path_finding_window.deiconify()
        
    def delete_route(self, scenario):
        scenario.remove_objects(scenario.master.path_finding_window.current_route)
        
    def popup(self, event, scenario):
        x, y = scenario.canvasx(event.x), scenario.canvasy(event.y)
        scenario.master.path_finding_window.current_route = scenario.object_id_to_object[scenario.find_closest(x, y)[0]]
        self.tk_popup(event.x_root, event.y_root)
        
