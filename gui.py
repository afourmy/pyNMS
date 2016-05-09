path_app = "C:\\Users\\afourmy\\Desktop\\Sauvegarde\\Python\\Network\\"
path_icon = "C:\\Users\\afourmy\\Desktop\\Sauvegarde\\Python\\Network\\Icons\\"

# add the path to the module in sys.path
import sys
if path_app not in sys.path:
    sys.path.append(path_app)

import tkinter as tk
from tkinter import ttk
import network
import collections
import node
import link
import math
import object_management_window
import path_finding_window
import graph_creation_window
import drawing_options_window
import frame
import scenario
import pickle
from PIL import ImageTk

class NetDim(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
            
        # ----- Programme principal : -----
        self.title("Network simulator")
    
        # ----- Menus : -----
        menubar = tk.Menu(self)
        main_menu = tk.Menu(menubar, tearoff=0)
        main_menu.add_command(label="Graph creation", command=lambda: self.graph_creation_window.deiconify())
        main_menu.add_command(label="Flow creation", command=lambda: self.nothing())
        main_menu.add_command(label="Link management", command=lambda: self.link_management_window.deiconify())
        main_menu.add_command(label="Node management", command=lambda: self.node_management_window.deiconify())
        main_menu.add_command(label="Route management", command=lambda: self.route_management_window.deiconify())
        main_menu.add_command(label="Add scenario", command=lambda: self.add_scenario())
        main_menu.add_command(label="Save project", command=lambda: self.save_project())
        main_menu.add_command(label="Load project", command=lambda: self.load_project())
        main_menu.add_separator()
        main_menu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="Main",menu=main_menu)
        menu_drawing = tk.Menu(menubar, tearoff=0)
        menu_drawing.add_command(label="Default drawing parameters", command=lambda: self.drawing_option_window.deiconify())
        menubar.add_cascade(label="Network drawing",menu=menu_drawing)
        menu_routing = tk.Menu(menubar, tearoff=0)
        menu_routing.add_command(label="Find path", command=lambda: self.path_finding_window.deiconify())
        menu_routing.add_command(label="Route flows", command=lambda: self.nothing())
        menubar.add_cascade(label="Network routing",menu=menu_routing)

        menu_options = tk.Menu(menubar, tearoff=0)        
        # menu to choose which label to display for links
        menu_trunk_label = tk.Menu(menubar, tearoff=0)
        menu_trunk_label.add_command(label="Name", command=lambda: self.current_scenario._refresh_object_labels("trunk", "name"))
        menu_trunk_label.add_command(label="Cost", command=lambda: self.current_scenario._refresh_object_labels("trunk", "cost"))
        menu_trunk_label.add_command(label="Capacity", command=lambda: self.current_scenario._refresh_object_labels("trunk", "capacity"))
        menu_trunk_label.add_command(label="Flow", command=lambda: self.current_scenario._refresh_object_labels("trunk", "flow"))
        menu_route_label = tk.Menu(menubar, tearoff=0)
        menu_route_label.add_command(label="Name", command=lambda: self.current_scenario._refresh_object_labels("route", "name"))
        menu_route_label.add_command(label="Cost", command=lambda: self.current_scenario._refresh_object_labels("route", "subnet"))
        
        # menu to choose which label to display for nodes
        menu_node_label = tk.Menu(menubar, tearoff=0)
        menu_node_label.add_command(label="Name", command=lambda: self.current_scenario._refresh_object_labels("node", "name"))
        menu_node_label.add_command(label="Position", command=lambda: self.current_scenario._refresh_object_labels("node", "position"))
        # add the node and link label menus to the option menu
        menu_options.add_cascade(label="Trunk label", menu=menu_trunk_label)
        menu_options.add_cascade(label="Route label", menu=menu_route_label)
        menu_options.add_cascade(label="Node label", menu=menu_node_label)
        menu_options.add_command(label="Change display", command=lambda: self.current_scenario.change_display())
        
        menubar.add_cascade(label="Options",menu=menu_options)
        self.config(menu=menubar)

        # scenario notebook
        self.scenario_notebook = ttk.Notebook(self)
        self.scenario_notebook.bind("<ButtonRelease-1>", self.change_current_scenario)
        self.dict_scenario = {}
        # create the first scenario
        self.current_scenario = scenario.Scenario(self, "scenario0")
        self.scenario_notebook.add(self.current_scenario, text=self.current_scenario.name, compound=tk.TOP)
        self.scenario_notebook.pack(fill=tk.BOTH, side=tk.RIGHT)
        self.dict_scenario["scenario0"] = self.current_scenario
        # node, link management windows
        self.node_management_window = object_management_window.NodeManagement(self)
        self.link_management_window = object_management_window.LinkManagement(self)
        # path finding window
        self.path_finding_window = path_finding_window.PathFinding(self)
        # manual graph creation window
        self.graph_creation_window = graph_creation_window.GraphCreation(self)
        
        # parameters for spring-based drawing: per project
        self.alpha = 1
        self.beta = 100000
        self.k = 0.5
        self.eta = 0.5
        self.delta = 0.35
        self.raideur = 0
        self.opd = 0
        # drawing options window
        self.drawing_option_window = drawing_options_window.DrawingOptions(self)
        
        # create a frame
        self.main_frame = frame.MainFrame(self)
        self.main_frame.pack(fill=tk.BOTH, side=tk.RIGHT)
        self.main_frame.pack_propagate(False)
        
        # image for motion
        self.image_pil_motion = ImageTk.Image.open(path_icon + "motion.png").resize((75, 75))
        self.image_motion = ImageTk.PhotoImage(self.image_pil_motion)
        self.main_frame.motion_mode.config(image = self.image_motion, width=75, height=75)
        
        # image for creation
        self.image_pil_creation = ImageTk.Image.open(path_icon + "creation.gif").resize((75, 75))
        self.image_creation = ImageTk.PhotoImage(self.image_pil_creation)
        self.main_frame.creation_mode.config(image = self.image_creation, width=75, height=75)
        
        # dict of nodes image for node creation
        self.dict_image = collections.defaultdict(dict)
        
        for color in ["default", "red"]:
            for node_type in scenario.Scenario.node_type_to_class:
                img_pil = ImageTk.Image.open(path_icon + color + "_" + node_type + ".gif").resize((scenario.Scenario.node_type_to_class[node_type].default_imagex, scenario.Scenario.node_type_to_class[node_type].default_imagey))
                img = ImageTk.PhotoImage(img_pil)
                # set the default image for the button of the frame
                if(color == "default"):
                    self.main_frame.type_to_button[node_type].config(image=img, width=50, height=50)
                self.dict_image[color][node_type] = img
                
        for link_type in scenario.Scenario.link_type_to_class:
            img_pil = ImageTk.Image.open(path_icon + link_type + ".png").resize((85, 15))
            img = ImageTk.PhotoImage(img_pil)
            self.dict_image["default"][link_type] = img
            self.main_frame.type_to_button[link_type].config(image=img, width=100, height=25, anchor=tk.CENTER)
        
    def change_current_scenario(self, event):
        current_scenario_name = self.scenario_notebook.tab(self.scenario_notebook.select(), "text")
        self.current_scenario = self.dict_scenario[current_scenario_name]
        
    def add_scenario(self):
        new_scenario_name = "scenario" + str(len(self.dict_scenario))
        new_scenario = scenario.Scenario(self, new_scenario_name)
        self.scenario_notebook.add(new_scenario, text=new_scenario_name, compound=tk.TOP)
        self.dict_scenario[new_scenario_name] = new_scenario
        
    def save_project(self):
        with open('netdim_node_data.pkl', 'wb') as output:
            pickle.dump(self.current_scenario.pool_network, output, pickle.HIGHEST_PROTOCOL)
                
    def load_project(self):
        with open('netdim_node_data.pkl', 'rb') as input:
            self.current_scenario.pool_network = pickle.load(input)
        # once the project is loaded, the network graph needs to be recreated
        for link_type in ["trunk", "traffic", "route"]:
            for link in self.current_scenario.pool_network[link_type].values():
                self.current_scenario.graph[link.source][link_type].add(link)
                self.current_scenario.graph[link.destination][link_type].add(link)
        
if __name__ == "__main__":
    netdim = NetDim()
    netdim.mainloop()
        