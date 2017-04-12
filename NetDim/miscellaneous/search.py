# NetDim (contact@netdim.fr)

import re
from objects.objects import *
from pythonic_tkinter.preconfigured_widgets import *

class SearchWindow(CustomTopLevel):
    
    def __init__(self, scenario):
        super().__init__()
        self.cs = scenario
        
        # label frame for area properties
        lf_search = Labelframe(self)
        lf_search.text = 'Search'
        lf_search.grid(0, 0)
        
        # list of types
        self.subtypes_list = Combobox(self, width=20)
        self.subtypes_list['values'] = tuple(object_properties.keys())
        self.subtypes_list.current(0)
        self.subtypes_list.bind('<<ComboboxSelected>>', self.update_properties)
        
        # list of properties
        self.property_list = Combobox(self, width=20)
        
        # combobox for regex-based search
        self.is_regex = tk.BooleanVar()
        button_regex = Checkbutton(self, variable=self.is_regex)
        button_regex.text = 'Regex search'
                            
        self.entry_search = Entry(self, width=20)
        
        button_OK = Button(self)
        button_OK.text = 'OK'
        button_OK.command = self.search
        
        self.subtypes_list.grid(0, 1, in_=lf_search)
        self.property_list.grid(1, 1, in_=lf_search)
        button_regex.grid(2, 1, in_=lf_search)
        self.entry_search.grid(3, 1, in_=lf_search)
        button_OK.grid(4, 1, in_=lf_search)
        
        # update property with first value of the list
        self.update_properties()

        # hide the window when closed
        self.protocol('WM_DELETE_WINDOW', self.withdraw)
        self.withdraw()
        
    def update_properties(self, *_):
        subtype = self.subtypes_list.text
        properties = object_properties[subtype]
        properties = tuple(prop_to_name[p] for p in properties)
        self.property_list['values'] = properties
        self.property_list.current(0)
        
    def search(self):
        self.cs.unhighlight_all()
        subtype, property = self.subtypes_list.text, self.property_list.text
        property = name_to_prop[property]
        type = subtype_to_type[subtype]
        input = self.entry_search.text
        for obj in self.cs.ntw.ftr(type, subtype):
            value = getattr(obj, property)
            if not self.is_regex.get():
                converted_input = self.cs.ms.objectizer(property, input)
                if value == converted_input:
                    self.cs.highlight_objects(obj)
            else:
                if re.search(str(input), str(value)):
                    self.cs.highlight_objects(obj)
                
        