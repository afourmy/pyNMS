import os
import warnings
from views.network_view import NetworkView
from views.site_view import SiteView
from objects.objects import *
from pythonic_tkinter.preconfigured_widgets import *
from tkinter import filedialog
try:
    import xlrd
    import xlwt
except ImportError:
    warnings.warn('Excel libraries missing: excel import/export disabled')

class Project():
    
    def __init__(self, controller, name):
        self.name = name
        self.controller = controller
        self.controller.current_project = self
        
        # global frame that contains network, site, and node views
        self.gf = CustomFrame(width=1300, height=800)        
        
        self.network_view = NetworkView(
                                        '{} : network view'.format(name),
                                        controller
                                        )
        self.site_view = SiteView(
                                '{} : site view'.format(name),
                                controller, 
                                )
        self.current_view = self.network_view
        self.network = self.current_view.network
        self.network_view.pack()
        
    def objectizer(self, property, value):
        if value == 'None': 
            return None
        elif property in self.network.prop_to_type:
            return self.network.prop_to_type[property](value)
        # if the property doesn't exist, we consider it is a string
        else:
            self.network.prop_to_type[property] = str
            return value
                        
    def mass_objectizer(self, properties, values):
        kwargs = {}
        for property, value in zip(properties, values):
            kwargs[property] = self.objectizer(property, value)
        return kwargs
        
    def refresh(self):
        
        commands = (
                    self.current_view.network.update_AS_topology,
                    self.current_view.network.vc_creation,
                    self.current_view.network.interface_configuration,
                    self.current_view.network.switching_table_creation,
                    self.current_view.network.routing_table_creation,
                    self.current_view.network.bgp_table_creation,
                    self.current_view.network.redistribution,
                    self.current_view.network.path_finder,
                    lambda: self.current_view.draw_all(False),
                    self.current_view.refresh_display
                    )
        
        for idx, boolean in enumerate(self.controller.routing_menu.action_booleans):
            if boolean.get():
                commands[idx]()
        
    def import_project(self, filepath=None):
                
        # filepath is set for unittest
        if not filepath:
            filepath = filedialog.askopenfilenames(
                            initialdir = self.controller.path_workspace, 
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
                            self.site_view.network.nf(node_type=name, **kwargs)
                        else:
                            self.network_view.network.nf(node_type=name, **kwargs)
                    if name in link_subtype: 
                        self.network_view.network.lf(subtype=name, **kwargs)
                
            # interface import
            elif name in ('ethernet interface', 'wdm interface'):
                if_properties = sheet.row_values(0)
                # creation of ethernet interfaces
                for row_index in range(1, sheet.nrows):
                    link, node, *args = sheet.row_values(row_index)
                    link = self.network_view.network.convert_link(link)
                    node = self.network_view.network.convert_node(node)
                    interface = link('interface', node)
                    for property, value in zip(if_properties[2:], args):
                        # we convert all (valid) string IPs to an OIPs
                        if property == 'ipaddress' and value != 'none':
                            value = self.network_view.network.OIPf(value, interface)
                        setattr(interface, property, value)
                        
            # AS import
            elif name == 'AS':
                for row_index in range(1, sheet.nrows):
                    name, AS_type, id, nodes, links = sheet.row_values(row_index)
                    id = int(id)
                    subtype = 'ethernet link' if AS_type != 'BGP' else 'BGP peering'
                    nodes = self.network_view.network.convert_node_set(nodes)
                    links = self.network_view.network.convert_link_set(links, subtype)
                    self.network_view.network.AS_factory(AS_type, name, id, links, nodes, True)
                
            # area import
            elif name == 'area':
                for row_index in range(1, sheet.nrows):
                    name, AS, id, nodes, links = sheet.row_values(row_index)
                    AS = self.network_view.network.AS_factory(name=AS)
                    nodes = self.network_view.network.convert_node_set(nodes)
                    links = self.network_view.network.convert_link_set(links)
                    new_area = AS.area_factory(name, int(id), links, nodes)
                    
            # per-AS node properties import
            elif name == 'per-AS node properties':
                for row_index in range(1, sheet.nrows):
                    AS, node, *args = sheet.row_values(row_index)
                    node = self.network_view.network.convert_node(node)
                    for idx, property in enumerate(perAS_properties[node.subtype]):
                        value = self.objectizer(property, args[idx])
                        node(AS, property, value)
                 
            # import of site objects
            elif name == 'sites':
                for row_index in range(1, sheet.nrows):
                    name, nodes, links = sheet.row_values(row_index)
                    site = self.site_view.network.convert_node(name)
                    links = set(self.network_view.network.convert_link_list(links))
                    nodes = set(self.network_view.network.convert_node_list(nodes))
                    site.add_to_site(*nodes)
                    site.add_to_site(*links)
                        
            # per-AS interface properties import
            else:
                for row_index in range(1, sheet.nrows):
                    AS, link, node, *args = sheet.row_values(row_index)
                    AS = self.network_view.network.AS_factory(name=AS)
                    link = self.network_view.network.convert_link(link)
                    node = self.network_view.network.convert_node(node)
                    interface = link('interface', node)
                    for idx, property in enumerate(ethernet_interface_perAS_properties):
                        value = self.objectizer(property, args[idx])
                        interface(AS.name, property, value)   
                        
        self.current_view.draw_all(False)
        self.site_view.draw_all(False)
        
    def export_project(self, filepath=None):
        
        # to convert a list of object into a string of a list of strings
        # useful for AS nodes, edges, links as well as area nodes and links
        to_string = lambda s: str(list(map(str, s)))
        
        # filepath is set for unittest
        if not filepath:
            selected_file = filedialog.asksaveasfile(
                                    initialdir = self.controller.path_workspace, 
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
                pool_obj = list(self.site_view.network.nodes.values())
            else:
                pool_obj = list(self.network_view.network.ftr(obj_type, obj_subtype))
            # we create an excel sheet only if there's at least one object
            # of a given subtype
            if pool_obj:
                xls_sheet = excel_workbook.add_sheet(obj_subtype)
                for id, property in enumerate(properties):
                    xls_sheet.write(0, id, property)
                    for i, obj in enumerate(pool_obj, 1):
                        xls_sheet.write(i, id, str(getattr(obj, property)))
                    
        pool_AS = list(self.network_view.network.pnAS.values())
        
        if pool_AS:
            AS_sheet = excel_workbook.add_sheet('AS')
            for i, AS in enumerate(self.network_view.network.pnAS.values(), 1):
                AS_sheet.write(i, 0, str(AS.name))
                AS_sheet.write(i, 1, str(AS.AS_type))
                AS_sheet.write(i, 2, str(AS.id))
                AS_sheet.write(i, 3, to_string(AS.pAS['node']))
                AS_sheet.write(i, 4, to_string(AS.pAS['link']))
                
            node_AS_sheet = excel_workbook.add_sheet('per-AS node properties')
                
            cpt = 1
            for AS in self.network_view.network.pnAS.values():
                for node in AS.nodes:
                    node_AS_sheet.write(cpt, 0, AS.name)
                    node_AS_sheet.write(cpt, 1, node.name)
                    for idx, property in enumerate(perAS_properties[node.subtype], 2):
                        node_AS_sheet.write(cpt, idx, str(node(AS.name, property)))
                    cpt += 1
                    
            if_AS_sheet = excel_workbook.add_sheet('per-AS interface properties')
            
            cpt = 1
            for AS in self.network_view.network.pnAS.values():
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
        pool_area = list(filter(has_area, self.network_view.network.pnAS.values()))
        
        if pool_area:
            area_sheet = excel_workbook.add_sheet('area')
        
            cpt = 1
            for AS in filter(lambda a: a.has_area, self.network_view.network.pnAS.values()):
                for area in AS.areas.values():
                    area_sheet.write(cpt, 0, str(area.name))
                    area_sheet.write(cpt, 1, str(area.AS))
                    area_sheet.write(cpt, 2, str(area.id))
                    area_sheet.write(cpt, 3, to_string(area.pa['node']))
                    area_sheet.write(cpt, 4, to_string(area.pa['link']))
                    cpt += 1
             
        if self.site_view.network.nodes:
            site_sheet = excel_workbook.add_sheet('sites')
            for cpt, site in enumerate(self.site_view.network.nodes.values()):
                site_sheet.write(cpt, 0, str(site.name))
                site_sheet.write(cpt, 1, to_string(site.ps['node']))
                site_sheet.write(cpt, 2, to_string(site.ps['link']))
                
        excel_workbook.save(selected_file.name)
        selected_file.close()
        
    def import_site(self):
    
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
            site = self.site_view.network.convert_node(site_name)
            node = self.network_view.network.convert_node(node)
            site.add_to_site(node)
                    