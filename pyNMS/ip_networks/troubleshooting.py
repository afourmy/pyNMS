# Copyright (C) 2017 Antoine Fourmy <antoine dot fourmy at gmail dot com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from miscellaneous.decorators import update_paths
from pyQT_widgets.Q_console_edit import QConsoleEdit
from PyQt5.QtWidgets import QWidget, QTabWidget, QTextEdit, QGridLayout

class TroubleshootingWindow(QTabWidget):
    
    @update_paths
    def __init__(self, node, controller):
        super().__init__()
        self.setMinimumSize(1000, 800)
        
        ## General troubleshooting commands
        
        debug_edit = QConsoleEdit()
        self.addTab(debug_edit, 'General troubleshooting commands')
        for line in self.general_troubleshooting_commands():
            debug_edit.insertPlainText(line)
        
        if any(AS.AS_type == 'RIP' for AS in node.AS):
            
            ## RIP Troubleshooting

            debug_rip = QConsoleEdit()
            self.addTab(debug_rip, 'RIP Troubleshooting')
            for line in self.rip_troubleshooting_commands():
                debug_rip.insertPlainText(line)
            
        if any(AS.AS_type == 'OSPF' for AS in node.AS):
        
            ## OSPF Information
            
            information_ospf = QConsoleEdit()
            self.addTab(information_ospf, 'OSPF Information')
            for line in self.ospf_information():
                information_ospf.insertPlainText(line)
            
            ## OSPF Troubleshooting
            
            debug_ospf = QConsoleEdit()
            self.addTab(debug_ospf, 'OSPF Troubleshooting')
            for line in self.ospf_troubleshooting_commands():
                debug_ospf.insertPlainText(line)

    def general_troubleshooting_commands(self):
        
        yield '        show ip route (sh ip ro)'
        yield '''

    Displays the IP routing table of the router, which contains:
        - directly connected subnet (C)
        - default (*) and static routes (S)
        - routes dynamically learned from a routing protocol:
            * RIP (R)
            * OSPF (O (intra-area), O IA (inter-area))
            * IS-IS (i L1 (intra-area), i L2 (inter-area))
    For each entry, there are two numbers in bracket: the first one is the
    administrative distance, and the second one is the metric.
    It also indicates the 'gateway of last resort': the path the router 
    use in case no other path is available.
    
        '''
        
        yield 'show ip protocols (sh ip pro)'
        yield '''
        
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
        
    Under the line 'Routing for Networks', there is the list of networks
    the protocol knows about.
    This is a way to check for which interfaces a given protocol is enabled.
    It also displays the list of passive interfaces for that protocol.
    
        '''
        
        yield 'show interface (sh int)'
        yield '''
        
    Displays many information about the configuration and status of all 
    interfaces, among which:
        - Interface status
        - IP address and subnet mask
        - Protocol status on the interface
        - MTU, bandwidth, utilization, errors 
        
        '''
        
        yield 'show interface (sh int)'
        yield '''
        
    Displays a summary of IP related information for all interfaces:
        - IP address and subnet mask of the interface
        - Administrative status (up / down)
        - Status of the IP protocol (up / down)
        
        '''
        
        yield 'show running configuration (sh run)'
        yield '''
        
    Displays the configuration in the memory.
    This configuration is not saved until the following command is entered:
    'copy running-configuration startup-configuration' ('copy run start').
    
        '''

    def rip_troubleshooting_commands(self):

        yield '        debug ip rip (deb ip rip)'
        yield '''
    
    Displays the RIP routing updates sent and received sent on the router's
    interfaces, and detects potential issues:
        - Mismatch in the RIP version
        
    The debug mode can be deactivated by typing:
        - no debug rip (rip only) / no debug all (all debug modes)
        - equivalently: undebug rip / undebug all
            
        '''

        yield 'show ip rip databse (sh ip rip)'
        yield '''
    
    Displays all summary address entries in the RIP routing database.
    If an address is not in this database, it cannot be advertised.
        
        '''
            
    def ospf_information(self):

        yield '''
    
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
    An area is a group of contiguous links (networks) defined by an 'Area ID'. 
    The backbone's ID is 0.
        
        '''
        
        yield 'Design of a multi-area OSPF topology'
        yield '''
    
    All areas must be connected to the main area, called the 'Backbone'.
    An area in OSPF is a set of links.
    A link cannot belong to more than one area. 
    After all areas have been defined as sets of links, the 'Update topology' 
    mechanism in the 'Manage AS' window must be triggered to automatically 
    assign areas to the routers. 
    A router at the edge of two or more areas is called an 'Area Border Router'.
        
        '''
        
        yield 'OSPF metric: cost assignment'
        yield '''
    
    In OSPF, the cost of a link is computed by default with the 
    following formula: Cost = Bandwidth reference / Link bandwidth. 
    The bandwidth reference default to 10^8 bps.
    The interface of a link can be changed from the property panel 
    (right-click on a link > Properties), but this will not automatically
    update the OSPF metric of the link.
    The 'Update costs' mechanism must be triggered in the 'Manage AS' window:
    it will compute and update the cost of the link for all links in the AS.
        
        '''
        
        yield 'OSPF load-balancing'
        yield '''
    
    In OSPF, the traffic can be load-balanced (shared) on multiple 
    'Equal-Cost Multi-Paths' (ECMP). 
    By default, the number of routes used for load-balancing is 4, but this can
    be modified from the property panel (right-click on a router > Properties).
    A router is capable of load-balancing the traffic on up to 16 routes.
        
        '''
        
        yield 'OSPF router ID'
        yield '''
    
    Each router has a ID which must be unique within the entire OSPF network: 
    it is a 32-bit IP address selected at the start of the OSPF process. 
    The router ID is chosen as:
    - the highest IP address among all router's active loopback interfaces 
    - if there is no activate loopback interface, the highest IP address 
    among all interfaces. 
    Once the router ID is elected, it does not change unless OSPF restarts, 
    or unless it is manually changed with the 'router-id 32-bit-ip-address' 
    command under router ospf process-id.
    This ID is used by the router to announce itself to the other OSPF routers.
        
        '''
        
        yield 'OSPF neighbors'
        yield '''
    
    A router learns about its OSPF neighbors and the AS topology by exchange 
    Link State Advertisements (LSA). An LSA is an OSPF packet that contains 
    link-state and routing information.
    It builds an 'adjacency topology': an adjacency is a relationship between 
    two OSPF neighbors that allows for the exchange of route updates. 
    Only neighbors with an established 'adjacency' share routes.
        
        '''
        
        yield 'OSPF states'
        yield '''
    
    When OSPF adjacency is formed, a router goes through several state changes 
    before it becomes fully adjacent with its neighbor.
    The main states are:
    - Down: This is the first OSPF neighbor state. It means that no information 
    ('Hello' LSA) has been received from this neighbor, but hello packets 
    can still be sent to the neighbor in this state.
    
    - 2-way: This state designates that bi-directional communication has been 
    established between two routers. Bi-directional means that each router has 
    seen the other's Hello packet. This state is attained when the router 
    receiving the hello packet sees its own Router ID within the received 
    Hello packet's neighbor field. Once the routers have entered a 
    two-way state, they are considered 'neighbors'.
    
    - Full: in this state, routers are fully adjacent with each other. 
    All the router and network LSAs are exchanged and the routers' databases 
    are fully synchronized. 
    Full is the normal state for an OSPF router. 
    If a router is stuck in another state, it is an indication that there are 
    problems in forming adjacencies.
    
    A 2-way state indicates that the two OSPF routers are neighbors, 
    but a full state means the completion of sharing links between routers.
        
        '''

    def ospf_troubleshooting_commands(self):
            
        yield '        show ip ospf (sh ip ospf)'
        yield '''
        
    Displays an overview of the router's OSPF configuration:
    - Process ID and router ID
    - Areas the router is connected to
    - Number of interfaces in each area
    - Number of times the SPF algorithm was computed (per area)
        
        '''
            
        yield 'show ip ospf interface brief (sh ip int br)'
        yield '''
        
    Displays the following information about all router's interfaces:
    - the IP address and the area it belongs to
    - the ID of the OSPF process
    - the OSPF router id
    - the cost of the interface (used for SPF algorithm)
    - the state of the interface
        
        '''
            
        yield 'show ip ospf neighbor (sh ip o n)'
        yield '''
        
    Displays OSPF-related information about all neighbors:
    - neighbor ID
    - neighbor state
    - neighbor IP address
    - neighbor interface
        
        '''
            
        yield 'debug ip ospf adj (deb ip o a)'
        yield '''
        
    Displays the following information:
    - DR/BDR election process and sharing of links with the DR
    - Mismatch authentication type (example: clear-text passwords on 
    one router, MD5 on the other)
    - Mismatch authentication key
        
        '''
            
        yield 'debug ip ospf events (deb ip o e)'
        yield '''
        
    Displays the following information:
    - Mismatched hello intervals 
    - Mismatched dead intervals
    - Mismatched subnet masks
        
        '''
            
        yield 'debug ip ospf events (deb ip o e)'
        yield '''
        
    Displays the following information:
    - Mismatched hello intervals 
    - Mismatched dead intervals
    - Mismatched subnet masks
        
        '''