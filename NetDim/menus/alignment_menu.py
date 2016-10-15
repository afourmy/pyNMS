# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk
from collections import OrderedDict

class AlignmentMenu(tk.Menu):
    
    def __init__(self, scenario, nodes):
        super().__init__(tearoff=0)
        self.cs = scenario
        
        cmds = OrderedDict([
        ("Horizontal alignment", lambda: self.cs.align(nodes)),
        ("Vertical alignment", lambda: self.cs.align(nodes, False)),
        ("Horizontal distribution", lambda: self.cs.distribute(nodes)),
        ("Vertical distribution", lambda: self.cs.distribute(nodes, False)),
        ])
    
        for label, cmd in cmds.items():
            self.add_command(label=label, command=cmd)