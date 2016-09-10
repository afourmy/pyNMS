# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

from miscellaneous.custom_toplevel import CustomTopLevel
from tkinter import ttk

class Area(object):
    
    class_type = "area"
    
    def __init__(self, name, id, AS, trunks, nodes):
        self.name = name
        self.id = int(id)
        self.AS = AS
        # it is important to write set(nodes) and not just nodes so that
        # both set are distinct in memory, and when we remove a node
        # (or trunk) from an area, it is not removed from the AS as well.
        self.pa = {"node": set(nodes), "trunk": set(trunks)}
        # update the AS dict for all objects, so that they are aware they
        # belong to this new area
        for obj in nodes | trunks:
            obj.AS[self.AS].add(self)
        # update the area dict of the AS with the new area
        self.AS.areas[name] = self
        # add the area to the AS management panel area listbox
        self.AS.management.create_area(name, id)
        
    def __repr__(self):
        return self.name
        
    def add_to_area(self, *objects):
        for obj in objects:
            self.pa[obj.type].add(obj)
            obj.AS[self.AS].add(self)
            
    def remove_from_area(self, *objects):
        for obj in objects:
            self.pa[obj.type].discard(obj)
            obj.AS[self.AS].discard(self)
            
class CreateArea(CustomTopLevel):
    def __init__(self, asm):
        super().__init__()      
        self.title("Create area")   
        
        self.label_name = ttk.Label(self, text="Area name")
        self.label_id = ttk.Label(self, text="Area id")
        self.entry_name = ttk.Entry(self, width=9)
        self.entry_id = ttk.Entry(self, width=9)
        
        self.label_name.grid(row=0, column=0, pady=5, padx=5)
        self.label_id.grid(row=1, column=0, pady=5, padx=5)
        self.entry_name.grid(row=0, column=1, pady=5, padx=5)
        self.entry_id.grid(row=1, column=1, pady=5, padx=5)
        
        self.button_OK = ttk.Button(self, text="OK", 
                                        command=lambda: self.create_area(asm))
        self.button_OK.grid(row=2, column=0, columnspan=2, 
                                        pady=5, padx=5, sticky="nsew")
        
    def create_area(self, asm):
        asm.create_area(self.entry_name.get(), self.entry_id.get())
        self.destroy()