# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import re
import tkinter as tk
from tkinter import ttk, messagebox
from objects.objects import perAS_properties
from pythonic_tkinter.preconfigured_widgets import *

class ObjectManagementWindow(FocusTopLevel):
    
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
    'default_route': (None,),
    'nh_tk': (None,),
    'nh_ip': (None,),
    'ipS': (None,),
    'ipD': (None,),
    'dst_sntw': (None,)
    }
                
    def __init__(self, master, type):
        super().__init__()
        self.ms = master
        self.title('Manage {} properties'.format(type))

        # current node which properties are displayed
        self.current_obj = None
        # current path of the object: computing a path is not saving it
        self.current_path = None
        # dictionnary containing all global properties entries / combobox
        self.dict_global_properties = {}
        # dictionnary containing all per-AS properties
        self.dict_perAS_properties = {}

        # create the property window
        
        # labelframe for global properties
        lf_global = Labelframe(self)
        lf_global.text = 'Global properties'
        lf_global.grid(1, 0, 1, 2)
        
        for index, property in enumerate(self.ms.object_properties[type]):
            
            # creation of the label associated to the property
            text = self.ms.prop_to_nice_name[property]
            label = Label(self)
            label.text = text
            
            # value of the property: drop-down list or entry
            if property in self.property_list:
                pvalue = Combobox(self, width=12)
                pvalue['values'] = self.property_list[property]
            else:
                s = 'readonly' if property in self.read_only else 'normal'
                pvalue = Entry(self, width=15, state=s)
                
            self.dict_global_properties[property] = pvalue
                
            label.grid(index+1, 0, pady=1, in_=lf_global)
            pvalue.grid(index+1, 1, pady=1, in_=lf_global)
            
        if type in perAS_properties:
            # labelframe for per-AS interface properties
            lf_perAS = Labelframe(self)
            lf_perAS.text = 'Per-AS properties'
            lf_perAS.grid(2, 0, 1, 2)
            self.dict_perAS_properties = {}
            
            # AS combobox
            self.AS_combobox = Combobox(self, width=20)
            self.AS_combobox.bind('<<ComboboxSelected>>', self.update_AS_properties)
            self.AS_combobox.grid(0, 0, in_=lf_perAS)
        
            for index, property in enumerate(perAS_properties[type]):
                
                # creation of the label associated to the property
                text = self.ms.prop_to_nice_name[property]
                label = Label(self)
                label.text = text
                
                # value of the property
                pvalue = Entry(self, width=15)
                
                self.dict_perAS_properties[property] = pvalue
                    
                label.grid(index+1, 0, pady=1, in_=lf_perAS)
                pvalue.grid(index+1, 1, pady=1, in_=lf_perAS)
            
        # route finding possibilities for a route
        # TODO 
        # if type == 'route':
        #     self.button_compute_path = ttk.Button(self, text='Compute path', 
        #                             command=lambda: self.find_path())
        #     self.button_compute_path.grid(row=n+1, column=0, columnspan=2, 
        #                                                         pady=5, padx=5)
                                                                
        button_save_obj = Button(self) 
        button_save_obj.text = 'Save'
        button_save_obj.command = lambda: self.save_obj()
        button_save_obj.grid(0, 1)
        
        # when the window is closed, save all parameters (in case the user
        # made a change), then withdraw the window.
        self.protocol('WM_DELETE_WINDOW', lambda: self.save_and_withdraw())
        self.withdraw()
        
    def update_AS_properties(self, _):
        AS = self.AS_combobox.text
        for property, entry in self.dict_perAS_properties.items():
            entry.text = str(self.current_obj.AS_properties[AS][property])
        
    # this function converts the user-defined constraints to python objects.
    # it is used both when reading the user inputs, and when saving the 
    # route properties.
    def conv(self, property):
        value = self.dict_var[property].get().replace(' ','').split(',')
        if property == 'excluded_trunks':
            return {self.ms.cs.ntw.lf(name=t) for t in filter(None, value)}
        elif property == 'excluded_nodes':
            return {self.ms.cs.ntw.nf(name=n) for n in filter(None, value)}
        else:
            return [self.ms.cs.ntw.nf(name=n) for n in filter(None, value)]
    
    def get_user_input(self):
        name = self.dict_var['name'].get()
        source = self.ms.cs.ntw.nf(name=self.dict_var['source'].get())
        destination = self.ms.cs.ntw.nf(name=self.dict_var['destination'].get())
        return (
                name, 
                source, 
                destination, 
                self.conv('excluded_trunks'), 
                self.conv('excluded_nodes'), 
                self.conv('path_constraints')
                )
        
    def find_path(self):
        name, *parameters = self.get_user_input()
        nodes, trunks = self.ms.cs.ntw.A_star(*parameters)
        
        if trunks:
            self.ms.cs.unhighlight_all()
            self.current_path = trunks
            self.dict_var['path'].set(trunks)
            self.ms.cs.highlight_objects(*(nodes + trunks))
        else:
            self.ms.cs.unhighlight_all()
            # activate focus to prevent the messagebox from removing the window
            self.var_focus.set(1)
            self.change_focus()
            messagebox.showinfo('Warning', 'No path found')
        
    def save_obj(self):
        for property, property_widget in self.dict_global_properties.items():
            value = property_widget.text
            # convert 'None' to None if necessary
            value = None if value == 'None' else value              
            if property == 'path':
                setattr(self.current_obj, property, self.current_path)
            if property == 'sites':
                value = set(re.sub(r'\s+', '', value).split(','))
                setattr(self.current_obj, property, value)
            elif property in self.property_list:
                setattr(self.current_obj, property, value)
            else:
                if property not in self.read_only and 'interface' not in property:
                    if property in ('path_constraints', 'excluded_nodes', 'excluded_trunks'): 
                        value = self.conv(property)
                    else:
                        value = self.ms.prop_to_type[property](value)
                        if property == 'name':
                            name = getattr(self.current_obj, property)
                            id = self.ms.cs.ntw.name_to_id.pop(name)
                            self.ms.cs.ntw.name_to_id[value] = id
                    setattr(self.current_obj, property, value)
            # refresh the label if it was changed
            self.ms.cs.refresh_label(self.current_obj)
            # move the node on the canvas in case it's coordinates were updated
            if self.current_obj.class_type == 'node':
                self.ms.cs.move_node(self.current_obj)
             
        if hasattr(self.current_obj, 'AS_properties'):
            if self.current_obj.AS_properties:
                AS = self.AS_combobox.text
                for property, entry in self.dict_perAS_properties.items():
                    value = self.ms.prop_to_type[property](entry.text)
                    self.current_obj(AS, property, value)
                
    def save_and_withdraw(self):
        self.save_obj()
        self.withdraw()
            
    def update(self):
        for property, property_widget in self.dict_global_properties.items():
            obj_prop = getattr(self.current_obj, property)
            if property == 'default_route':
                # in practice, the default route can also be set as an outgoing
                # interface, but the router has to do an ARP request for each
                # unknown destination IP address to fill the destination 
                # MAC field of the Ethernet frame, which may result in 
                # ARP table being overloaded: to be avoided in real-life and
                # forbidden here.
                attached_ints = (None,) + tuple(filter(None, 
                                    self.ms.cs.ntw.nh_ips(self.current_obj)))
                property_widget['values'] = attached_ints
                property_widget.text = obj_prop
            elif property == 'nh_tk':
                src_route = self.current_obj.source
                attached_ints = tuple(filter(None, (trunk for _, trunk 
                                in self.ms.cs.ntw.graph[src_route]['trunk'])))
                property_widget['values'] = attached_ints
                property_widget.text = obj_prop
            elif property == 'dst_sntw':
                dest_node = self.current_obj.destination
                attached_ips = (None,) + tuple(filter(None, 
                            (trunk.sntw for _, trunk
                            in self.ms.cs.ntw.graph[dest_node]['trunk']
                            ))) 
                property_widget['values'] = attached_ips
                property_widget.text = obj_prop
            elif property == 'ipS':
                src = self.current_obj.source
                attached_ips = (None,) + tuple(filter(None, 
                                    self.ms.cs.ntw.attached_ips(src)))
                property_widget['values'] = attached_ips
                property_widget.text = obj_prop
            elif property == 'nh_ip':
                nh_ips = (None,) + tuple(filter(None, 
                                    self.ms.cs.ntw.nh_ips(self.current_obj)))
                property_widget['values'] = nh_ips
                property_widget.text = obj_prop
            elif property == 'ipD':
                dest = self.current_obj.destination
                attached_ips = (None,) + tuple(filter(None, 
                                    self.ms.cs.ntw.attached_ips(dest)))
                property_widget['values'] = attached_ips
                property_widget.text = obj_prop
            elif property == 'AS':
                property_widget.text = ','.join(map(str, obj_prop.keys()))
            elif type(obj_prop) in (list, set):
                property_widget.text = ','.join(map(str, obj_prop))
            else:
                property_widget.text = str(obj_prop)
            # if there is a path, we set current_path in case the object is saved
            # without computing a new path
            if property == 'path':
                self.current_path = self.current_obj.path
                
        if self.current_obj.subtype in perAS_properties:
            self.AS_combobox['values'] = tuple(self.current_obj.AS_properties)
            has_AS = bool(self.current_obj.AS_properties)
            first_AS = next(iter(self.current_obj.AS_properties)) if has_AS else ''
            self.AS_combobox.text = first_AS
            for property, property_widget in self.dict_perAS_properties.items():
                if has_AS:
                    value = str(self.current_obj.AS_properties[first_AS][property])
                else:
                    value = ''
                property_widget.text = value
                
class PropertyChanger(FocusTopLevel):
                                    
    def __init__(self, master, objects, type):
        super().__init__()
        self.ms = master
        
        # list of properties
        self.property_list = Combobox(self, width=15)
        self.property_list['values'] = self.ms.object_properties[type]
        self.property_list.current(0)        
                            
        self.entry_prop = Entry(self, width=15)
        button_OK = Button(self)
        button_OK.text = 'OK'
        button_OK.command = lambda: self.confirm(objects)
                                        
        self.property_list.grid(0, 0)
        self.entry_prop.grid(1, 0)
        button_OK.grid(2, 0)
        
    def confirm(self, objects):
        selected_property = self.property_list.text
        value = self.ms.prop_to_type[selected_property](self.entry_prop.text)
        for object in objects:
            setattr(object, selected_property, value)
        self.destroy()
        