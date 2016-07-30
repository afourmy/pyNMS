from network_functions import compute_network
from tkinter.scrolledtext import ScrolledText
import tkinter as tk

class RoutingTable(tk.Toplevel):
    def __init__(self, node, scenario):
        super().__init__() 
        self.cs = scenario
        self.rt = ScrolledText(self, wrap="word", bg="beige")
        self.wm_attributes("-topmost", True)
        
        types = {"OSPF": "O", "RIP": "R", "ISIS": "i"}
        # faire ospf: ("O", 110), 

        codes = """
Codes: C - connected, S - static, R - RIP, M - mobile, B - BGP
        D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area
        N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2
        E1 - OSPF external type 1, E2 - OSPF external type 2
        i - IS-IS, su - IS-IS summary, L1 - IS-IS level-1, L2 - IS-IS level-2
        ia - IS-IS inter area, * - candidate default, U - per-user static route
        o - ODR, P - periodic downloaded static route\n\n"""
        
        self.rt.insert("insert", codes)
        
        gateway = "Gateway of last resort is not set\n\n"
        self.rt.insert("insert", gateway)

        for _, adj_trunk in scenario.ntw.graph[node]["trunk"]:
            exit_if = adj_trunk("interface", node)
            ntw = adj_trunk.sntw
            
            # entry for a connected interface in the routing table.
            # it is the summarized ip of both interfaces of the connected link.
            c_if = "C       {ntw} is directly connected, {exit_if}\n"\
                                                .format(ntw=ntw, exit_if=exit_if)  
            self.rt.insert("insert", c_if)
                
        for AS in node.AS:
            # rajouter l'interface
            for (rtype, sntw), (ex_ip, ex_int) in node.routing_table[AS].items():
                rtype = rtype + " "*(8 - len(rtype))
                route = "{rtype}{sntw} via {ex_ip}, {ex_int}\n"\
                    .format(rtype=rtype, sntw=sntw, ex_ip=ex_ip, ex_int=ex_int)
                self.rt.insert("insert", route)
                
        self.rt.pack(fill=tk.BOTH, expand=tk.YES)
                                            