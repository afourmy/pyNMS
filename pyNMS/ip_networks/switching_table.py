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

from miscellaneous.decorators import update_paths
from tkinter.scrolledtext import ScrolledText
from operator import itemgetter
import tkinter as tk

class SwitchingTable(tk.Toplevel):
    
    @update_paths
    def __init__(self, node, controller):
        super().__init__() 
        
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