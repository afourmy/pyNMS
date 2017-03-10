# NetDim
# Copyright (C) 2017 Antoine Fourmy (contact@netdim.fr)
# Released under the GNU General Public License GPLv3

import tkinter as tk
from os.path import join
from objects.objects import *
from tkinter import ttk
from PIL import ImageTk
from pythonic_tkinter.preconfigured_widgets import *
from collections import OrderedDict
from graph_generation.network_dimension import NetworkDimension

class ViewMenu(ScrolledFrame):
    
    def __init__(self, notebook, master):
        super().__init__(notebook, width=200, height=600, borderwidth=1, relief='solid')
        self.ms = master
        font = ('Helvetica', 8, 'bold')
        
        # label frame to manage sites
        lf_site_display = Labelframe(self.infr)
        lf_site_display.text = 'Viewing mode'
        lf_site_display.grid(1, 0, sticky='nsew')
        
        self.dict_image = {}
        
        self.dict_size_image = {
        'network_view': (125, 125),
        'site': (125, 125),
        }
        
        for image_type, image_size in self.dict_size_image.items():
            x, y = image_size
            img_path = join(self.ms.path_icon, image_type + '.png')
            img_pil = ImageTk.Image.open(img_path).resize(image_size)
            img = ImageTk.PhotoImage(img_pil)
            self.dict_image[image_type] = img
        
        self.type_to_button = {}
                
        # site view
        self.network_view_button = TKButton(self.infr)
        self.network_view_button.config(image=self.dict_image['network_view'])
        self.network_view_button.command = lambda: self.switch_view('network')
        self.network_view_button.config(width=150, height=150, relief='sunken')
        self.network_view_button.grid(0, 0, 2, 2, padx=20, in_=lf_site_display)
        
        self.site_view_button = TKButton(self.infr)
        self.site_view_button.config(image=self.dict_image['site'])
        self.site_view_button.command = lambda: self.switch_view('site')
        self.site_view_button.config(width=150, height=150)
        self.site_view_button.grid(0, 2, 2, 2, padx=20, in_=lf_site_display)
        
    def switch_view(self, view):
        self.ms.cs.viewing_mode = view        
        # delete eveyrthing on the canvas
        self.ms.cs.erase_all()
        self.ms.cs.cvs.delete('all')
        if view == 'site':
            self.site_view_button.config(relief='sunken')
            self.network_view_button.config(relief='raised')
            # draw the sites
            self.ms.cs.draw_objects(
                                    self.ms.cs.ntw.ftr('node', 'site'), 
                                    random_drawing = False, 
                                    draw_site = True
                                    )
        else:
            # view is network: we draw all network objects
            self.site_view_button.config(relief='raised')
            self.network_view_button.config(relief='sunken')
            # switch back to motion
            self.ms.cs._mode = 'motion'
            self.ms.cs.switch_binding()
            self.ms.cs.draw_all(False)
            
    def enter_site(self, site):
        self.ms.cs.erase_all()
        self.ms.cs.cvs.delete('all')
        self.ms.cs.draw_objects(self.ms.cs.ntw.nodes[site.id].get_obj())
                    