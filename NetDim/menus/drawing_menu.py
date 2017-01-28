# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk
from os.path import join
from objects.objects import *
from tkinter import ttk
from PIL import ImageTk
from tkinter.colorchooser import askcolor
from pythonic_tkinter.preconfigured_widgets import *
from collections import OrderedDict
from graph_generation.network_dimension import NetworkDimension
from drawing import drawing_options_window

class DrawingMenu(CustomFrame):
    
    def __init__(self, notebook, master):
        super().__init__(width=200, height=600, borderwidth=1, relief='solid')
        self.ms = master
        font = ('Helvetica', 8, 'bold')
        
        # label frame for multi-layer display
        lf_fb_drawing = Labelframe(self)
        lf_fb_drawing.text = 'Force-based drawing parameters'
        lf_fb_drawing.grid(0, 0, sticky='nsew')
                
        # label frame to manage sites
        lf_shapes_drawing = Labelframe(self)
        lf_shapes_drawing.text = 'Shapes and text drawing'
        lf_shapes_drawing.grid(1, 0, sticky='nsew')
        
        self.dict_image = {}
        
        self.dict_size_image = {
        'draw': self.draw,
        'text': lambda: self.change_creation_mode('text'),
        'rectangle': lambda: self.change_creation_mode('rectangle'),
        'circle': lambda: 43,
        'color': self.get_color
        }
        
        for image_type, image_size in self.dict_size_image.items():
            img_path = join(self.ms.path_icon, image_type + '.png')
            if image_type == 'draw':
                img_pil = ImageTk.Image.open(img_path).resize((150, 150))
            else:
                img_pil = ImageTk.Image.open(img_path).resize((75, 75))
            img = ImageTk.PhotoImage(img_pil)
            self.dict_image[image_type] = img
        
        self.type_to_button = {}
        
        for obj_type, command in self.dict_size_image.items():
            button = TKButton(self, relief=tk.SUNKEN, command=command)
            button.config(image=self.dict_image[obj_type])
            if obj_type == 'draw':
                button.config(width=150, height=150)
            else:
                button.config(width=65, height=65)
                button.configure(text=obj_type, compound='top', font=font)
            self.type_to_button[obj_type] = button
        
        # drawing algorithm and parameters: per project
        self.drawing_algorithm = 'Spring-based layout'

        self.drawing_params = OrderedDict([
        ('Coulomb factor', 10000),
        ('Spring stiffness', 0.5),
        ('Speed factor', 0.35),
        ('Equilibrium length', 8.),
        ('Optimal pairwise distance', 0.)
        ])
        
        self.stay_withing_screen_bounds = False
        
        self.type_to_button['draw'].grid(0, 0, 2, 2, sticky='ew', in_=lf_fb_drawing)
        
        sep = Separator(self)
        sep.grid(2, 0, 1, 2, in_=lf_fb_drawing)
        
        # combobox for the user to change the drawing algorithm
        self.drawing_type_list = Combobox(self, width=30)
        self.drawing_type_list['values'] = (
                                        'Spring-based layout', 
                                        'Fructhermann-Reingold layout',
                                        'BFS-clusterization layout',
                                        'Random'
                                        )
        self.drawing_type_list.set(self.drawing_algorithm)
        self.drawing_type_list.grid(3, 0, 1, 2, in_=lf_fb_drawing)
        
        self.drawing_algorithms = {
        'Spring-based layout': self.ms.cs.spring_based_drawing,
        'Fructhermann-Reingold layout': self.ms.cs.FR_drawing,
        'BFS-clusterization layout': self.ms.cs.bfs_cluster_drawing,
        'Random': self.random
        }
        
        # list of all entries
        self.entries = []
        # parameters labels and entries
        for index, (param, value) in enumerate(self.drawing_params.items(), 4):
            label = Label(self, text=param)
            entry = Entry(self, width=12)
            entry.text = value
            self.entries.append(entry)
            label.grid(index, 0, in_=lf_fb_drawing)
            entry.grid(index, 1, in_=lf_fb_drawing)
                                        
        # check button for nodes to stay in the screen 
        self.stay_withing_screen_bounds = tk.BooleanVar()
        self.button_limit = Checkbutton(self, text='Screen limit', 
                                                        variable=self.stay_withing_screen_bounds)
        self.stay_withing_screen_bounds.set(False)
        
        self.button_limit.grid(9, 0, 1, 2, in_=lf_fb_drawing)
        
        # shapes and text drawing
        self.type_to_button['text'].grid(0, 0, in_=lf_shapes_drawing)
        self.type_to_button['rectangle'].grid(0, 1, in_=lf_shapes_drawing)
        self.type_to_button['circle'].grid(0, 2, in_=lf_shapes_drawing)
        self.type_to_button['color'].grid(0, 3, in_=lf_shapes_drawing)
        
    def draw(self):
        # apply the algorithm to all selected nodes, or all nodes in the
        # network if nothing is selected
        nodes = self.ms.cs.so['node'] or self.ms.cs.ntw.pn['node'].values()
        if self.drawing_algorithm == 'Random':
            self.ms.cs.draw_objects(nodes)
            self.ms.cs.move_nodes(nodes)
        else:
            # replace true with a BooleanVar randomly spread nodes on the canvas beforehand
            self.ms.cs.draw_objects(nodes, True)            
            self.drawing_algorithms[self.drawing_type_list.text](nodes)
            
    def get_color(self):
        color = askcolor()
        print(color)
        
    def random(self, nodes):
        self.ms.cs.draw_objects(nodes)
        self.ms.cs.move_nodes(nodes)
        
    def change_creation_mode(self, mode):
        # change the mode to creation 
        self.switch_to('creation')
        self.ms.cs._creation_mode = mode
        for obj_type in self.type_to_button:
            if mode == obj_type:
                self.type_to_button[obj_type].config(relief=tk.SUNKEN)
            else:
                self.type_to_button[obj_type].config(relief=tk.FLAT)
        self.ms.cs.switch_binding()

        