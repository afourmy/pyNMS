# NetDim (contact@netdim.fr)

import tkinter as tk
from tkinter import ttk
import re
from miscellaneous.decorators import update_paths
from pythonic_tkinter.preconfigured_widgets import *
from miscellaneous.network_functions import tomask

class RouterConfiguration(tk.Toplevel):
    
    @update_paths
    def __init__(self, node, controller):
        super().__init__() 
        
        notebook = ttk.Notebook(self)
        pastable_config_frame = ttk.Frame(notebook)
        st_pastable_config = CustomScrolledText(pastable_config_frame)
        notebook.add(pastable_config_frame, text='Pastable configuration ')
        
        self.wm_attributes('-topmost', True)
        
        for conf in self.network.build_router_configuration(node):
            st_pastable_config.insert('insert', conf + '\n')
            
        # disable the scrolledtext so that it cannot be edited
        st_pastable_config.config(state=tk.DISABLED)
        
        # pack the scrolledtexts in the frames
        st_pastable_config.pack(fill=tk.BOTH, expand=tk.YES)
        
        # and the notebook in the window
        notebook.pack(fill=tk.BOTH, expand=tk.YES)
        
class SwitchConfiguration(tk.Toplevel):
    
    @update_paths
    def __init__(self, node, controller):
        super().__init__() 
        
        notebook = ttk.Notebook(self)
        pastable_config_frame = ttk.Frame(notebook)
        st_pastable_config = CustomScrolledText(pastable_config_frame)
        notebook.add(pastable_config_frame, text='Configuration ')
        
        self.wm_attributes('-topmost', True)
        
        for conf in self.network.build_switch_configuration(node):
            st_config.insert('insert', conf + '\n')
            
        # disable the scrolledtext so that it cannot be edited
        st_pastable_config.config(state=tk.DISABLED)
        
        # pack the scrolledtexts in the frames
        st_pastable_config.pack(fill=tk.BOTH, expand=tk.YES)
        
        # and the notebook in the window
        notebook.pack(fill=tk.BOTH, expand=tk.YES)
        