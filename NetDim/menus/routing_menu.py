# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk
from os.path import join
from objects.objects import *
from tkinter import ttk
from pythonic_tkinter.preconfigured_widgets import *
from collections import OrderedDict

class RoutingMenu(ScrolledFrame):
    
    def __init__(self, notebook, master):
        super().__init__(notebook, width=200, height=600, borderwidth=1, relief='solid')
        self.ms = master
        self.ntw = self.ms.cs.ntw
        font = ('Helvetica', 8, 'bold')
        
        # label frame for object selection
        lf_allocation = Labelframe(self.infr)
        lf_allocation.text = 'Automatic allocation'
        lf_allocation.grid(0, 0, sticky='nsew')
        
        button_ip_allocation = Button(self)
        button_ip_allocation.text = 'IP address'
        button_ip_allocation.command = self.ntw.ip_allocation
        
        button_mac_allocation = Button(self)
        button_mac_allocation.text = 'MAC address'
        button_mac_allocation.command = self.ntw.mac_allocation
        
        button_if_allocation = Button(self)
        button_if_allocation.text = 'Interface name'
        button_if_allocation.command = self.ntw.interface_allocation
        
        button_ip_allocation.grid(0, 0, in_=lf_allocation)
        button_mac_allocation.grid(1, 0, in_=lf_allocation)
        button_if_allocation.grid(2, 0, in_=lf_allocation)
        
        # label frame for object creation
        lf_refresh = Labelframe(self.infr)
        lf_refresh.text = 'Refresh actions'
        lf_refresh.grid(1, 0, sticky='nsew')
        
        refresh_actions = OrderedDict([
        ('Update AS topology', self.ntw.update_AS_topology),
        ('VC creation', self.ntw.vc_creation),
        ('Switching tables creation', self.ntw.switching_table_creation),
        ('Routing tables creation', self.ntw.routing_table_creation),
        ('Path finding procedure', self.ntw.path_finder),
        ])
        
        self.action_booleans = []
        for id, (action, cmd) in enumerate(refresh_actions.items()):
            action_bool = tk.BooleanVar()
            action_bool.set(True)
            self.action_booleans.append(action_bool)
            self.button_limit = Checkbutton(self.infr, variable=action_bool)
            self.button_limit.text = action
            self.button_limit.command = cmd
            self.button_limit.grid(id, 0, in_=lf_refresh)
        
class Computation(CustomTopLevel):
            
    def __init__(self, master):
        super().__init__()
        self.ms = master

        self.functions = OrderedDict([
        ('Update AS topology', self.ms.cs.ntw.update_AS_topology),
        ('Interface allocation', self.ms.cs.ntw.interface_allocation),
        ('IP addressing', self.ms.cs.ntw.ip_allocation),
        ('Create routing tables', self.ms.cs.ntw.rt_creation),
        ('Route traffic links', self.ms.cs.ntw.path_finder),
        ('Refresh labels', self.ms.cs.refresh_all_labels)
        ])
        
        self.lb_functions = ObjectListbox(self, activestyle='none', width=15, 
                                            height=7, selectmode='extended')
                                            
        for function in self.functions:
            self.lb_functions.insert(function) 
            
        # button to confirm selection and trigger functions
        self.OK_button = ttk.Button(self, text='OK', command=self.OK)
                                
        self.lb_functions.pack(fill=tk.BOTH, expand=1)
        self.OK_button.pack()
        
    def OK(self):
        for function in self.lb_functions.selected():
            print(function)
            self.functions[function]()
        self.destroy()