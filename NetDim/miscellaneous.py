# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk
from tkinter import ttk

def overrides(interface_class):
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider    
    
class ObjectListbox(tk.Listbox):
    
    def __contains__(self, obj):
        return obj in self.get(0, "end")
        
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
            
class CustomTopLevel(tk.Toplevel):
    
    def __init__(self):
        super().__init__()
        self.configure(background="#A1DBCD")        
        ttk.Style().configure("TButton", background="#A1DBCD")
        ttk.Style().configure("TLabel", background="#A1DBCD")
        ttk.Style().configure("Treeview", background="#A1DBCD", 
                                                            foreground="black")
        ttk.Style().configure('TLabelframe', background="#A1DBCD")
        ttk.Style().configure('TLabelframe.Label', background="#A1DBCD")
        ttk.Style().configure('TCheckbutton', background="#A1DBCD")
        
class FocusTopLevel(CustomTopLevel):
    def __init__(self):
        super().__init__()
        
        self.var_focus = tk.IntVar()
        self.checkbutton_focus = tk.Checkbutton(self, text="Focus", 
            bg="#A1DBCD", variable=self.var_focus, command=self.change_focus)
        self.checkbutton_focus.grid(row=0, column=0, sticky=tk.W)
            
    def change_focus(self):
        self.wm_attributes("-topmost", self.var_focus.get())
        
class UnionFind:
    
    def __init__(self, nodes):
        self.up = {node: node for node in nodes}
        self.rank = {node: 0 for node in nodes}
        
    def find(self, node):
        if self.up[node] == node:
            return node
        else:
            self.up[node] = self.find(self.up[node])
            return self.up[node]
            
    def union(self, nA, nB):
        repr_nA = self.find(nA)
        repr_nB = self.find(nB)
        if repr_nA == repr_nB:
            return False
        if self.rank[repr_nA] >= self.rank[repr_nB]:
            self.up[repr_nB] = repr_nA
            if self.rank[repr_nA] == self.rank[repr_nB]:
                self.rank[repr_nA] += 1   
        else:
            self.up[repr_nA] == repr_nB
        return True
