# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import tkinter as tk
from tkinter import ttk
from miscellaneous.custom_toplevel import CustomTopLevel
from collections import defaultdict
from heapq import heappop, heappush
from . import area
from . import AS_management

class AutonomousSystem(object):
    
    class_type = "AS"
    has_area = False

    def __init__(
                 self, 
                 scenario,
                 name, 
                 id,
                 trunks = set(), 
                 nodes = set(), 
                 imp = False
                 ):
        self.cs = scenario
        self.ntw = self.cs.ntw
        self.name = name
        self.id = id

        # pAS as in "pool AS": same as pool network
        self.pAS = {
        "trunk": set(trunks), 
        "node": set(nodes)
        }
        
        # unselect everything
        scenario.unhighlight_all()
        
    def __repr__(self):
        return self.name
        
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name
        
    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __hash__(self):
        return hash(self.name)
        
    def add_to_AS(self, area, *objects):
        area.add_to_area(*objects)
        for obj in objects:
            # add objects in the AS corresponding pool
            self.pAS[obj.type].add(obj)
        
    def remove_from_AS(self, *objects):
        for obj in objects:
            # we remove the object from its pool in the AS
            self.pAS[obj.type].discard(obj)
            # we pop the AS from the dict of object AS, and retrieve the list
            # of area it belongs to in this AS
            obj_areas = obj.AS.pop(self, set())
            # for each area, we delete the object from the corresponding pool
            for area in obj_areas:
                area.remove_from_area(obj)
                
    def build_RFT(self):
        allowed_nodes = self.pAS['node']
        allowed_trunks =  self.pAS['trunk'] - self.ntw.fdtks
        for node in self.pAS['node']:
            self.RFT_builder(node, allowed_nodes, allowed_trunks)
                
class ASWithArea(AutonomousSystem):
    
    has_area = True
    
    def __init__(self, *args):
        super().__init__(*args)
        
        # areas is a dict associating a name to an area
        self.areas = {}
        
    def area_factory(self, name, id=0, trunks=set(), nodes=set()):
        if name not in self.areas:
            self.areas[name] = area.Area(name, id, self, trunks, nodes)
        return self.areas[name]
        
    def delete_area(self, area):
        # we remove the area of the AS areas dictionary
        area = self.areas.pop(area.name)
        for obj_type in ("node", "trunk"):
            for obj in area.pa[obj_type]:
                # we remove the area to the list of area in the AS 
                # dictionary, for all objects of the area
                obj.AS[area.AS].remove(area)
                
class RIP_AS(AutonomousSystem):
    
    AS_type = "RIP"
    
    def __init__(self, *args):
        *common_args, imp = args
        super().__init__(*common_args)
        
        # management window of the AS 
        self.management = AS_management.RIP_Management(self, imp)
        
        # the metric used to compute the shortest path. By default, it is 
        # a hop count for a RIP AS, and bandwidth-dependent for ISIS or OSPF.
        # if the metric is bandwidth, it is calculated based on the interface
        # of the trunk, and a user-defined reference bandwidth.
        self.metric = "hop count"
        
    def RFT_builder(self, source, allowed_nodes, allowed_trunks):
        K = source.LB_paths
        visited = set()
        # we keep track of all already visited subnetworks so that we 
        # don't add them more than once to the mapping dict.
        visited_subnetworks = set()
        heap = [(0, source, [], None)]
        # cost of the shortesth path to a subnetwork
        SP_cost = {}
        
        while heap:
            dist, node, path_trunk, ex_int = heappop(heap)  
            if (node, ex_int) not in visited:
                visited.add((node, ex_int))
                for neighbor, l3vc in self.ntw.graph[node.id]['l3vc']:
                    adj_trunk = l3vc("link", node)
                    remote_trunk = l3vc("link", neighbor)
                    if adj_trunk in path_trunk:
                        continue
                    # excluded and allowed nodes
                    if neighbor not in allowed_nodes:
                        continue
                    # excluded and allowed trunks
                    if adj_trunk not in allowed_trunks: 
                        continue
                    if node == source:
                        ex_ip = remote_trunk('ipaddress', neighbor)
                        ex_int = adj_trunk('interface', source)
                        source.rt[adj_trunk.sntw] = {('C', ex_ip, ex_int,
                                            dist, neighbor, adj_trunk)}
                        SP_cost[adj_trunk.sntw] = 0
                    heappush(heap, (dist + adj_trunk('cost', node), 
                            neighbor, path_trunk + [adj_trunk], ex_int))
                    
            if path_trunk:
                trunk = path_trunk[-1]
                ex_tk = path_trunk[0]
                nh = ex_tk.destination if ex_tk.source == source else ex_tk.source
                ex_ip = ex_tk("ipaddress", nh)
                ex_int = ex_tk("interface", source)
                if trunk.sntw not in source.rt:
                    SP_cost[trunk.sntw] = dist
                    source.rt[trunk.sntw] = {('R', ex_ip, ex_int, 
                                                dist, nh, ex_tk)}
                else:
                    if (dist == SP_cost[trunk.sntw] 
                        and K > len(source.rt[trunk.sntw])):
                        source.rt[trunk.sntw].add(('R', ex_ip, ex_int, 
                                                dist, nh, ex_tk))
        
class ISIS_AS(ASWithArea):
    
    AS_type = "ISIS"
    
    def __init__(self, *args):
        *common_args, imp = args
        super().__init__(*common_args)
        self.metric = "bandwidth"
        
        # management window of the AS 
        self.management = AS_management.ISIS_Management(self, imp)
        
        # contains all L1/L2 nodes
        self.border_routers = set()
        
        # imp tells us if the AS is imported or created from scratch.
        trunks, nodes = self.pAS["node"], self.pAS["trunk"]
        if not imp:
            self.area_factory("Backbone", id=2, trunks=trunks, nodes=nodes)
            
    def RFT_builder(self, source, allowed_nodes, allowed_trunks):
        K = source.LB_paths
        visited = set()
        # we keep track of all already visited subnetworks so that we 
        # don't add them more than once to the mapping dict.
        visited_subnetworks = set()
        heap = [(0, source, [], None)]
        # source area: we make sure that if the node is connected to an area,
        # the path we find to any subnetwork in that area is an intra-area path.
        src_areas = source.AS[self]
        # cost of the shortesth path to a subnetwork
        SP_cost = {}
                
        # if source is an L1 there will be a default route to
        # 0.0.0.0 heading to the closest L1/L2 node.
        src_area ,= source.AS[self]
        
        # we keep a boolean telling us if source is L1 so that we know we
        # must add the i*L1 default route when we first meet a L1/L2 node
        # and all other routes are i L1 as rtype (route type).
        isL1 = source not in self.border_routers and src_area.name != 'Backbone'
        
        while heap:
            dist, node, path_trunk, ex_int = heappop(heap)  
            if (node, ex_int) not in visited:
                visited.add((node, ex_int))
                for neighbor, l3vc in self.ntw.graph[node.id]['l3vc']:
                    adj_trunk = l3vc("link", node)
                    remote_trunk = l3vc("link", neighbor)
                    if adj_trunk in path_trunk:
                        continue
                    # excluded and allowed nodes
                    if neighbor not in allowed_nodes:
                        continue
                    # excluded and allowed trunks
                    if adj_trunk not in allowed_trunks: 
                        continue
                    if node == source:
                        ex_ip = remote_trunk('ipaddress', neighbor)
                        ex_int = adj_trunk('interface', source)
                        source.rt[adj_trunk.sntw] = {('C', ex_ip, ex_int,
                                            dist, neighbor, adj_trunk)}
                        SP_cost[adj_trunk.sntw] = 0
                    heappush(heap, (dist + adj_trunk('cost', node), 
                            neighbor, path_trunk + [adj_trunk], ex_int))
                    
            if path_trunk:
                trunk = path_trunk[-1]
                ex_tk = path_trunk[0]
                nh = ex_tk.destination if ex_tk.source == source else ex_tk.source
                ex_ip = ex_tk("ipaddress", nh)
                ex_int = ex_tk("interface", source)
                if isL1:
                    if (node in self.border_routers 
                                        and '0.0.0.0' not in source.rt):
                        source.rt['0.0.0.0'] = {('i*L1', ex_ip, ex_int,
                                                    dist, nh, ex_tk)}
                    else:
                        if (('i L1', trunk.sntw) not in visited_subnetworks 
                                        and trunk.AS[self] & ex_tk.AS[self]):
                            visited_subnetworks.add(('i L1', trunk.sntw))
                            source.rt[trunk.sntw] = {('i L1', ex_ip, ex_int,
                                    dist + trunk('cost', node), nh, ex_tk)}
                else:
                    trunkAS ,= trunk.AS[self]
                    exit_area ,= ex_tk.AS[self]
                    rtype = 'i L1' if (trunk.AS[self] & ex_tk.AS[self] and 
                                    trunkAS.name != 'Backbone') else 'i L2'
                    # we favor intra-area routes by excluding a 
                    # route if the area of the exit trunk is not
                    # the one of the subnetwork
                    if (not ex_tk.AS[self] & trunk.AS[self] 
                                    and trunkAS.name == 'Backbone'):
                        continue
                    # if the source is an L1/L2 node and the destination
                    # is an L1 area different from its own, we force it
                    # to use the backbone by forbidding it to use the
                    # exit interface in the source area
                    if (rtype == 'i L2' and source in self.border_routers and 
                                exit_area.name != 'Backbone'):
                        continue
                    if (('i L1', trunk.sntw) not in visited_subnetworks 
                        and ('i L2', trunk.sntw) not in visited_subnetworks):
                        visited_subnetworks.add((rtype, trunk.sntw))
                        source.rt[trunk.sntw] = {(rtype, ex_ip, ex_int,
                                dist + trunk('cost', node), nh, ex_tk)}
                    # TODO
                    # IS-IS uses per-address unequal cost load balancing 
                    # a user-defined variance defined as a percentage of the
                    # primary path cost defines which paths can be used
                    # (up to 9).
                
class OSPF_AS(ASWithArea):
    
    AS_type = "OSPF"
    
    def __init__(self, *args):
        *common_args, imp = args
        super().__init__(*common_args)
        self.metric = "bandwidth"
        self.ref_bw = 10**8
        
        # management window of the AS 
        self.management = AS_management.OSPF_Management(self, imp)
        
        # contains all ABRs
        self.border_routers = set()
        
        # node used to exit the domain (ASBR for OSPF)
        self.exit_point = None
        
        # imp tells us if the AS is imported or created from scratch.
        trunks, nodes = self.pAS["node"], self.pAS["trunk"]
        if not imp:
            self.area_factory("Backbone", id=0, trunks=trunks, nodes=nodes)
            
    def RFT_builder(self, source, allowed_nodes, allowed_trunks):
        print(source)
        K = source.LB_paths
        visited = set()
        # we keep track of all already visited subnetworks so that we 
        # don't add them more than once to the mapping dict.
        visited_subnetworks = set()
        heap = [(0, source, [], None)]
        # source area: we make sure that if the node is connected to an area,
        # the path we find to any subnetwork in that area is an intra-area path.
        src_areas = source.AS[self]
        # cost of the shortesth path to a subnetwork
        SP_cost = {}
        
        while heap:
            dist, node, path_trunk, ex_int = heappop(heap)  
            if (node, ex_int) not in visited:
                visited.add((node, ex_int))
                for neighbor, l3vc in self.ntw.graph[node.id]['l3vc']:
                    adj_trunk = l3vc("link", node)
                    remote_trunk = l3vc("link", neighbor)
                    if adj_trunk in path_trunk:
                        continue
                    # excluded and allowed nodes
                    if neighbor not in allowed_nodes:
                        continue
                    # excluded and allowed trunks
                    if adj_trunk not in allowed_trunks: 
                        continue
                    if node == source:
                        ex_ip = remote_trunk('ipaddress', neighbor)
                        ex_int = adj_trunk('interface', source)
                        source.rt[adj_trunk.sntw] = {('C', ex_ip, ex_int,
                                            dist, neighbor, adj_trunk)}
                        SP_cost[adj_trunk.sntw] = 0
                    heappush(heap, (dist + adj_trunk('cost', node), 
                            neighbor, path_trunk + [adj_trunk], ex_int))
                    
            if path_trunk:
                trunk = path_trunk[-1]
                ex_tk = path_trunk[0]
                nh = ex_tk.destination if ex_tk.source == source else ex_tk.source
                ex_ip = ex_tk("ipaddress", nh)
                ex_int = ex_tk("interface", source)
                # we check if the trunk has any common area with the
                # exit trunk: if it does not, it is an inter-area route.
                rtype = 'O' if (trunk.AS[self] & ex_tk.AS[self]) else 'O IA'
                if trunk.sntw not in source.rt:
                    SP_cost[trunk.sntw] = dist
                    source.rt[trunk.sntw] = {(rtype, ex_ip, ex_int, 
                                                dist, nh, ex_tk)}
                else:
                    for route in source.rt[trunk.sntw]:
                        break
                    if route[0] == 'O' and rtype == 'IA':
                        continue
                    elif route[0] == 'O IA' and rtype == 'O':
                        SP_cost[trunk.sntw] = dist
                        source.rt[trunk.sntw] = {(rtype, ex_ip, ex_int, 
                                                dist, nh, ex_tk)}
                    else:
                        if (dist == SP_cost[trunk.sntw]
                            and K > len(source.rt[trunk.sntw])):
                            source.rt[trunk.sntw].add((
                                                    rtype, ex_ip, ex_int, 
                                                        dist, nh, ex_tk
                                                        ))
                if (rtype, trunk.sntw) not in visited_subnetworks:
                    if ('O', trunk.sntw) in visited_subnetworks:
                        continue
                    else:
                        visited_subnetworks.add((rtype, trunk.sntw))
                        source.rt[trunk.sntw] = {(rtype, ex_ip, ex_int, 
                                                        dist, nh, ex_tk)}
            
    # def add_to_ASBR(self, node):
    #     self.pAS["edge"].add(node)
    #     
    # def remove_from_ASBR(self, node):
    #     self.pAS["edge"].discard(node)
                    
class ModifyAS(CustomTopLevel):
    def __init__(self, scenario, mode, obj, AS=set()):
        super().__init__()
        # TODO put that in the dict
        titles = {
        "add": "Add to AS/area", 
        "remove": "Remove from AS", 
        "remove area": "Remove from area",
        "manage": "Manage AS"
        }
        self.title(titles[mode])
        # always at least one row and one column with a weight > 0
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        if mode == "add":
            command = lambda: self.add(scenario, *obj)
            values = tuple(map(str, scenario.ntw.pnAS.values()))
        elif mode == "remove":
            values = tuple(map(str, AS))
            command = lambda: self.remove_from_AS(scenario, *obj)
        elif mode == "remove area":
            values = tuple(map(str, AS))
            command = lambda: self.remove_from_area(scenario, *obj)
        elif mode == "manage":
            values = tuple(map(str, AS))
            command = lambda: self.manage_AS(scenario)
        
        # List of existing AS
        self.AS_list = ttk.Combobox(self, width=9)
        self.AS_list["values"] = values
        self.AS_list.current(0)
        self.AS_list.grid(row=0, column=0, columnspan=2, 
                                            pady=5, padx=5, sticky="nsew")
        self.AS_list.bind('<<ComboboxSelected>>', 
                                        lambda e: self.update_value(scenario))
        
        if mode in ("add", "remove area"):
            self.area_list = ttk.Combobox(self, width=9)
            self.update_value(scenario)
            self.area_list.current(0)
            self.area_list.grid(row=1, column=0, columnspan=2, 
                                            pady=5, padx=5, sticky="nsew")
        
        # Button to add in an AS
        self.button_add_AS = ttk.Button(self, text="OK", command=command)
        #row = 2 if mode in ("add", "remove area") else 1
        self.button_add_AS.grid(row=2, column=0, columnspan=2, 
                                            pady=5, padx=5, sticky="nsew")
        
    # when a different AS is selected, the area combobox is updated accordingly
    def update_value(self, scenario):
        selected_AS = scenario.ntw.AS_factory(name=self.AS_list.get())
        self.area_list["values"] = tuple(map(str, selected_AS.areas))
        
    # TODO merge these three functions into one with the mode 
    # they share the check + destroy
    def add(self, scenario, *objects):
        selected_AS = scenario.ntw.AS_factory(name=self.AS_list.get())
        selected_AS.management.add_to_AS(self.area_list.get(), *objects)
        self.destroy()
        
    def remove_from_area(self, scenario, *objects):
        selected_AS = scenario.ntw.AS_factory(name=self.AS_list.get())
        selected_AS.management.remove_from_area(self.area_list.get(), *objects)
        self.destroy()
        
    def remove_from_AS(self, scenario, *objects):
        selected_AS = scenario.ntw.AS_factory(name=self.AS_list.get())
        selected_AS.management.remove_from_AS(*objects)
        self.destroy()
        
    def manage_AS(self, scenario):
        selected_AS = scenario.ntw.AS_factory(name=self.AS_list.get())
        selected_AS.management.deiconify()
        self.destroy()
        
class ASCreation(CustomTopLevel):
    def __init__(self, scenario, nodes, trunks):
        super().__init__()
        self.so = scenario.so
        self.title("Create AS")
        
        # List of AS type
        self.var_AS_type = tk.StringVar()
        self.AS_type_list = ttk.Combobox(self, 
                                    textvariable=self.var_AS_type, width=6)
        self.AS_type_list["values"] = ("RIP", "ISIS", "OSPF", "RSTP", "BGP")
        self.AS_type_list.current(0)

        # retrieve and save node data
        self.button_create_AS = ttk.Button(self, text="Create AS", 
                        command=lambda: self.create_AS(scenario, nodes, trunks))
        
        # Label for the name/type of the AS
        self.label_name = tk.Label(self, bg="#A1DBCD", text="Name")
        self.label_type = tk.Label(self, bg="#A1DBCD", text="Type")
        self.label_id = tk.Label(self, bg="#A1DBCD", text="ID")
        
        # Entry box for the name of the AS
        self.entry_name  = tk.Entry(self, width=10)
        self.entry_id  = tk.Entry(self, width=10)
        
        self.label_name.grid(row=0, column=0, pady=5, padx=5, sticky=tk.W)
        self.label_id.grid(row=1, column=0, pady=5, padx=5, sticky=tk.W)
        self.entry_name.grid(row=0, column=1, sticky=tk.W)
        self.entry_id.grid(row=1, column=1, sticky=tk.W)
        self.label_type.grid(row=2, column=0, pady=5, padx=5, sticky=tk.W)
        self.AS_type_list.grid(row=2, column=1, pady=5, padx=5, sticky=tk.W)
        self.button_create_AS.grid(row=3, column=0, columnspan=2, pady=5, padx=5)

    def create_AS(self, scenario, nodes, trunks):
        # automatic initialization of the AS id in case it is empty
        if self.entry_id.get():
            id = int(self.entry_id.get())
        else:
            id = len(scenario.ntw.pnAS) + 1
        
        new_AS = scenario.ntw.AS_factory(
                                         self.var_AS_type.get(), 
                                         self.entry_name.get(), 
                                         id,
                                         trunks, 
                                         nodes
                                         )
        self.destroy()
            