# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import re
from .custom_toplevel import CustomTopLevel
import tkinter as tk
from tkinter import ttk

class SearchObject(CustomTopLevel):
    
    def __init__(self, master):
        super().__init__()
        self.ms = master
        
        # list of types
        self.subtypes_list = ttk.Combobox(self, width=20)
        self.subtypes_list["values"] = tuple(self.ms.object_properties.keys())
        self.subtypes_list.current(0)
        self.subtypes_list.bind('<<ComboboxSelected>>', self.update_properties)
        self.subtypes_list.grid(row=0, column=1, pady=5, padx=5)
        
        # list of properties
        self.property_list = ttk.Combobox(self, width=20)
        self.property_list.grid(row=1, column=1, pady=5, padx=5)
        
        # combobox for regex-based search
        self.is_regex = tk.BooleanVar()
        self.button_regex = ttk.Checkbutton(self, text="Regex search", 
                                                        variable=self.is_regex)
        self.button_regex.grid(row=2, column=1, pady=5, padx=5, sticky="nsew")
                            
        self.entry_search = ttk.Entry(self, width=20)
        self.entry_search.grid(row=3, column=1, pady=5, padx=5)
        
        self.button_OK = ttk.Button(self, text="OK", command=self.search)
        self.button_OK.grid(row=4, column=1, pady=5, padx=5, sticky="nsew")
        
        # update property with first value of the list
        self.update_properties()
        
    def update_properties(self, *_):
        subtype = self.subtypes_list.get()
        properties = self.ms.object_properties[subtype]
        properties = tuple(self.ms.prop_to_nice_name[p] for p in properties)
        self.property_list["values"] = properties
        self.property_list.current(0)
        
    def search(self):
        self.ms.cs.unhighlight_all()
        subtype, property = self.subtypes_list.get(), self.property_list.get()
        property = self.ms.name_to_prop[property]
        type = self.ms.st_to_type[subtype]
        input = self.entry_search.get()
        for obj in self.ms.cs.ntw.ftr(type, subtype):
            value = getattr(obj, property)
            if not self.is_regex.get():
                converted_input = self.ms.prop_to_type[property](input)
                if value == converted_input:
                    self.ms.cs.highlight_objects(obj)
            else:
                if re.search(str(input), str(value)):
                    self.ms.cs.highlight_objects(obj)
                
        