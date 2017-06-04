# NetDim (contact@netdim.fr)

import tkinter as tk
from miscellaneous.decorators import update_paths
from pythonic_tkinter.preconfigured_widgets import *
from operator import itemgetter

class ARPTable(tk.Toplevel):
    
    @update_paths
    def __init__(self, node, controller):
        super().__init__() 
        
        self.ST = ScrolledText(self, wrap='word', bg='beige')
        self.wm_attributes('-topmost', True)

        introduction = '''
                    Address Resolution Protocol Table
----------------------------------------------------------------------------
         Address     |     Hardware Addr     |     Type     |     Interface\n\n'''
        
        self.ST.insert('insert', introduction)
                
        arp_table = sorted(node.arpt.items(), key=itemgetter(0))
        for oip, (mac_addr, outgoing_interface) in arp_table:
            line = (oip.ip_addr, mac_addr, 'ARPA', str(outgoing_interface), '\n')
            self.ST.insert('insert', 8*" " + (9*" ").join(line))
                                                                
        self.ST.pack(fill='both', expand='yes')

