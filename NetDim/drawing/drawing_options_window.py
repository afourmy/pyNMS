# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk
from tkinter import ttk
from miscellaneous.custom_toplevel import FocusTopLevel, CustomTopLevel
import collections

class DrawingOptions(FocusTopLevel):
    
    def __init__(self, master):
        
        self.ms = master
        super().__init__()
        
        self.title('Graph drawing with force-directed algorithms')
        # contains all labels and associated entries
        self.widgets = {'Spring layout': [], 'F-R layout': []}
        # contains all variables
        self.vars = {'Spring layout': [], 'F-R layout': []}
    
        # label frame for the spring layout parameters
        self.lf_spring = ttk.Labelframe(self, padding=(6, 6, 12, 12), 
                                                        text='Spring layout')
        self.lf_spring.grid(column=0, columnspan=2, pady=5, padx=5, 
                                                        row=1, sticky='nsew')
                                                        
        # label frame for the Fruchterman-Reingold layout parameters
        self.lf_fr = ttk.Labelframe(self, padding=(6, 6, 12, 12), 
                                                        text='F-R layout')
        self.lf_fr.grid(column=2, columnspan=2, pady=5, padx=5, 
                                                        row=1, sticky='nsew')
        
        # combobox for the user to change the drawing algorithm
        self.var_drawing_type = tk.StringVar()
        self.drawing_type_list = ttk.Combobox(self, 
                                textvariable=self.var_drawing_type, width=11)
        self.drawing_type_list['values'] = (
                                            'Spring layout', 
                                            'F-R layout',
                                            'BFS-cluster layout'
                                            )
        self.drawing_type_list.set(self.ms.drawing_algorithm)
        self.drawing_type_list.grid(row=0, column=2, pady=5, padx=5, sticky=tk.W)
        
        # parameters labels and entries
        for param, value in self.ms.drawing_params['Spring layout'].items():
            var = tk.DoubleVar()
            label = ttk.Label(self, text=param)
            var.set(value)
            entry = tk.Entry(self, textvariable=var, width=6)
            self.widgets['Spring layout'].append((label, entry))
            self.vars['Spring layout'].append(var)
            
        for id, (lbl, etr) in enumerate(self.widgets['Spring layout']):
            lbl.grid(in_=self.lf_spring, row=id, column=0, pady=5, padx=5, sticky=tk.W)
            etr.grid(in_=self.lf_spring, row=id, column=1, sticky=tk.W)

        
        # optimal pairwise distance for fruchterman-reingold
        self.label_opd = ttk.Label(self, text = 'OPD')
        self.var_opd = tk.DoubleVar()
        self.var_opd.set(self.ms.drawing_params['F-R layout']['OPD'])
        self.entry_opd = tk.Entry(self, textvariable=self.var_opd, width=6)
        self.vars['F-R layout'].append(self.var_opd)
                                        
        # check button for nodes to stay in the screen 
        self.var_limit = tk.BooleanVar()
        self.button_limit = ttk.Checkbutton(self, text='Screen limit', 
                                                        variable=self.var_limit)
        self.var_limit.set(bool(self.ms.drawing_params['F-R layout']['limit']))
        self.vars['F-R layout'].append(self.var_limit)
        
        self.button_save = ttk.Button(self, text='Save', 
                                        command=lambda: self.save())
        
        # affichage des boutons / label dans la grille
        self.label_opd.grid(in_=self.lf_fr, row=0, column=0, pady=5, padx=5, sticky=tk.W)
        self.entry_opd.grid(in_=self.lf_fr, row=0, column=1, sticky=tk.W)
        self.button_limit.grid(in_=self.lf_fr, row=1, column=0, sticky=tk.W)
        self.button_save.grid(row=6, column=0, pady=5, padx=5, sticky=tk.W)
    
    def save(self):
        # retrieve variables values
        self.ms.drawing_algorithm = self.var_drawing_type.get()
        for alg in ('Spring layout', 'F-R layout'):
            keys = list(self.ms.drawing_params[alg].keys())
            vars = (v.get() for v in self.vars[alg])
            param = list(zip(keys, vars))
            self.ms.drawing_params[alg] = collections.OrderedDict(param)

