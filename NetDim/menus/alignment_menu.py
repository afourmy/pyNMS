# NetDim (contact@netdim.fr)

from pythonic_tkinter.preconfigured_widgets import *
from collections import OrderedDict

class AlignmentMenu(Menu):
    
    def __init__(self, scenario, nodes):
        super().__init__(0)
        self.cs = scenario
        
        cmds = OrderedDict([
        ('Horizontal alignment', lambda: self.cs.align(nodes)),
        ('Vertical alignment', lambda: self.cs.align(nodes, False)),
        ('Horizontal distribution', lambda: self.cs.distribute(nodes)),
        ('Vertical distribution', lambda: self.cs.distribute(nodes, False)),
        ])
    
        for label, cmd in cmds.items():
            self.add_command(label=label, command=cmd)