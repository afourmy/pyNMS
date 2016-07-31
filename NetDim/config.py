from tkinter.scrolledtext import ScrolledText
import tkinter as tk

class Configuration(tk.Toplevel):
    def __init__(self, node, scenario):
        super().__init__() 
        self.entry_config = ScrolledText(self, wrap="word", bg="beige")
        self.wm_attributes("-topmost", True)

        enable_mode = " {name}> enable\n".format(name=node.name)  
        conf_t = " {name}# configure terminal\n".format(name=node.name)

        self.entry_config.insert("insert", enable_mode)
        self.entry_config.insert("insert", conf_t)
        
        # configuration of the loopback interface
        lo = " {name}(config)# interface Loopback0\n".format(name=node.name)
        lo_ip = " {name}(config-if)# ip address {ip} {mask}\n"\
                .format(name=node.name, ip=node.ipaddress, mask=node.subnetmask)
                
        self.entry_config.insert("insert", lo)
        self.entry_config.insert("insert", lo_ip)
        exit = " {name}(config-if)# exit\n".format(name=node.name)
        self.entry_config.insert("insert", exit)
        
        for _, adj_trunk in scenario.ntw.graph[node]["trunk"]:
            direction = "S"*(adj_trunk.source == node) or "D"
            interface = getattr(adj_trunk, "interface" + direction)
            ip = getattr(adj_trunk, "ipaddress" + direction)
            mask = getattr(adj_trunk, "subnetmask" + direction)
            
            interface_conf = " {name}(config)# interface {interface}\n"\
                                    .format(name=node.name, interface=interface)
            interface_ip = " {name}(config-if)# ip address {ip} {mask}\n"\
                                    .format(name=node.name, ip=ip, mask=mask)
            no_shut = " {name}(config-if)# no shutdown\n".format(name=node.name)
            
            self.entry_config.insert("insert", interface_conf)
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
                    direction = "S"*(adj_trunk.source == node) or "D"
                    if adj_trunk in AS.pAS["trunk"]:
                        ip = getattr(adj_trunk, "ipaddress" + direction)
                        
                        interface_ip = " {name}(config-router)# network {ip}\n"\
                                                .format(name=node.name, ip=ip)
                        self.entry_config.insert("insert", interface_ip)
                    else:
                        interface = getattr(adj_trunk, "interface" + direction)
                        pi = " {name}(config-router)# passive-interface {i}\n"\
                                .format(name=node.name, i=interface)
                        self.entry_config.insert("insert", pi)
                
            elif AS.type == "OSPF":
                
                activate_ospf = " {name}(config)# router ospf 1\n"\
                                                    .format(name=node.name)
                self.entry_config.insert("insert", activate_ospf)
                
                for _, adj_trunk in scenario.ntw.graph[node]["trunk"]:
                    direction = "S"*(adj_trunk.source == node) or "D"
                    if adj_trunk in AS.pAS["trunk"]:
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
                
            elif AS.type == "ISIS":
                
                # we need to know:
                # - whether the node is in the backbone area (L1/L2 or L2) 
                # or a L1 area
                # - whether the node is at the edge of its area (L1/L2)
                node_area ,= node.AS[AS]
                in_backbone = node_area.id == 2
                level = "level-1-2" if node in AS.border_routers else (
                        "level-2" if in_backbone else "level-1")
                
                # An IS-IS NET (Network Entity Title) is made up of:
                    # - AFI must be 1 byte
                    # - Area ID can be 0 to 12 bytes long
                    # - System ID must be 6 bytes long
                    # - SEL must be 1 byte
                    
                # The AFI, or the Authority & Format Identifier.
                # In an IP-only environment, this number has no meaning 
                # separate from the Area ID itself. Most vendors and operators 
                # tend to stay compliant with the defunct protocols by 
                # specifying an AFI of “49”. 
                # We will stick to this convention.
                
                # Area ID’s function just as they do in OSPF.
                
                # System ID can be anything chosen by the administrator, 
                # similarly to an OSPF Router ID. However, best practice 
                # with NETs is to keep the configuration as simple as 
                # humanly possible.
                # We will derive it from the router's loopback address
                    
                AFI = "49." + str(format(node_area.id, "04d"))
                sid = ".".join((format(int(n), "03d") for n in node.ipaddress.split(".")))
                net = ".".join((AFI, sid, "00"))
            
                activate_isis = " {name}(config)# router isis\n"\
                                                    .format(name=node.name)
                net_conf = " {name}(config-router)# net {net}\n"\
                                            .format(name=node.name, net=net)                   
                level_conf = " {name}(config-router)# is-type {level}\n"\
                                        .format(name=node.name, level=level)                           
                plo= " {name}(config-router)# passive-interface Loopback0\n"\
                                                .format(name=node.name)
                exit = " {name}(config-router)# exit\n".format(name=node.name)
                                                
                self.entry_config.insert("insert", activate_isis)
                self.entry_config.insert("insert", net_conf)
                self.entry_config.insert("insert", level_conf)
                self.entry_config.insert("insert", plo)
                self.entry_config.insert("insert", exit)
                                   
                for neighbor, adj_trunk in scenario.ntw.graph[node]["trunk"]:
                    
                    # we configure isis only if the neighbor 
                    # belongs to the same AS.
                    if AS in neighbor.AS:
                        direction = "S"*(adj_trunk.source == node) or "D"
                        interface = getattr(adj_trunk, "interface" + direction)
                        interface_conf = " {name}(config)# interface {interface}\n"\
                                        .format(name=node.name, interface=interface)
                        isis_conf = " {name}(config-if)# ip router isis\n"\
                                                            .format(name=node.name)
                                                            
                        # we need to check what area the neighbor belongs to.
                        # If it belongs to the node's area, the interface is 
                        # configured as L1 with circuit-type, else with L2.            
                        neighbor_area ,= neighbor.AS[AS]
                        
                        # we configure circuit-type as level 2 if the routers
                        # belong to different areas, or they both belong to
                        # the backbone
                        l2 = node_area != neighbor_area or node_area.id == 2
                        cct_type = "level-2" if l2 else "level-1"
                        cct_type_conf = " {name}(config-if)# isis circuit-type {ct}\n"\
                                            .format(name=node.name, ct=cct_type)
                            
                        self.entry_config.insert("insert", interface_conf)
                        self.entry_config.insert("insert", isis_conf)
                        self.entry_config.insert("insert", cct_type_conf)
                        
                end = " {name}(config-if)# end\n".format(name=node.name)
                self.entry_config.insert("insert", end)
                
        self.entry_config.pack(fill=tk.BOTH, expand=tk.YES)

        