# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

from tkinter.scrolledtext import ScrolledText
from operator import itemgetter
import tkinter as tk

class SwitchingTable(tk.Toplevel):
    def __init__(self, node, scenario):
        super().__init__() 
        self.cs = scenario
        self.ST = ScrolledText(self, wrap='word', bg='beige')
        self.wm_attributes('-topmost', True)

        introduction = '''
                            Mac Address Table
----------------------------------------------------------------------------
                    Vlan    |    Mac Address    |    Type    |    Ports\n\n'''
        
        self.ST.insert('insert', introduction)
                
        switching_table = sorted(node.st.items(), key=itemgetter(0))
        for mac_address, outgoing_interface in switching_table:
            line = ('All', mac_address, 'DYNAMIC', str(outgoing_interface), '\n')
            self.ST.insert('insert', 16*" " + (8*" ").join(line))
                                                                
        self.ST.pack(fill=tk.BOTH, expand=tk.YES)