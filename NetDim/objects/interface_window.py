# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

from pythonic_tkinter.preconfigured_widgets import *

class InterfaceWindow(FocusTopLevel):
    
    interface_properties = (
                 "ipaddress",
                 "subnetmask",
                 "macaddress"
                )
                
    def __init__(self, master, trunk, node):
        super().__init__()
        self.ms = master
        self.trunk = trunk
        self.node = node
        self.title("Manage interface properties")

        # create the property window
        self.dict_var = {}
        for index, property in enumerate(self.interface_properties):
            # creation of the label associated to the property
            label = Label(self)
            label.text = self.ms.prop_to_nice_name[property]
            label.grid(index+1, 0, pady=1)
            
            property_entry = Entry(self, width=15)
            print(property, trunk(property, node))
            property_entry.text = str(trunk(property, node))
            self.dict_var[property] = property_entry
            property_entry.grid(index+1, 1, pady=1)
            
        # when the window is closed, save all parameters (in case the user
        # made a change), then withdraw the window.
        self.protocol("WM_DELETE_WINDOW", lambda: self.save_and_destroy())
        
    def save_and_destroy(self):
        for property, entry in self.dict_var.items():
            value = self.ms.prop_to_type[property + 'S'](entry.get())
            self.trunk(property, self.node, value)
        self.destroy()