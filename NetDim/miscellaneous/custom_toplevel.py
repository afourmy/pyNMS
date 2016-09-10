# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk
from tkinter import ttk
            
class CustomTopLevel(tk.Toplevel):
    
    def __init__(self):
        super().__init__()
        self.configure(background="#A1DBCD")        
        ttk.Style().configure("TButton", background="#A1DBCD")
        ttk.Style().configure("TLabel", background="#A1DBCD")
        ttk.Style().configure("Treeview", background="#A1DBCD", 
                                                            foreground="black")
        ttk.Style().configure('TLabelframe', background="#A1DBCD")
        ttk.Style().configure('TLabelframe.Label', background="#A1DBCD")
        ttk.Style().configure('TCheckbutton', background="#A1DBCD")
        
class FocusTopLevel(CustomTopLevel):
    
    def __init__(self):
        super().__init__()
        
        self.var_focus = tk.IntVar()
        self.checkbutton_focus = tk.Checkbutton(self, text="Focus", 
            bg="#A1DBCD", variable=self.var_focus, command=self.change_focus)
        self.checkbutton_focus.grid(row=0, column=0, sticky=tk.W)
            
    def change_focus(self):
        self.wm_attributes("-topmost", self.var_focus.get())