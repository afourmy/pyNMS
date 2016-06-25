# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import sys
import tkinter as tk
import os
from os.path import abspath, pardir, join
from tkinter import ttk, filedialog
from miscellaneous import FocusTopLevel
import network
import collections
import object_management_window as omw
import advanced_graph_options as ago
import drawing_options_window as dow
import frame
import scenario
import pickle
import csv
import xlrd, xlwt
import xml.etree.ElementTree as etree
import warnings
from PIL import ImageTk

class NetDim(tk.Tk):
    
    def __init__(self, path_app):
        tk.Tk.__init__(self)
        path_parent = abspath(join(path_app, pardir))
        self.path_icon = path_parent + "\\Icons\\"
        self.path_workspace = path_parent + "\\Workspace\\"
            
        ## ----- Main app : -----
        self.title("NetDim")
        netdim_icon = tk.PhotoImage(file=self.path_icon + "netdim_icon.gif")
        self.tk.call('wm', 'iconphoto', self._w, netdim_icon)
        
        ## User-defined properties and labels per type of object
        
        # I used ordered dicts to have the same menu order 
        node_properties = (
        "name", 
        "x", 
        "y", 
        "longitude", 
        "latitude", 
        "ipaddress", 
        "subnetmask", 
        "AS"
        )
        
        self.object_properties = collections.OrderedDict([
        ("router", node_properties),
        ("oxc", node_properties),
        ("host", node_properties),
        ("antenna", node_properties),
        ("regenerator", node_properties),
        ("splitter", node_properties),
        
        ("trunk", 
        (
        "name", 
        "source", 
        "destination", 
        "distance", 
        "costSD", 
        "costDS", 
        "capacitySD", 
        "capacityDS", 
        "trafficSD", 
        "trafficDS",
        "flowSD", 
        "flowDS",
        "ipaddressS", 
        "subnetmaskS", 
        "interfaceS",
        "ipaddressD", 
        "subnetmaskD", 
        "interfaceD",
        "AS"
        )),
        
        ("route", 
        (
        "name",
        "source", 
        "destination", 
        "distance", 
        "path_constraints", 
        "excluded_nodes", 
        "excluded_trunks", 
        "path", 
        "subnets", 
        "cost", 
        "traffic", 
        "AS"
        )),
        
        ("traffic", 
        (
        "name", 
        "source", 
        "destination", 
        "distance", 
        "throughput",
        ))])
        
        self.object_label = collections.OrderedDict([
        ("Node", 
        (
        "None", 
        "Name", 
        "Position", 
        "Coordinates", 
        "IPAddress"
        )),
        
        ("Trunk", 
        (
        "None", 
        "Name", 
        "Distance", 
        "Cost", 
        "Capacity", 
        "Flow", 
        "Traffic", 
        "IPaddress"
        )),
        
        ("Route", 
        (
        "None", 
        "Name", 
        "Distance", 
        "Type", 
        "Path", 
        "Cost", 
        "Subnet", 
        "Traffic"
        )),
        ("Traffic", 
        (
        "None", 
        "Name", 
        "Distance", 
        "Throughput"
        ))])
        
        # object import export (properties)
        self.object_ie = collections.OrderedDict([
        ("node", (
        "name", 
        "x", 
        "y", 
        "longitude", 
        "latitude", 
        "ipaddress", 
        "subnetmask", 
        )),
        
        ("trunk", 
        (
        "name", 
        "source", 
        "destination", 
        "distance", 
        "costSD", 
        "costDS", 
        "capacitySD", 
        "capacityDS", 
        "trafficSD",
        "trafficDS",
        "ipaddressS", 
        "subnetmaskS", 
        "interfaceS",
        "ipaddressD", 
        "subnetmaskD", 
        "interfaceD",
        )),
        
        ("route", 
        (
        "name", 
        "source", 
        "destination", 
        "distance", 
        "path_constraints",
        "excluded_nodes", 
        "excluded_trunks", 
        "cost", 
        "subnets", 
        )),
        
        ("traffic", 
        (
        "name", 
        "source", 
        "destination", 
        "distance", 
        "throughput"
        ))])
        
        # methods for string to object conversions
        convert_node = lambda n: self.cs.ntw.nf(name=n)
        convert_link = lambda l: self.cs.ntw.lf(name=l)
        convert_AS = lambda AS: self.cs.ntw.AS_factory(name=AS)
        self.convert_nodes_set = lambda ln: set(map(convert_node, eval(ln)))
        convert_nodes_list = lambda ln: list(map(convert_node, eval(ln)))
        self.convert_links_set = lambda ll: set(map(convert_link, eval(ll)))
        convert_links_list = lambda ll: list(map(convert_link, eval(ll)))
        
        # dict property to conversion methods: used at import
        #TODO string to type and type to string needed to refactor
        # the code for AS export
        self.prop_to_type = {
        "name": str, 
        "ipaddress": str,
        "subnetmask": str,
        "x": float, 
        "y": float, 
        "longitude": float, 
        "latitude": float,
        "distance": float, 
        "costSD": float, 
        "costDS": float, 
        "cost": float,
        "capacitySD": int, 
        "capacityDS": int,
        "traffic": float,
        "trafficSD": float,
        "trafficDS": float,
        "flowSD": int,
        "flowDS": int,
        "ipaddressS": str,
        "subnetmaskS": str,
        "ipaddressD": str,
        "subnetmaskD": str, 
        "interfaceS": str,
        "interfaceD": str,
        "throughput": float,
        "source": convert_node, 
        "destination": convert_node, 
        "path_constraints": convert_nodes_list, 
        "excluded_nodes": self.convert_nodes_set,
        "excluded_trunks": self.convert_links_set, 
        "path": convert_links_list, 
        "subnets": str, 
        "AS": convert_AS
        }
        
        ## ----- Menus : -----
        menubar = tk.Menu(self)
        main_menu = tk.Menu(menubar, tearoff=0)
        main_menu.add_command(label="Add scenario", 
                                        command=lambda: self.add_scenario())
        main_menu.add_command(label="Delete scenario", 
                                        command=lambda: self.delete_scenario())
        main_menu.add_separator()
        main_menu.add_command(label="Import graph", 
                                        command=lambda: self.import_graph())
        main_menu.add_command(label="Export graph", 
                                        command=lambda: self.export_graph())
        main_menu.add_separator()
        main_menu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="Main",menu=main_menu)
        menu_drawing = tk.Menu(menubar, tearoff=0)
        menu_drawing.add_command(label="Default drawing parameters", 
                        command=lambda: self.drawing_option_window.deiconify())
        menubar.add_cascade(label="Network drawing",menu=menu_drawing)
        menu_routing = tk.Menu(menubar, tearoff=0)
        menu_routing.add_command(label="Advanced graph options", 
                        command=lambda: self.advanced_graph_options.deiconify())
        menu_routing.add_command(label="Network Tree View", 
                                        command=lambda: NetworkTreeView(self))
        menubar.add_cascade(label="Network routing",menu=menu_routing)

        # choose which label to display per type of object
        menu_options = tk.Menu(menubar, tearoff=0)
        for obj_type, label_type in self.object_label.items():
            menu_type = tk.Menu(menubar, tearoff=0)
            for lbl in label_type:
                cmd = lambda o=obj_type, l=lbl: self.cs._refresh_object_labels(o.lower(), l.lower())
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
        
        # cs for "current scenario" (the first one, which we create)
        self.cs = scenario.Scenario(self, "scenario 0")
        self.cpt_scenario = 0
        self.scenario_notebook.add(self.cs, text=self.cs.name, compound=tk.TOP)
        self.scenario_notebook.pack(fill=tk.BOTH, side=tk.RIGHT)
        self.dict_scenario["scenario 0"] = self.cs
        
        # object management windows
        self.dict_obj_mgmt_window = {}
        for obj in self.object_properties:
            self.dict_obj_mgmt_window[obj] = omw.ObjectManagementWindow(self, obj)
        
        # parameters for spring-based drawing: per project
        self.alpha = 0.5
        self.beta = 10000
        self.k = 0.5
        self.eta = 0.5
        self.delta = 0.35
        self.L0 = 8
        self.opd = 0
        self.drawing_param = (self.alpha, self.beta, self.k, self.eta,
                                                        self.delta, self.L0)
        
        # drawing options window
        self.drawing_option_window = dow.DrawingOptions(self)
        # advanced graph options
        self.advanced_graph_options = ago.AdvancedGraphOptionsWindow(self)
        
        # create a frame
        self.main_frame = frame.MainFrame(self)
        self.main_frame.pack(fill=tk.BOTH, side=tk.RIGHT)
        self.main_frame.pack_propagate(False)
        
        # dict of nodes image for node creation
        self.dict_image = collections.defaultdict(dict)
        
        self.node_size_image = {
        "router": (33, 25), 
        "oxc": (35, 32), 
        "host": (35, 32), 
        "antenna": (35, 35), 
        "regenerator": (64, 50), 
        "splitter": (64, 50)
        }
        
        self.dict_size_image = {
        "general": {
        "netdim": (75, 75), 
        "motion": (75, 75), 
        "multi-layer": (75, 75)
        },
        
        "l_type": {
        l_type: (85, 15) for l_type in self.cs.ntw.link_type
        },
        
        "ntw_topo": {
        "ring": (38, 33), 
        "tree": (35, 21), 
        "star": (36, 35), 
        "full-mesh": (40, 36)
        },
        
        "drawing": {
        "draw": (50, 50), 
        "stop": (50, 50)
        }}
        
        for color in ["default", "red"]:
            for node_type in self.cs.ntw.node_type:
                img_path = "".join((self.path_icon, color, "_", node_type, ".gif"))
                img_pil = ImageTk.Image.open(img_path).resize(self.node_size_image[node_type])
                img = ImageTk.PhotoImage(img_pil)
                # set the default image for the button of the frame
                if color == "default":
                    self.main_frame.type_to_button[node_type].config(image=img, 
                                                        width=50, height=50)
                self.dict_image[color][node_type] = img
        
        for category_type, dict_size in self.dict_size_image.items():
            for image_type, image_size in dict_size.items():
                x, y = image_size
                img_path = "".join((self.path_icon, image_type, ".png"))
                img_pil = ImageTk.Image.open(img_path).resize(image_size)
                img = ImageTk.PhotoImage(img_pil)
                self.dict_image[category_type][image_type] = img
                self.main_frame.type_to_button[image_type].config(image=img, 
                                                        width=x, height=y+10)
                
        # image for a link failure
        img_pil = ImageTk.Image.open(self.path_icon + "failure.png").resize((25,25))
        self.img_failure = ImageTk.PhotoImage(img_pil)
            
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
            filepath = filedialog.askopenfilenames(
                            initialdir=self.path_workspace, 
                            title="Import graph", 
                            filetypes=(
                            ("all files","*.*"), 
                            ("csv files","*.csv"), 
                            ("xls files","*.xls"), 
                            ("txt files","*.txt")
                            ))
            
            # no error when closing the window
            if not filepath: 
                return
            else: 
                filepath ,= filepath

        if filepath.endswith(".csv"):
            try:
                file_to_import = open(filepath, "rt")
                reader = csv.reader(file_to_import)
                for row in filter(None, reader):
                    obj_type, *other = row
                    if other:
                        if obj_type == "node":
                            n, *param = self.str_to_object(other, "node")
                            self.cs.ntw.nf(*param, node_type="router", name=n)
                        else:
                            n, s, d, *param = self.str_to_object(other, obj_type)
                            self.cs.ntw.lf(*param, link_type=obj_type, 
                                                            name=n, s=s, d=d)
                            
            finally:
                file_to_import.close()
                    
        elif filepath.endswith(".xls"):
            book = xlrd.open_workbook(filepath)
            for id, obj_type in enumerate(self.object_ie):
                xls_sheet = book.sheets()[id]
                for row_index in range(1, xls_sheet.nrows):
                    if obj_type == "node":
                        n, *param = self.str_to_object(
                                    xls_sheet.row_values(row_index), "node")
                        self.cs.ntw.nf(*param, node_type="router", name=n)
                    else:
                        n, s, d, *param = self.str_to_object(
                                    xls_sheet.row_values(row_index), obj_type)
                        new_link = self.cs.ntw.lf(*param, link_type=obj_type, 
                                                            name=n, s=s, d=d)
                        
            AS_sheet, area_sheet = book.sheets()[4], book.sheets()[5]
        
            # creation of the AS
            for row_index in range(1, AS_sheet.nrows):
                AS_name, AS_type, AS_nodes, AS_trunks, AS_edges, *o = AS_sheet.row_values(row_index)
                AS_nodes = self.convert_nodes_set(AS_nodes)
                AS_trunks = self.convert_links_set(AS_trunks)
                AS_edges = self.convert_nodes_set(AS_edges)
                self.cs.ntw.AS_factory(AS_name, AS_type, AS_trunks, AS_nodes, 
                                                        AS_edges, set(), True)
            
            # creation of the area
            for row_index in range(1, area_sheet.nrows):
                name, AS, id, nodes, trunks = area_sheet.row_values(row_index)
                AS = self.cs.ntw.AS_factory(name=AS)
                nodes = self.convert_nodes_set(nodes)
                trunks = self.convert_links_set(trunks)
                new_area = AS.area_factory(name, int(id), trunks, nodes)
            
                
        # for the topology zoo network graphs
        elif filepath.endswith(".graphml"):
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
                        if child.attrib["attr.name"] in properties and child.attrib["for"] == "node":
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
                            # in some graphml files, nodes have no latitude/longitude
                            try:
                                p_s = dict_id_to_prop[s_id][coord.capitalize()]
                                setattr(src, coord, float(p_s))
                                p_d = dict_id_to_prop[d_id][coord.capitalize()]
                                setattr(dest, coord, float(p_d))
                            except KeyError:
                                # we catch the KeyError exception, but 
                                # the resulting haversine distance will be wrong
                                warnings.warn("Wrong geographical coordinates")
                        
                        # distance between src and dest
                        distance = round(self.cs.ntw.haversine_distance(src, dest))

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

        if file_format == ".csv":
            graph_per_line = []
            for obj_type, properties in self.object_ie.items():
                graph_per_line.append(obj_type)
                for obj in self.cs.ntw.pn[obj_type].values():
                    param = ",".join(str(getattr(obj, property)) for property in properties)
                    graph_per_line.append(",".join((obj_type, param)))
            graph_writer = csv.writer(selected_file, delimiter=",", lineterminator="\n")
            for line in graph_per_line:
                graph_writer.writerow(line.split(","))
            
        if file_format == ".xls":
            excel_workbook = xlwt.Workbook()
            for obj_type, properties in self.object_ie.items():
                xls_sheet = excel_workbook.add_sheet(obj_type)
                for id, property in enumerate(properties):
                    xls_sheet.write(0, id, property)
                    for i, t in enumerate(self.cs.ntw.pn[obj_type].values(), 1):
                        xls_sheet.write(i, id, str(getattr(t, property)))
            AS_sheet = excel_workbook.add_sheet("AS")
            for i, AS in enumerate(self.cs.ntw.pnAS.values(), 1):
                AS_sheet.write(i, 0, str(AS.name))
                AS_sheet.write(i, 1, str(AS.type))
                AS_sheet.write(i, 2, str(list(map(str, AS.pAS["node"]))))
                AS_sheet.write(i, 3, str(list(map(str, AS.pAS["trunk"]))))
                AS_sheet.write(i, 4, str(list(map(str, AS.pAS["edge"]))))
                AS_sheet.write(i, 5, str(list(AS.areas.keys())))
                
            area_sheet = excel_workbook.add_sheet("area")
            cpt = 1
            for AS in self.cs.ntw.pnAS.values():
                for area in AS.areas.values():
                    area_sheet.write(cpt, 0, str(area.name))
                    area_sheet.write(cpt, 1, str(area.AS))
                    area_sheet.write(cpt, 2, str(area.id))
                    area_sheet.write(cpt, 3, str(list(map(str, area.pa["node"]))))
                    area_sheet.write(cpt, 4, str(list(map(str, area.pa["trunk"]))))
                    cpt += 1
            excel_workbook.save(selected_file.name)
            
        selected_file.close()
        
class NetworkTreeView(FocusTopLevel):

    def __init__(self, master):
        super().__init__()
        self.geometry("900x500")
        self.title("Network Tree View")
        # TODO add AS property too, botrh in manage AS and here
        self.ntv = ttk.Treeview(self, selectmode="extended")
        n = max(map(len, master.object_ie.values()))

        self.ntv["columns"] = tuple(map(str, range(n)))
        for i in range(n):
            self.ntv.column(str(i), width=70)
            
        self.ntv.bind('<ButtonRelease-1>', lambda e: self.select(e))
        
        for obj_type, properties in master.object_ie.items():
            self.ntv.insert("", "end", obj_type, text=obj_type.title(), 
                                                            values=properties)
            for obj in master.cs.ntw.pn[obj_type].values():
                values = tuple(map(lambda p: getattr(obj, p), properties))
                self.ntv.insert(obj_type, "end", text=obj.name, values=values)
        
        self.ntv.pack(expand=tk.YES, fill=tk.BOTH)
        
        self.deiconify()
        
    def select(self, event):
        for item in self.ntv.selection():
            item_text = self.ntv.item(item,"text")
            print(item_text)