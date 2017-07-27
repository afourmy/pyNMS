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

from . import area
from pythonic_tkinter.preconfigured_widgets import *
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
        QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QInputDialog, QLabel, QLineEdit, QComboBox, QListWidget, QAbstractItemView, QTabWidget)

class ASManagement(QWidget):
    
    def __init__(self, AS, is_imported):
        super().__init__()
        self.AS = AS
        self.network = self.AS.view.network
        self.dict_listbox = {}
        self.setWindowTitle('Manage AS')
        
        self.frame_notebook = QTabWidget(self)
        
        # first tab: the common management window
        common_frame = QWidget(self.frame_notebook)
        self.frame_notebook.addTab(common_frame, ' Common management ')

        # group box for properties
        AS_management = QGroupBox()
        AS_management.setTitle('AS management')
        
        label_name = QLabel('AS name')
        label_id = QLabel('AS ID')
        label_type = QLabel('AS type')
        name_edit = QLineEdit()
        name_edit.setMaximumWidth(120)
        id_edit = QLineEdit()
        id_edit.setMaximumWidth(120)
        AS_type = QLabel(AS.AS_type)
        
        # delete the AS
        button_delete_AS = QPushButton()
        button_delete_AS.setText('Delete AS')
        button_delete_AS.clicked.connect(self.AS.delete_AS)
        
        # automatic cost allocation
        button_cost_allocation = QPushButton()
        button_cost_allocation.setText('Automatic cost allocation')
        button_cost_allocation.clicked.connect(lambda: self.network.WSP_TS(AS))
        
        AS_management_layout = QGridLayout()
        AS_management_layout.addWidget(label_name, 0, 0)
        AS_management_layout.addWidget(label_id, 1, 0)
        AS_management_layout.addWidget(label_type, 2, 0)
        AS_management_layout.addWidget(name_edit, 0, 1)
        AS_management_layout.addWidget(id_edit, 1, 1)
        AS_management_layout.addWidget(AS_type, 2, 1)
        AS_management_layout.addWidget(button_delete_AS, 0, 2)
        AS_management_layout.addWidget(button_cost_allocation, 1, 2)
        AS_management.setLayout(AS_management_layout)
        
        # group box for links and nodes
        object_management = QGroupBox()
        object_management.setTitle('AS objects')
        
        nodes = QLabel('AS nodes')
        self.node_list = QListWidget()
        self.node_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.dict_listbox['node'] = self.node_list
        
        links = QLabel('AS links')
        self.link_list = QListWidget()
        self.link_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.dict_listbox['link'] = self.link_list
            
        # add all physical links between nodes of the AS
        button_find_links = QPushButton()
        button_find_links.setText('Find links')
        button_find_links.clicked.connect(self.find_links)
        
        # find domain physical links: the physical links between nodes of the AS
        button_remove_nodes = QPushButton()
        button_remove_nodes.setText('Remove nodes')
        button_remove_nodes.clicked.connect(lambda: self.remove_selected('node'))
        
        object_layout = QGridLayout()
        object_layout.addWidget(nodes, 0, 0)
        object_layout.addWidget(self.node_list, 0, 1)
        object_layout.addWidget(links, 0, 1)
        object_layout.addWidget(self.link_list, 1, 1)
        object_layout.addWidget(button_find_links, 2, 0)
        object_layout.addWidget(button_remove_nodes, 2, 1)
        object_management.setLayout(object_layout)
        
        # layout of the creation menu
        common_frame_layout = QVBoxLayout(common_frame)
        common_frame_layout.addWidget(AS_management)
        common_frame_layout.addWidget(object_management)
            
    ## Functions used directly from the AS Management window
        
    # refresh display
    def refresh_display(self):
        # populate the listbox with all AS objects
        for obj_type in ('link', 'node'):
            self.dict_listbox[obj_type].clear()
            for obj in self.AS.pAS[obj_type]:
                self.dict_listbox[obj_type].insert(obj)
        
    # function to highlight the selected object on the canvas
    def highlight_object(self, event, obj_type):        
        self.AS.view.unhighlight_all()
        for selected_object in self.dict_listbox[obj_type].selected():
            so = self.network.of(name=selected_object, _type=obj_type)
            self.AS.view.highlight_objects(so)
            
    # remove the object selected in 'obj_type' listbox from the AS
    def remove_selected(self, obj_type):
        # remove and retrieve the selected object in the listbox
        for selected_obj in self.dict_listbox[obj_type].pop_selected():
            # remove it from the AS as well
            so = self.network.of(name=selected_obj, _type=obj_type)
            self.AS.remove_from_AS(so)
        
    def add_to_AS(self, *objects):
        self.AS.add_to_AS(*objects)
        for obj in objects:
            self.dict_listbox[obj.class_type].insert(obj)
            
    def find_links(self):
        links_between_domain_nodes = set()
        for node in self.AS.pAS['node']:
            for neighbor, adj_link in self.network.graph[node.id]['plink']:
                if neighbor in self.AS.pAS['node']:
                    links_between_domain_nodes |= {adj_link}
            #TODO refactor this
            for neighbor, vc in self.network.gftr(node, 'l2link', 'l2vc'):
                if neighbor in self.AS.pAS['node']:
                    links_between_domain_nodes |= {vc.linkS, vc.linkD}
            for neighbor, vc in self.network.gftr(node, 'l3link', 'l3vc'):
                if neighbor in self.AS.pAS['node']:
                    links_between_domain_nodes |= {vc.linkS, vc.linkD}
            
        self.add_to_AS(*links_between_domain_nodes)
            
    ## Functions used to modify AS from the right-click menu
                
    def remove_from_AS(self, *objects):
        self.AS.remove_from_AS(*objects)
        for obj in objects:
            if obj.type == 'node':
                # remove the node from nodes listbox
                self.dict_listbox['node'].pop(obj)
            elif obj.class_type == 'link':
                self.dict_listbox['link'].pop(obj)
            
class ASManagementWithArea(ASManagement):
    
    def __init__(self, *args):
        super().__init__(*args)
                
        if self.AS.AS_type == 'VLAN':
            mode = 'VLAN'
        else:
            mode = 'Area'
        
        self.area_frame = CustomFrame(self.frame_notebook)
        self.frame_notebook.add(self.area_frame, text=' Area management ')
        self.area_listbox = ('name', 'link', 'node')
        self.dict_area_listbox = {}
        
        # label frame for area properties
        lf_area_main = Labelframe(self.area_frame)
        lf_area_main.text = 'Area properties'
        lf_area_main.grid(0, 0)
        
        area_names_label = Label(self.area_frame)
        area_names_label.text = 'List of all ' + mode
        
        self.area_names = ObjectListbox(self.area_frame, width=15, height=7)
        yscroll_names = Scrollbar(self.area_frame)
        yscroll_names.command = self.area_names.yview
        self.area_names.configure(yscrollcommand=yscroll_names.set)
        self.area_names.bind('<<ListboxSelect>>', lambda e: self.display_area(e))
        
        #TODO add entry / label for all area properties
        
        area_names_label.grid(0, 0, in_=lf_area_main)
        self.area_names.grid(1, 0, in_=lf_area_main)
        yscroll_names.grid(1, 1, in_=lf_area_main)
        
        # label frame for area objects
        lf_area_objects = Labelframe(self.area_frame)
        lf_area_objects.text = 'Area objects'
        lf_area_objects.grid(1, 0)
                    
        # listbox for area nodes
        area_nodes_label = Label(self.area_frame)
        area_nodes_label.text = mode + ' nodes'
        
        self.area_nodes = ObjectListbox(self.area_frame, width=15, height=7)
        yscroll_nodes = Scrollbar(self.area_frame)
        yscroll_nodes.command = self.area_nodes.yview
        self.area_nodes.configure(yscrollcommand=yscroll_nodes.set)
        self.area_nodes.bind('<<ListboxSelect>>', lambda e: self.display_area(e))
        
        area_nodes_label.grid(0, 0, in_=lf_area_objects)
        self.area_nodes.grid(1, 0, in_=lf_area_objects)
        yscroll_nodes.grid(1, 1, in_=lf_area_objects)
        
        # listbox for area physical links
        area_links_label = Label(self.area_frame)
        area_links_label.text = mode + ' physical links'
        
        self.area_links = ObjectListbox(self.area_frame, width=15, height=7)
        yscroll_links = Scrollbar(self.area_frame)
        yscroll_links.command = self.area_links.yview
        self.area_links.configure(yscrollcommand=yscroll_links.set)
        self.area_links.bind('<<ListboxSelect>>', lambda e: self.display_area(e))
        
        area_links_label.grid(0, 2, in_=lf_area_objects)
        self.area_links.grid(1, 2, in_=lf_area_objects)
        yscroll_links.grid(1, 3, in_=lf_area_objects)
                                                          
        # button to create an area
        button_create_area = Button(self.area_frame) 
        button_create_area.text = 'Create ' + mode
        button_create_area.command = lambda: area.CreateArea(self)
                                
        # button to delete an area
        button_delete_area = Button(self.area_frame)
        button_delete_area.text = 'Delete area'
        button_delete_area.command = lambda: self.delete_area()
            
        # button under the area column
        button_create_area.grid(2, 0, in_=lf_area_objects)
        button_delete_area.grid(2, 2, in_=lf_area_objects)
        
        # at first, the backbone is the only area: we insert it in the listbox
        self.default_area = 'Default VLAN' if mode == 'VLAN' else 'Backbone'
        self.area_names.insert(self.default_area)
            
    # function to highlight the selected object on the canvas
    def highlight_area_object(self, event, obj_type):        
        self.AS.view.unhighlight_all()
        lb = self.area_nodes if obj_type == 'node' else self.area_links
        for selected_object in lb.selected():
            so = self.network.of(name=selected_object, _type=obj_type)
            self.AS.view.highlight_objects(so)
        
    ## Functions used directly from the AS Management window

    def create_area(self, name, id):
        self.AS.area_factory(name, id)
        self.area_names.insert(name)

    def delete_area(self):
        for area_name in self.area_names.pop_selected():
            selected_area = self.AS.area_factory(name=area_name)
            self.AS.delete_area(selected_area)
                
    def display_area(self, event):
        for area in self.area_names.selected():
            area = self.AS.area_factory(area)
            self.AS.view.unhighlight_all()
            self.AS.view.highlight_objects(*(area.pa['node'] | area.pa['link']))
            self.area_nodes.clear()
            self.area_links.clear()
            for node in area.pa['node']:
                self.area_nodes.insert(node)
            for link in area.pa['link']:
                self.area_links.insert(link)
                
    ## Functions used to modify AS from the right-click menu
    
    def add_to_AS(self, *objects):
        super(ASManagementWithArea, self).add_to_AS(*objects)  
    
    def add_to_area(self, area, *objects):
        self.AS.areas[area].add_to_area(*objects)
            
    def remove_from_area(self, area, *objects):
        self.AS.areas[area].remove_from_area(*objects)
        
class IPManagement(ASManagement):
    
    def __init__(self, *args):
        super().__init__(*args)
                    
        self.ip_frame = CustomFrame(self.frame_notebook)
        self.frame_notebook.add(self.ip_frame, text=' IP management ')
        
        # label frame for area properties
        lf_redistribution = Labelframe(self.ip_frame)
        lf_redistribution.text = 'Redistribution'
        lf_redistribution.grid(0, 0)
        
        default_route_label = Label(self.ip_frame)
        default_route_label.text = 'Propagate default route :'
        
        self.choose_router = Combobox(self.ip_frame, width=15, height=7)
        self.choose_router['values'] = tuple(self.AS.nodes)
        self.choose_router.current(0)
        
        default_route_label.grid(0, 0, in_=lf_redistribution)
        self.choose_router.grid(0, 1, in_=lf_redistribution)
                
class RIP_Management(ASManagement):
    
    def __init__(self, *args):
        super().__init__(*args)
        
class STP_Management(ASManagement):
    
    def __init__(self, *args):
        super().__init__(*args)
        
        STP_frame = CustomFrame(self.frame_notebook)
        self.frame_notebook.add(STP_frame, text='STP Specifics')
        
        # label frame for links and nodes
        lf_stp_specifics = Labelframe(STP_frame)
        lf_stp_specifics.text = 'STP specifics properties'
        lf_stp_specifics.grid(0, 0)
        
        # compute the spanning tree
        button_compute_SPT = Button(STP_frame) 
        button_compute_SPT.text='Compute STP'
        button_compute_SPT.command = self.AS.build_SPT
        
        # highlight all physical links that are part of the spanning tree
        button_highlight_SPT = Button(STP_frame) 
        button_highlight_SPT.text='Highlight spanning tree'
        button_highlight_SPT.command = self.highlight_SPT
        
        # trigger a root election
        button_elect_root = Button(STP_frame) 
        button_elect_root.text='Elect a root switch'
        button_elect_root.command = self.elect_root
        
        button_compute_SPT.grid(0, 0, in_=lf_stp_specifics)
        button_highlight_SPT.grid(1, 0, in_=lf_stp_specifics)
        button_elect_root.grid(2, 0, in_=lf_stp_specifics)
        
    def highlight_SPT(self):
        self.AS.view.highlight_objects(*self.AS.SPT_links)
        
    def elect_root(self):
        self.AS.root_election()
        self.AS.view.highlight_objects(self.AS.root)
        
class VLAN_Management(ASManagementWithArea):
    
    def __init__(self, *args):
        super().__init__(*args)
        
class ISIS_Management(ASManagementWithArea, IPManagement):
    
    def __init__(self, *args):
        super().__init__(*args)
        
        # interface to cost dictionnary. This is used for OSPF and IS-IS, 
        # because the cost of a physical link depends on the bandwidth.
        # Trunk_cost = Ref_BW / BW
        self.if_to_cost = {
        'FE': 10**7,
        'GE': 10**8,
        '10GE': 10**9,
        '40GE': 4*10**9,
        '100GE':10**10
        }
        
    def add_to_AS(self, *objects):
        super(ISIS_Management, self).add_to_AS(*objects)  
        self.add_to_area(self.default_area, *objects)
                
    def update_cost(self):
        for link in self.AS.pAS['link']:
            bw = self.if_to_cost[link.interface]
            # the cost of a link cannot be less than 1. This also means that,
            # by default, all interfaces from GE to 100GE will result in the
            # same metric: 1.
            cost = max(1, self.AS.ref_bw / bw)
            link.costSD = link.costDS = cost
        
class OSPF_Management(ASManagementWithArea, IPManagement):
    
    def __init__(self, *args):
        super().__init__(*args)
        
        # interface to cost dictionnary. This is used for OSPF and IS-IS, 
        # because the cost of a physical link depends on the bandwidth.
        # Trunk_cost = Ref_BW / BW
        self.if_to_cost = {
        'FE': 10**7,
        'GE': 10**8,
        '10GE': 10**9,
        '40GE': 4*10**9,
        '100GE':10**10
        }
        
        # combobox to choose the exit ASBR
        self.exit_asbr = tk.StringVar()
        self.router_list = ttk.Combobox(self, 
                                    textvariable=self.exit_asbr, width=10)
        self.router_list['values'] = (None,) + tuple(
                                        self.dict_listbox['node'].yield_all())
        self.exit_asbr.set(None)
        
        # hide the window when closed
        self.protocol('WM_DELETE_WINDOW', self.save_parameters)
        
    def add_to_AS(self, *objects):
        super(OSPF_Management, self).add_to_AS(*objects)  
        self.add_to_area(self.default_area, *objects)
                
    def update_cost(self):
        for link in self.AS.pAS['link']:
            bw = self.if_to_cost[link.interface]
            # the cost of a link cannot be less than 1. This also means that,
            # by default, all interfaces from GE to 100GE will result in the
            # same metric: 1.
            cost = max(1, self.AS.ref_bw / bw)
            link.costSD = link.costDS = cost 
            
    ## saving function: used when closing the window
    
    def save_parameters(self):
        if self.exit_asbr.get() != 'None':
            exit_asbr = self.network.pn['node'][self.exit_asbr.get()]
            self.AS.exit_point = exit_asbr
        self.withdraw()
        
class BGP_Management(ASManagementWithArea):
    
    def __init__(self, *args):
        super().__init__(*args)