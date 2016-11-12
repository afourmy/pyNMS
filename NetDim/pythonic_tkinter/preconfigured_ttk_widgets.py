# Pythonic Tkinter
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

## Preconfigured widgets
# the grid method is overwritten to create pre-padded (with preinitialized 
#  padx, pady) widgets.
# 'x' / 'y' parameters are used instead of the classic ttk row / column
# arguments, and 'xs' / 'ys' replace rowspan and columnspan.
# sticky is initialized to its most common value: west (~ left)

import tkinter as tk
from tkinter import ttk
from .custom_listbox import ObjectListbox
            
def overrides(interface_class):
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider
        
class MainWindow(tk.Tk):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        color = "#A1DBCD"
        for widget in (
                       'Button', 
                       'Label', 
                       'Labelframe', 
                       'Labelframe.Label', 
                       'Checkbutton'
                       ):
            ttk.Style().configure('T' + widget, background=color)
            
class Menu(tk.Menu):
    
    def __init__(self, *args, **kwargs):
        if 'tearoff' not in kwargs:
            kwargs['tearoff'] = 0
        super().__init__(*args, **kwargs)
        
    def entry(self, text, cmd):
        self.add('command', {'label':text, 'command':cmd})        

class LF(ttk.LabelFrame):
    
    def __init__(self, *args, **kwargs):
        if 'padding' not in kwargs:
            kwargs['padding'] = (6, 6, 12, 12)

        super().__init__(*args, **kwargs)
    
def class_factory(name, OriginalWidget, defaults):
    
    px, py, sy = defaults
        
    @overrides(OriginalWidget)
    def grid(self, x, y, xs=1, ys=1, padx=px, pady=py, sticky=sy, cnf={}, **kw):
        # x (resp. y) is the row (resp. column) number
        # xs and ys stands for xspan / yspan (~ rowspan / columnspan)
        kw.update({
                   'padx': padx, 
                   'pady': pady,
                   'row': x,
                   'rowspan': xs,
                   'column': y,              
                   'columnspan': ys,
                   'sticky': sticky
                   })
        
        self.tk.call(('grid', 'configure', self._w) + self._options(cnf, kw))
              
    @property
    def text(self):
        return self.get()
        
    @text.setter
    def text(self, value):
        self.configure(text=value)
        
    widget_functions = {'grid': grid, 'text': text}
        
    if name in ('Button', 'Checkbutton'):
        @property
        def command(self):
            self.cget('command')
            
        @command.setter
        def command(self, value):
            self.configure(command=value)
            
        widget_functions.update({'command': command})
            
    newclass = type(name, (OriginalWidget,), widget_functions)
    globals()[name] = newclass
    
subwidget_creation = (
                      ('Label', ttk.Label, (4, 4, 'w')), 
                      ('Entry', ttk.Entry, (4, 4, 'w')), 
                      ('Button', ttk.Button, (4, 4, 'w')),
                      ('Labelframe', LF, (10, 10, 'w')),
                      ('Listbox', ObjectListbox, (0, 0, 'w')),
                      ('Scrollbar', tk.Scrollbar, (0, 0, 'ns')),
                      ('Combobox', ttk.Combobox, (4, 4, 'w')),
                      ('Checkbutton', ttk.Checkbutton, (4, 4, 'w'))
                      )
    
for subwidget, ttk_class, defaults in subwidget_creation:
    class_factory(subwidget, ttk_class, defaults)