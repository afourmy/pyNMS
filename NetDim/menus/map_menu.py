# NetDim (contact@netdim.fr)

from pythonic_tkinter.preconfigured_widgets import *
from collections import OrderedDict

class MapMenu(Menu):
    
    def __init__(self, scenario, nodes):
        super().__init__(0)
        self.cs = scenario
        
        cmds = OrderedDict([
                    ('Update geographical coordinates with current position', 
                        lambda: self.cs.update_geographical_coordinates(*nodes)
                    ),
                    ('Update logical coordinates with current position', 
                        lambda: self.cs.update_logical_coordinates(*nodes)
                    ),
                    ('Move selected nodes to geographical coordinates', 
                        lambda: self.cs.move_to_geographical_coordinates(*nodes)
                    ),
                    ('Move selected nodes to logical coordinates', 
                        lambda: self.cs.move_to_logical_coordinates(*nodes)
                    ),
                    ('move to geo', lambda: self.cs.to_geo(*nodes)),
        ])
    
        for label, cmd in cmds.items():
            self.add_command(label=label, command=cmd)