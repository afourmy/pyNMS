# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

from pythonic_tkinter.preconfigured_widgets import *

class Debug(CustomTopLevel):
    def __init__(self, master):
        super().__init__() 
        label_debug = Label(self)
        label_debug.text = 'Query :'
        
        self.entry_debug  = Entry(self, width=20)

        button_debug = Button(self, width=10)
        button_debug.text = 'Debug'
        button_debug.command = lambda: self.query_netdim(master)
                                
        self.ST = Text(self)
        self.wm_attributes('-topmost', True)                     

        label_debug.grid(0, 0, sticky='e')
        self.entry_debug.grid(0, 1)
        button_debug.grid(0, 2)
        self.ST.grid(1, 0, 1, 3)
        
        # hide the window when closed
        self.protocol('WM_DELETE_WINDOW', self.withdraw)
        # close the window when initialized
        self.withdraw()
        
    def query_netdim(self, master):
        query = self.entry_debug.text
        print(query)
        test = eval(query)
        print(test)
        self.ST.delete('1.0', 'end')
        self.ST.insert('insert', test)

