# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

from miscellaneous.network_functions import compute_network
from tkinter.scrolledtext import ScrolledText
from operator import itemgetter
import tkinter as tk

class BGPTable(tk.Toplevel):
    def __init__(self, node, scenario):
        super().__init__() 
        self.cs = scenario
        self.ST = ScrolledText(self, wrap="word", bg="beige")
        self.wm_attributes("-topmost", True)

        codes = """
BGP table version is 6, local router ID is {ip}
Status codes: s suppressed, d damped, h history, * valid, > best, i - internal,
              r RIB-failure, S Stale, m multipath, b backup-path, x best-external, f RT-Filter, a additional-path
Origin codes: i - IGP, e - EGP, ? - incomplete
RPKI validation codes: V valid, I invalid, N Not found"""\
                                            .format(ip=node.ipaddress)
        
        self.ST.insert("insert", codes)
        
        if node.default_route:
            gateway = "Gateway of last resort is {gw} to network 0.0.0.0\n\n"\
                                        .format(gw=node.default_route)
        else:
            gateway = "Gateway of last resort is not set\n\n"
        self.ST.insert("insert", gateway)
                
        for sntw, routes in node.bgpt.items():
            if len(routes) - 1:
                for idx, route in enumerate(routes):
                    weight, nh, source, AS_path = route
                    rtype = "N*" + " "*8
                    if not idx:
                        line = "{rtype} {sntw} {nh}    0    , {weight} {path}\n"\
                                        .format(
                                                rtype = rtype, 
                                                sntw = sntw, 
                                                nh = nh,
                                                weight = weight,
                                                path = "".join(map(str, AS_path))
                                                )
                    else:
                        spaces = " "*(len(rtype) + len(sntw))
                        line = "{spaces} {nh}    0    , {weight} {path}\n"\
                                        .format(
                                                spaces = spaces,
                                                nh = nh,
                                                weight = weight,
                                                path = "".join(map(str, AS_path))
                                                )
                    self.ST.insert("insert", line)
                        
            # else:
            #     route ,= routes
            #     rtype, ex_ip, ex_int, cost, *_ ,= route
            #     rtype = rtype + " "*(8 - len(rtype))

                                        
        self.ST.pack(fill=tk.BOTH, expand=tk.YES)