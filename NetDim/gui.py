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
from miscellaneous import network_tree_view as ntv
from miscellaneous import debug
from graph_generation import advanced_graph as adv_gr
from optical_networks import rwa_window as rwaw
from miscellaneous.network_functions import IPAddress
from menus import creation_menu, display_menu, drawing_menu, routing_menu
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
        self.scenario_notebook = Notebook(self)
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
                
        # advanced menu:
        
        advanced_menu = Menu(netdim_menu)
        
        advanced_graph_entry = MenuEntry(advanced_menu)
        advanced_graph_entry.text = 'Advanced graph'
        advanced_graph_entry.command = self.advanced_graph.deiconify
        
        advanced_algorithms_entry = MenuEntry(advanced_menu)
        advanced_algorithms_entry.text = 'Advanced algorithms'
        advanced_algorithms_entry.command = self.advanced_graph_options.deiconify

        network_tree_view_entry = MenuEntry(advanced_menu)
        network_tree_view_entry.text = 'Network Tree View'
        network_tree_view_entry.command = lambda: ntv.NetworkTreeView(self)
        
        wavelenght_assignment_entry = MenuEntry(advanced_menu)
        wavelenght_assignment_entry.text = 'Wavelength assignment'
        wavelenght_assignment_entry.command = self.rwa_window.deiconify
        
        advanced_menu.create_menu()
        netdim_menu.add_cascade(label='Network routing',menu=advanced_menu)

        # choose which label to display per type of object
        label_menu = Menu(netdim_menu)
        for obj_type, label_type in object_labels.items():
            menu_type = Menu(netdim_menu)
            label_menu.add_cascade(label=obj_type + ' label', menu=menu_type)
            for lbl in label_type:
                cmd = lambda o=obj_type, l=lbl: self.cs.refresh_labels(o, l)
                type_entry = MenuEntry(menu_type)
                type_entry.text = lbl
                type_entry.command = cmd
            menu_type.create_menu()
                    
        netdim_menu.add_cascade(label='Options', menu=label_menu)
        
        self.config(menu=netdim_menu)
        
        ## Images
        
        # dict of nodes image for node creation
        self.dict_image = defaultdict(dict)
        self.dict_pil = defaultdict(dict)
        
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
        
        for color in colors:
            for node_type in node_subtype:
                img_path = join(self.path_icon, ''.join(
                                            (color, '_', node_type, '.gif')))
                img_pil = ImageTk.Image.open(img_path).resize(
                                            self.node_size_image[node_type])
                img = ImageTk.PhotoImage(img_pil)
                self.dict_image[color][node_type] = img
                self.dict_pil[color][node_type] = img_pil
                
        # image for a link failure
        img_pil = ImageTk.Image.open(join(self.path_icon, 'failure.png'))\
                                                                .resize((20, 20))
        self.img_failure = ImageTk.PhotoImage(img_pil)
        
        # object management windows
        self.dict_obj_mgmt_window = {}
        for obj in object_properties:
            self.dict_obj_mgmt_window[obj] = omw.ObjectManagementWindow(self, obj)
                
        self.menu_notebook = Notebook(self)
        
        # main menu for creation and selection of objects
        self.creation_menu = creation_menu.CreationMenu(self.menu_notebook, self)
        self.creation_menu.pack(fill=tk.BOTH, side=tk.LEFT)
        
        # display menu to control the display
        self.display_menu = display_menu.DisplayMenu(self.menu_notebook, self)
        self.display_menu.pack(fill=tk.BOTH, side=tk.LEFT)
        
        # drawing menu (force-based algorithm parameters + paint-like drawing)
        self.drawing_menu = drawing_menu.DrawingMenu(self.menu_notebook, self)
        self.drawing_menu.pack(fill=tk.BOTH, side=tk.LEFT)
        
        # routing menu (addresss allocation + tables creation + routing)
        self.routing_menu = routing_menu.RoutingMenu(self.menu_notebook, self)
        self.routing_menu.pack(fill=tk.BOTH, side=tk.LEFT)
        
        self.menu_notebook.add(self.creation_menu, text=' Creation ')
        self.menu_notebook.add(self.display_menu, text=' Display ')
        self.menu_notebook.add(self.drawing_menu, text=' Drawing ')
        self.menu_notebook.add(self.routing_menu, text=' Routing ')
        
        self.menu_notebook.pack(side=tk.LEFT, fill=tk.BOTH)
        
        # notebooks of scenarios
        self.scenario_notebook.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        
    def refresh(self):
        
        commands = (
                    self.cs.ntw.update_AS_topology,
                    self.cs.ntw.vc_creation,
                    self.cs.ntw.interface_configuration,
                    self.cs.ntw.switching_table_creation,
                    self.cs.ntw.routing_table_creation,
                    self.cs.ntw.bgp_table_creation,
                    self.cs.ntw.redistribution,
                    self.cs.ntw.path_finder,
                    lambda: self.cs.draw_all(False),
                    self.cs.refresh_display
                    )
        
        for idx, boolean in enumerate(self.routing_menu.action_booleans):
            if boolean.get():
                commands[idx]()
            
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
        
    def objectizer(self, property, value):
        if value == 'None': 
            return None
        else:
            return self.cs.ntw.prop_to_type[property](value)
                        
    def mass_objectizer(self, properties, values):
        kwargs = {}
        for property, value in zip(properties, values):
            kwargs[property] = self.objectizer(property, value)
        return kwargs
                
    def import_graph(self, filepath=None):
                
        # filepath is set for unittest
        if not filepath:
            filepath = filedialog.askopenfilenames(
                            initialdir = self.path_workspace, 
                            title = 'Import graph', 
                            filetypes = (
                            ('all files','*.*'),
                            ('xls files','*.xls'),
                            ))
            
            # no error when closing the window
            if not filepath: 
                return
            else: 
                filepath ,= filepath
                  
        book = xlrd.open_workbook(filepath)
        
        # the order in which objects are imported is extremely important:
        # - nodes must be imported first, before links
        # - physical links must be imported second, before interface
        # - interface must be imported third, for IP addresses to be created
        # at interface import (the interface being specified at IP creation),
        # else if a traffic link was imported before the interface, the IP
        # address would be created via the ipS/D parameter and it would have
        # no attached interface
        # - then, the remaining links can be imported (routes, traffic)
        # - AS and area can be imported
        # - Finally, per-AS object properties can be imported
        sheet_names_import_order = (
                                    'router',
                                    'switch',
                                    'oxc', 
                                    'host',
                                    'antenna',
                                    'regenerator',
                                    'splitter',
                                    'cloud',
                                    'ethernet',
                                    'ethernet interface',
                                    'wdm', 
                                    'wdm interface',
                                    'static route',
                                    'BGP peering',
                                    'OSPF virtual link',
                                    'Label Switched Path',
                                    'routed traffic',
                                    'static traffic',
                                    'AS',
                                    'area',
                                    'per-AS node properties',
                                    'per-AS interface properties'
                                    )
                                        
        for name in sheet_names_import_order:
            try:
                sheet = book.sheet_by_name(name)
            # if the sheet cannot be found, there's nothing to import
            except xlrd.biffh.XLRDError:
                continue
            
            # nodes and links import
            if name in all_subtypes:
                properties = sheet.row_values(0)
                for row in range(1, sheet.nrows):
                    values = sheet.row_values(row)
                    kwargs = self.mass_objectizer(properties, values)
                    if name in node_subtype: 
                        self.cs.ntw.nf(node_type=name, **kwargs)
                    if name in link_subtype: 
                        self.cs.ntw.lf(subtype=name, **kwargs)
                
            # interface import
            elif name in ('ethernet interface', 'wdm interface'):
                if_properties = sheet.row_values(0)
                # creation of ethernet interfaces
                for row_index in range(1, sheet.nrows):
                    link, node, *args = sheet.row_values(row_index)
                    link = self.cs.ntw.convert_link(link)
                    node = self.cs.ntw.convert_node(node)
                    interface = link('interface', node)
                    for property, value in zip(if_properties[2:], args):
                        # we convert all (valid) string IPs to an OIPs
                        if property == 'ipaddress' and value != 'none':
                            value = self.cs.ntw.OIPf(value, interface)
                        setattr(interface, property, value)
                        
            # AS import
            elif name == 'AS':
                for row_index in range(1, sheet.nrows):
                    name, AS_type, id, nodes, links = sheet.row_values(row_index)
                    id = int(id)
                    subtype = 'ethernet' if AS_type != 'BGP' else 'BGP peering'
                    nodes = self.cs.ntw.convert_node_set(nodes)
                    links = self.cs.ntw.convert_link_set(links, subtype)
                    self.cs.ntw.AS_factory(AS_type, name, id, links, nodes, True)
                
            # area import
            elif name == 'area':
                for row_index in range(1, sheet.nrows):
                    name, AS, id, nodes, links = sheet.row_values(row_index)
                    AS = self.cs.ntw.AS_factory(name=AS)
                    nodes = self.cs.ntw.convert_node_set(nodes)
                    links = self.cs.ntw.convert_link_set(links)
                    new_area = AS.area_factory(name, int(id), links, nodes)
                    
            # per-AS node properties import
            elif name == 'per-AS node properties':
                for row_index in range(1, sheet.nrows):
                    AS, node, *args = sheet.row_values(row_index)
                    node = self.cs.ntw.convert_node(node)
                    for idx, property in enumerate(perAS_properties[node.subtype]):
                        value = self.objectizer(property, args[idx])
                        node(AS, property, value)
                    
            # per-AS interface properties import
            else:
                for row_index in range(1, sheet.nrows):
                    AS, link, node, *args = sheet.row_values(row_index)
                    AS = self.cs.ntw.AS_factory(name=AS)
                    link = self.cs.ntw.convert_link(link)
                    node = self.cs.ntw.convert_node(node)
                    interface = link('interface', node)
                    for idx, property in enumerate(ethernet_interface_perAS_properties):
                        value = self.objectizer(property, args[idx])
                        interface(AS.name, property, value)      
        
        self.cs.draw_all(False)        
        
    def export_graph(self, filepath=None):
        
        # to convert a list of object into a string of a list of strings
        # useful for AS nodes, edges, links as well as area nodes and links
        to_string = lambda s: str(list(map(str, s)))
        
        # filepath is set for unittest
        if not filepath:
            selected_file = filedialog.asksaveasfile(
                                    initialdir = self.path_workspace, 
                                    title = 'Export graph', 
                                    mode = 'w', 
                                    defaultextension = '.xls'
                                    )
                                    
            if not selected_file: 
                return 
            else:
                filename, file_format = os.path.splitext(selected_file.name)
                
        else:
            filename, file_format = os.path.splitext(filepath)
            selected_file = open(filepath, 'w')
            
        excel_workbook = xlwt.Workbook()
        for obj_subtype, properties in object_ie.items():
            # we have one excel sheet per subtype of object.
            # we filter the network pool based on the subtype to 
            # retrieve only the object of the corresponding subtype
            # this was done because objects have different properties
            # depending on the subtype, and we want to avoid using 
            # hasattr() all the time to check if a property exists.
            obj_type = subtype_to_type[obj_subtype]
            pool_obj = list(self.cs.ntw.ftr(obj_type, obj_subtype))
            # we create an excel sheet only if there's at least one object
            # of a given subtype
            if pool_obj:
                xls_sheet = excel_workbook.add_sheet(obj_subtype)
                for id, property in enumerate(properties):
                    xls_sheet.write(0, id, property)
                    for i, obj in enumerate(pool_obj, 1):
                        xls_sheet.write(i, id, str(getattr(obj, property)))
                    
        pool_AS = list(self.cs.ntw.pnAS.values())
        
        if pool_AS:
            AS_sheet = excel_workbook.add_sheet('AS')
            for i, AS in enumerate(self.cs.ntw.pnAS.values(), 1):
                AS_sheet.write(i, 0, str(AS.name))
                AS_sheet.write(i, 1, str(AS.AS_type))
                AS_sheet.write(i, 2, str(AS.id))
                AS_sheet.write(i, 3, to_string(AS.pAS['node']))
                AS_sheet.write(i, 4, to_string(AS.pAS['link']))
                
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
                if AS.AS_type != 'BGP':
                    for link in AS.links:
                        for interface in (link.interfaceS, link.interfaceD):
                            if_AS_sheet.write(cpt, 0, AS.name)
                            if_AS_sheet.write(cpt, 1, str(interface.link))
                            if_AS_sheet.write(cpt, 2, str(interface.node)) 
                            for idx, property in enumerate(ethernet_interface_perAS_properties, 3):
                                if_AS_sheet.write(cpt, idx, str(interface(AS.name, property)))
                            cpt += 1
            
        has_area = lambda a: a.has_area
        pool_area = list(filter(has_area, self.cs.ntw.pnAS.values()))
        
        if pool_area:
            area_sheet = excel_workbook.add_sheet('area')
        
            cpt = 1
            for AS in filter(lambda a: a.has_area, self.cs.ntw.pnAS.values()):
                for area in AS.areas.values():
                    area_sheet.write(cpt, 0, str(area.name))
                    area_sheet.write(cpt, 1, str(area.AS))
                    area_sheet.write(cpt, 2, str(area.id))
                    area_sheet.write(cpt, 3, to_string(area.pa['node']))
                    area_sheet.write(cpt, 4, to_string(area.pa['link']))
                    cpt += 1
                
        excel_workbook.save(selected_file.name)
        selected_file.close()
        