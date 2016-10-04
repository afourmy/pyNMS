from .custom_toplevel import FocusTopLevel
import tkinter as tk
from tkinter import ttk

class SearchObject(FocusTopLevel):
    
    def __init__(self, master):
        super().__init__()
        self.ms = master
        
        # list of types
        self.subtypes_list = ttk.Combobox(self, width=10)
        self.subtypes_list["values"] = tuple(self.ms.object_properties.keys())
        self.subtypes_list.current(0)
        self.subtypes_list.bind('<<ComboboxSelected>>', self.update_properties)
        self.subtypes_list.grid(row=0, column=1, pady=5, padx=5)
        
        # list of properties
        self.property_list = ttk.Combobox(self, width=10)
        self.property_list.grid(row=1, column=1, pady=5, padx=5)
                            
        self.entry_search = ttk.Entry(self, width=10)
        self.entry_search.grid(row=2, column=1, pady=5, padx=5)
        
        self.button_OK = ttk.Button(self, text="OK", command=self.search)
        self.button_OK.grid(row=3, column=1, pady=5, padx=5, sticky="nsew")
                                        
        # update property with first value of the list
        self.update_properties()
        
    def update_properties(self):
        subtype = self.subtypes_list.get()
        self.property_list["values"] = self.ms.object_properties[subtype]
        self.property_list.current(0)
        
    def search(self):
        self.ms.cs.unhighlight_all()
        subtype, property = self.subtypes_list.get(), self.property_list.get()
        type = self.ms.st_to_type[subtype]
        user_input = self.ms.prop_to_type[property](self.entry_search.get())
        for obj in self.ms.cs.ntw.ftr(type, subtype):
            if getattr(obj, property) == user_input:
                self.ms.cs.highlight_objects(obj)
                
        