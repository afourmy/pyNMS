# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk
from os.path import join
from objects.objects import *
from tkinter import ttk
from PIL import ImageTk
from pythonic_tkinter.preconfigured_widgets import *
from collections import OrderedDict
from graph_generation.network_dimension import NetworkDimension
from drawing import drawing_options_window

class DisplayMenu(CustomFrame):
    
    def __init__(self, notebook, master):
        super().__init__(width=200, height=600, borderwidth=1, relief='solid')
        self.ms = master
        font = ('Helvetica', 8, 'bold')
        
        # label frame for multi-layer display
        lf_multilayer_display = Labelframe(self)
        lf_multilayer_display.text = 'Multi-layer display'
        lf_multilayer_display.grid(0, 0, sticky='nsew')
        
        # label frame to control the display per subtype
        lf_object_display = Labelframe(self)
        lf_object_display.text = 'Per-object display'
        lf_object_display.grid(1, 0, sticky='nsew')
        
        self.dict_image = {}
        
        self.dict_size_image = {
        'netdim': (75, 75), 
        'motion': (75, 75), 
        'multi-layer': (75, 75),
        'ethernet': (85, 15),
        'wdm': (85, 15),
        'static route': (85, 15),
        'BGP peering': (85, 15),
        'OSPF virtual link': (85, 15),
        'Label Switched Path': (85, 15),
        'routed traffic': (85, 15),
        'static traffic': (85, 15),
        'ring': (50, 40), 
        'tree': (50, 30), 
        'star': (50, 50), 
        'full-mesh': (50, 45)
        }
        
        for image_type, image_size in self.dict_size_image.items():
            x, y = image_size
            img_path = join(self.ms.path_icon, image_type + '.png')
            img_pil = ImageTk.Image.open(img_path).resize(image_size)
            img = ImageTk.PhotoImage(img_pil)
            self.dict_image[image_type] = img
        
        self.type_to_button = {}
                
        # multi-layer button
        ml_button = TKButton(self)
        ml_button.config(image=self.dict_image['multi-layer'])
        ml_button.command = self.ms.cs.switch_display_mode
        ml_button.config(width=100, height=100)
        ml_button.grid(0, 0, 2, 2, in_=lf_multilayer_display)
                
        self.layer_boolean = []
        for layer in range(1, 5):
            layer_bool = tk.BooleanVar()
            layer_bool.set(True)
            self.layer_boolean.append(layer_bool)
            self.button_limit = Checkbutton(self, variable = layer_bool)
            self.button_limit.text = 'L' + str(layer)
            self.button_limit.command = self.update_display
            row, col = layer > 2, 2 + layer%2
            self.button_limit.grid(row, col, in_=lf_multilayer_display)
            
        # display filter
        self.filter_label = Label(self)
        self.filter_label.text = 'Display filters'
        self.filter_entry = Entry(self, width=16)
        self.filter_label.grid(2, 0, 1, 2, in_=lf_multilayer_display)
        self.filter_entry.grid(2, 2, 1, 2, in_=lf_multilayer_display)
        
        for obj_type in object_properties:
            if obj_type not in ('l2vc', 'l3vc'):
                cmd = lambda o=obj_type: self.invert_display(o)
                button = TKButton(self, relief=tk.SUNKEN, command=cmd)
                if obj_type in self.ms.cs.ntw.link_class:
                    button.configure(text={
                                        'ethernet': 'Ethernet link',
                                        'wdm': 'WDM link',
                                        'static route': 'Static route',
                                        'BGP peering': 'BGP peering',
                                        'OSPF virtual link': 'OSPF virtual link',
                                        'Label Switched Path': 'MPLS LSP',
                                        'routed traffic': 'Routed traffic',
                                        'static traffic': 'Static traffic' 
                                }[obj_type], compound='top', font=font)
                    button.config(image=self.dict_image[obj_type])
                    button.config(width=160, height=40)
                else:
                    button.config(image=self.ms.dict_image['default'][obj_type])
                    button.config(width=75, height=75)
                self.type_to_button[obj_type] = button
        
        # creation mode: type of node or link
        self.type_to_button['router'].grid(0, 0, padx=2, in_=lf_object_display)
        self.type_to_button['switch'].grid(0, 1, padx=2, in_=lf_object_display)
        self.type_to_button['oxc'].grid(0, 2, padx=2, in_=lf_object_display)
        self.type_to_button['host'].grid(0, 3, padx=2, in_=lf_object_display)
        self.type_to_button['regenerator'].grid(1, 0, padx=2, in_=lf_object_display)
        self.type_to_button['splitter'].grid(1, 1, padx=2, in_=lf_object_display)
        self.type_to_button['antenna'].grid(1, 2, padx=2, in_=lf_object_display)
        self.type_to_button['cloud'].grid(1, 3, padx=2, in_=lf_object_display)
        
        sep = Separator(self)
        sep.grid(2, 0, 1, 4, in_=lf_object_display)
        
        self.type_to_button['ethernet'].grid(3, 0, 1, 2, in_=lf_object_display)
        self.type_to_button['wdm'].grid(3, 2, 1, 2, in_=lf_object_display)
                                                
        self.type_to_button['static route'].grid(4, 0, 1, 2, in_=lf_object_display)
        self.type_to_button['BGP peering'].grid(4, 2, 1, 2, in_=lf_object_display)
        self.type_to_button['OSPF virtual link'].grid(5, 0, 1, 2, in_=lf_object_display)
        self.type_to_button['Label Switched Path'].grid(5, 2, 1, 2, in_=lf_object_display)
        
        self.type_to_button['routed traffic'].grid(6, 0, 1, 2, in_=lf_object_display)
        self.type_to_button['static traffic'].grid(6, 2, 1, 2, in_=lf_object_display)

    def update_display(self):
        display_settings = [0] + list(map(lambda x: x.get(), self.layer_boolean))
        self.ms.cs.display_layer = display_settings
        self.ms.cs.draw_all(False)
        
    def invert_display(self, obj_type):
        value = self.ms.cs.show_hide(obj_type)
        relief = tk.SUNKEN if value else tk.RAISED
        print(relief)
        self.type_to_button[obj_type].config(relief=relief)

        