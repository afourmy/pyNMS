from tkinter import ttk

class CustomFrame(ttk.Frame):
    
    def __init__(self, *notebook):
        super().__init__(*notebook)
        color = "#A1DBCD"
        ttk.Style().configure("TFrame", background=color)
        ttk.Style().configure("TButton", background=color)
        ttk.Style().configure("TLabel", background=color)
        ttk.Style().configure('TLabelframe', background=color)
        ttk.Style().configure('TLabelframe.Label', background=color)
        ttk.Style().configure('TCheckbutton', background=color)