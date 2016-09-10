# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

from tkinter.scrolledtext import ScrolledText
        
class CustomScrolledText(ScrolledText):
    
    def __init__(self, parent_frame):
        super().__init__(
        parent_frame,
        wrap = "word", 
        bg = "beige"
        )
        
        self.tag_config(
        "title", 
        foreground="blue", 
        font=("Helvetica", "12", "bold underline")
        )