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

from pythonic_tkinter.preconfigured_widgets import *
from miscellaneous.decorators import update_paths

class Debug(CustomTopLevel):
    
    def __init__(self, controller):
        super().__init__() 
        self.controller = controller
        
        # label frame for debugging
        lf_debug = Labelframe(self)
        lf_debug.text = 'Debug'
        lf_debug.grid(0, 0)
        
        values = (
                  'Objects',
                  'Nodes',
                  'Physical links',
                  'L2 links',
                  'L3 links',
                  'Traffic links',
                  'Interfaces',
                  'AS',
                  'IP addresses'
                  )
        
        # List of debugging options
        self.debug_list = Combobox(self, width=15)
        self.debug_list['values'] = values
        self.debug_list.current(0)
        self.debug_list.bind('<<ComboboxSelected>>', lambda e: self.debug())
        
        self.entry_debug  = Entry(self, width=60)

        button_debug = Button(self, width=10)
        button_debug.text = 'Debug'
        button_debug.command = lambda: self.query_netdim
                                
        self.ST = Text(self)
        self.wm_attributes('-topmost', True)                     

        self.debug_list.grid(0, 0, in_=lf_debug)
        self.entry_debug.grid(0, 1, in_=lf_debug)
        button_debug.grid(0, 2, in_=lf_debug)
        self.ST.grid(1, 0, 1, 3, in_=lf_debug)
        
        # hide the window when closed
        self.protocol('WM_DELETE_WINDOW', self.withdraw)
        # close the window when initialized
        self.withdraw()
        
    def query_netdim(self, master):
        query = self.entry_debug.text
        query_result = eval(query)
        self.ST.delete('1.0', 'end')
        self.ST.insert('insert', query_result)
        
    @update_paths
    def debug(self):
        self.ST.delete('1.0', 'end')
        value = self.debug_list.text
        if value == 'Objects':
            query_result = eval('self.view.object_id_to_object')
        elif value == 'Nodes':
            query_result = eval('self.main_network.nodes')
        elif value == 'Physical links':
            query_result = eval('self.main_network.plinks')
        elif value == 'L2 links':
            query_result = eval('self.main_network.l2links')
        elif value == 'L3 links':
            query_result = eval('self.main_network.l3links')
        elif value == 'Traffic links':
            query_result = eval('self.main_network.traffics')
        elif value == 'Interfaces':
            query_result = eval('self.main_network.interfaces')
        elif value == 'IP addresses':
            query_result = eval('self.main_network.ip_to_oip')
        else:
            query_result = ''
            # for AS, more details
            for AS in self.main_network.pnAS.values():
                query_result += '''AS name: {name}
AS type: {type}
AS id: {id}
AS nodes: {nodes}
AS links: {links}
                '''.format(
                           name = AS.name, 
                           type = AS.AS_type, 
                           id = AS.id,
                           nodes = AS.nodes,
                           links = AS.links
                           )
        self.ST.insert('insert', query_result)
            

