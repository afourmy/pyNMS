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

import tkinter as tk
from os.path import join
from objects.objects import *
from tkinter import ttk
from PIL import ImageTk
from pythonic_tkinter.preconfigured_widgets import *
from collections import OrderedDict
from miscellaneous.decorators import update_paths

class RoutingMenu(ScrolledFrame):
    
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
        
        # label frame for object creation
        lf_refresh = Labelframe(self.infr)
        lf_refresh.text = 'Refresh actions'
        lf_refresh.grid(0, 0, sticky='nsew')
        
        img_path = join(self.controller.path_icon, 'refresh.png')
        img_pil = ImageTk.Image.open(img_path).resize((128, 128))
        self.img_refresh = ImageTk.PhotoImage(img_pil)
        
        button_routing = TKButton(self.infr)
        button_routing.command = self.refresh
        button_routing.config(image=self.img_refresh, relief='flat')
        button_routing.config(width=150, height=150)
        button_routing.grid(0, 0, sticky='ew', in_=lf_refresh)
        
        select_all_button = Button(self)
        select_all_button.text = 'Select / Unselect all'
        select_all_button.command = self.selection
        select_all_button.grid(1, 0, sticky='ew', in_=lf_refresh)
        
        self.actions = (
                        'Update AS topology',
                        'Creation of all virtual connections',
                        'Names / addresses interface allocation',
                        'Creation of all ARP / MAC tables',
                        'Creation of all routing tables',
                        'Creation of all BGP tables',
                        'Route redistribution',
                        'Path finding procedure (traffic flows)',
                        'Redraw the graph',
                        'Refresh the display (including labels)'
                        )
        
        self.action_booleans = []
        for id, action in enumerate(self.actions, 3):
            action_bool = tk.BooleanVar()
            action_bool.set('interface' not in action)
            self.action_booleans.append(action_bool)
            button = Checkbutton(self.infr, variable=action_bool)
            button.text = action
            button.grid(id, 0, in_=lf_refresh)
            
    @update_paths
    def refresh(self):
        self.project.refresh()
        
    def selection(self):
        values = list(map(lambda a: a.get(), self.action_booleans))
        select_all = len(set(values)) > 1 or True not in values
        for action_bool in self.action_booleans:
            action_bool.set(select_all)

        