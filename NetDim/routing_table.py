from tkinter.scrolledtext import ScrolledText
import tkinter as tk

class RoutingTable(tk.Toplevel):
    def __init__(self, node, scenario):
        super().__init__() 
        self.entry_config = ScrolledText(self, wrap="word", bg="beige")
        self.wm_attributes("-topmost", True)

        codes = """
        Codes: C - connected, S - static, R - RIP, M - mobile, B - BGP
               D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area
               N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2
               E1 - OSPF external type 1, E2 - OSPF external type 2
               i - IS-IS, su - IS-IS summary, L1 - IS-IS level-1, L2 - IS-IS level-2
               ia - IS-IS inter area, * - candidate default, U - per-user static route
               o - ODR, P - periodic downloaded static route
        """

        for _, adj_trunk in scenario.ntw.graph[node]["trunk"]:
            exit_if = adj_trunk("interface", source)
            exit_if_ip = adj_trunk("ipaddress", source)
            exit_if_mask = adj_trunk("subnetmask", source)
            
            # entry for a connected interface in the routing table.
            # it is the summarized ip of both interfaces of the connected link.
            c_if = "C       {ip} is directly connected, {exit_if}\n"\
                                                .format(ip=ip, exit_if=exit_if)  

        
        conf_t = " {name}# configure terminal\n".format(name=node.name)

        self.entry_config.insert("insert", enable_mode)
        self.entry_config.insert("insert", conf_t)
        