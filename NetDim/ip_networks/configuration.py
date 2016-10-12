# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk
from tkinter import ttk
import re
from miscellaneous.custom_scrolledtext import CustomScrolledText
from miscellaneous.network_functions import tomask

class Configuration(tk.Toplevel):
    def __init__(self, node, scenario):
        super().__init__() 
        self.cs = scenario
        
        notebook = ttk.Notebook(self)
        pastable_config_frame = ttk.Frame(notebook)
        detailed_config_frame = ttk.Frame(notebook)
        st_pastable_config = CustomScrolledText(pastable_config_frame)
        st_detailed_config = CustomScrolledText(detailed_config_frame)
        notebook.add(pastable_config_frame, text="Pastable configuration ")
        notebook.add(detailed_config_frame, text="Detailed configuration ")
        
        self.wm_attributes("-topmost", True)
        
        for conf in self.build_config(node):
            pastable_conf = re.search("[#|>](.*)", conf).group(1) + "\n"
            st_detailed_config.insert("insert", conf)
            st_pastable_config.insert("insert", pastable_conf)
            
        # disable the scrolledtext so that it cannot be edited
        st_pastable_config.config(state=tk.DISABLED)
        st_detailed_config.config(state=tk.DISABLED)
        
        
        # pack the scrolledtexts in the frames
        st_pastable_config.pack(fill=tk.BOTH, expand=tk.YES)
        st_detailed_config.pack(fill=tk.BOTH, expand=tk.YES)
        
        # and the notebook in the window
        notebook.pack(fill=tk.BOTH, expand=tk.YES)
        
    def build_config(self, node):

        # initialization
        yield " {name}> enable\n".format(name=node.name)  
        yield " {name}# configure terminal\n".format(name=node.name)
        
        # configuration of the loopback interface
        yield " {name}(config)# interface Loopback0\n".format(name=node.name)
        yield " {name}(config-if)# ip address {ip} {mask}\n"\
                                        .format(
                                                name = node.name, 
                                                ip = node.ipaddress, 
                                                mask = node.subnetmask
                                                )
                
        yield " {name}(config-if)# exit\n".format(name=node.name)
        
        for _, sr in self.cs.ntw.gftr(node, "route", "static route", False):
            sntw, mask = sr.dst_sntw.split("/")
            mask = tomask(int(mask))
            yield " {name}(config)# ip route {sntw} {mask} {nh_ip}\n"\
                                    .format(
                                            name = node.name, 
                                            sntw = sntw,
                                            mask = mask,
                                            nh_ip = sr.nh_ip
                                            )
            
        if node.bgp_AS:
            AS = self.cs.ntw.pnAS[node.bgp_AS]
            yield " {name}(config)# router bgp {AS_id}\n"\
                                        .format(name=node.name, AS_id=AS.id)
            
        for bgp_nb, bgp_pr in self.cs.ntw.gftr(node, "route", "BGP peering"):
            nb_AS = self.cs.ntw.pnAS[bgp_nb.bgp_AS]
            yield " {name}(config-router)# neighbor {ip} remote-as {AS}\n"\
                                    .format(
                                            name = node.name, 
                                            ip = bgp_pr("ip", bgp_nb),
                                            AS = nb_AS.id
                                            )
        
        for neighbor, adj_trunk in self.cs.ntw.graph[node]["trunk"]:
            direction = "S"*(adj_trunk.source == node) or "D"
            interface = getattr(adj_trunk, "interface" + direction)
            ip = getattr(adj_trunk, "ipaddress" + direction)
            mask = getattr(adj_trunk, "subnetmask" + direction)
            
            yield " {name}(config)# interface {interface}\n"\
                                    .format(name=node.name, interface=interface)
            yield " {name}(config-if)# ip address {ip} {mask}\n"\
                                    .format(name=node.name, ip=ip, mask=mask)
            yield " {name}(config-if)# no shutdown\n".format(name=node.name)
            
            if any(AS.type == "OSPF" for AS in adj_trunk.AS):
                direction = "SD" if direction == "S" else "DS"
                cost = getattr(adj_trunk, "cost" + direction)
                if cost != 1:
                    yield (" {name}(config-if)#"
                                    " ip ospf cost {cost}\n")\
                                    .format(name=node.name, cost=cost)
                    
            # IS-IS is configured both in "config-router" mode and on the 
            # interface itself: the code is set here so that the user doesn't
            # have the exit the interace, then come back to it for IS-IS.
            for AS in node.AS:
                
                # we configure isis only if the neighbor 
                # belongs to the same AS.
                if AS in neighbor.AS and AS.type == "ISIS":
                    
                    node_area ,= node.AS[AS]
                    in_backbone = node_area.name == "Backbone"
                    
                    # activate IS-IS on the interface
                    yield " {name}(config-if)# ip router isis\n"\
                                                        .format(name=node.name)
                                                        
                    # we need to check what area the neighbor belongs to.
                    # If it belongs to the node's area, the interface is 
                    # configured as L1 with circuit-type, else with L2.            
                    neighbor_area ,= neighbor.AS[AS]
                    
                    # we configure circuit-type as level 2 if the routers
                    # belong to different areas, or they both belong to
                    # the backbone
                    l2 = node_area != neighbor_area or in_backbone
                    cct_type = "level-2" if l2 else "level-1"
                    yield " {name}(config-if)# isis circuit-type {ct}\n"\
                                        .format(name=node.name, ct=cct_type)
                    
            yield " {name}(config-if)# exit\n".format(name=node.name)
            
        for AS in node.AS:
            
            if AS.type == "RIP":
                yield " {name}(config)# router rip\n"\
                                                .format(name=node.name)
                
                for _, adj_trunk in self.cs.ntw.graph[node]["trunk"]:
                    direction = "S"*(adj_trunk.source == node) or "D"
                    if adj_trunk in AS.pAS["trunk"]:
                        ip = getattr(adj_trunk, "ipaddress" + direction)
                        
                        yield " {name}(config-router)# network {ip}\n"\
                                                .format(name=node.name, ip=ip)
                    else:
                        interface = getattr(adj_trunk, "interface" + direction)
                        yield " {name}(config-router)# passive-interface {i}\n"\
                                .format(name=node.name, i=interface)
                
            elif AS.type == "OSPF":
                
                yield " {name}(config)# router ospf 1\n"\
                                                    .format(name=node.name)
                
                for _, adj_trunk in self.cs.ntw.graph[node]["trunk"]:
                    direction = "S"*(adj_trunk.source == node) or "D"
                    if adj_trunk in AS.pAS["trunk"]:
                        ip = getattr(adj_trunk, "ipaddress" + direction)
                        trunk_area ,= adj_trunk.AS[AS]
                        yield (" {name}(config-router)# network" 
                                        " {ip} 0.0.0.3 area {area_id}\n")\
                        .format(name=node.name, ip=ip, area_id=trunk_area.id)
                            
                    else:
                        interface = getattr(adj_trunk, "interface" + direction)
                        yield " {name}(config-router)# passive-interface {i}\n"\
                                .format(name=node.name, i=interface)
                        
                if AS.exit_point == node:
                    yield " {name}(config-router)# default-information originate\n"\
                                                        .format(name=node.name)
                
            elif AS.type == "ISIS":
                
                # we need to know:
                # - whether the node is in the backbone area (L1/L2 or L2) 
                # or a L1 area
                # - whether the node is at the edge of its area (L1/L2)
                node_area ,= node.AS[AS]
                in_backbone = node_area.name == "Backbone"
                level = "level-1-2" if node in AS.border_routers else (
                        "level-2" if in_backbone else "level-1")
                
                # An IS-IS NET (Network Entity Title) is made up of:
                    # - AFI must be 1 byte
                    # - Area ID can be 0 to 12 bytes long
                    # - System ID must be 6 bytes long
                    # - SEL must be 1 byte
                    
                # The AFI, or the Authority & Format Identifier.
                # In an IP-only environment, this number has no meaning 
                # separate from the Area ID it Most vendors and operators 
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
            
                yield " {name}(config)# router isis\n"\
                                                    .format(name=node.name)
                yield " {name}(config-router)# net {net}\n"\
                                            .format(name=node.name, net=net)                   
                yield " {name}(config-router)# is-type {level}\n"\
                                        .format(name=node.name, level=level)                           
                yield " {name}(config-router)# passive-interface Loopback0\n"\
                                                .format(name=node.name)
                yield " {name}(config-router)# exit\n".format(name=node.name)
                
        # configuration of the static routes, including the default one
        if node.default_route:
            yield " {name}(config)# ip route 0.0.0.0 0.0.0.0 {def_route}\n"\
                    .format(name=node.name, def_route=node.default_route)
                    
        yield " {name}(config)# end\n".format(name=node.name)
