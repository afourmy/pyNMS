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

class DrawingMenu(ScrolledFrame):
    
    def __init__(self, notebook, master):
        super().__init__(notebook, width=200, height=600, borderwidth=1, relief='solid')
        self.ms = master
        font = ('Helvetica', 8, 'bold')

        # label frame for multi-layer display
        lf_fb_drawing = Labelframe(self.infr)
        lf_fb_drawing.text = 'Force-based drawing parameters'
        lf_fb_drawing.grid(0, 0, sticky='nsew')
                
        # label frame to manage sites
        lf_shapes_drawing = Labelframe(self.infr)
        lf_shapes_drawing.text = 'Shapes and text drawing'
        lf_shapes_drawing.grid(1, 0, sticky='nsew')
        
        self.dict_image = {}
        
        self.dict_size_image = {
        'draw': self.draw,
        'stop': lambda: 42,
        'text': lambda: self.change_creation_mode('text'),
        'rectangle': lambda: self.change_creation_mode('rectangle'),
        'oval': lambda: self.change_creation_mode('oval'),
        'color': self.get_color
        }
        
        for image_type, image_size in self.dict_size_image.items():
            img_path = join(self.ms.path_icon, image_type + '.png')
            if image_type == 'draw':
                img_pil = ImageTk.Image.open(img_path).resize((150, 150))
            else:
                img_pil = ImageTk.Image.open(img_path).resize((55, 55))
            img = ImageTk.PhotoImage(img_pil)
            self.dict_image[image_type] = img
        
        self.type_to_button = {}
        
        for obj_type, command in self.dict_size_image.items():
            button = TKButton(self.infr, command=command)
            button.config(image=self.dict_image[obj_type])
            if obj_type == 'draw':
                button.config(width=150, height=150)
                button.configure(relief=tk.RAISED)
            else:
                button.config(width=75, height=75)
            self.type_to_button[obj_type] = button
        
        # drawing algorithm and parameters: per project
        self.drawing_algorithm = 'Spring-based layout'

        self.drawing_params = OrderedDict([
        ('Coulomb factor', 10000),
        ('Spring stiffness', 0.5),
        ('Speed factor', 0.35),
        ('Equilibrium length', 8.),
        # ('Optimal pairwise distance', 0.)
        ])
        
        self.stay_withing_screen_bounds = False
        
        self.type_to_button['draw'].grid(0, 0, 2, 2, padx=100, in_=lf_fb_drawing)
        
        sep = Separator(self.infr)
        sep.grid(2, 0, 1, 2, in_=lf_fb_drawing)
        
        # combobox for the user to change the drawing algorithm
        self.drawing_type_list = Combobox(self.infr, width=30)
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
            label = Label(self.infr, text=param)
            entry = Entry(self.infr, width=12)
            entry.text = value
            self.entries.append(entry)
            label.grid(index, 0, in_=lf_fb_drawing)
            entry.grid(index, 1, in_=lf_fb_drawing)
            
        # check button to randomly distribute the selected nodes on the canvas 
        # before starting the actual force-based algorithm
        self.random_distribution = tk.BooleanVar()
        button_distribute = Checkbutton(self.infr, variable=self.random_distribution)
        button_distribute.text = 'Randomly distribution first'
        self.random_distribution.set(True)
        
        button_distribute.grid(9, 0, 1, 2, in_=lf_fb_drawing)
                                        
        # check button for nodes to stay within the screen bounds
        self.stay_withing_screen_bounds = tk.BooleanVar()
        button_limit = Checkbutton(self.infr, variable=self.stay_withing_screen_bounds)
        button_limit.text = 'Screen limit'
        self.stay_withing_screen_bounds.set(False)
        
        button_limit.grid(10, 0, 1, 2, in_=lf_fb_drawing)
        
        # check button to create virtual links between the virtual nodes, for
        # the BFS-clusterization drawing algorithm
        self.virtual_links = tk.BooleanVar()
        button_vlinks = Checkbutton(self.infr, variable=self.virtual_links)
        button_vlinks.text = 'Create virtual links between virtual nodes'
        self.virtual_links.set(True)
        
        button_vlinks.grid(11, 0, 1, 2, in_=lf_fb_drawing)
        
        # shapes and text drawing
        self.type_to_button['text'].grid(0, 0, in_=lf_shapes_drawing)
        self.type_to_button['rectangle'].grid(0, 1, in_=lf_shapes_drawing)
        self.type_to_button['oval'].grid(0, 2, in_=lf_shapes_drawing)
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
            self.ms.cs.draw_objects(nodes, self.random_distribution.get())            
            self.drawing_algorithms[self.drawing_type_list.text](nodes)
            
    def get_color(self):
        color = askcolor()
        print(color)
        
    def random(self, nodes):
        self.ms.cs.draw_objects(nodes)
        self.ms.cs.move_nodes(nodes)
        
    def change_creation_mode(self, mode):
        # change the mode to creation 
        self.ms.cs._mode = mode
        self.ms.cs._creation_mode = mode
        self.ms.cs.switch_binding()
        # update the button display
        for shape in ('text', 'rectangle', 'oval'):
            if shape == mode:
                self.type_to_button[shape].configure(relief='sunken')
            else:
                self.type_to_button[shape].configure(relief='raised')
                

        