# NetDim
# Copyright (C) 2017 Antoine Fourmy (contact@netdim.fr)
# Released under the GNU General Public License GPLv3

from pythonic_tkinter.preconfigured_widgets import *

class Debug(CustomTopLevel):
    def __init__(self, master):
        super().__init__() 
        
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
        self.debug_list.bind('<<ComboboxSelected>>', lambda e: self.debug(master))
        
        self.entry_debug  = Entry(self, width=60)

        button_debug = Button(self, width=10)
        button_debug.text = 'Debug'
        button_debug.command = lambda: self.query_netdim(master)
                                
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
        
    def debug(self, master):
        self.ST.delete('1.0', 'end')
        value = self.debug_list.text
        if value == 'Objects':
            query_result = eval('master.cs.object_id_to_object')
        elif value == 'Nodes':
            query_result = eval('master.cs.ntw.nodes')
        elif value == 'Physical links':
            query_result = eval('master.cs.ntw.plinks')
        elif value == 'L2 links':
            query_result = eval('master.cs.ntw.l2links')
        elif value == 'L3 links':
            query_result = eval('master.cs.ntw.l3links')
        elif value == 'Traffic links':
            query_result = eval('master.cs.ntw.traffics')
        elif value == 'Interfaces':
            query_result = eval('master.cs.ntw.interfaces')
        elif value == 'IP addresses':
            query_result = eval('master.cs.ntw.ip_to_oip')
        else:
            query_result = ''
            # for AS, more details
            for AS in master.cs.ntw.pnAS.values():
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
            

