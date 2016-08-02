from network_functions import compute_network
from tkinter.scrolledtext import ScrolledText
from operator import itemgetter
import tkinter as tk

class RoutingTable(tk.Toplevel):
    def __init__(self, node, scenario):
        super().__init__() 
        self.cs = scenario
        self.ST = ScrolledText(self, wrap="word", bg="beige")
        self.wm_attributes("-topmost", True)

        codes = """
Codes: C - connected, S - static, R - RIP, M - mobile, B - BGP
        D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area
        N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2
        E1 - OSPF external type 1, E2 - OSPF external type 2
        i - IS-IS, su - IS-IS summary, L1 - IS-IS level-1, L2 - IS-IS level-2
        ia - IS-IS inter area, * - candidate default, U - per-user static route
        o - ODR, P - periodic downloaded static route\n\n"""
        
        self.ST.insert("insert", codes)
        
        gateway = "Gateway of last resort is not set\n\n"
        self.ST.insert("insert", gateway)
                
        list_RT = sorted(node.rt.items(), key=itemgetter(1))
        for sntw, routes in list_RT:
            if len(routes) - 1:
                for idx, route in enumerate(routes):
                    rtype, ex_ip, ex_int, cost, *_ ,= route
                    rtype = rtype + " "*(8 - len(rtype))
                    if not idx:
                        line = "{rtype}{sntw} [110/{cost}] via {ex_ip}, {ex_int}\n"\
                                                            .format(
                                                                    cost = cost, 
                                                                    rtype = rtype, 
                                                                    sntw = sntw, 
                                                                    ex_ip = ex_ip, 
                                                                    ex_int = ex_int
                                                                    )
                    else:
                        spaces = " "*(len(rtype) + len(sntw))
                        line = "{spaces} [110/{cost}] via {ex_ip}, {ex_int}\n"\
                                                            .format(
                                                                    cost = cost, 
                                                                    spaces = spaces,
                                                                    ex_ip = ex_ip, 
                                                                    ex_int = ex_int
                                                                    )
                    self.ST.insert("insert", line)
                        
            else:
                route ,= routes
                rtype, ex_ip, ex_int, cost, *_ ,= route
                rtype = rtype + " "*(8 - len(rtype))
                print(rtype)
                if rtype[0] == "O":
                    route = "{rtype}{sntw} [110/{cost}] via {ex_ip}, {ex_int}\n"\
                                                            .format(
                                                                    cost = cost, 
                                                                    rtype = rtype, 
                                                                    sntw = sntw, 
                                                                    ex_ip = ex_ip, 
                                                                    ex_int = ex_int
                                                                    )
                elif rtype[0] == "i":
                    route = "{rtype}{sntw} [115/{cost}] via {ex_ip}, {ex_int}\n"\
                                                            .format(
                                                                    cost = cost, 
                                                                    rtype = rtype, 
                                                                    sntw = sntw, 
                                                                    ex_ip = ex_ip, 
                                                                    ex_int = ex_int
                                                                    )
                else:
                    route = "{rtype}{sntw} is directly connected, {ex_int}\n"\
                        .format(rtype=rtype, sntw=sntw, ex_ip=ex_ip, ex_int=ex_int)
                self.ST.insert("insert", route)
                
        self.ST.pack(fill=tk.BOTH, expand=tk.YES)
                                            