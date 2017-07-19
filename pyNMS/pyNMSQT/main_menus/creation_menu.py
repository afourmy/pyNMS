# NetDim (contact@netdim.fr)

import tkinter as tk
from os.path import join
from objects.objects import *
from tkinter import ttk
from PIL import ImageTk
from pythonic_tkinter.preconfigured_widgets import *
from collections import OrderedDict
from graph_generation.network_dimension import NetworkDimension
from miscellaneous.decorators import update_paths

class CreationMenu(ScrolledFrame):
        
    def __init__(self, notebook, controller):
        self.controller = controller
        super().__init__(
                         notebook, 
                         width = 200, 
                         height = 600, 
                         borderwidth = 1, 
                         relief = 'solid'
                         )
        font = ('Helvetica', 8, 'bold')
        
        # label frame for object selection
        lf_selection = Labelframe(self.infr)
        lf_selection.text = 'Selection mode'
        lf_selection.grid(1, 0, sticky='nsew')
        
        # label frame for object creation
        lf_creation = Labelframe(self.infr)
        lf_creation.text = 'Creation mode'
        lf_creation.grid(2, 0, sticky='nsew')
        
        # label frame for automatic generation of classic graph
        lf_generation = Labelframe(self.infr)
        lf_generation.text = 'Graph generation'
        lf_generation.grid(3, 0, sticky='nsew')
        
        self.dict_image = {}
        
        self.dict_size_image = {
        'motion': (100, 100), 
        'multi-layer': (75, 75),
        'ethernet link': (100, 15),
        'optical link': (100, 18),
        'optical channel': (100, 18),
        'etherchannel': (100, 15),
        'pseudowire': (100, 15),
        'BGP peering': (100, 18),
        'routed traffic': (100, 15),
        'static traffic': (100, 15),
        'ring': (50, 40), 
        'tree': (50, 30), 
        'star': (50, 50), 
        'full-mesh': (50, 45)
        }
        
        for image_type, image_size in self.dict_size_image.items():
            x, y = image_size
            img_path = join(self.controller.path_icon, image_type + '.png')
            img_pil = ImageTk.Image.open(img_path).resize(image_size)
            img = ImageTk.PhotoImage(img_pil)
            self.dict_image[image_type] = img
        
        self.type_to_button = {}
        
        self.type_to_action = {
        'motion': lambda: self.switch_to('motion'),
        'multi-layer': self.switch_display_mode
        }
        
        for topo in ('tree', 'star', 'full-mesh', 'ring'):
            self.type_to_action[topo] = lambda t=topo: NetworkDimension(t, controller)
            
        for obj_type in link_class:
            if obj_type not in ('l2vc', 'l3vc'):
                cmd = lambda o=obj_type: self.change_creation_mode(o)
                self.type_to_action[obj_type] = cmd
                
        for obj_type in node_class:
            label = TKLabel(image=self.controller.dict_image['default'][obj_type])
            label.image = self.controller.dict_image['default'][obj_type]
            label.config(width=75, height=75)
            set_dnd = lambda _, type=obj_type: self.change_creation_mode(type)
            label.bind('<Button-1>', set_dnd)
            self.type_to_button[obj_type] = label
        
        for button_type, cmd in self.type_to_action.items():
            button = TKButton(self.infr, relief='flat', command=cmd)                
            if button_type in link_class:
                button.configure(text={
                                       'ethernet link': 'Ethernet link',
                                       'optical link': 'Optical link',
                                       'optical channel': 'Optical channel',
                                       'etherchannel': 'Etherchannel',
                                       'pseudowire': 'Pseudowire',
                                       'BGP peering': 'BGP peering',
                                       'routed traffic': 'Routed traffic',
                                       'static traffic': 'Static traffic' 
                            }[button_type], compound='top', font=font)
                button.config(width=160, height=40)
            elif button_type in ('text', 'rectangle'):
                button.configure(compound='top', font=font, text=button_type)
            else:
                button.configure(compound='top', font=font)                                                        
            if button_type not in node_subtype:
                button.config(image=self.dict_image[button_type])
            if button_type in ('tree', 'star', 'full-mesh', 'ring'):
                button.config(width=75, height=75)
            self.type_to_button[button_type] = button
                
        # netdim mode: motion or creation
        self.type_to_button['motion'].grid(0, 0, 3, padx=20, in_=lf_selection)
        
        self.selection_mode = {}
        for id, mode in enumerate(('node', 'link', 'shape')):
            bool = tk.BooleanVar()
            bool.set(not id)
            self.selection_mode[mode] = bool
            button = Checkbutton(self.infr, variable=bool)
            button.text = mode.capitalize() + ' selection'
            button.grid(id, 1, in_=lf_selection)

        # creation mode: type of node or link
        self.type_to_button['router'].grid(0, 0, padx=2, in_=lf_creation)
        self.type_to_button['switch'].grid(0, 1, padx=2, in_=lf_creation)
        self.type_to_button['oxc'].grid(0, 2, padx=2, in_=lf_creation)
        self.type_to_button['host'].grid(0, 3, padx=2, in_=lf_creation)
        self.type_to_button['regenerator'].grid(1, 0, padx=2, in_=lf_creation)
        self.type_to_button['splitter'].grid(1, 1, padx=2, in_=lf_creation)
        self.type_to_button['antenna'].grid(1, 2, padx=2, in_=lf_creation)
        self.type_to_button['cloud'].grid(1, 3, padx=2, in_=lf_creation)
        self.type_to_button['firewall'].grid(2, 0, padx=2, in_=lf_creation)
        self.type_to_button['load_balancer'].grid(2, 1, padx=2, in_=lf_creation)
        self.type_to_button['server'].grid(2, 2, padx=2, in_=lf_creation)
        self.type_to_button['site'].grid(2, 3, padx=2, in_=lf_creation)
        
        sep = Separator(self.infr)
        sep.grid(3, 0, 1, 4, in_=lf_creation)
        
        self.type_to_button['ethernet link'].grid(4, 0, 1, 2, in_=lf_creation)
        self.type_to_button['optical link'].grid(4, 2, 1, 2, in_=lf_creation)
        self.type_to_button['optical channel'].grid(5, 0, 1, 2, in_=lf_creation)
        self.type_to_button['etherchannel'].grid(5, 2, 1, 2, in_=lf_creation)                             
        self.type_to_button['pseudowire'].grid(6, 0, 1, 2, in_=lf_creation)
        self.type_to_button['BGP peering'].grid(6, 2, 1, 2, in_=lf_creation)
        
        self.type_to_button['routed traffic'].grid(7, 0, 1, 2, in_=lf_creation)
        self.type_to_button['static traffic'].grid(7, 2, 1, 2, in_=lf_creation)
        
        # graph generation
        self.type_to_button['tree'].grid(0, 0, in_=lf_generation)
        self.type_to_button['star'].grid(0, 1, in_=lf_generation)
        self.type_to_button['full-mesh'].grid(0, 2, in_=lf_generation)
        self.type_to_button['ring'].grid(0, 3, in_=lf_generation)
        
    def activate_dnd(self, node_type):
        self.controller.dnd = node_type
       
    @update_paths
    def refresh(self):
        self.project.refresh()
       
    @update_paths
    def switch_display_mode(self):
        self.view.switch_display_mode()

    @update_paths
    def update_display(self):
        display_settings = list(map(lambda x: x.get(), self.layer_boolean))
        self.view.display_layer = display_settings
        self.view.draw_all(False)
        
    @update_paths
    def change_selection(self, mode):
        self.view.obj_selection = mode
        
    @update_paths
    def switch_to(self, mode):
        relief = 'sunken' if mode == 'motion' else 'raised'
        self.type_to_button['motion'].config(relief=relief)
        self.view.mode = mode
        self.view.switch_binding(mode)
        
    @update_paths
    def change_creation_mode(self, mode):
        # activate drag and drop
        self.activate_dnd(mode)
        # change the view and update the current view
        if mode == 'site':
            # if it is a site, display the site view
            self.controller.view_menu.switch_view('site')
        else:
            if self.controller.view_menu.current_view == 'site':
                self.controller.view_menu.switch_view('network')
        # change the mode to creation 
        self.switch_to('creation')
        self.view.creation_mode = mode
        for obj_type in self.type_to_button:
            if obj_type in node_subtype:
                continue
            if mode == obj_type:
                self.type_to_button[obj_type].config(relief='sunken')
            else:
                self.type_to_button[obj_type].config(relief='flat')
        self.view.switch_binding(mode)
        
    def erase_graph(self, view):
        self.view.erase_graph()
        self.network.erase_network()
                