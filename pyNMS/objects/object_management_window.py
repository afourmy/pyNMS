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

import re
from objects.objects import *
from miscellaneous.decorators import update_paths
from pyQT_widgets.Q_object_combo_box import QObjectComboBox
from PyQt5.QtWidgets import (
                             QGridLayout,
                             QGroupBox,
                             QLabel, 
                             QLineEdit,
                             QWidget
                             )

class ObjectManagementWindow(QWidget):
    
    read_only = (
                 'source', 
                 'destination',
                 'path',
                 'flowSD',
                 'flowDS', 
                 'bgp_AS',
                 'AS'
                )
                
    property_list = {
    'interface': ('FE', 'GE', '10GE', '40GE', '100GE'),
    'site_type': ('Physical', 'Logical'),
    'controller_type': ('DefaultController', 'RemoteController'),
    'default_route': (None,),
    'nh_tk': (None,),
    'nh_ip': (None,),
    'ipS': (None,),
    'ipD': (None,),
    'dst_sntw': (None,)
    }
    
    perAS_properties = ()
                
    @update_paths
    def __init__(self, obj, controller):
        super().__init__()
        self.setWindowTitle('Properties')
        self.current_obj = obj
        
        # dictionnary containing all global properties entries / combobox
        self.dict_global_properties = {}
        
        # dictionnary containing all per-AS properties
        self.dict_perAS_properties = {}
        
        # global properties
        global_properties = QGroupBox('Global properties')
        global_properties_layout = QGridLayout(global_properties)
        
        for index, property in enumerate(object_properties[obj.subtype]):
            
            # too much trouble handling interfaces here
            if property.name in ('interfaceS', 'interfaceD'):
                continue
            
            # creation of the label associated to the property
            label = QLabel(property.pretty_name)
            
            # value of the property: drop-down list or entry
            if property.multiple_values and property.choose_one_value:
                pvalue = QObjectComboBox()
                pvalue.addItems(property.values)
            else:
                # s = 'readonly' if property in self.read_only else 'normal'
                pvalue = QLineEdit()
                if property.hide_view:
                    pvalue.setEchoMode(QLineEdit.Password)
                
            self.dict_global_properties[property] = pvalue
            global_properties_layout.addWidget(label, index + 1, 0, 1, 1)
            global_properties_layout.addWidget(pvalue, index + 1, 1, 1, 1)
            
        if obj.subtype in self.perAS_properties:
            
            # global properties
            perAS_properties = QGroupBox('Per-AS properties')
            perAS_properties_layout = QGridLayout(perAS_properties)

            self.dict_perAS_properties = {}
            
            # AS combobox
            self.AS_list = QComboBox()
            self.AS_list.addItems(obj.AS)
            self.AS_list.activated.connect(self.update_AS_properties)
        
            for index, property in enumerate(perAS_properties[obj.subtype]):
                
                # creation of the label associated to the property
                label = QLabel(property.pretty_name)
                pvalue = QLineEdit()
                
                self.dict_perAS_properties[property] = pvalue
                perAS_properties_layout.addWidget(label, index + 1, 0)
                perAS_properties_layout.addWidget(pvalue, index + 1, 1)
                
        # update all properties with the selected object properties
        self.update()
            
        layout = QGridLayout()
        layout.addWidget(global_properties, 0, 0)
        if obj.subtype in self.perAS_properties:
            layout.addWidget(perAS_properties, 1, 0)
        self.setLayout(layout)
        
    def update_AS_properties(self, _):
        AS = self.AS_combobox.text
        for property, entry in self.dict_perAS_properties.items():
            entry.text = str(self.current_obj.AS_properties[AS][property])
        
    def closeEvent(self, _):
        for property, property_widget in self.dict_global_properties.items():
            try:
                value = property_widget.text()
            except (AttributeError, TypeError):
                value = property_widget.text
            # convert 'None' to None if necessary
            value = None if value == 'None' else value              
            if property.name == 'sites':
                value = filter(None, set(re.sub(r'\s+', '', value).split(',')))
                value = set(map(self.site_network.convert_node, value))
                setattr(self.current_obj, property.name, value)
            elif property.name in self.property_list:
                if property.name in ('ipS', 'ipD', 'default_route'):
                    # convert the IP to a Object IP, if it isn't None
                    if value:
                        value = self.network.ip_to_oip[value]
                setattr(self.current_obj, property.name, value)
            else:
                if (property.name not in self.read_only 
                and 'interface' not in property.name):
                    if property == 'name':
                        name = getattr(self.current_obj, property.name)
                        id = self.network.name_to_id.pop(name)
                        self.network.name_to_id[value] = id
                    if property.is_editable:
                        setattr(self.current_obj, property.name, value)
             
        # if hasattr(self.current_obj, 'AS_properties'):
        #     if self.current_obj.AS_properties:
        #         AS = self.AS_combobox.text
        #         for property, entry in self.dict_perAS_properties.items():
        #             value = self.network.prop_to_type[property](entry.text)
        #             self.current_obj(AS, property, value)
            
    def update(self):
        for property, property_widget in self.dict_global_properties.items():
            obj_prop = getattr(self.current_obj, property.name)
            if property == 'nh_tk':
                src_route = self.current_obj.source
                attached_ints = tuple(filter(None, (plink for _, plink 
                                in self.network.graph[src_route]['plink'])))
                property_widget.addItems(attached_ints)
                # property_widget.text = obj_prop
            elif property == 'dst_sntw':
                dest_node = self.current_obj.destination
                attached_ips = (None,) + tuple(filter(None, 
                            (plink.sntw for _, plink
                            in self.network.graph[dest_node]['plink']
                            ))) 
                property_widget.addItems(attached_ips)
                # property_widget.text = obj_prop
            elif property == 'ipS':
                src = self.current_obj.source
                attached_ips = (None,) + tuple(filter(None, 
                                    self.network.attached_ips(src)))
                property_widget.addItems(attached_ips)
                # property_widget.text = obj_prop
            elif property == 'nh_ip':
                nh_ips = (None,) + tuple(filter(None, 
                                    self.network.nh_ips(self.current_obj)))
                property_widget.addItems(nh_ips)
                # property_widget.text = obj_prop
            elif property == 'ipD':
                dest = self.current_obj.destination
                attached_ips = (None,) + tuple(filter(None, 
                                    self.network.attached_ips(dest)))
                property_widget.addItems(attached_ips)
                # property_widget.text = obj_prop
            elif property in self.property_list:
                property_widget.setCurrentIndex(1)
            elif property == 'AS':
                property_widget.setText(','.join(map(str, obj_prop.keys())))
            elif type(obj_prop) in (list, set):
                property_widget.setText(','.join(map(str, obj_prop)))
            else:
                property_widget.setText(str(obj_prop))
                
        # if self.current_obj.subtype in perAS_properties:
        #     self.AS_combobox.addItems(tuple(self.current_obj.AS_properties))
        #     has_AS = bool(self.current_obj.AS_properties)
        #     first_AS = next(iter(self.current_obj.AS_properties)) if has_AS else ''
        #     self.AS_combobox.setText = first_AS
        #     for property, property_widget in self.dict_perAS_properties.items():
        #         if has_AS:
        #             value = str(self.current_obj.AS_properties[first_AS][property])
        #         else:
        #             value = ''
        #         property_widget.setText = value
        