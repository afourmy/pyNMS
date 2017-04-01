# NetDim
# Copyright (C) 2017 Antoine Fourmy (contact@netdim.fr)

from pythonic_tkinter.preconfigured_widgets import *
from miscellaneous.network_functions import compute_network
from .script import Script

class ScriptCreation(FocusTopLevel):
    def __init__(self, master):
        super().__init__() 
        self.ms = master
        
        # main label frame
        lf_script_creation = Labelframe(self)
        lf_script_creation.text = 'Script creation'
        lf_script_creation.grid(0, 0)
        
        label_script = Label(self)
        label_script.text = 'Script :'
        
        self.script_list = Combobox(self, width=15)
        self.script_list['values'] = tuple(self.ms.scripts)
        self.script_list.bind('<<ComboboxSelected>>', lambda e: self.load_script())
        
        label_save = Button(self)
        label_save.text = 'Save script'
        label_save.command = self.save_script
        
        self.entry_script_name  = Entry(self, width=20)
                                
        self.ST = ScrolledText(self)
        self.wm_attributes('-topmost', True)                    

        label_script.grid(0, 0, in_=lf_script_creation)
        self.script_list.grid(0, 1, in_=lf_script_creation)
        self.entry_script_name.grid(0, 2, in_=lf_script_creation)
        label_save.grid(0, 3, in_=lf_script_creation)
        self.ST.grid(row=1, column=0, columnspan=5, in_=lf_script_creation)
        
        # hide the window when closed
        self.protocol('WM_DELETE_WINDOW', self.withdraw)
        # hide the window at creation
        self.withdraw()
        
    def save_script(self):
        # create the Script object
        instructions = self.ST.get(1.0, 'end').split('\n')
        script = Script(self.entry_script_name.text, instructions)
        # fill the scripts dictionnary
        self.ms.scripts[script.name] = script
        # update the combobx
        self.script_list['values'] += (script.name,)
        self.script_list.text = script.name
        
    def load_script(self):
        # delete the content of the combobox
        self.ST.delete('1.0', 'end')
        # retrieve the Script object
        script = self.ms.scripts[self.script_list.text]
        # update the name entry with the script name
        self.entry_script_name.text = script.name
        # insert the script instructions in the scrolledtext
        self.ST.insert('insert', str(script))
        