# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

from pythonic_tkinter.preconfigured_widgets import *
from operator import itemgetter

class ARPTable(CustomTopLevel):
    def __init__(self, node, scenario):
        super().__init__() 
        self.cs = scenario
        self.ST = ScrolledText(self)
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

