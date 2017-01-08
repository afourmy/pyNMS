# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

from pythonic_tkinter.preconfigured_widgets import *

class InterfaceWindow(FocusTopLevel):
    
    interface_properties = (
                 'ipaddress',
                 'subnetmask',
                 'macaddress'
                )
                
    def __init__(self, master, interface):
        super().__init__()
        self.ms = master
        self.interface = interface
        self.title('Manage interface properties')
        self.dict_global_properties = {}

        # labelframe for global interface properties 
        lf_global = Labelframe(self)
        lf_global.text = 'Global properties'
        lf_global.grid(0, 0)
        
        for index, property in enumerate(interface.public_properties):
            # creation of the label associated to the property
            label = Label(self)
            label.text = self.ms.prop_to_nice_name[property]
            
            property_entry = Entry(self, width=15)
            property_entry.text = str(getattr(self.interface, property))
            self.dict_global_properties[property] = property_entry
            
            label.grid(index+1, 0, pady=1, in_=lf_global)
            property_entry.grid(index+1, 1, pady=1, in_=lf_global)
            
        if self.interface.AS_properties:
            # labelframe for per-AS interface properties
            lf_perAS = Labelframe(self)
            lf_perAS.text = 'Per-AS properties'
            lf_perAS.grid(1, 0)
            self.dict_perAS_properties = {}
            
            # AS combobox
            self.AS_combobox = Combobox(self, width=20)
            self.AS_combobox['values'] = tuple(self.interface.AS_properties)
            self.AS_combobox.current(0)
            self.AS_combobox.bind('<<ComboboxSelected>>', self.update_AS_properties)
            self.AS_combobox.grid(0, 0, 1, 2, in_=lf_perAS)
            
            for index, property in enumerate(interface.perAS_properties):
                # creation of the label associated to the property
                label = Label(self)
                label.text = self.ms.prop_to_nice_name[property]
                
                property_entry = Entry(self, width=15)
                property_entry.text = str(self.interface(self.AS_combobox.text, property))
                self.dict_perAS_properties[property] = property_entry
                
                label.grid(index+1, 0, pady=1, in_=lf_perAS)
                property_entry.grid(index+1, 1, pady=1, in_=lf_perAS)
            
        # when the window is closed, save all parameters (in case the user
        # made a change), then withdraw the window.
        self.protocol('WM_DELETE_WINDOW', lambda: self.save_and_destroy())
        
    def update_AS_properties(self, _):
        AS = self.AS_combobox.text
        for property, entry in self.dict_perAS_properties.items():
            entry.text = self.interface(AS, property)
        
    def save_and_destroy(self):
        for property, entry in self.dict_global_properties.items():
            value = self.ms.prop_to_type[property](entry.get())
            setattr(self.interface, property, value)
            
        if self.interface.AS_properties:
            AS = self.AS_combobox.text
            for property, entry in self.dict_perAS_properties.items():
                self.interface(AS, property, entry.text)
                
        self.destroy()