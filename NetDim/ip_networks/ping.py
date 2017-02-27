# NetDim
# Copyright (C) 2017 Antoine Fourmy (contact@netdim.fr)
# Released under the GNU General Public License GPLv3

from pythonic_tkinter.preconfigured_widgets import *
from miscellaneous.network_functions import compute_network

class Ping(FocusTopLevel):
    def __init__(self, source, scenario):
        super().__init__() 
        self.cs = scenario
        
        # main label frame
        lf_ping = Labelframe(self)
        lf_ping.text = 'Ping a distant node'
        lf_ping.grid(0, 0)
        
        label_src_IP = Label(self)
        label_src_IP.text = 'Source IP :'
        
        self.IP_list = Combobox(self, width=15)
        self.IP_list['values'] = tuple(self.cs.ntw.attached_ips(source))
        self.IP_list.current(0)
        
        label_dst_IP = Label(self)
        label_dst_IP.text = 'Destination IP :'
        
        self.entry_IP  = Entry(self, width=20)

        button_ping = Button(self, width=10)
        button_ping.text = 'Ping' 
        button_ping.command = lambda: self.ping_IP(source)
                                
        self.ST = ScrolledText(self)
        self.wm_attributes('-topmost', True)                    

        label_src_IP.grid(0, 0, in_=lf_ping)
        self.IP_list.grid(0, 1, in_=lf_ping)
        label_dst_IP.grid(0, 2, in_=lf_ping)
        self.entry_IP.grid(0, 3, in_=lf_ping)
        button_ping.grid(0, 4, in_=lf_ping)
        self.ST.grid(row=1, column=0, columnspan=5, in_=lf_ping)
        
    def ping_IP(self, source):
        src_IP = self.cs.ntw.ip_to_oip[self.IP_list.text]
        dst_IP = self.cs.ntw.ip_to_oip[self.entry_IP.text]
        # dummy traffic link to retrieve the path of an IP packet
        traffic = self.cs.ntw.lf(
                                    source = source, 
                                    destination = dst_IP.interface.node, 
                                    subtype = 'routed traffic'
                                    )
        traffic.ipS, traffic.ipD = src_IP, dst_IP
        self.ST.delete('1.0', 'end')
        _, path = self.cs.ntw.RFT_path_finder(traffic)
        self.ST.insert('insert', '\n\n\n'.join(path))
        # delete the dummy traffic link
        self.cs.ntw.remove_link(traffic)

