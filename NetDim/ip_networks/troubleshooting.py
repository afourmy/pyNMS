# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

from tkinter import ttk
from miscellaneous.custom_scrolledtext import CustomScrolledText
import tkinter as tk

class Troubleshooting(tk.Toplevel):
    def __init__(self, node, scenario):
        super().__init__() 
        
        notebook = ttk.Notebook(self)

        
        self.wm_attributes("-topmost", True)
        
        ## General troubleshooting commands
        
        debug_frame = ttk.Frame(notebook)
        st_debug = CustomScrolledText(debug_frame)
        notebook.add(debug_frame, text=" General troubleshooting commands ")
                
        show_ip_route = "show ip route (sh ip ro)"
        show_ip_route_text = """

    Displays the IP routing table of the router, which contains:
        - directly connected subnet (C)
        - default (*) and static routes (S)
        - routes dynamically learned from a routing protocol:
            * RIP (R)
            * OSPF (O (intra-area), O IA (inter-area))
            * IS-IS (i L1 (intra-area), i L2 (inter-area))
    For each entry, there are two numbers in bracket: the first one is the
    administrative distance, and the second one is the metric.
    It also indicates the "gateway of last resort": the path the router 
    use in case no other path is available.
    
        """
        
        show_ip_protocols = "show ip protocols (sh ip pro)"
        show_ip_protocols_text = """
        
    Displays all IP protocols that have been configured and are running on
    the router, with the following information:
        - Timers:
            * Routing updates interval (default: 30s) 
            * Invalid (time interval after which a route is declared invalid /
            default: 180s)
            * Flush (~ route garbage collection: time that must pass
            before the route is removed from the routing table / default: 240s)
        - Version of the protocol
        - Maximum path (~ number of path used for load-sharing)
        - Default administrative distance
        
    Under the line "Routing for Networks", there is the list of networks
    the protocol knows about.
    This is a way to check for which interfaces a given protocol is enabled.
    It also displays the list of passive interfaces for that protocol.
    
        """
        
        show_ip_interface = "show interface (sh int)"
        show_ip_interface_text = """
        
    Displays many information about the configuration and status of all 
    interfaces, among which:
        - Interface status
        - IP address and subnet mask
        - Protocol status on the interface
        - MTU, bandwidth, utilization, errors 
        
        """
        
        show_ip_interface_brief = "show interface (sh int)"
        show_ip_interface_brief_text = """
        
    Displays a summary of IP related information for all interfaces:
        - IP address and subnet mask of the interface
        - Administrative status (up / down)
        - Status of the IP protocol (up / down)
        
        """
        
        show_running_configuration = "show running configuration (sh run)"
        show_running_configuration_text = """
        
    Displays the configuration in the memory.
    This configuration is not saved until the following command is entered:
    "copy running-configuration startup-configuration" ("copy run start").
    
        """
        
        st_debug.insert("insert", "        ")
        st_debug.insert("insert", show_ip_route, "title")
        st_debug.insert("insert", show_ip_route_text)
        st_debug.insert("insert", show_ip_protocols, "title")
        st_debug.insert("insert", show_ip_protocols_text)
        st_debug.insert("insert", show_ip_interface, "title")
        st_debug.insert("insert", show_ip_interface_text)
        st_debug.insert("insert", show_ip_interface_brief, "title")
        st_debug.insert("insert", show_ip_interface_brief_text)
        st_debug.insert("insert", show_running_configuration, "title")
        st_debug.insert("insert", show_running_configuration_text)
        
        # disable the scrolledtext so that it cannot be edited
        st_debug.config(state=tk.DISABLED)
        # pack the scrolledtext in the frames, and the notebook in the window
        st_debug.pack(fill=tk.BOTH, expand=tk.YES)
        
        if any(AS.type == "RIP" for AS in node.AS):
            
            ## RIP Troubleshooting

            debug_rip = ttk.Frame(notebook)
            st_debug_rip = CustomScrolledText(debug_rip)
            notebook.add(debug_rip, text=" RIP Troubleshooting ")
    
            debug_ip_rip = "debug ip rip (deb ip rip)"
            debug_ip_rip_text = """
        
    Displays the RIP routing updates sent and received sent on the router's
    interfaces, and detects potential issues:
        - Mismatch in the RIP version
        
    The debug mode can be deactivated by typing:
        - no debug rip (rip only) / no debug all (all debug modes)
        - equivalently: undebug rip / undebug all
            
        """
            
            show_ip_rip_database = "show ip rip databse (sh ip rip)"
            show_ip_rip_database_text = """
        
    Displays all summary address entries in the RIP routing database.
    If an address is not in this database, it cannot be advertised.
        
        """
        
            st_debug_rip.insert("insert", "        ")
            st_debug_rip.insert("insert", debug_ip_rip, "title")
            st_debug_rip.insert("insert", debug_ip_rip_text)
            
            st_debug_rip.config(state=tk.DISABLED)
            st_debug_rip.pack(fill=tk.BOTH, expand=tk.YES)
            
        if any(AS.type == "OSPF" for AS in node.AS):
        
            ## OSPF Information
            
            ospf_info = ttk.Frame(notebook)
            st_ospf_info = CustomScrolledText(ospf_info)
            notebook.add(ospf_info, text=" OSPF Information ")
            
            ospf_introduction = """
        
    OSPF in an open-standard link-state protocol (RFC 2328), with the 
    following characteristics:
    - uses SPF (Dijkstra) to provide a loop-free topology
    - fast convergence
    - incremental updates with Link-State Advertisements (LSAs)
    - supports load-balancing 
    - computes the default metric based on the bandwidth of the interface
    
    Running OSPF on a router has the following disadvantages:
    - requires a lot of memory (adjacency topology and routing table)
    - requires a lot of CPU processing (to run the SPF algorithm)
    
    For scalability purposes, an OSPF network can be broken down into 
    multiple areas to provide a hierarchical topology. 
    An area is a group of contiguous links (networks) defined by an "Area ID". 
    The backbone's ID is 0.
        
        """
            
            multi_area_design = "Design of a multi-area OSPF topology"
            multi_area_design_text = """
        
    All areas must be connected to the main area, called the "Backbone".
    An area in OSPF is a set of links.
    A link cannot belong to more than one area. 
    After all areas have been defined as sets of links, the "Update topology" 
    mechanism in the "Manage AS" window must be triggered to automatically 
    assign areas to the routers. 
    A router at the edge of two or more areas is called an "Area Border Router".
        
        """
            
            cost_assignment = "OSPF metric: cost assignment"
            cost_assignment_text = """
        
    In OSPF, the cost of a link is computed by default with the 
    following formula: Cost = Bandwidth reference / Link bandwidth. 
    The bandwidth reference default to 10^8 bps.
    The interface of a link can be changed from the property panel 
    (right-click on a link > Properties), but this will not automatically
    update the OSPF metric of the link.
    The "Update costs" mechanism must be triggered in the "Manage AS" window:
    it will compute and update the cost of the link for all links in the AS.
        
        """
            
            load_balancing = "OSPF load-balancing"
            load_balancing_text = """
        
    In OSPF, the traffic can be load-balanced (shared) on multiple 
    "Equal-Cost Multi-Paths" (ECMP). 
    By default, the number of routes used for load-balancing is 4, but this can
    be modified from the property panel (right-click on a router > Properties).
    A router is capable of load-balancing the traffic on up to 16 routes.
        
        """
            
            router_id = "OSPF router ID"
            router_id_text = """
        
    Each router has a ID which must be unique within the entire OSPF network: 
    it is a 32-bit IP address selected at the start of the OSPF process. 
    The router ID is chosen as:
    - the highest IP address among all router's active loopback interfaces 
    - if there is no activate loopback interface, the highest IP address 
    among all interfaces. 
    Once the router ID is elected, it does not change unless OSPF restarts, 
    or unless it is manually changed with the "router-id 32-bit-ip-address" 
    command under router ospf process-id.
    This ID is used by the router to announce itself to the other OSPF routers.
        
        """
            
            neighbors = "OSPF neighbors"
            neighbors_text = """
        
    A router learns about its OSPF neighbors and the AS topology by exchange 
    Link State Advertisements (LSA). An LSA is an OSPF packet that contains 
    link-state and routing information.
    It builds an "adjacency topology": an adjacency is a relationship between 
    two OSPF neighbors that allows for the exchange of route updates. 
    Only neighbors with an established "adjacency" share routes.
        
        """
            
            states = "OSPF states"
            states_text = """
        
    When OSPF adjacency is formed, a router goes through several state changes 
    before it becomes fully adjacent with its neighbor.
    The main states are:
    - Down: This is the first OSPF neighbor state. It means that no information 
    ("Hello" LSA) has been received from this neighbor, but hello packets 
    can still be sent to the neighbor in this state.
    
    - 2-way: This state designates that bi-directional communication has been 
    established between two routers. Bi-directional means that each router has 
    seen the other's Hello packet. This state is attained when the router 
    receiving the hello packet sees its own Router ID within the received 
    Hello packet's neighbor field. Once the routers have entered a 
    two-way state, they are considered "neighbors".
    
    - Full: in this state, routers are fully adjacent with each other. 
    All the router and network LSAs are exchanged and the routers' databases 
    are fully synchronized. 
    Full is the normal state for an OSPF router. 
    If a router is stuck in another state, it is an indication that there are 
    problems in forming adjacencies.
    
    A 2-way state indicates that the two OSPF routers are neighbors, 
    but a full state means the completion of sharing links between routers.
        
        """
            
            st_ospf_info.insert("insert", "        ")
            st_ospf_info.insert("insert", "OSPF", "title")
            st_ospf_info.insert("insert", ospf_introduction)
            st_ospf_info.insert("insert", multi_area_design, "title")
            st_ospf_info.insert("insert", multi_area_design_text)
            st_ospf_info.insert("insert", cost_assignment, "title")
            st_ospf_info.insert("insert", cost_assignment_text)
            st_ospf_info.insert("insert", load_balancing, "title")
            st_ospf_info.insert("insert", load_balancing_text)
            st_ospf_info.insert("insert", router_id, "title")
            st_ospf_info.insert("insert", router_id_text)
            st_ospf_info.insert("insert", neighbors, "title")
            st_ospf_info.insert("insert", neighbors_text)
            
            # disable the scrolledtext so that it cannot be edited
            st_ospf_info.config(state=tk.DISABLED)
            # pack the scrolledtext in the frames
            st_ospf_info.pack(fill=tk.BOTH, expand=tk.YES)
            
            ## OSPF Troubleshooting commands
            
            ospf_troubleshooting = ttk.Frame(notebook)
            st_ospf_troubleshooting = CustomScrolledText(ospf_troubleshooting)
            notebook.add(ospf_troubleshooting, text=" OSPF Troubleshooting")
            
            show_ip_ospf = "show ip ospf (sh ip ospf)"
            show_ip_ospf_text = """
        
    Displays an overview of the router's OSPF configuration:
    - Process ID and router ID
    - Areas the router is connected to
    - Number of interfaces in each area
    - Number of times the SPF algorithm was computed (per area)
        
        """
            
            show_ip_ospf_int_br = "show ip ospf interface brief (sh ip int br)"
            show_ip_ospf_int_br_text = """
        
    Displays the following information about all router's interfaces:
    - the IP address and the area it belongs to
    - the ID of the OSPF process
    - the OSPF router id
    - the cost of the interface (used for SPF algorithm)
    - the state of the interface
        
        """
            
            show_ip_ospf_neighbor = "show ip ospf neighbor (sh ip o n)"
            show_ip_ospf_neighbor_text = """
        
    Displays OSPF-related information about all neighbors:
    - neighbor ID
    - neighbor state
    - neighbor IP address
    - neighbor interface
        
        """
            
            debug_ip_ospf_adj = "debug ip ospf adj (deb ip o a)"
            debug_ip_ospf_adj_text = """
        
    Displays the following information:
    - DR/BDR election process and sharing of links with the DR
    - Mismatch authentication type (example: clear-text passwords on 
    one router, MD5 on the other)
    - Mismatch authentication key
        
        """
            
            debug_ip_ospf_events = "debug ip ospf events (deb ip o e)"
            debug_ip_ospf_events_text = """
        
    Displays the following information:
    - Mismatched hello intervals 
    - Mismatched dead intervals
    - Mismatched subnet masks
        
        """
            
            debug_ip_ospf_events = "debug ip ospf events (deb ip o e)"
            debug_ip_ospf_events_text = """
        
    Displays the following information:
    - Mismatched hello intervals 
    - Mismatched dead intervals
    - Mismatched subnet masks
        
        """
            
            st_ospf_troubleshooting.insert("insert", "        ")
            st_ospf_troubleshooting.insert("insert", show_ip_ospf, "title")
            st_ospf_troubleshooting.insert("insert", show_ip_ospf_text)
            st_ospf_troubleshooting.insert("insert", show_ip_ospf_int_br, "title")
            st_ospf_troubleshooting.insert("insert", show_ip_ospf_int_br_text)
            st_ospf_troubleshooting.insert("insert", show_ip_ospf_neighbor, "title")
            st_ospf_troubleshooting.insert("insert", show_ip_ospf_neighbor_text)
            st_ospf_troubleshooting.insert("insert", debug_ip_ospf_adj, "title")
            st_ospf_troubleshooting.insert("insert", debug_ip_ospf_adj_text)
            st_ospf_troubleshooting.insert("insert", debug_ip_ospf_events, "title")
            st_ospf_troubleshooting.insert("insert", debug_ip_ospf_events_text)
    
            # disable the scrolledtext so that it cannot be edited
            st_ospf_troubleshooting.config(state=tk.DISABLED)
            # pack the scrolledtext in the frames
            st_ospf_troubleshooting.pack(fill=tk.BOTH, expand=tk.YES)

        notebook.pack(fill=tk.BOTH, expand=tk.YES)