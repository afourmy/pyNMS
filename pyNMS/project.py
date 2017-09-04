# Copyright (C) 2017 Antoine Fourmy <antoine dot fourmy at gmail dot com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import warnings
from views.main_network_view import MainNetworkView
from views.site_view import SiteView
from objects.objects import *
from objects.properties import property_classes
try:
    import xlrd
    import xlwt
    from yaml import dump, load
except ImportError:
    warnings.warn('Excel/YAML libraries missing')
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QFileDialog


class Project(QWidget):
    
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
    import_order = (
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
    
    def __init__(self, controller, name):
        super().__init__(controller)

        self.network_view = MainNetworkView(controller)
        self.site_view = SiteView(controller)
        
        self.hlayout = QHBoxLayout(self)
        self.hlayout.addWidget(self.network_view) 
        self.hlayout.addWidget(self.site_view) 
        self.site_view.hide()

        self.name = name
        self.controller = controller
        self.controller.current_project = self
        self.current_view = self.network_view
        self.network = self.current_view.network
        self.view_type = 'network'
        
    def show_network_view(self):
        self.current_view.hide()
        self.network_view.show()
        self.current_view = self.network_view
        self.view_type = 'network'
        self.controller.change_menu('network')
        
    def show_site_view(self):
        self.current_view.hide()
        self.site_view.show()
        self.current_view = self.site_view
        self.view_type = 'site'
        self.controller.change_menu('site')
        
    def show_internal_site_view(self, site):
        self.current_view.hide()
        site.site_view.show()
        self.current_view = site.site_view
        self.view_type = 'insite'
        self.controller.change_menu('network')
        
    def show_internal_node_view(self, gnode):
        self.current_view.hide()
        gnode.internal_view.show()
        self.current_view = gnode.internal_view
        self.view_type = 'innode'
        self.controller.change_menu('innode')
        
    def show_parent_view(self):
        if self.current_view.subtype == 'insite':
            self.show_site_view()
        elif self.current_view.subtype == 'innode':
            self.current_view.hide()
            self.current_view = self.current_view.parent_view
            self.current_view.show()
            self.view_type = self.current_view.subtype
            self.controller.change_menu(self.view_type)
        
    def refresh(self):
        
        commands = (
                    self.current_view.network.update_AS_topology,
                    self.current_view.network.vc_creation,
                    self.current_view.network.interface_configuration,
                    self.current_view.network.switching_table_creation,
                    self.current_view.network.routing_table_creation,
                    self.current_view.network.path_finder,
                    self.current_view.refresh_display
                    )
        
        for idx, boolean in enumerate(self.controller.routing_panel.checkboxes):
            if boolean.isChecked():
                commands[idx]()
                
    def yaml_import(self, filepath=None):
        if not filepath:
            filepath = QFileDialog.getOpenFileName(
                                            self, 
                                            'Import project', 
                                            'Choose a project to import'
                                            )[0]
                                
        with open(filepath, 'r') as file:
            yaml_project = load(file)
            
            for subtype in self.import_order:
                if subtype not in yaml_project:
                    continue
                for obj, properties in yaml_project[subtype].items():
                    kwargs = {}
                    for property_name, value in properties.items():
                        value = self.network.objectizer(property_name, value)
                        kwargs[property_name] = value
                    if subtype in node_subtype:
                        if subtype == 'site':
                            self.site_view.network.nf(subtype=subtype, **kwargs)
                        else:

                            self.network_view.network.nf(subtype=subtype, **kwargs)
                    if subtype in link_subtype: 
                        self.network_view.network.lf(subtype=subtype, **kwargs)
                        
        self.network_view.refresh_display()
        self.network_view.move_to_geographical_coordinates()
        
    def yaml_export(self, filepath=None):
                
        # filepath is set for unittest
        if not filepath:
            filepath = QFileDialog.getSaveFileName(
                                                   self, 
                                                   "Export project",
                                                   self.name, 
                                                   ".yaml"
                                                   )
            filepath = ''.join(filepath)
        else:
            selected_file = open(filepath, 'w')
        
        with open(filepath, 'w') as file:                                                            
            project_objects = {
            subtype: {
                      str(obj.name):  {
                                       property.name: str(getattr(obj, property.name))
                                       for property in properties
                                       }
                      for obj in self.network_view.network.ftr(
                                                subtype_to_type[subtype], 
                                                subtype
                                                )
                      }
            for subtype, properties in object_ie.items()
            }

            dump(project_objects, file, default_flow_style=False)
    
    def excel_import(self, filepath=None):
        if not filepath:
            # filepath is set for unittest
            filepath = QFileDialog.getOpenFileName(
                                            self, 
                                            'Import project', 
                                            'Choose a project to import'
                                            )[0]

        book = xlrd.open_workbook(filepath)
                                        
        for name in self.import_order:
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
                    kwargs = self.network.mass_objectizer(properties, values)
                    if name in node_subtype:
                        if name == 'site':
                            self.site_view.network.nf(subtype=name, **kwargs)
                        else:
                            self.network_view.network.nf(subtype=name, **kwargs)
                    if name in link_subtype: 
                        self.network_view.network.lf(subtype=name, **kwargs)
                
            # interface import
            elif name in ('ethernet interface', 'optical interface'):
                if_properties = sheet.row_values(0)
                # creation of ethernet interfaces
                for row_index in range(1, sheet.nrows):
                    name, link, node, *args = sheet.row_values(row_index)
                    link = self.network_view.network.convert_link(link)
                    node = self.network_view.network.convert_node(node)
                    interface = link('interface', node)
                    for property, value in zip(if_properties[2:], args):
                        # we convert all (valid) string IPs to an OIPs
                        if property == 'ip_address' and value != 'none':
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
                        value = self.network.objectizer(property, args[idx])
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
                        value = self.network.objectizer(property, args[idx])
                        interface(AS.name, property, value)   
                        
        self.network_view.refresh_display()
        self.network_view.move_to_geographical_coordinates()
        
    def excel_export(self, selected_file=None):
        
        # to convert a list of object into a string of a list of strings
        # useful for AS nodes, edges, links as well as area nodes and links
        to_string = lambda s: str(list(map(str, s)))
        
        # filepath is set for unittest
        if not selected_file:
            filepath = QFileDialog.getSaveFileName(
                                                   self, 
                                                   "Export project",
                                                   self.name, 
                                                   ".xls"
                                                   )
            selected_file = ''.join(filepath)
        print(selected_file)
        # else:
        #     selected_file = open(filepath, 'w')
        
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
                    xls_sheet.write(0, id, property.name)
                    for i, obj in enumerate(pool_obj, 1):
                        xls_sheet.write(i, id, str(getattr(obj, property.name)))
                    
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
                        node_AS_sheet.write(cpt, idx, str(node(AS.name, property.name)))
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
                                if_AS_sheet.write(cpt, idx, str(interface(AS.name, property.name)))
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
                
        excel_workbook.save(selected_file)
        # selected_file.close()
        
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
                    