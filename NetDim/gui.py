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
import collections
import network
import scenario
from os.path import abspath, pardir, join
from tkinter import ttk, filedialog
from pythonic_tkinter.preconfigured_widgets import *
from objects import object_management_window as omw
from miscellaneous import graph_algorithms as galg
from drawing import drawing_options_window as dow
from graph_generation import advanced_graph as adv_gr
from optical_networks import rwa_window as rwaw
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
        
        ## Netdim objects
        
        self.nd_obj = {
        'router': 'node',
        'oxc': 'node',
        'host': 'node',
        'antenna': 'node',
        'regenerator': 'node',
        'splitter': 'node',
        'cloud': 'node',
        'switch': 'node',
        'ethernet': 'trunk',
        'wdm': 'trunk',
        'route': 'route',
        'traffic': 'traffic'
        }
        
        self.st_to_type = {
        'router': 'node',
        'oxc': 'node',
        'host': 'node',
        'antenna': 'node',
        'regenerator': 'node',
        'splitter': 'node',
        'switch': 'node',
        'cloud': 'node',
        'ethernet': 'trunk',
        'wdm': 'trunk',
        'l2vc': 'l2vc',
        'l3vc': 'l3vc',
        'static route': 'route',
        'BGP peering': 'route',
        'OSPF virtual link': 'route',
        'Label Switched Path': 'route',
        'routed traffic': 'traffic',
        'static traffic': 'traffic'
        }
        
        ## User-defined properties and labels per type of object
        
        # ordered dicts are needed to have the same menu order 
        node_common_properties = (
        'name', 
        'x', 
        'y', 
        'longitude', 
        'latitude', 
        'ipaddress', 
        'subnetmask', 
        'sites',
        'AS',
        )
        
        # we exclude the AS from node_common_properties. We don't need to 
        # import/export the AS of a node, because when the AS itself is imported, 
        # we rebuild #its logical topology, and that includes 
        # rebuilding the nodes AS dict
        node_common_ie_properties = node_common_properties[:-1]
        
        trunk_common_properties = (
        'name', 
        'source', 
        'destination', 
        'interface',
        'interfaceS',
        'interfaceD',
        'distance', 
        'costSD', 
        'costDS', 
        'capacitySD', 
        'capacityDS', 
        # if there is no failure simulation, the traffic property tells us how
        # much traffic is transiting on the trunk in a 'no failure' situation
        # if there is a link in failure, the traffic that is redirected will 
        # also contribute to this 'traffic parameter'.
        'trafficSD', 
        'trafficDS',
        # unlike the traffic property above, wctraffic is the worst case
        # traffic. It is the traffic that we use for dimensioning purposes, and
        # it considers the maximum traffic that the link must be able to 
        # handle, considering all possible failure cases.
        'wctrafficSD',
        'wctrafficDS',
        # the trunk which failure results in the worst case traffic
        'wcfailure',
        'flowSD', 
        'flowDS',
        'sites',
        'sntw',
        'AS',
        )
        
        interface_common_properties = (
        'link',
        'node',
        'name'
        )
        
        ethernet_interface_properties = interface_common_properties + (
        'ipaddress',
        'subnetmask',
        'macaddress'
        )
        
        route_common_properties = (
        'name',
        'subtype',
        'source', 
        'destination',
        'sites'
        )
        
        vc_common_properties = (
        'name',
        'source', 
        'destination',
        'linkS',
        'linkD',
        'sites'
        )
        
        traffic_common_properties = (
        'name', 
        'subtype',
        'source', 
        'destination', 
        'throughput',
        'sites'
        )
        
        trunk_common_ie_properties = (
        'name', 
        'source', 
        'destination', 
        'interface',
        'distance', 
        'costSD', 
        'costDS', 
        'capacitySD', 
        'capacityDS', 
        'sites'
        )
                
        route_common_ie_properties = (
        'name',
        'source', 
        'destination',
        'sites'
        )
        
        traffic_common_ie_properties = (
        'name', 
        'source', 
        'destination', 
        'throughput',
        'sites'
        )
        
        self.object_properties = collections.OrderedDict([
        ('router', node_common_properties + ('default_route', 'bgp_AS')),
        ('oxc', node_common_properties),
        ('host', node_common_properties),
        ('antenna', node_common_properties),
        ('regenerator', node_common_properties),
        ('splitter', node_common_properties),
        ('cloud', node_common_properties),
        ('switch', node_common_properties),
        
        ('ethernet', trunk_common_properties),
        ('wdm', trunk_common_properties + ('lambda_capacity',)),
        
        ('l2vc', vc_common_properties),
        ('l3vc', vc_common_properties),
        
        ('static route', route_common_properties + (
        'nh_ip',
        'dst_sntw',
        'ad'
        )),
        
        ('BGP peering', route_common_properties + (
        'bgp_type',
        'ipS',
        'ipD',
        'weightS',
        'weightD'
        )),
        
        ('OSPF virtual link', route_common_properties + (
        'nh_tk',
        'dst_sntw'
        )),
        
        ('Label Switched Path', route_common_properties + (
        'lsp_type',
        'path'
        )),
        
        ('routed traffic', traffic_common_properties),
        ('static traffic', traffic_common_properties),
        
        ])
        
        self.object_label = collections.OrderedDict([
        ('Node', 
        (
        'None', 
        'Name', 
        'Position', 
        'Coordinates', 
        'IPAddress',
        'Default_Route'
        )),
        
        ('Trunk', 
        (
        'None', 
        'Name', 
        'Type',
        'Distance', 
        'Traffic', 
        'WCTraffic',
        'Sntw'
        )),
        
        ('Interface', 
        (
        'None', 
        'Name', 
        'Cost',
        'Capacity',
        'Flow',
        'IPaddress',
        'Traffic', 
        'WCTraffic',
        )),
        
        ('L2vc',
        (
        'None', 
        'Name', 
        )),
        
        ('L3vc',
        (
        'None', 
        'Name', 
        )),
        
        ('Route', 
        (
        'None', 
        'Name', 
        'Distance', 
        'Type', 
        'Path', 
        'Cost', 
        'Subnet', 
        'Traffic'
        )),
        
        ('Traffic', 
        (
        'None', 
        'Name', 
        'Throughput'
        ))])
        
        # object import export (properties)
        self.object_ie = collections.OrderedDict([
        ('router', node_common_ie_properties + ('default_route', 'bgp_AS')),
        ('oxc', node_common_ie_properties),
        ('host', node_common_ie_properties),
        ('antenna', node_common_ie_properties),
        ('regenerator', node_common_ie_properties),
        ('splitter', node_common_ie_properties),
        ('cloud', node_common_ie_properties),
        ('switch', node_common_ie_properties),
        
        ('ethernet', trunk_common_ie_properties),
        ('wdm', trunk_common_ie_properties + ('lambda_capacity',)),
        
        ('static route', route_common_ie_properties + (
        'nh_ip',
        'dst_sntw',
        'ad'
        )),
        
        ('BGP peering', route_common_ie_properties + (
        'bgp_type',
        'ipS',
        'ipD',
        'weightS',
        'weightD'
        )),
        
        ('OSPF virtual link', route_common_ie_properties + (
        'nh_tk',
        'dst_ip'
        )),
        
        ('Label Switched Path', route_common_ie_properties + (
        'lsp_type',
        'path'
        )),
        
        ('routed traffic', traffic_common_ie_properties),
        ('static traffic', traffic_common_ie_properties),
        
        ('ethernet interface', ethernet_interface_properties),
        ('wdm interface', interface_common_properties)
        ])
        
        # ordered dicts are needed to have the same menu order 
        # box properties defines which properties are to be displayed in the
        # upper left corner of the canvas when hoverin over an object
        
        node_box_properties = (
        'name', 
        'subtype',
        'ipaddress', 
        'subnetmask'
        )
        
        trunk_box_properties = (
        'name', 
        'subtype',
        'interface',
        'interfaceS',
        'interfaceD',
        'source', 
        'destination',
        'sntw'
        )
        
        vc_box_properties = (
        'name', 
        'type',
        'source', 
        'destination',
        'linkS',
        'linkD'
        )
        
        self.box_properties = collections.OrderedDict([
        ('router', node_box_properties + ('default_route', 'bgp_AS')),
        ('oxc', node_box_properties),
        ('host', node_box_properties),
        ('antenna', node_box_properties),
        ('regenerator', node_box_properties),
        ('splitter', node_box_properties),
        ('cloud', node_box_properties),
        ('switch', node_box_properties),
        
        ('ethernet', trunk_box_properties),
        ('wdm', trunk_box_properties + ('lambda_capacity',)),
        
        ('l2vc', vc_box_properties),
        ('l3vc', vc_box_properties),
        
        ('static route', route_common_properties + (
        'nh_ip',
        'dst_sntw',
        'ad'
        )),
        
        ('BGP peering', route_common_properties + (
        'bgp_type',
        'ipS',
        'ipD',
        'weightS',
        'weightD'
        )),
        
        ('OSPF virtual link', route_common_properties + (
        'nh_tk',
        'dst_sntw'
        )),
        
        ('Label Switched Path', route_common_properties + (
        'lsp_type',
        )),                
        
        ('routed traffic', traffic_common_properties),
        ('static traffic', traffic_common_properties)
        ])
        
        # methods for string to object conversions
        self.convert_node = lambda n: self.cs.ntw.nf(name=n)
        self.convert_link = lambda l: self.cs.ntw.lf(name=l)
        convert_AS = lambda AS: self.cs.ntw.AS_factory(name=AS)
        self.convert_nodes_set = lambda ln: set(map(self.convert_node, eval(ln)))
        convert_nodes_list = lambda ln: list(map(self.convert_node, eval(ln)))
        self.convert_links_set = lambda ll: set(map(self.convert_link, eval(ll)))
        convert_links_list = lambda ll: list(map(self.convert_link, eval(ll)))
        
        # dict property to conversion methods: used at import
        # the code for AS export
        self.prop_to_type = {
        'name': str, 
        'protocol': str,
        'interface': str,
        'ipaddress': str,
        'subnetmask': str,
        'LB_paths': int,
        'default_route': str,
        'x': float, 
        'y': float, 
        'longitude': float, 
        'latitude': float,
        'distance': float, 
        'costSD': float, 
        'costDS': float, 
        'cost': float,
        'capacitySD': int, 
        'capacityDS': int,
        'traffic': float,
        'trafficSD': float,
        'trafficDS': float,
        'wctrafficSD': float,
        'wctrafficDS': float,
        'wcfailure': str,
        'flowSD': float,
        'flowDS': float,
        'interfaceS': str,
        'interfaceD': str,
        'ipaddress': str,
        'subnetmask': str,
        'macaddress': str,
        'sntw': str,
        'throughput': float,
        'lambda_capacity': int,
        'source': self.convert_node, 
        'destination': self.convert_node, 
        'node': self.convert_node, 
        'link': self.convert_link, 
        'nh_tk': str,
        'nh_ip': str,
        'ipS': str,
        'ipD': str,
        'bgp_AS': str,
        'weightS': int,
        'weightD': int,
        'dst_sntw': str,
        'ad': int,
        'subtype': str,
        'bgp_type': str,
        'lsp_type': str,
        'path_constraints': convert_nodes_list, 
        'excluded_nodes': self.convert_nodes_set,
        'excluded_trunks': self.convert_links_set, 
        'path': convert_links_list, 
        'subnets': str, 
        'sites': str,
        'AS': convert_AS
        }
        
        self.prop_to_nice_name = {
        'name': 'Name',
        'type': 'Type',
        'protocol': 'Protocol',
        'interface': 'Interface',
        'ipaddress': 'IP address',
        'subnetmask': 'Subnet mask',
        'LB_paths': 'Maximum paths (LB)',
        'default_route': 'Default Route',
        'x': 'X coordinate', 
        'y': 'Y coordinate', 
        'longitude': 'Longitude', 
        'latitude': 'Latitude',
        'distance': 'Distance',
        'node': 'Node',
        'link': 'Link',
        'linkS': 'Source link',
        'linkD': 'Destination link', 
        'costSD': 'Cost S -> D', 
        'costDS': 'Cost D -> S', 
        'cost': 'Cost',
        'capacitySD': 'Capacity S -> D', 
        'capacityDS': 'Capacity D -> S', 
        'traffic': 'Traffic',
        'trafficSD': 'Traffic S -> D', 
        'trafficDS': 'Traffic D -> S', 
        'wctrafficSD': 'Worst case traffic S -> D', 
        'wctrafficDS': 'Worst case traffic D -> S', 
        'wcfailure': 'Worst case failure',
        'flowSD': 'Flow S -> D', 
        'flowDS': 'Flow D -> S', 
        'ipaddressS': 'IP address (source)',
        'subnetmaskS': 'Subnet mask (source)',
        'ipaddressD': 'IP address (destination)',
        'subnetmaskD': 'Subnet mask (destination)',
        'interfaceS': 'Interface (source)',
        'interfaceD': 'Interface (destination)',
        'macaddressS': 'MAC address (source)',
        'macaddressD': 'MAC address (destination)',
        'macaddress': 'MAC address',
        'weightS': 'Weight (source)',
        'weightD': 'Weight (destination)',
        'sntw': 'Subnetwork',
        'throughput': 'Throughput',
        'lambda_capacity': 'Lambda capacity',
        'source': 'Source',
        'destination': 'Destination',
        'nh_tk': 'Next-hop trunk',
        'nh_ip': 'Next-hop IP',
        'ipS': 'Source IP',
        'ipD': 'Destination IP',
        'bgp_AS': 'BGP AS',
        'dst_sntw': 'Destination subnetwork',
        'ad': 'Administrative distance',
        'router_id': 'Router ID',
        'subtype': 'Type',
        'bgp_type': 'BGP Type',
        'lsp_type': 'LSP Type',
        'path_constraints': 'Path constraints',
        'excluded_nodes': 'Excluded nodes',
        'excluded_trunks': 'Excluded trunks',
        'path': 'Path',
        'subnets': 'Subnets', 
        'sites': 'Sites',
        'AS': 'Autonomous system'
        }
        
        self.name_to_prop = {v: k for k, v in self.prop_to_nice_name.items()}
        
        colors = ['default', 'red', 'purple']
        
        ## ----- Menus : -----
        menubar = tk.Menu(self)
        upper_menu = tk.Menu(menubar, tearoff=0)
        upper_menu.add_command(label='Add scenario', 
                                        command=lambda: self.add_scenario())
        upper_menu.add_command(label='Delete scenario', 
                                        command=lambda: self.delete_scenario())
        upper_menu.add_command(label='Duplicate scenario', 
                                    command=lambda: self.duplicate_scenario())
        upper_menu.add_separator()
        upper_menu.add_command(label='Import graph', 
                                        command=lambda: self.import_graph())
        upper_menu.add_command(label='Export graph', 
                                        command=lambda: self.export_graph())
        upper_menu.add_separator()
        upper_menu.add_command(label='Exit', command=self.destroy)
        menubar.add_cascade(label='Main',menu=upper_menu)
        menu_drawing = tk.Menu(menubar, tearoff=0)
        menu_drawing.add_command(label='Default drawing parameters', 
                        command=lambda: dow.DrawingOptions(self))
        menubar.add_cascade(label='Network drawing',menu=menu_drawing)
        menu_routing = tk.Menu(menubar, tearoff=0)
        menu_routing.add_command(label='Advanced graph', 
                        command=lambda: self.advanced_graph.deiconify())
        menu_routing.add_command(label='Advanced algorithms', 
                        command=lambda: self.advanced_graph_options.deiconify())
        menu_routing.add_command(label='Network Tree View', 
                                        command=lambda: NetworkTreeView(self))
        menu_routing.add_command(label='Wavelength assignment', 
                                    command=lambda: self.rwa_window.deiconify())
                                                             
        menubar.add_cascade(label='Network routing',menu=menu_routing)

        # choose which label to display per type of object
        menu_options = tk.Menu(menubar, tearoff=0)
        for obj_type, label_type in self.object_label.items():
            menu_type = tk.Menu(menubar, tearoff=0)
            menu_options.add_cascade(label=obj_type + ' label', menu=menu_type)
            for lbl in label_type:
                cmd = lambda o=obj_type, l=lbl: self.cs.refresh_labels(o, l)
                menu_type.add_command(label=lbl, command=cmd)
            
        menu_options.add_command(label='Change display', 
                                    command=lambda: self.cs.change_display())
        
        # show / hide option per type of objects
        menu_display = tk.Menu(menubar, tearoff=0)
        for index, type in enumerate(self.object_properties):
            new_label = ' '.join(('Hide', type))
            cmd = lambda t=type, i=index: self.cs.show_hide(menu_display, t, i)
            menu_display.add_command(label=new_label, command=cmd)
        menu_options.add_cascade(label='Show/hide object', menu=menu_display)
            
        menubar.add_cascade(label='Options',menu=menu_options)
        
        self.config(menu=menubar)

        # scenario notebook
        self.scenario_notebook = ttk.Notebook(self)
        self.scenario_notebook.bind('<ButtonRelease-1>', self.change_cs)
        self.dict_scenario = {}
        
        # cs for 'current scenario' (the first one, which we create)        
        self.cs = scenario.Scenario(self, 'scenario 0')
        self.cpt_scenario = 0
        self.scenario_notebook.add(self.cs, text=self.cs.name, compound=tk.TOP)
        self.dict_scenario['scenario 0'] = self.cs
        
        # object management windows
        self.dict_obj_mgmt_window = {}
        for obj in self.object_properties:
            self.dict_obj_mgmt_window[obj] = omw.ObjectManagementWindow(self, obj)
        
        # drawing algorithm and parameters: per project
        self.drawing_algorithm = 'Spring layout'

        self.drawing_params = {
        'Spring layout': collections.OrderedDict([
        ('Coulomb factor', 10000),
        ('Spring stiffness', 0.5),
        ('Speed factor', 0.35),
        ('Equilibrium length', 8.)
        ]),
        'F-R layout': collections.OrderedDict([
        ('OPD', 0.),
        ('limit', True)
        ])}
        
        # advanced graph options
        self.advanced_graph_options = galg.GraphAlgorithmWindow(self)
        
        # routing and wavelength assignment window
        self.rwa_window = rwaw.RWAWindow(self)
        
        # graph generation window
        self.advanced_graph = adv_gr.AdvancedGraph(self)
        
        # create a menu
        self.main_menu = main_menu.MainMenu(self)
        self.main_menu.pack(fill=tk.BOTH, side=tk.LEFT)
        self.scenario_notebook.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        
        # dict of nodes image for node creation
        self.dict_image = collections.defaultdict(dict)
        
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
            value = self.prop_to_type[property](value)
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
            for id, obj_type in enumerate(self.object_ie):
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
                    link = self.convert_link(link)
                    node = self.convert_node(node)
                    interface = link('interface', node)
                    for property, value in zip(if_properties[2:], args):
                        setattr(interface, property, value)
                                                        
            AS_sheet, area_sheet = book.sheets()[18], book.sheets()[19]
        
            # creation of the AS
            for row_index in range(1, AS_sheet.nrows):
                name, type, id, nodes, trunks = AS_sheet.row_values(row_index)
                id = int(id)
                nodes = self.convert_nodes_set(nodes)
                trunks = self.convert_links_set(trunks)
                self.cs.ntw.AS_factory(type, name, id, trunks, nodes, True)
            
            # creation of the area
            for row_index in range(1, area_sheet.nrows):
                name, AS, id, nodes, trunks = area_sheet.row_values(row_index)
                AS = self.cs.ntw.AS_factory(name=AS)
                nodes = self.convert_nodes_set(nodes)
                trunks = self.convert_links_set(trunks)
                new_area = AS.area_factory(name, int(id), trunks, nodes)
                
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
        # useful for AS nodes, edges, trunks as well as area nodes and trunks
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
        for obj_type, properties in self.object_ie.items():
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
                    type = self.st_to_type[obj_type]
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
            AS_sheet.write(i, 4, to_string(AS.pAS['trunk']))
            
        area_sheet = excel_workbook.add_sheet('area')
        cpt = 1
        for AS in self.cs.ntw.pnAS.values():
            for area in AS.areas.values():
                area_sheet.write(cpt, 0, str(area.name))
                area_sheet.write(cpt, 1, str(area.AS))
                area_sheet.write(cpt, 2, str(area.id))
                area_sheet.write(cpt, 3, to_string(area.pa['node']))
                area_sheet.write(cpt, 4, to_string(area.pa['trunk']))
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