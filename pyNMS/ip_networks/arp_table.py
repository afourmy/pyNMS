# Copyright (C) 2017 Antoine Fourmy <antoine dot fourmy at gmail dot com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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

