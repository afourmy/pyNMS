import tkinter as tk
import os
import csv
from tkinter import filedialog

class ImportWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__()
        self.geometry("300x300")
        self.title("Import a graph")
        
        # this allows to change the behavior of closing the window. 
        # I don't want the window to be destroyed, simply hidden
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        
        # current node which properties are displayed
        self.current_node = None
        
        # retrieve and save node data
        self.button_select_file = tk.Button(self, text="Import graph", command=lambda: self.select_file())
        
        # Label displaying the file path
        self.var_filepath = tk.StringVar()
        self.label_filepath = tk.Label(self, textvariable=self.var_filepath)
        
        # Positions in the grid
        self.button_select_file.grid(row=0,column=0, pady=5, padx=5, sticky=tk.W)
        self.label_filepath.grid(row=0, column=1, pady=5, padx=5, sticky=tk.W)
        #self.wm_attributes('-topmost', 1)
        
        self.withdraw()
        
    def select_file(self):
        # hidden top-level instance: no decorations, 0 size, top left corner
        # we lift for focus
        fake_window = tk.Tk()
        fake_window.withdraw()
        fake_window.overrideredirect(True)
        fake_window.geometry('0x0+0+0')
        fake_window.deiconify()
        fake_window.lift()
        fake_window.focus_force()
        
        # retrieve the path and kill fake window
        filepath = filedialog.askopenfilenames(parent=fake_window)
        fake_window.destroy()
        self.var_filepath.set(os.path.abspath(filepath))
        