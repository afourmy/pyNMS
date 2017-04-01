# NetDim
# Copyright (C) 2017 Antoine Fourmy (contact@netdim.fr)

import tkinter as tk
import warnings
import os
from scenarios import network_scenario, site_scenario
from collections import defaultdict
from os.path import abspath, pardir, join
from tkinter import ttk, filedialog
from objects.objects import *
from pythonic_tkinter.preconfigured_widgets import *
from miscellaneous import graph_algorithms as galg
from miscellaneous import network_tree_view as ntv
from miscellaneous import debug
from ip_networks import ssh_management
from graph_generation import advanced_graph as adv_gr
from optical_networks import rwa_window as rwaw
from automation import script_creation
from menus import (
                   creation_menu, 
                   routing_menu,
                   display_menu, 
                   drawing_menu, 
                   view_menu
                   )
from PIL import ImageTk
try:
    import xlrd
    import xlwt
except ImportError:
    warnings.warn('Excel libraries missing: excel import/export disabled')
try:
    import shapefile as shp
    import shapely.geometry as sgeo
except ImportError:
    warnings.warn('SHP librairies missing: map import disabled')

class Controller(MainWindow):
    
    def __init__(self, path_app):
        super().__init__()
        self.path_app = path_app
        path_parent = abspath(join(path_app, pardir))
        self.path_icon = join(path_parent, 'Icons')
        self.path_workspace = join(path_parent, 'Workspace')
            
        ## ----- Main app : -----
        self.title('NetDim')
        netdim_icon = tk.PhotoImage(file=join(self.path_icon, 'netdim_icon.gif'))
        self.tk.call('wm', 'iconphoto', self._w, netdim_icon)
        
        colors = ['default', 'red', 'purple']
        
        # dict of script (script name -> Script object)
        self.scripts = {}
        
        # scenario notebook
        self.scenario_notebook = Notebook(self)
        self.scenario_notebook.bind('<ButtonRelease-1>', self.change_cs)
        
        # global frame that contains network, site, and node scenarios
        self.gf = CustomFrame(width=1300, height=800)
        self.dict_scenario = {}
        self.scenario_notebook.add(self.gf, text='main', compound='top')
        
        # ns for 'network scenario' (contains all network devices on a map)
        # ss for 'site scenario' (contains all sites on a map)
        self.ns = network_scenario.NetworkScenario(self, 'scenario 0: network')
        self.ss = site_scenario.SiteScenario(self, 'scenario 0: site')
        # self.cpt_scenario = 0
        # self.dict_scenario['scenario 0'] = self.ns
        self.ns.pack()
        
        # cs for current scenario, the scenario being displayed
        self.cs = self.ns
        
        # advanced graph options
        self.advanced_graph_options = galg.GraphAlgorithmWindow(self)
        
        # routing and wavelength assignment window
        self.rwa_window = rwaw.RWAWindow(self)
        
        # graph generation window
        self.advanced_graph = adv_gr.AdvancedGraph(self)
        
        # debug window
        self.debug_window = debug.Debug(self)
        
        # SSH management window
        self.ssh_management_window = ssh_management.SSHWindow(self)
        
        # Script creation window
        self.script_creation_window = script_creation.ScriptCreation(self)
        
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
        
        site_import = MenuEntry(general_menu)
        site_import.text = 'Site import'
        site_import.command = self.site_import
        
        export_graph = MenuEntry(general_menu)
        export_graph.text = 'Export graph'
        export_graph.command = self.export_graph

        general_menu.separator()
        
        import_map = MenuEntry(general_menu)
        import_map.text = 'Import SHP map'
        import_map.command = self.import_map
        
        delete_map = MenuEntry(general_menu)
        delete_map.text = 'Delete SHP map'
        delete_map.command = self.delete_map
        
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
        
        ssh_management_entry = MenuEntry(advanced_menu)
        ssh_management_entry.text = 'SSH connection management'
        ssh_management_entry.command = self.ssh_management_window.deiconify
        
        script_creation_entry = MenuEntry(advanced_menu)
        script_creation_entry.text = 'Script creation'
        script_creation_entry.command = self.script_creation_window.deiconify
        
        advanced_menu.create_menu()
        netdim_menu.add_cascade(label='Network routing',menu=advanced_menu)

        # choose which label to display per type or subtype of object:
        # - a first menu contains all types of objects, each type unfolding
        # a sub-menu that contains all i/e properties common to a type
        # - a second menu contains all types of objects, each type unfolding
        # a sub-menu that contains all i/e properties common to a subtypes
        
        per_type_label_menu = Menu(netdim_menu)
        for obj_type, labels in type_labels.items():
            menu_type = Menu(netdim_menu)
            entry_name = '{type} label'.format(type=obj_type)
            per_type_label_menu.add_cascade(label=entry_name, menu=menu_type)
            for label in labels:
                cmd = lambda o=obj_type, l=label: self.cs.refresh_labels(o, l)
                type_entry = MenuEntry(menu_type)
                type_entry.text = prop_to_nice_name[label]
                type_entry.command = cmd
            menu_type.create_menu()
                    
        netdim_menu.add_cascade(
                                label = 'Per-type labels', 
                                menu = per_type_label_menu
                                )
        
        per_subtype_label_menu = Menu(netdim_menu)
        for obj_type, labels in object_ie.items():
            menu_type = Menu(netdim_menu)
            entry_name = '{subtype} label'.format(subtype=obj_type)
            per_subtype_label_menu.add_cascade(label=entry_name, menu=menu_type)
            for label in ('None',) + labels:
                cmd = lambda o=obj_type, l=label: self.cs.refresh_subtype_labels(o, l)
                type_entry = MenuEntry(menu_type)
                text = 'None' if label == 'None' else prop_to_nice_name[label]
                type_entry.text =  text
                type_entry.command = cmd
            menu_type.create_menu()
                    
        netdim_menu.add_cascade(
                                label = 'Per-subtype labels', 
                                menu = per_subtype_label_menu
                                )
        
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
        'firewall': (40, 40),
        'load_balancer': (60, 40),
        'server': (52, 52),
        'site': (50, 50)
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
        
        self.menu_notebook = Notebook(self)
        
        # main menu for creation and selection of objects
        self.creation_menu = creation_menu.CreationMenu(self.menu_notebook, self)
        self.creation_menu.pack(fill='both', side='left')
    
        # routing menu (addresss allocation + tables creation + routing)
        self.routing_menu = routing_menu.RoutingMenu(self.menu_notebook, self)
        self.routing_menu.pack(fill='both', side='left')
        
        # drawing menu (force-based algorithm parameters + paint-like drawing)
        self.drawing_menu = drawing_menu.DrawingMenu(self.menu_notebook, self)
        self.drawing_menu.pack(fill='both', side='left')
        
        # display menu to control the display
        self.display_menu = display_menu.DisplayMenu(self.menu_notebook, self)
        self.display_menu.pack(fill='both', side='left')
        
        # display menu to control the display
        self.view_menu = view_menu.ViewMenu(self.menu_notebook, self)
        self.view_menu.pack(fill='both', side='left')
        
        self.menu_notebook.add(self.creation_menu, text=' Creation ')
        self.menu_notebook.add(self.routing_menu, text=' Routing ')
        self.menu_notebook.add(self.drawing_menu, text=' Drawing ')
        self.menu_notebook.add(self.display_menu, text=' Display ')
        self.menu_notebook.add(self.view_menu, text=' View ')
        
        self.menu_notebook.pack(side='left', fill='both')
        
        # notebooks of scenarios
        self.scenario_notebook.pack(side='left', fill='both', expand=1)
        
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
        self.scenario_notebook.add(new_scenario, text=name, compound='top')
        self.dict_scenario[name] = new_scenario
        return new_scenario
        
    def delete_scenario(self):
        del self.dict_scenario[self.cs.name]
        self.scenario_notebook.forget(self.cs)
        self.change_cs()
        
    def objectizer(self, property, value):
        if value == 'None': 
            return None
        elif property in self.cs.ntw.prop_to_type:
            return self.cs.ntw.prop_to_type[property](value)
        # if the property doesn't exist, we consider it is a string
        else:
            self.cs.ntw.prop_to_type[property] = str
            return value
                        
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
                                    'site',
                                    'ethernet link',
                                    'ethernet interface',
                                    'optical link', 
                                    'optical interface',
                                    'etherchannel',
                                    'optical channel',
                                    'BGP peering',
                                    'pseudowire',
                                    'routed traffic',
                                    'static traffic',
                                    'AS',
                                    'area',
                                    'per-AS node properties',
                                    'per-AS interface properties',
                                    'sites'
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
                        if name == 'site':
                            self.ss.ntw.nf(node_type=name, **kwargs)
                        else:
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
                 
            # import of site objects
            elif name == 'sites':
                for row_index in range(1, sheet.nrows):
                    name, nodes, links = sheet.row_values(row_index)
                    site = self.ss.ntw.convert_node(name)
                    links = set(self.cs.ntw.convert_link_list(links))
                    nodes = set(self.cs.ntw.convert_node_list(nodes))
                    site.add_to_site(*nodes)
                    site.add_to_site(*links)
                        
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
        self.ss.draw_all(False)
        
    def site_import(self):
    
        # filepath is set for unittest
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
        
        try:
            sheet = book.sheet_by_name('site')
        # if the sheet cannot be found, there's nothing to import
        except xlrd.biffh.XLRDError:
            print('the excel sheet must be called site')
            
        for row_index in range(sheet.nrows):
            site_name, node = sheet.row_values(row_index)
            site = self.ss.ntw.convert_node(site_name)
            node = self.cs.ntw.convert_node(node)
            site.add_to_site(node)
        
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
            if obj_subtype == 'site':
                pool_obj = list(self.ss.ntw.nodes.values())
            else:
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
             
        if self.ss.ntw.nodes:
            site_sheet = excel_workbook.add_sheet('sites')
            for cpt, site in enumerate(self.ss.ntw.nodes.values()):
                site_sheet.write(cpt, 0, str(site.name))
                site_sheet.write(cpt, 1, to_string(site.ps['node']))
                site_sheet.write(cpt, 2, to_string(site.ps['link']))
                
        excel_workbook.save(selected_file.name)
        selected_file.close()
        
    def import_map(self, filepath=None):
                
        filepath = filedialog.askopenfilenames(
                                initialdir = join(self.path_workspace, 'map'),
                                title = 'Import SHP map', 
                                filetypes = (
                                ('shp files','*.shp'),
                                ('all files','*.*')
                                ))
        
        # no error when closing the window
        if not filepath: 
            return
        else: 
            filepath ,= filepath
        
        # shapefile with all countries
        sf = shp.Reader(filepath)
        
        shapes = sf.shapes()
        
        for shape in shapes:
            shape = sgeo.shape(shape)
            wkt_shape = [('.Mainland', str(shape), 'D',  None, None, None, 'green')]
            self.cs.world_map.load_shp_file(wkt_shape)
            
        for idx in self.cs.world_map.map_ids:
            self.cs.cvs.tag_lower(idx)
            
    def delete_map(self):
        
        for idx in self.cs.world_map.map_ids:
            self.cs.cvs.delete(idx)
            