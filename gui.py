import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog
import network
import collections
import object_management_window
import advanced_graph_options
import drawing_options_window
import frame
import scenario
import pickle
import csv
import xlrd, xlwt
import xml.etree.ElementTree as etree
from PIL import ImageTk

class NetDim(tk.Tk):
    def __init__(self, path_app):
        tk.Tk.__init__(self)
        self.path_icon = path_app + "Icons\\"
        self.path_workspace = path_app + "Workspace\\"
            
        ## ----- Programme principal : -----
        self.title("NetDim")
        netdim_icon = tk.PhotoImage(file=self.path_icon+"netdim.png")
        self.tk.call('wm', 'iconphoto', self._w, netdim_icon)
        
        ## User-defined properties and labels per type of object
        
        # I used ordered dicts to have the same menu order 
        self.object_properties = collections.OrderedDict([
        ("router", ("name", "x", "y", "longitude", "latitude")),
        ("oxc", ("name", "x", "y", "longitude", "latitude")),
        ("host", ("name", "x", "y", "longitude", "latitude")),
        ("antenna", ("name", "x", "y", "longitude", "latitude")),
        ("trunk", ("name", "source", "destination", "distance", "cost", "capacity", "flow")),
        ("route", ("name","source", "destination", "distance", 
        "path_constraints", "excluded_nodes", "excluded_trunks", "path", "subnets")),
        ("traffic", ("name", "source", "destination", "distance"))
        ])
        
        self.object_label = collections.OrderedDict([
        ("Node", ("None", "Name", "Position", "Coordinates")),
        ("Trunk", ("None", "Name", "Distance", "Cost", "Capacity", "Flow")),
        ("Route", ("None", "Name", "Distance", "Type", "Path", "Subnet")),
        ("Traffic", ("None", "Name", "Distance"))
        ])
        
        self.object_import_export = collections.OrderedDict([
        ("node", ("name", "x", "y", "longitude", "latitude")),
        ("trunk", ("name", "source", "destination", "distance", "cost", "capacity")),
        ("route", ("name", "source", "destination", "distance", 
        "path_constraints", "excluded_nodes", "excluded_trunks", "path", "subnets")),
        ("traffic", ("name", "source", "destination", "distance"))
        ])
        
        ## ----- Menus : -----
        menubar = tk.Menu(self)
        main_menu = tk.Menu(menubar, tearoff=0)
        main_menu.add_command(label="Add scenario", command=lambda: self.add_scenario())
        main_menu.add_command(label="Delete scenario", command=lambda: self.delete_scenario())
        main_menu.add_separator()
        main_menu.add_command(label="Save project", command=lambda: self.save_project())
        main_menu.add_command(label="Load project", command=lambda: self.load_project())
        main_menu.add_separator()
        main_menu.add_command(label="Import graph", command=lambda: self.import_graph())
        main_menu.add_command(label="Export graph", command=lambda: self.export_graph())
        main_menu.add_separator()
        main_menu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="Main",menu=main_menu)
        menu_drawing = tk.Menu(menubar, tearoff=0)
        menu_drawing.add_command(label="Default drawing parameters", command=lambda: self.drawing_option_window.deiconify())
        menubar.add_cascade(label="Network drawing",menu=menu_drawing)
        menu_routing = tk.Menu(menubar, tearoff=0)
        menu_routing.add_command(label="Advanced graph options", command=lambda: self.advanced_graph_options.deiconify())
        menubar.add_cascade(label="Network routing",menu=menu_routing)

        # label submenus
        menu_options = tk.Menu(menubar, tearoff=0)
        for obj_type, label_type in self.object_label.items():
            menu_type = tk.Menu(menubar, tearoff=0)
            for lbl in label_type:
                menu_type.add_command(label=lbl, command=lambda obj_type=obj_type, lbl=lbl:  self.cs._refresh_object_labels(obj_type.lower(), lbl.lower()))
            menu_options.add_cascade(label=obj_type + " label", menu=menu_type)
            
        menu_options.add_command(label="Change display", command=lambda: self.cs.change_display())
        
        menu_display = tk.Menu(menubar, tearoff=0)
        for index, type in enumerate(self.object_properties):
            new_label = " ".join(("Hide", type))
            menu_display.add_command(label=new_label, command=lambda type=type, index=index: self.cs.show_hide(menu_display, type, index))
        menu_options.add_cascade(label="Show/hide object", menu=menu_display)
            
        menubar.add_cascade(label="Options",menu=menu_options)
        
        self.config(menu=menubar)

        # scenario notebook
        self.scenario_notebook = ttk.Notebook(self)
        self.scenario_notebook.bind("<ButtonRelease-1>", self.change_cs)
        self.dict_scenario = {}
        
        # cs for "current scenario" (the first one which we create)
        self.cs = scenario.Scenario(self, "scenario 0")
        self.cpt_scenario = 0
        self.scenario_notebook.add(self.cs, text=self.cs.name, compound=tk.TOP)
        self.scenario_notebook.pack(fill=tk.BOTH, side=tk.RIGHT)
        self.dict_scenario["scenario 0"] = self.cs
        
        # object management windows
        self.dict_obj_mgmt_window = {}
        for obj in self.object_properties:
            self.dict_obj_mgmt_window[obj] = object_management_window.ObjectManagementWindow(self,obj)
        
        # parameters for spring-based drawing: per project
        self.alpha = 1
        self.beta = 10000
        self.k = 0.5
        self.eta = 0.5
        self.delta = 0.35
        self.raideur = 8
        self.opd = 0
        
        # drawing options window
        self.drawing_option_window = drawing_options_window.DrawingOptions(self)
        # advanced graph options
        self.advanced_graph_options = advanced_graph_options.AdvancedGraphOptionsWindow(self)
        
        # create a frame
        self.main_frame = frame.MainFrame(self)
        self.main_frame.pack(fill=tk.BOTH, side=tk.RIGHT)
        self.main_frame.pack_propagate(False)
        
        # image for motion
        self.image_pil_motion = ImageTk.Image.open(self.path_icon + "motion.png").resize((75, 75))
        self.image_motion = ImageTk.PhotoImage(self.image_pil_motion)
        self.main_frame.motion_mode.config(image = self.image_motion, width=75, height=75)
        
        # image for creation
        self.image_pil_creation = ImageTk.Image.open(self.path_icon + "creation.png").resize((75, 75))
        self.image_creation = ImageTk.PhotoImage(self.image_pil_creation)
        self.main_frame.creation_mode.config(image = self.image_creation, width=75, height=75)
        
        # dict of nodes image for node creation
        self.dict_image = collections.defaultdict(dict)
        
        self.dict_size_image = {
        "router": (33, 25), 
        "oxc": (35, 32), 
        "host": (35, 32), 
        "antenna": (35, 35)
        }
        
        for color in ["default", "red"]:
            for node_type in scenario.Scenario.node_type_to_class:
                img_path = "".join((self.path_icon, color, "_", node_type, ".gif"))
                img_pil = ImageTk.Image.open(img_path).resize(self.dict_size_image[node_type])
                img = ImageTk.PhotoImage(img_pil)
                # set the default image for the button of the frame
                if(color == "default"):
                    self.main_frame.type_to_button[node_type].config(image=img, width=50, height=50)
                self.dict_image[color][node_type] = img
                
        for link_type in scenario.Scenario.link_type_to_class:
            img_path = "".join((self.path_icon, link_type, ".png"))
            img_pil = ImageTk.Image.open(img_path).resize((85, 15))
            img = ImageTk.PhotoImage(img_pil)
            self.dict_image["default"][link_type] = img
            self.main_frame.type_to_button[link_type].config(image=img, width=100, height=25, anchor=tk.CENTER)
        
        dict_size = {"ring": (76, 66), "tree": (71, 43), "star": (72, 70), "full-mesh": (81, 72)}
        for network_topology in ("ring", "tree", "star", "full-mesh"):
            x, y = dict_size[network_topology]
            img_pil = ImageTk.Image.open(self.path_icon + network_topology + ".png").resize((x,y))
            img = ImageTk.PhotoImage(img_pil)
            self.dict_image["topology"][network_topology] = img
            self.main_frame.type_to_button[network_topology].config(image=img, width=x, height=y, anchor=tk.CENTER)
            
        for drawing_icons in ("draw", "stop"):
            img_pil = ImageTk.Image.open(self.path_icon + drawing_icons + ".png").resize((50, 50))
            img = ImageTk.PhotoImage(img_pil)
            self.dict_image["drawing"][drawing_icons] = img
            self.main_frame.type_to_button[drawing_icons].config(image=img, width=60, height=60, anchor=tk.CENTER)
            
    def change_cs(self, event=None):
        cs_name = self.scenario_notebook.tab(self.scenario_notebook.select(), "text")
        self.cs = self.dict_scenario[cs_name]
        
    def add_scenario(self):
        self.cpt_scenario += 1
        new_scenario_name = " ".join(("scenario", str(self.cpt_scenario)))
        new_scenario = scenario.Scenario(self, new_scenario_name)
        self.scenario_notebook.add(new_scenario, text=new_scenario_name, compound=tk.TOP)
        self.dict_scenario[new_scenario_name] = new_scenario
        
    def delete_scenario(self):
        del self.dict_scenario[self.cs.name]
        self.scenario_notebook.forget(self.cs)
        self.change_cs()
        
    def save_project(self):
        with open('netdim_node_data.pkl', 'wb') as output:
            pickle.dump(self.cs.pn, output, pickle.HIGHEST_PROTOCOL)
                
    def load_project(self):
        with open('netdim_node_data.pkl', 'rb') as input:
            self.cs.pn = pickle.load(input)
        # once the project is loaded, the network graph needs to be recreated
        for link_type in ["trunk", "traffic", "route"]:
            for link in self.cs.pn[link_type].values():
                self.cs.graph[link.source][link_type].add(link)
                self.cs.graph[link.destination][link_type].add(link)
                
    def import_graph(self):
        # retrieve the path and kill fake window
        filepath = filedialog.askopenfilenames(initialdir=self.path_workspace, title="Import graph", filetypes=(("all files","*.*"), ("csv files","*.csv"), ("xls files","*.xls"), ("txt files","*.txt")))
        
        if not filepath: return
        else: filepath ,= filepath

        if(filepath.endswith(".csv")):
            try:
                file_to_import = open(filepath, "rt")
                reader = csv.reader(file_to_import)
                for row in filter(None,reader):
                    source_name, destination_name = row
                    self.cs.graph_from_names(source_name, destination_name)
            finally:
                file_to_import.close()
                
        elif(filepath.endswith(".txt")):
            with open(filepath, "r") as file_to_import:
                for row in file_to_import:
                    source_name, destination_name = row.split()
                    self.cs.graph_from_names(source_name, destination_name)
                    
        elif(filepath.endswith(".xls")):
            book = xlrd.open_workbook(filepath)
            for id, obj_type in enumerate(self.object_import_export):
                xls_sheet = book.sheets()[id]
                for row_index in range(1, xls_sheet.nrows):
                    if(obj_type == "node"):
                        # TODO multiple argument error when adding *param as an argument
                        n, *param = xls_sheet.row_values(row_index)
                        print(n, param)
                        self.cs.node_factory(*param, node_type="router", name=n)
                    else:
                        n, s, d, *param = xls_sheet.row_values(row_index)
                        src, dest = self.cs.node_factory(name=s), self.cs.node_factory(name=d)
                        self.cs.link_factory(*param, link_type=obj_type, name=n, s=src, d=dest)
                
        # for the topology zoo network graphs
        elif(filepath.endswith(".graphml")):
            tree = etree.parse(filepath)
            # dict associating an id ("dxx") to a property ("label", etc)
            dict_prop_values = {}
            # dict associating a node id to node properties
            dict_id_to_prop = collections.defaultdict(dict)
            # label will be the name of the node
            properties = ["label", "Longitude", "Latitude"]
            
            label_id = None
            for element in tree.iter():
                for child in element:
                    if "key" in child.tag:
                        if(child.attrib["attr.name"] in properties and child.attrib["for"] == "node"):
                            dict_prop_values[child.attrib["id"]] = child.attrib["attr.name"]
                    if "node" in child.tag:
                        node_id = child.attrib["id"]
                        for prop in child:
                            if prop.attrib["key"] in dict_prop_values:
                                dict_id_to_prop[node_id][dict_prop_values[prop.attrib["key"]]] = prop.text
                    if "edge" in child.tag:
                        s_id, d_id = child.attrib["source"], child.attrib["target"]
                        src_name = dict_id_to_prop[s_id]["label"]
                        src = self.cs.node_factory(name=src_name)
                        dest_name = dict_id_to_prop[d_id]["label"]
                        dest = self.cs.node_factory(name=dest_name)
                        
                        # set the latitude and longitude of the newly created nodes
                        for coord in ("latitude", "longitude"):
                            src.__dict__[coord] = dict_id_to_prop[s_id][coord.capitalize()]
                            dest.__dict__[coord] = dict_id_to_prop[d_id][coord.capitalize()]
                        
                        # distance between src and dest
                        param = map(float, (src.longitude, src.latitude, dest.longitude, dest.latitude))
                        distance = round(self.cs.haversine_distance(*param))

                        # in some graphml files, there are nodes with loopback link
                        if src_name != dest_name:
                            new_link = self.cs.link_factory(s=src, d=dest)
                            new_link.distance = distance
        
        self.cs.draw_all(False)
        self.cs._refresh_object_labels("trunk", "distance")
        
        
    def export_graph(self):
        selected_file = filedialog.asksaveasfile(initialdir=self.path_workspace, title="Export graph", mode='w', defaultextension=".xls")
        
        if not selected_file: return            
        filename, file_format = os.path.splitext(selected_file.name)

        if(file_format in (".txt", ".csv")):
            graph_per_line = ("{},{}".format(t.source, t.destination) for t in self.cs.pn["trunk"].values())
            if(file_format == ".txt"):
                selected_file.write("\n".join(graph_per_line))
            else:
                graph_writer = csv.writer(selected_file, delimiter=",", lineterminator="\n")
                for line in graph_per_line:
                    graph_writer.writerow(line.split(","))
            
        if(file_format == ".xls"):
            excel_workbook = xlwt.Workbook()
            for obj_type in self.object_import_export:
                xls_sheet = excel_workbook.add_sheet(obj_type)
                for id, property in enumerate(self.object_import_export[obj_type]):
                    xls_sheet.write(0, id, property)
                    for i, t in enumerate(self.cs.pn[obj_type].values(), 1):
                        xls_sheet.write(i, id, str(t.__dict__[property]))
            excel_workbook.save(selected_file.name)
        selected_file.close()
        