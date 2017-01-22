# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import sys
import tkinter as tk
import os
import copy
import csv
import xml.etree.ElementTree as etree
import warnings
import network
import scenario
from collections import OrderedDict, defaultdict
from os.path import abspath, pardir, join
from tkinter import ttk, filedialog
from objects import object_management_window as omw
from objects.objects import *
from pythonic_tkinter.preconfigured_widgets import *
from miscellaneous import graph_algorithms as galg
from miscellaneous import debug
from drawing import drawing_options_window as dow
from graph_generation import advanced_graph as adv_gr
from optical_networks import rwa_window as rwaw
from miscellaneous.network_functions import IPAddress
from menus import main_menu
from PIL import ImageTk
try:
    import xlrd
    import xlwt
except ImportError:
    warnings.warn('Excel library missing: excel import/export disabled')

class NetDim(MainWindow):
    
    def __init__(self, path_app):
        super().__init__()
        path_parent = abspath(join(path_app, pardir))
        self.path_icon = join(path_parent, 'Icons')
        self.path_workspace = join(path_parent, 'Workspace')
            
        ## ----- Main app : -----
        self.title('NetDim')
        netdim_icon = tk.PhotoImage(file=join(self.path_icon, 'netdim_icon.gif'))
        self.tk.call('wm', 'iconphoto', self._w, netdim_icon)
        
        colors = ['default', 'red', 'purple']
        
        # scenario notebook
        self.scenario_notebook = ttk.Notebook(self)
        self.scenario_notebook.bind('<ButtonRelease-1>', self.change_cs)
        self.dict_scenario = {}
        
        # cs for 'current scenario' (the first one, which we create)        
        self.cs = scenario.Scenario(self, 'scenario 0')
        self.cpt_scenario = 0
        self.scenario_notebook.add(self.cs, text=self.cs.name, compound=tk.TOP)
        self.dict_scenario['scenario 0'] = self.cs
        
        # advanced graph options
        self.advanced_graph_options = galg.GraphAlgorithmWindow(self)
        
        # routing and wavelength assignment window
        self.rwa_window = rwaw.RWAWindow(self)
        
        # graph generation window
        self.advanced_graph = adv_gr.AdvancedGraph(self)
        
        # debug window
        self.debug_window = debug.Debug(self)
        
        ## ----- Menus : -----
        netdim_menu = Menu(self)
        
        # general menu: add/delete scenario, import/export graph, exit NetDim
        
        general_menu = Menu(netdim_menu)
        
        add_scenario = MenuEntry(general_menu)
        add_scenario.text = 'Add scenario'
        add_scenario.command = self.add_scenario
        
        delete_scenario = MenuEntry(general_menu)
        delete_scenario.text = 'Delete scenario'
        delete_scenario.command = self.delete_scenario
        
        general_menu.separator()
        
        import_graph = MenuEntry(general_menu)
        import_graph.text = 'Import graph'
        import_graph.command = self.import_graph
        
        export_graph = MenuEntry(general_menu)
        export_graph.text = 'Export graph'
        export_graph.command = self.export_graph

        general_menu.separator()
        
        debug_entry = MenuEntry(general_menu)
        debug_entry.text = 'Debug'
        debug_entry.command = self.debug_window.deiconify
        
        exit = MenuEntry(general_menu)
        exit.text = 'Exit'
        exit.command = self.destroy

        general_menu.create_menu()
        netdim_menu.add_cascade(label='Main',menu=general_menu)
        
        # drawing menu: for default drawing parameters
        drawing_menu = Menu(netdim_menu)
        
        drawing_parameters_entry = MenuEntry(drawing_menu)
        drawing_parameters_entry.text = 'Default drawing parameters'
        drawing_parameters_entry.command = lambda: dow.DrawingOptions(self)
        
        drawing_menu.create_menu()
        
        netdim_menu.add_cascade(label='Network drawing',menu=drawing_menu)
        
        # routing menu:
        
        routing_menu = Menu(netdim_menu)
        
        advanced_graph_entry = MenuEntry(routing_menu)
        advanced_graph_entry.text = 'Advanced graph'
        advanced_graph_entry.command = self.advanced_graph.deiconify
        
        advanced_algorithms_entry = MenuEntry(routing_menu)
        advanced_algorithms_entry.text = 'Advanced algorithms'
        advanced_algorithms_entry.command = self.advanced_graph_options.deiconify

        network_tree_view_entry = MenuEntry(routing_menu)
        network_tree_view_entry.text = 'Network Tree View'
        network_tree_view_entry.command = lambda: NetworkTreeView(self)
        
        wavelenght_assignment_entry = MenuEntry(routing_menu)
        wavelenght_assignment_entry.text = 'Wavelength assignment'
        wavelenght_assignment_entry.command = self.rwa_window.deiconify
        
        routing_menu.create_menu()
        netdim_menu.add_cascade(label='Network routing',menu=routing_menu)

        # choose which label to display per type of object
        display_menu = Menu(netdim_menu)
        for obj_type, label_type in object_labels.items():
            menu_type = Menu(netdim_menu)
            display_menu.add_cascade(label=obj_type + ' label', menu=menu_type)
            for lbl in label_type:
                cmd = lambda o=obj_type, l=lbl: self.cs.refresh_labels(o, l)
                type_entry = MenuEntry(menu_type)
                type_entry.text = lbl
                type_entry.command = cmd
            menu_type.create_menu()
        
        # show / hide option per type of objects
        show_menu = Menu(netdim_menu)
        for index, type in enumerate(object_properties):
            new_label = ' '.join(('Hide', type))
            cmd = lambda t=type, i=index: self.cs.show_hide(show_menu, t, i)
            show_entry = MenuEntry(show_menu)
            show_entry.text = new_label
            show_entry.command = cmd
        show_menu.create_menu()
            
        display_menu.add_cascade(label='Show/hide object', menu=show_menu)
        netdim_menu.add_cascade(label='Options', menu=display_menu)
        
        self.config(menu=netdim_menu)
        
        # object management windows
        self.dict_obj_mgmt_window = {}
        for obj in object_properties:
            self.dict_obj_mgmt_window[obj] = omw.ObjectManagementWindow(self, obj)
        
        # drawing algorithm and parameters: per project
        self.drawing_algorithm = 'Spring layout'

        self.drawing_params = {
        'Spring layout': OrderedDict([
        ('Coulomb factor', 10000),
        ('Spring stiffness', 0.5),
        ('Speed factor', 0.35),
        ('Equilibrium length', 8.)
        ]),
        
        'F-R layout': OrderedDict([
        ('OPD', 0.),
        ('limit', True)
        ])}
        
        # create a menu
        self.main_menu = main_menu.MainMenu(self)
        self.main_menu.pack(fill=tk.BOTH, side=tk.LEFT)
        self.scenario_notebook.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        
        # dict of nodes image for node creation
        self.dict_image = defaultdict(dict)
        
        self.node_size_image = {
        'router': (33, 25), 
        'switch': (54, 36),
        'oxc': (35, 32), 
        'host': (35, 32), 
        'regenerator': (64, 50), 
        'splitter': (64, 50),
        'antenna': (35, 35),
        'cloud': (60, 35),
        }
        
        self.dict_size_image = {
        'general': {
        'netdim': (75, 75), 
        'motion': (75, 75), 
        'multi-layer': (75, 75)
        },
        
        'l_type': {
        'ethernet': (85, 15),
        'wdm': (85, 15),
        'static route': (85, 15),
        'BGP peering': (85, 15),
        'OSPF virtual link': (85, 15),
        'Label Switched Path': (85, 15),
        'routed traffic': (85, 15),
        'static traffic': (85, 15)
        },
        
        'ntw_topo': {
        'ring': (38, 33), 
        'tree': (35, 21), 
        'star': (36, 35), 
        'full-mesh': (40, 36)
        }}
        
        for color in colors:
            for node_type in self.cs.ntw.node_subtype:
                img_path = join(self.path_icon, ''.join(
                                            (color, '_', node_type, '.gif')))
                img_pil = ImageTk.Image.open(img_path).resize(
                                            self.node_size_image[node_type])
                img = ImageTk.PhotoImage(img_pil)
                # set the default image for the button of the frame
                if color == 'default':
                    self.main_menu.type_to_button[node_type].config(image=img, 
                                                        width=50, height=50)
                self.dict_image[color][node_type] = img
        
        for category_type, dict_size in self.dict_size_image.items():
            for image_type, image_size in dict_size.items():
                x, y = image_size
                img_path = join(self.path_icon, image_type + '.png')
                img_pil = ImageTk.Image.open(img_path).resize(image_size)
                img = ImageTk.PhotoImage(img_pil)
                self.dict_image[category_type][image_type] = img
                self.main_menu.type_to_button[image_type].config(image=img, 
                                                        width=x, height=y+10)
                
        # image for a link failure
        img_pil = ImageTk.Image.open(join(self.path_icon, 'failure.png'))\
                                                                .resize((25,25))
        self.img_failure = ImageTk.PhotoImage(img_pil)
        
            
    def change_cs(self, event=None):
        cs_name = self.scenario_notebook.tab(self.scenario_notebook.select(), 'text')
        self.cs = self.dict_scenario[cs_name]
        
    def add_scenario(self, name=None):
        self.cpt_scenario += 1
        if not name:
            name = ' '.join(('scenario', str(self.cpt_scenario)))
        new_scenario = scenario.Scenario(self, name)
        self.scenario_notebook.add(new_scenario, text=name, compound=tk.TOP)
        self.dict_scenario[name] = new_scenario
        return new_scenario
        
    def duplicate_scenario(self):
        pass
        
    def delete_scenario(self):
        del self.dict_scenario[self.cs.name]
        self.scenario_notebook.forget(self.cs)
        self.change_cs()
                        
    def objectizer(self, properties, values, obj_type):
        kwargs = {}
        for property, value in zip(properties, values):
            print(property, value)
            value = self.cs.ntw.prop_to_type[property](value)
            if value == "None":
                value = None
            kwargs[property] = value
        return kwargs
                
    def import_graph(self, filepath=None):
                
        # filepath is set for unittest
        if not filepath:
            filepath = filedialog.askopenfilenames(
                            initialdir=self.path_workspace, 
                            title='Import graph', 
                            filetypes=(
                            ('all files','*.*'),
                            ('csv files','*.csv'),
                            ('xls files','*.xls'),
                            ))
            
            # no error when closing the window
            if not filepath: 
                return
            else: 
                filepath ,= filepath
                  
        if filepath.endswith('.xls'):
            book = xlrd.open_workbook(filepath)
            for id, obj_type in enumerate(object_ie):
                xls_sheet = book.sheets()[id]
                properties = xls_sheet.row_values(0)
                for row in range(1, xls_sheet.nrows):
                    values = xls_sheet.row_values(row)
                    kwargs = self.objectizer(properties, values, obj_type)
                    if obj_type in self.cs.ntw.node_subtype: 
                        self.cs.ntw.nf(node_type=obj_type, **kwargs)
                    if obj_type in self.cs.ntw.link_subtype: 
                        self.cs.ntw.lf(subtype=obj_type, **kwargs)
                        
            # interface properties update
            for i in range(16, 18):
                interface_sheet = book.sheets()[i]
                if_properties = interface_sheet.row_values(0)
                # creation of ethernet interfaces
                for row_index in range(1, interface_sheet.nrows):
                    link, node, *args = interface_sheet.row_values(row_index)
                    link = self.cs.ntw.convert_link(link)
                    node = self.cs.ntw.convert_node(node)
                    interface = link('interface', node)
                    for property, value in zip(if_properties[2:], args):
                        # we convert all string IPs to an OIPs
                        if property == 'ipaddress':
                            value = self.cs.ntw.OIPf(value, interface)
                        setattr(interface, property, value)
                                                        
            AS_sheet = book.sheets()[18]
        
            # creation of the AS
            for row_index in range(1, AS_sheet.nrows):
                name, type, id, nodes, plinks = AS_sheet.row_values(row_index)
                id = int(id)
                nodes = self.cs.ntw.convert_node_set(nodes)
                plinks = self.cs.ntw.convert_link_set(plinks)
                self.cs.ntw.AS_factory(type, name, id, plinks, nodes, True)
                
            area_sheet = book.sheets()[19]
            
            # creation of the area
            for row_index in range(1, area_sheet.nrows):
                name, AS, id, nodes, plinks = area_sheet.row_values(row_index)
                AS = self.cs.ntw.AS_factory(name=AS)
                nodes = self.cs.ntw.convert_node_set(nodes)
                plinks = self.cs.ntw.convert_link_set(plinks)
                new_area = AS.area_factory(name, int(id), plinks, nodes)
                
            node_AS_sheet = book.sheets()[20]
            
            for row_index in range(1, node_AS_sheet.nrows):
                AS, node, *args = node_AS_sheet.row_values(row_index)
                node = self.cs.ntw.convert_node(node)
                for idx, property in enumerate(perAS_properties[node.subtype]):
                    node(AS, property, args[idx])
                    
            if_AS_sheet = book.sheets()[21]
            
            for row_index in range(1, if_AS_sheet.nrows):
                AS, link, node, *args = if_AS_sheet.row_values(row_index)
                AS = self.cs.ntw.AS_factory(name=AS)
                link = self.cs.ntw.convert_link(link)
                node = self.cs.ntw.convert_node(node)
                interface = link('interface', node)
                for idx, property in enumerate(ethernet_interface_perAS_properties):
                    interface(AS.name, property, args[idx])
                
        # if_AS_sheet = excel_workbook.add_sheet('per-AS interface properties')
        # 
        # cpt = 1
        # for AS in self.cs.ntw.pnAS.values():
        #     for link in AS.plinks:
        #         for interface in (link.interfaceS, link.interfaceD):
        #             if_AS_sheet.write(cpt, 0, AS.name)
        #             if_AS_sheet.write(cpt, 1, str(interface.link))
        #             if_AS_sheet.write(cpt, 2, str(interface.node)) 
        #             for idx, property in enumerate(ethernet_interface_perAS_properties, 3):
        #                 if_AS_sheet.write(cpt, idx, str(interface(AS.name, property)))
        #             cpt += 1
                
        # for the topology zoo network graphs
        elif filepath.endswith('.graphml'):
            tree = etree.parse(filepath)
            # dict associating an id ('dxx') to a property ('label', etc)
            dict_prop_values = {}
            # dict associating a node id to node properties
            dict_id_to_prop = collections.defaultdict(dict)
            # label will be the name of the node
            properties = ['label', 'Longitude', 'Latitude']
            
            for element in tree.iter():
                for child in element:
                    if 'key' in child.tag:
                        if child.attrib['attr.name'] in properties and child.attrib['for'] == 'node':
                            dict_prop_values[child.attrib['id']] = child.attrib['attr.name']
                    if 'node' in child.tag:
                        node_id = child.attrib['id']
                        for prop in child:
                            if prop.attrib['key'] in dict_prop_values:
                                dict_id_to_prop[node_id][dict_prop_values[prop.attrib['key']]] = prop.text
                    if 'edge' in child.tag:
                        s_id, d_id = child.attrib['source'], child.attrib['target']
                        src_name = dict_id_to_prop[s_id]['label']
                        src = self.cs.ntw.nf(name=src_name)
                        dest_name = dict_id_to_prop[d_id]['label']
                        dest = self.cs.ntw.nf(name=dest_name)
                        
                        # set the latitude and longitude of the newly created nodes
                        for coord in ('latitude', 'longitude'):
                            # in some graphml files, nodes have no latitude/longitude
                            try:
                                p_s = dict_id_to_prop[s_id][coord.capitalize()]
                                setattr(src, coord, float(p_s))
                                p_d = dict_id_to_prop[d_id][coord.capitalize()]
                                setattr(dest, coord, float(p_d))
                            except KeyError:
                                # we catch the KeyError exception, but 
                                # the resulting haversine distance will be wrong
                                warnings.warn('Wrong geographical coordinates')
                        
                        # distance between src and dest
                        distance = round(self.cs.ntw.haversine_distance(src, dest))

                        # in some graphml files, there are nodes with loopback link
                        if src_name != dest_name:
                            new_link = self.cs.ntw.lf(source=src, destination=dest)
                            new_link.distance = distance
        
        self.cs.draw_all(False)        
        
    def export_graph(self, filepath=None):
        
        # to convert a list of object into a string of a list of strings
        # useful for AS nodes, edges, plinks as well as area nodes and plinks
        to_string = lambda s: str(list(map(str, s)))
        
        # filepath is set for unittest
        if not filepath:
            selected_file = filedialog.asksaveasfile(
                                    initialdir=self.path_workspace, 
                                    title='Export graph', 
                                    mode='w', 
                                    defaultextension='.xls'
                                    )
            if not selected_file: 
                return 
            else:
                filename, file_format = os.path.splitext(selected_file.name)
        else:
            filename, file_format = os.path.splitext(filepath)
            selected_file = open(filepath, 'w')
            
        excel_workbook = xlwt.Workbook()
        for obj_type, properties in object_ie.items():
            xls_sheet = excel_workbook.add_sheet(obj_type)
            for id, property in enumerate(properties):
                xls_sheet.write(0, id, property)
                # we have one excel sheet per subtype of object.
                # we filter the network pool based on the subtype to 
                # retrieve only the object of the corresponding subtype
                # this was done because objects have different properties
                # depending on the subtype, and we want to avoid using 
                # hasattr() all the time to check if a property exists.
                ftr = lambda o: o.subtype == obj_type
                if obj_type in self.cs.ntw.link_class:
                    type = subtype_to_type[obj_type]
                    pool_obj = filter(ftr, self.cs.ntw.pn[type].values())
                elif obj_type in self.cs.ntw.node_subtype:
                    pool_obj = filter(ftr, self.cs.ntw.pn['node'].values()) 
                # if it is neither a node nor an interface, it is a node
                else:
                    pool_obj = self.cs.ntw.interfaces[obj_type.split()[0]]
                for i, t in enumerate(pool_obj, 1):
                    xls_sheet.write(i, id, str(getattr(t, property)))
                    
        AS_sheet = excel_workbook.add_sheet('AS')
        
        for i, AS in enumerate(self.cs.ntw.pnAS.values(), 1):
            AS_sheet.write(i, 0, str(AS.name))
            AS_sheet.write(i, 1, str(AS.AS_type))
            AS_sheet.write(i, 2, str(AS.id))
            AS_sheet.write(i, 3, to_string(AS.pAS['node']))
            AS_sheet.write(i, 4, to_string(AS.pAS['plink']))
            
        area_sheet = excel_workbook.add_sheet('area')
        
        cpt = 1
        for AS in filter(lambda a: a.has_area, self.cs.ntw.pnAS.values()):
            for area in AS.areas.values():
                area_sheet.write(cpt, 0, str(area.name))
                area_sheet.write(cpt, 1, str(area.AS))
                area_sheet.write(cpt, 2, str(area.id))
                area_sheet.write(cpt, 3, to_string(area.pa['node']))
                area_sheet.write(cpt, 4, to_string(area.pa['plink']))
                cpt += 1
                
        node_AS_sheet = excel_workbook.add_sheet('per-AS node properties')
        
        cpt = 1
        for AS in self.cs.ntw.pnAS.values():
            for node in AS.nodes:
                node_AS_sheet.write(cpt, 0, AS.name)
                node_AS_sheet.write(cpt, 1, node.name)
                for idx, property in enumerate(perAS_properties[node.subtype], 2):
                    node_AS_sheet.write(cpt, idx, str(node(AS.name, property)))
                cpt += 1
                
        if_AS_sheet = excel_workbook.add_sheet('per-AS interface properties')
        
        cpt = 1
        for AS in self.cs.ntw.pnAS.values():
            for link in AS.plinks:
                for interface in (link.interfaceS, link.interfaceD):
                    if_AS_sheet.write(cpt, 0, AS.name)
                    if_AS_sheet.write(cpt, 1, str(interface.link))
                    if_AS_sheet.write(cpt, 2, str(interface.node)) 
                    for idx, property in enumerate(ethernet_interface_perAS_properties, 3):
                        if_AS_sheet.write(cpt, idx, str(interface(AS.name, property)))
                    cpt += 1
                
        excel_workbook.save(selected_file.name)
        selected_file.close()
        
class NetworkTreeView(CustomTopLevel):

    def __init__(self, master):
        super().__init__()
        self.geometry('900x500')
        self.title('Network Tree View')
        # TODO add AS property too, botrh in manage AS and here
        self.ntv = ttk.Treeview(self, selectmode='extended')
        n = max(map(len, master.object_ie.values()))

        self.ntv['columns'] = tuple(map(str, range(n)))
        for i in range(n):
            self.ntv.column(str(i), width=70)
            
        self.ntv.bind('<ButtonRelease-1>', lambda e: self.select(e))
        
        for obj_subtype, properties in master.object_ie.items():
            self.ntv.insert('', 'end', obj_subtype, text=obj_subtype.title(), 
                                                            values=properties)
            obj_type = master.nd_obj[obj_subtype]
            flt = lambda o: o.subtype == obj_subtype
            for obj in filter(flt, master.cs.ntw.pn[obj_type].values()):
                values = tuple(map(lambda p: getattr(obj, p), properties))
                self.ntv.insert(obj_subtype, 'end', text=obj.name, values=values)
        
        self.ntv.pack(expand=tk.YES, fill=tk.BOTH)
        
        self.deiconify()
        
    def select(self, event):
        for item in self.ntv.selection():
            item = self.ntv.item(item)
            print(item)
            
            #item_text = self.ntv.item(item, 'text')