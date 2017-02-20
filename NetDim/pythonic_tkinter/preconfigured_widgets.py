# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
            
def overrider(interface_class):
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider
    
# decorating __init__ to initialize properties
def defaultizer(**default_kwargs_values):
    def inner_decorator(init):
        def wrapper(self, *args, **kwargs):
            for property, default_value in default_kwargs_values.items():
                if property not in kwargs:
                    kwargs[property] = default_value
            init(self, *args, **kwargs)
        return wrapper
    return inner_decorator
    
class Canvas(tk.Canvas):
    
    @defaultizer(background='white', width=1000, height=800)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class CustomFrame(tk.Frame):
    
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        color = '#A1DBCD'
        self.configure(background=color)    
        
class CustomScrolledText(ScrolledText):
    
    def __init__(self, parent_frame):
        super().__init__(parent_frame, wrap='word', bg='beige')
        default_font = ('Helvetica', '12', 'bold underline')
        self.tag_config('title', foreground='blue', font=default_font)    
        
class CustomTopLevel(tk.Toplevel):
    
    def __init__(self):
        super().__init__()
        color = '#A1DBCD'
        self.configure(background=color)
        
class FocusTopLevel(CustomTopLevel):
    
    def __init__(self):
        super().__init__()
        self.var_focus = tk.IntVar()
        checkbutton_focus = Checkbutton(self, variable=self.var_focus)
        checkbutton_focus.text = 'Focus'
        checkbutton_focus.command = self.change_focus                                
        checkbutton_focus.grid(0, 0)
            
    def change_focus(self):
        self.wm_attributes('-topmost', self.var_focus.get())

class ImprovedListbox(tk.Listbox):
    
    @defaultizer(activestyle='none', selectmode='extended')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind('<Button-1>', self.set_index)
        self.bind('<B1-Motion>', self.move_selected_row)
        self.cur_index = None
    
    def __contains__(self, obj):
        return obj in self.get(0, 'end')
        
    def insert(self, obj, i='end'):
        super(ImprovedListbox, self).insert(i, obj)
        
    def yield_all(self):
        for obj in self.get(0, 'end'):
            yield obj
        
    def selected(self):
        for selected_line in self.curselection():
            yield self.get(selected_line)
        
    def pop(self, obj):
        if str(obj) in self:
            obj_index = self.get(0, 'end').index(str(obj))
            self.delete(obj_index)
            return obj
        
    def pop_selected(self):
        # indexes stored in curselection are retrieved once and for all,
        # and as we remove objects from the listbox, the real index is updated:
        # we have to decrease the curselection index by how many objects
        # we've deleted so far.
        for idx, obj in enumerate(self.curselection()):
            yield self.pop(self.get(obj - idx))
        
    def clear(self):
        self.delete(0, 'end')
        
    def set_index(self, event):
        self.cur_index = self.nearest(event.y)
        
    def move_selected_row(self, event):
        row_id = self.nearest(event.y)
        value = self.get(row_id)
        if row_id != self.cur_index:
            self.delete(row_id)
            self.insert(value, row_id + 1 - 2*(row_id > self.cur_index))
            self.cur_index = row_id
            
class ImprovedTKButton(tk.Button):
    
    @defaultizer(bg='#A1DBCD')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
class LF(ttk.LabelFrame):
    
    @defaultizer(padding=(6, 6, 12, 12))
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
class MainWindow(tk.Tk):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        color = '#A1DBCD'
        for widget in (
                       'Button',
                       'Radiobutton',
                       'Label', 
                       'Labelframe', 
                       'Labelframe.Label', 
                       'Checkbutton'
                       ):
            ttk.Style().configure('T' + widget, background=color)
        ttk.Style().configure('Treeview', rowheight=25)
            
class Menu(tk.Menu):
    
    @defaultizer(tearoff=0)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.menu_entries = []
        
    def separator(self):
        self.menu_entries.append('separator')
        
    def create_menu(self):
        for entry in self.menu_entries:
            if entry == 'separator':
                self.add_separator()
            else:
                self.add('command', {'label': entry.label, 'command': entry.cmd})  
            
class MenuEntry(object):
    
    
    def __init__(self, menu):
        menu.menu_entries.append(self)
        self.label = 'Menu text'
        self.cmd = lambda: None
        
    @property
    def text(self):
        return self.label
        
    @text.setter
    def text(self, value):
        self.label = value
        
    @property
    def command(self):
        return self.command
        
    @command.setter
    def command(self, cmd):
        self.cmd = cmd
            
class NoDuplicateListbox(ImprovedListbox):
    
    @overrider(ImprovedListbox)
    def insert(self, obj, i='end'):
        if str(obj) not in self:
            super(NoDuplicateListbox, self).insert(obj, i)
        
class Notebook(ttk.Notebook):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
class ImprovedTreeView(ttk.Treeview):
    
    @defaultizer(selectmode='extended')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
class VerticalScrolledFrame(CustomFrame):
    
    def __init__(self, parent, *args, **kw):
        CustomFrame.__init__(self, parent, *args, **kw)            

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = Scrollbar(self)
        vscrollbar.pack(fill='y', side='right', expand=0)
        canvas = tk.Canvas(
                           self, 
                           bd = 0, 
                           highlightthickness = 0,
                           yscrollcommand = vscrollbar.set, 
                           background = '#A1DBCD'
                           )
        canvas.pack(side='left', fill='both', expand=1)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # inner frame
        self.infr = CustomFrame(canvas)
        self.infr_id = canvas.create_window(0, 0, window=self.infr, anchor='nw')

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def configure_infr(event):
            # update the scrollbars to match the size of the inner frame
            size = (self.infr.winfo_reqwidth(), self.infr.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if self.infr.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=self.infr.winfo_reqwidth())
        self.infr.bind('<Configure>', configure_infr)

        def _configure_canvas(event):
            if self.infr.winfo_reqwidth() != canvas.winfo_width():
                # fill the canvas with the inner frame
                canvas.itemconfigure(self.infr_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)
    
def class_factory(name, OriginalWidget, defaults):
    
    px, py, sy = defaults
        
    @overrider(OriginalWidget)
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
        
    if name == 'Entry':
        
        @text.setter
        def text(self, value):
            self.delete(0, 'end')
            self.insert(0, value)
            
    elif name =='Text':
        
        @text.setter
        def text(self, value):
            self.delete('1.0', 'end')
            self.insert('1.0', value)
            
    elif name =='Combobox':
        
        @text.setter
        def text(self, value):
            self.set(str(value))
            
    else:
        
        @text.setter
        def text(self, value):
            self.configure(text=value)
        
    widget_functions = {'grid': grid, 'text': text}
        
    if name in ('Button', 'TKButton', 'Checkbutton', 'Scrollbar', 'Radiobutton'):
        
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
                      ('Text', tk.Text, (4, 4, 'w')),
                      ('Entry', ttk.Entry, (4, 4, 'w')),
                      ('Button', ttk.Button, (4, 4, 'w')),
                      ('Treeview', ImprovedTreeView, (4, 4, 'w')),
                      # ttk buttons do not have a relief option:
                      # tk buttons can therefore be useful too
                      ('TKButton', ImprovedTKButton, (4, 4, 'w')),
                      ('Radiobutton', ttk.Radiobutton, (4, 4, 'w')),
                      ('Labelframe', LF, (10, 10, 'w')),
                      ('Listbox', ImprovedListbox, (0, 0, 'w')),
                      ('ObjectListbox', NoDuplicateListbox, (0, 0, 'w')),
                      ('Scrollbar', tk.Scrollbar, (0, 0, 'ns')),
                      ('Combobox', ttk.Combobox, (4, 4, 'w')),
                      ('Checkbutton', ttk.Checkbutton, (4, 4, 'w')),
                      ('Separator', ttk.Separator, (4, 4, 'ew')),
                      ('ScrolledFrame', VerticalScrolledFrame, (4, 4, 'w')),
                      ('AScrolledText', CustomScrolledText, (4, 4, 'w'))
                      )
    
for subwidget, ttk_class, defaults in subwidget_creation:
    print(subwidget)
    class_factory(subwidget, ttk_class, defaults)