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

from . import area, area_operations
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
        QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QInputDialog, QLabel, QLineEdit, QComboBox, QListWidget, QAbstractItemView, QTabWidget)

class ASManagement(QTabWidget):
    
    def __init__(self, AS, is_imported):
        super().__init__()
        self.AS = AS
        self.network = self.AS.view.network
        self.setMinimumSize(300, 300)
        self.dict_listbox = {}
        self.setWindowTitle('Manage AS')
        
        # self.frame_notebook = QTabWidget(self)
        
        # first tab: the common management window
        common_frame = QWidget(self)
        self.addTab(common_frame, 'Common management')

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
        self.node_list.setSortingEnabled(True)
        self.node_list.itemSelectionChanged.connect(lambda: self.highlight_object('node'))
        self.dict_listbox['node'] = self.node_list
        
        links = QLabel('AS links')
        self.link_list = QListWidget()
        self.link_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.link_list.setSortingEnabled(True)
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
        object_layout.addWidget(links, 1, 0)
        object_layout.addWidget(self.link_list, 1, 1)
        object_layout.addWidget(button_find_links, 2, 0)
        object_layout.addWidget(button_remove_nodes, 2, 1)
        object_management.setLayout(object_layout)
        
        # layout for the group box
        common_frame_layout = QVBoxLayout(common_frame)
        common_frame_layout.addWidget(AS_management)
        common_frame_layout.addWidget(object_management)
        
        self.show()
            
    ## Functions used directly from the AS Management window
        
    # refresh display
    def refresh_display(self):
        # populate the listbox with all AS objects
        for obj_type in ('link', 'node'):
            self.dict_listbox[obj_type].clear()
            for obj in self.AS.pAS[obj_type]:
                self.dict_listbox[obj_type].addItem(str(obj))
        
    # function to highlight the selected object on the canvas
    def highlight_object(self, obj_type):
        self.AS.view.scene.clearSelection() 
        for selected_item in self.dict_listbox[obj_type].selectedItems():
            obj = self.network.of(name=selected_item.text(), _type=obj_type)
            obj.gobject.setSelected(True)
                        
    # remove the object selected in 'obj_type' listbox from the AS
    def remove_selected(self, obj_type):
        # remove and retrieve the selected object in the listbox
        for selected_item in self.dict_listbox[obj_type].selectedItems():
            # self.dict_listbox[obj_type].removeItem(selected_item)
            # remove it from the AS as well
            so = self.network.of(name=selected_item.text(), _type=obj_type)
            self.AS.remove_from_AS(so)
            row = self.dict_listbox[obj_type].row(selected_item)
            self.dict_listbox[obj_type].takeItem(row)
        
    def add_to_AS(self, *objects):
        self.AS.add_to_AS(*objects)
        for obj in objects:
            if self.dict_listbox[obj.class_type].findItems(str(obj), Qt.MatchExactly):
                continue
            self.dict_listbox[obj.class_type].addItem(str(obj))
            
    def find_links(self):
        links_between_domain_nodes = set()
        for node in self.AS.pAS['node']:
            for neighbor, adj_link in self.network.graph[node.id]['plink']:
                if neighbor in self.AS.pAS['node']:
                    links_between_domain_nodes |= {adj_link}
        self.add_to_AS(*links_between_domain_nodes)
            
    ## Functions used to modify AS from the right-click menu
                
    def remove_from_AS(self, *objects):
        self.AS.remove_from_AS(*objects)
        for obj in objects:
            item ,= self.dict_listbox[obj.class_type].findItems(str(obj), Qt.MatchExactly)
            row = self.dict_listbox[obj.class_type].row(item)
            self.dict_listbox[obj.class_type].takeItem(row)
            
class ASManagementWithArea(ASManagement):
    
    def __init__(self, *args):
        super().__init__(*args)
                
        if self.AS.AS_type == 'VLAN':
            mode = 'VLAN'
        else:
            mode = 'Area'
            
        # first tab: the area management window
        area_frame = QWidget(self)
        self.addTab(area_frame, '{} management'.format(mode))
        
        # group box for area management
        area_management = QGroupBox()
        area_management.setTitle('Area properties')
        
        area_names = QLabel('List of all {}'.format(mode.lower()))
        self.area_list = QListWidget()
        self.area_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.area_list.setSortingEnabled(True)
        self.area_list.itemSelectionChanged.connect(self.display_area)
        
        area_management_layout = QGridLayout()
        area_management_layout.addWidget(area_names, 0, 0)
        area_management_layout.addWidget(self.area_list, 1, 0)
        area_management.setLayout(area_management_layout)
        
        # group box for area objects
        area_objects = QGroupBox()
        area_objects.setTitle('Area objects')
        
        # list of area nodes
        area_nodes = QLabel('{} nodes'.format(mode))
        self.area_nodes_list = QListWidget()
        self.area_nodes_list.setSelectionMode(QAbstractItemView.ExtendedSelection) 
        self.area_nodes_list.setSortingEnabled(True)
        self.area_nodes_list.itemSelectionChanged.connect(lambda: self.highlight_area_object('node'))
        
        # list of area links
        area_links = QLabel('{} links'.format(mode))
        self.area_links_list = QListWidget()
        self.area_links_list.setSelectionMode(QAbstractItemView.ExtendedSelection) 
        self.area_links_list.setSortingEnabled(True)
        self.area_links_list.itemSelectionChanged.connect(lambda: self.highlight_area_object('link'))
        
        # create an area
        button_create_area = QPushButton()
        button_create_area.setText('Create {}'.format(mode.lower()))
        button_create_area.clicked.connect(self.create_area)
        
        # delete an area
        button_delete_area = QPushButton()
        button_delete_area.setText('Delete {}'.format(mode.lower()))
        button_delete_area.clicked.connect(self.delete_area)
                                                          
        area_objects_layout = QGridLayout()
        area_objects_layout.addWidget(area_nodes, 0, 0)
        area_objects_layout.addWidget(self.area_nodes_list, 1, 0)
        area_objects_layout.addWidget(area_links, 0, 1)
        area_objects_layout.addWidget(self.area_links_list, 1, 1)
        area_objects_layout.addWidget(button_create_area, 2, 0)
        area_objects_layout.addWidget(button_delete_area, 2, 1)
        area_objects.setLayout(area_objects_layout)
        
        # layout for the group box
        area_frame_layout = QVBoxLayout(area_frame)
        area_frame_layout.addWidget(area_management)
        area_frame_layout.addWidget(area_objects)
            
    # function to highlight the selected object on the canvas
    def highlight_area_object(self, obj_type):        
        self.AS.view.scene.clearSelection()
        lb = self.area_nodes_list if obj_type == 'node' else self.area_links_list
        for selected_item in lb.selectedItems():
            selected_object = self.network.of(name=selected_item.text(), _type=obj_type)
            selected_object.gobject.setSelected(True)
        
    ## Functions used directly from the AS Management window
        
    def create_area(self):
        self.create_area_window = area_operations.CreateArea(self)
        self.create_area_window.show()

    def add_area(self, name, id):
        self.AS.area_factory(name, id)
        self.area_list.addItem(name)

    def delete_area(self):
        for area_item in self.area_list.selectedItems():
            selected_area = self.AS.area_factory(name=area_item.text())
            self.AS.delete_area(selected_area)
            self.area_list.takeItem(self.area_list.row(area_item))
                
    def display_area(self):
        self.area_nodes_list.clear()
        self.area_links_list.clear()
        self.AS.view.scene.clearSelection()
        for area in self.area_list.selectedItems():
            area = self.AS.area_factory(area.text())
            for obj in area.pa['node'] | area.pa['link']:
                obj.gobject.setSelected(True)
            for node in area.pa['node']:
                self.area_nodes_list.addItem(str(node))
            for link in area.pa['link']:
                self.area_links_list.addItem(str(link))
                
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
        
    def add_to_AS(self, *objects):
        super(OSPF_Management, self).add_to_AS(*objects)  
        self.add_to_area('Backbone', *objects)
                
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
