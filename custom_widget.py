import tkinter as tk

def overrides(interface_class):
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider
    
class ObjectListbox(tk.Listbox):
    
    def __contains__(self, obj):
        return obj in self.get(0, "end")
        
    def selected(self):
        return self.get(self.curselection())
        
    def pop(self, obj):
        if str(obj) in self:
            obj_index = self.get(0, tk.END).index(str(obj))
            self.delete(obj_index)
            return obj
        
    def pop_selected(self):
        selection = self.get(self.curselection())
        self.pop(selection)
        
    @overrides(tk.Listbox)
    def insert(self, obj):
        if str(obj) not in self:
            super(ObjectListbox, self).insert(tk.END, obj)