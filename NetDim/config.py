from tkinter.scrolledtext import ScrolledText
import tkinter as tk

class Configuration(tk.Toplevel):
    def __init__(self, node, scenario):
        super().__init__()
        self.geometry("600x400")   
        self.entry_config = ScrolledText(self, wrap="word", bg="beige")
        self.wm_attributes("-topmost", True)

        enable_mode = " {name}> enable\n".format(name=node.name)  
        conf_t = " {name}# configure terminal\n".format(name=node.name)

        self.entry_config.insert("insert", enable_mode)
        self.entry_config.insert("insert", conf_t)
        
        for _, adj_trunk in scenario.ntw.graph[node]["trunk"]:
            direction = "S"*(adj_trunk.source == node) or "D"
            interface = getattr(adj_trunk, "interface" + direction)
            ip = getattr(adj_trunk, "ipaddress" + direction)
            mask = getattr(adj_trunk, "subnetmask" + direction)
            
            interface_config = " {name}(config)# interface {interface}\n"\
                                    .format(name=node.name, interface=interface)
            interface_ip = " {name}(config-if)# ip address {ip} {mask}\n"\
                                    .format(name=node.name, ip=ip, mask=mask)
            no_shut = " {name}(config-if)# no shutdown\n".format(name=node.name)
            
            self.entry_config.insert("insert", interface_config)
            self.entry_config.insert("insert", interface_ip)
            self.entry_config.insert("insert", no_shut)
            
            if any(AS.type == "OSPF" for AS in adj_trunk.AS):
                direction = "SD" if direction == "S" else "DS"
                cost = getattr(adj_trunk, "cost" + direction)
                if cost != 1:
                    change_cost = (" {name}(config-if)#"
                                    " ip ospf cost {cost}\n")\
                                    .format(name=node.name, cost=cost)
                    self.entry_config.insert("insert", change_cost)
                    
            exit = " {name}(config-if)# exit\n".format(name=node.name)
            self.entry_config.insert("insert", exit)
            
        for AS in node.AS:
            if AS.type == "RIP":
                activate_rip = " {name}(config)# router rip\n"\
                                                .format(name=node.name)
                self.entry_config.insert("insert", activate_rip)
                
                for _, adj_trunk in scenario.ntw.graph[node]["trunk"]:
                    if adj_trunk in AS.pAS["trunk"]:
                        direction = "S"*(adj_trunk.source == node) or "D"
                        ip = getattr(adj_trunk, "ipaddress" + direction)
                        
                        interface_ip = " {name}(config-router)# network {ip}\n"\
                                                .format(name=node.name, ip=ip)
                        self.entry_config.insert("insert", interface_ip)
                    else:
                        interface = getattr(adj_trunk, "interface" + direction)
                        pi = " {name}(config-router)# passive-interface {i}\n"\
                                .format(name=node.name, i=interface)
                        self.entry_config.insert("insert", pi)
                        
                end = " {name}(config-router)# end\n"\
                                    .format(name=node.name, ip=ip)
                self.entry_config.insert("insert", end)
                
            elif AS.type == "OSPF":
                activate_ospf = " {name}(config)# router ospf 1\n"\
                                                    .format(name=node.name)
                self.entry_config.insert("insert", activate_ospf)
                
                for _, adj_trunk in scenario.ntw.graph[node]["trunk"]:
                    if adj_trunk in AS.pAS["trunk"]:
                        direction = "S"*(adj_trunk.source == node) or "D"
                        ip = getattr(adj_trunk, "ipaddress" + direction)
                        trunk_area ,= adj_trunk.AS[AS]
                        interface_ip = (" {name}(config-router)# network" 
                                        " {ip} 0.0.0.3 area {area_id}\n")\
                        .format(name=node.name, ip=ip, area_id=trunk_area.id)
                        self.entry_config.insert("insert", interface_ip)
                            
                    else:
                        interface = getattr(adj_trunk, "interface" + direction)
                        pi = " {name}(config-router)# passive-interface {i}\n"\
                                .format(name=node.name, i=interface)
                        self.entry_config.insert("insert", pi)
                        
                end = " {name}(config-router)# end\n"\
                                    .format(name=node.name, ip=ip)
                self.entry_config.insert("insert", end)
                
        self.entry_config.pack(fill=tk.BOTH, expand=tk.YES)

        