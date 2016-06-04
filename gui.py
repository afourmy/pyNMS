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
import ast
from PIL import ImageTk

class NetDim(tk.Tk):
    
    def __init__(self, path_app):
        tk.Tk.__init__(self)
        self.path_icon = path_app + "Icons\\"
        self.path_workspace = path_app + "Workspace\\"
            
        ## ----- Programme principal : -----
        self.title("NetDim")
        netdim_icon = tk.PhotoImage(file=self.path_icon+"netdim_icon.gif")
        self.tk.call('wm', 'iconphoto', self._w, netdim_icon)
        
        ## User-defined properties and labels per type of object
        
        # I used ordered dicts to have the same menu order 
        self.object_properties = collections.OrderedDict([
        ("router", ("name", "x", "y", "longitude", "latitude", "AS")),
        ("oxc", ("name", "x", "y", "longitude", "latitude", "AS")),
        ("host", ("name", "x", "y", "longitude", "latitude", "AS")),
        ("antenna", ("name", "x", "y", "longitude", "latitude", "AS")),
        ("regenerator", ("name", "x", "y", "longitude", "latitude", "AS")),
        ("splitter", ("name", "x", "y", "longitude", "latitude", "AS")),
        ("trunk", ("name", "source", "destination", "distance", "costSD", "costDS", "capacitySD", "capacityDS", "flowSD", "flowDS", "AS")),
        ("route", ("name","source", "destination", "distance", "path_constraints", 
        "excluded_nodes", "excluded_trunks", "path", "subnets", "AS")),
        ("traffic", ("name", "source", "destination", "distance"))
        ])
        
        self.object_label = collections.OrderedDict([
        ("Node", ("None", "Name", "Position", "Coordinates")),
        ("Trunk", ("None", "Name", "Distance", "Cost", "Capacity", "Flow")),
        ("Route", ("None", "Name", "Distance", "Type", "Path", "Subnet")),
        ("Traffic", ("None", "Name", "Distance"))
        ])
        
        # object import export (properties)
        self.object_ie = collections.OrderedDict([
        ("node", ("name", "x", "y", "longitude", "latitude")),
        ("trunk", ("name", "source", "destination", "distance", "costSD", "costDS", "capacitySD", "capacityDS")),
        ("route", ("name", "source", "destination", "distance", 
        "path_constraints", "excluded_nodes", "excluded_trunks", "path", "subnets")),
        ("traffic", ("name", "source", "destination", "distance"))
        ])
        
        # methods for string to object conversions
        # ast.literal_eval doesn't work for set (known python bug)
        convert_node = lambda n: self.cs.ntw.nf(name=n)
        convert_link = lambda l, t: self.cs.ntw.lf(name=l)
        convert_AS = lambda AS: self.cs.ntw.AS_factory(name=AS)
        convert_nodes_set = lambda ln: set(map(convert_node, eval(ln)))
        convert_nodes_list = lambda ln: list(map(convert_node, ast.literal_eval(ln)))
        convert_links_set = lambda ll: set(map(convert_link, eval(ll)))
        convert_links_list = lambda ll: list(map(convert_link, ast.literal_eval(ll)))
        
        # dict property to conversion methods: used at import
        self.prop_to_type = {
        "name": str, "x": float, "y": float, "longitude": float, "latitude": float,
        "distance": float, "source": convert_node, "destination": convert_node, 
        "path_constraints": convert_nodes_list, "excluded_nodes": convert_nodes_set,
        "excluded_trunks": convert_links_set, "path": convert_links_list, 
        "costSD": float, "costDS": float, "capacitySD": int, "capacityDS": int,
        "subnets": str, "AS": convert_AS
        }
        
        ## ----- Menus : -----
        menubar = tk.Menu(self)
        main_menu = tk.Menu(menubar, tearoff=0)
        main_menu.add_command(label="Add scenario", command=lambda: self.add_scenario())
        main_menu.add_command(label="Delete scenario", command=lambda: self.delete_scenario())
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

        # choose which label to display per type of object
        menu_options = tk.Menu(menubar, tearoff=0)
        for obj_type, label_type in self.object_label.items():
            menu_type = tk.Menu(menubar, tearoff=0)
            for lbl in label_type:
                cmd = lambda o=obj_type, l=lbl:  self.cs._refresh_object_labels(o.lower(), l.lower())
                menu_type.add_command(label=lbl, command=cmd)
            menu_options.add_cascade(label=obj_type + " label", menu=menu_type)
            
        menu_options.add_command(label="Change display", command=lambda: self.cs.change_display())
        
        # show / hide option per type of objects
        menu_display = tk.Menu(menubar, tearoff=0)
        for index, type in enumerate(self.object_properties):
            new_label = " ".join(("Hide", type))
            cmd = lambda t=type, i=index: self.cs.show_hide(menu_display, t, i)
            menu_display.add_command(label=new_label, command=cmd)
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
        
        # dict of nodes image for node creation
        self.dict_image = collections.defaultdict(dict)
        
        self.node_size_image = {"router": (33, 25), "oxc": (35, 32), "host": (35, 32), 
        "antenna": (35, 35), "regenerator": (64, 50), "splitter": (64, 50)}
        
        self.dict_size_image = {
        "general": {general: (75, 75) for general in ("netdim", "motion", "creation")},
        "l_type": {l_type: (85, 15) for l_type in self.cs.ntw.link_type},
        "ntw_topo": {"ring": (38, 33), "tree": (35, 21), 
        "star": (36, 35), "full-mesh": (40, 36)},
        "drawing": {"draw": (50, 50), "stop": (50, 50), "multi-layer": (160, 120)}
        }
        
        for color in ["default", "red"]:
            for node_type in self.cs.ntw.node_type:
                img_path = "".join((self.path_icon, color, "_", node_type, ".gif"))
                img_pil = ImageTk.Image.open(img_path).resize(self.node_size_image[node_type])
                img = ImageTk.PhotoImage(img_pil)
                # set the default image for the button of the frame
                if(color == "default"):
                    self.main_frame.type_to_button[node_type].config(image=img, width=50, height=50)
                self.dict_image[color][node_type] = img
        
        for category_type, dict_size in self.dict_size_image.items():
            for image_type, image_size in dict_size.items():
                x, y = image_size
                img_path = "".join((self.path_icon, image_type, ".png"))
                img_pil = ImageTk.Image.open(img_path).resize(image_size)
                img = ImageTk.PhotoImage(img_pil)
                self.dict_image[category_type][image_type] = img
                self.main_frame.type_to_button[image_type].config(image=img, width=x, height=y+10)
                
            
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
                
    def str_to_object(self, obj_param, type):
        return [self.prop_to_type[p](obj_param[id]) for id, p in enumerate(self.object_ie[type])]
                
    def import_graph(self, filepath=None):
        # filepath is set for unittest
        if not filepath:
            filepath = filedialog.askopenfilenames(initialdir=self.path_workspace, title="Import graph", filetypes=(("all files","*.*"), ("csv files","*.csv"), ("xls files","*.xls"), ("txt files","*.txt")))
            
            # no error when closing the window
            if not filepath: 
                return
            else: 
                filepath ,= filepath

        if(filepath.endswith(".csv")):
            try:
                file_to_import = open(filepath, "rt")
                reader = csv.reader(file_to_import)
                for row in filter(None, reader):
                    obj_type, *other = row
                    if(other):
                        if(obj_type == "node"):
                            n, *param = self.str_to_object(other, "node")
                            self.cs.ntw.nf(*param, node_type="router", name=n)
                        else:
                            n, s, d, *param = self.str_to_object(other, obj_type)
                            self.cs.ntw.lf(*param, link_type=obj_type, name=n, s=s, d=d)
                            
            finally:
                file_to_import.close()
                
        elif(filepath.endswith(".txt")):
            with open(filepath, "r") as file_to_import:
                for row in file_to_import:
                    obj_type, *other = row.split(",")
                    if(other):
                        if(obj_type == "node"):
                            n, *param = self.str_to_object(other, "node")
                            self.cs.ntw.nf(*param, node_type="router", name=n)
                        else:
                            n, s, d, *param = self.str_to_object(other, obj_type)
                            self.cs.ntw.lf(*param, link_type=obj_type, name=n, s=s, d=d)
                    
        elif(filepath.endswith(".xls")):
            book = xlrd.open_workbook(filepath)
            for id, obj_type in enumerate(self.object_ie):
                xls_sheet = book.sheets()[id]
                for row_index in range(1, xls_sheet.nrows):
                    if(obj_type == "node"):
                        n, *param = self.str_to_object(xls_sheet.row_values(row_index), "node")
                        self.cs.ntw.nf(*param, node_type="router", name=n)
                    elif(obj_type == "link"):
                        n, s, d, *param = self.str_to_object(xls_sheet.row_values(row_index), obj_type)
                        self.cs.ntw.lf(*param, link_type=obj_type, name=n, s=s, d=d)
                
        # for the topology zoo network graphs
        elif(filepath.endswith(".graphml")):
            tree = etree.parse(filepath)
            # dict associating an id ("dxx") to a property ("label", etc)
            dict_prop_values = {}
            # dict associating a node id to node properties
            dict_id_to_prop = collections.defaultdict(dict)
            # label will be the name of the node
            properties = ["label", "Longitude", "Latitude"]
            
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
                        src = self.cs.ntw.nf(name=src_name)
                        dest_name = dict_id_to_prop[d_id]["label"]
                        dest = self.cs.ntw.nf(name=dest_name)
                        
                        # set the latitude and longitude of the newly created nodes
                        for coord in ("latitude", "longitude"):
                            src.__dict__[coord] = dict_id_to_prop[s_id][coord.capitalize()]
                            dest.__dict__[coord] = dict_id_to_prop[d_id][coord.capitalize()]
                        
                        # distance between src and dest
                        param = map(float, (src.longitude, src.latitude, dest.longitude, dest.latitude))
                        distance = round(self.cs.ntw.haversine_distance(*param))

                        # in some graphml files, there are nodes with loopback link
                        if src_name != dest_name:
                            new_link = self.cs.ntw.lf(s=src, d=dest)
                            new_link.distance = distance
        
        self.cs.draw_all(False)
        self.cs._refresh_object_labels("trunk", "distance")
        
        
    def export_graph(self, filepath=None):
        # filepath is set for unittest
        if not filepath:
            selected_file = filedialog.asksaveasfile(initialdir=self.path_workspace, title="Export graph", mode='w', defaultextension=".xls")
            
            if not selected_file: 
                return 
            else:
                filename, file_format = os.path.splitext(selected_file.name)
        else:
            filename, file_format = os.path.splitext(filepath)
            selected_file = open(filepath, "w")

        if(file_format in (".txt", ".csv")):
            graph_per_line = []
            for obj_type, properties in self.object_ie.items():
                graph_per_line.append(obj_type)
                for obj in self.cs.ntw.pn[obj_type].values():
                    param = ",".join(str(obj.__dict__[property]) for property in properties)
                    graph_per_line.append(",".join((obj_type, param)))
            if(file_format == ".txt"):
                selected_file.write("\n".join(graph_per_line))
            else:
                graph_writer = csv.writer(selected_file, delimiter=",", lineterminator="\n")
                for line in graph_per_line:
                    graph_writer.writerow(line.split(","))
            
        if(file_format == ".xls"):
            excel_workbook = xlwt.Workbook()
            for obj_type, properties in self.object_ie.items():
                xls_sheet = excel_workbook.add_sheet(obj_type)
                for id, property in enumerate(properties):
                    xls_sheet.write(0, id, property)
                    for i, t in enumerate(self.cs.ntw.pn[obj_type].values(), 1):
                        xls_sheet.write(i, id, str(t.__dict__[property]))
            AS_sheet = excel_workbook.add_sheet("AS")
            for i, AS in enumerate(self.cs.ntw.pn["AS"].values(), 1):
                AS_sheet.write(i, 0, str(AS.name))
                AS_sheet.write(i, 1, str(AS.type))
                AS_sheet.write(i, 2, str(list(map(str, AS.pAS["node"]))))
                AS_sheet.write(i, 3, str(list(map(str, AS.pAS["trunk"]))))
                AS_sheet.write(i, 4, str(list(map(str, AS.pAS["edge"]))))
                AS_sheet.write(i, 5, str(list(AS.areas.keys())))
                
            area_sheet = excel_workbook.add_sheet("area")
            cpt = 1
            for AS in self.cs.ntw.pn["AS"].values():
                for area in AS.areas.values():
                    area_sheet.write(cpt, 0, str(area.name))
                    area_sheet.write(cpt, 1, str(area.AS))
                    area_sheet.write(cpt, 2, str(list(map(str, area.pa["node"]))))
                    area_sheet.write(cpt, 3, str(list(map(str, area.pa["trunk"]))))
                    cpt += 1
            excel_workbook.save(selected_file.name)
            
            
        selected_file.close()
        