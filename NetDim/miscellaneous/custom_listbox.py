# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk

def overrides(interface_class):
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider    
    
class ObjectListbox(tk.Listbox):
    
    def __contains__(self, obj):
        return obj in self.get(0, "end")
        
    def yield_all(self):
        for obj in self.get(0, "end"):
            yield obj
        
    def selected(self):
        for selected_line in self.curselection():
            yield self.get(selected_line)
        
    def pop(self, obj):
        if str(obj) in self:
            obj_index = self.get(0, tk.END).index(str(obj))
            self.delete(obj_index)
            return obj
        
    def pop_selected(self):
        # the tricky part here is that indexes stored in curselection are 
        # retrieved once and for all, and as we remove objects from the listbox, 
        # the real index is updated, and we have to decrease the curselection
        # index by how many objects we've deleted so far.
        for idx, obj in enumerate(self.curselection()):
            yield self.pop(self.get(obj - idx))
        
    def clear(self):
        self.delete(0, tk.END)
        
    @overrides(tk.Listbox)
    def insert(self, obj):
        if str(obj) not in self:
            super(ObjectListbox, self).insert(tk.END, obj)