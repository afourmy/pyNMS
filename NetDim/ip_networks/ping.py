# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

from miscellaneous.custom_toplevel import FocusTopLevel
from tkinter.scrolledtext import ScrolledText
import tkinter as tk
from tkinter import ttk
from miscellaneous.network_functions import compute_network

class Ping(FocusTopLevel):
    def __init__(self, source, scenario):
        super().__init__() 
        self.cs = scenario
        self.label_IP = tk.Label(self, bg="#A1DBCD", text="Destination IP :")
        self.entry_IP  = tk.Entry(self, width=20)

        self.bt_ping = ttk.Button(self, text="Ping", 
                                command=lambda: self.ping_IP(source), width=10)
                                
        self.ST = ScrolledText(self, wrap="word", bg="beige")
        self.wm_attributes("-topmost", True)                     

        self.label_IP.grid(row=0, column=0, pady=5, padx=5, sticky="e")
        self.entry_IP.grid(row=0, column=1, pady=5, padx=5)
        self.bt_ping.grid(row=0, column=2, pady=5, padx=5)
        self.ST.grid(row=1, column=0, columnspan=3, pady=5, padx=5)
        
    def ping_IP(self, source):
        dest_IP = self.entry_IP.get()
        self.ST.delete("1.0", tk.END)
        for trunk in self.cs.ntw.pn["trunk"].values():
            if dest_IP in (trunk.ipaddressS, trunk.ipaddressD):
                sntw = trunk.sntw
                for rt_entry in self.cs.ntw.ping(source, sntw):
                    self.ST.insert("insert", str(rt_entry) + "\n")
                break
        else:
            print("ip address not found in the network")
