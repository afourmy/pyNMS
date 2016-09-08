# Introduction

NetDim is a network design and planning software.

A network in NetDim is made of:
- devices (router, optical switch, host machine, etc)
- physical links (<a href="https://en.wikipedia.org/wiki/Link_aggregation">trunks</a>)
- logical links (static route, pseudowires, BGP peer relationship, OSPF virtual link)
- traffic links (demands in Mbps)
- [autonomous systems] (https://en.wikipedia.org/wiki/Autonomous_system_%28Internet%29) (AS)

A physical link in NetDim is called a trunk: it represents a set of physical links aggregated together.
An autonomous system is a set of devices exchanging routing and signalization messages to carry the incoming traffic.
The path of a traffic flow inside an AS depends on the [protocol] (https://en.wikipedia.org/wiki/Communications_protocol) used
in the AS.

# Getting started

The following modules are used in NetDim:
```
PIL / Pillow (mandatory)
xlrd, xlwt (desirable: used for saving projects)
numpy, cvxopt (optional: used for linear programming)
```

In order to use NetDim, you need to run **main.py**.
```
python main.py
```

What you should see after running main.py:

![NetDim](https://github.com/mintoo/networks/raw/master/Readme/netdim_app.png)

# Features

## Graph visualization

The first step to network modelization is graph visualization. One way to visualize a network is to locate all devices on a map. However, this can only be done if we have all GPS coordinates: it is rarely the case. Instead, NetDim relies on graph visualization algorithms to display the network.
Two spring-layout algorithms are implemented: 
- Eades algorithm
- Fructherman-Reingold algorithm

On a 4-layer deep tree which nodes are initially drawn at a random position on the canvas, the algorithm converges within a few seconds to a visually pleasing tree shape.

![Graph visualization](https://github.com/mintoo/networks/raw/master/Readme/visualization.PNG)

## Saving and import/export

Projects can be imported from / exported to an excel or a csv file. This allows to import an existing network into NetDim.

![Excel project](https://github.com/mintoo/networks/raw/master/Readme/xls_import.PNG)

It is also possible to import graphml files from the [Topology Zoo] (http://www.topology-zoo.org/). The Topology Zoo gathers information about existing networks. All files are provided in the Workspace Folder.
As an example, this is the topology of the RENATER network in France, in 2010:

![Graphml Impport](https://github.com/mintoo/networks/raw/master/Readme/RENATER.PNG)

## AS Management

Nodes and trunks can be added to an AS by selecting them on the canvas, with the right-click menu. The AS topology is displayed in the "AS Management" panel. This window is also used to create and manage areas.

![AS Management](https://github.com/mintoo/networks/raw/master/Readme/domain_management.PNG)

## Automatic device configuration

After an AS is created, NetDim shows all Cisco commands required to properly configure the protocol on the device. 
This information can in turn be used along with network emulator like GNS3 to learn how to configure a network.

![Automatic configuration](https://github.com/mintoo/networks/raw/master/Readme/config.PNG)

## Routing algorithms

Four algorithms have been implemented to find the shortest path between two devices:
- Dijkstra and A* algorithm
- Bellman-Ford algorithm
- Floyd-Warshall algorithm
- Shortest path with linear programming (GLPK)

However, a shortest path algorithm is not enough to find the path of a traffic flow inside a network, because:
- a router is capable of load-balancing the traffic among several equal (OSPF) or unequal (IS-IS, EIGRP) cost paths.
- multi-area topologies can lead to suboptimal routing:
  * In IS-IS, an L1 router sends all traffic to the closest L1/L2 router, even though there could be a shorter path (in terms of metric) if there are multiple L1/L2 routers in the starting area.
  * In OSPF, intra-area routes are always favored over inter-area routes, even when inter-area routes happen to be the shortest. An ABR can advertize the wrong cost to other routers, which results in "area hijacking".

The only way to properly route flows in a network is to bring the model as close to real-life routing as possible: 
  1. First, NetDim automatically assigns IP addresses and interfaces to all routers.
  2. For each device, a switching / routing table is created to associate a destination address to an exit interface.

![Routing table](https://github.com/mintoo/networks/raw/master/Readme/routing_table.png)

## Troubleshooting commands

NetDim also provides an help with troubleshooting. You can right-click on a router and select the "Troubleshooting" entry to get a list of (Cisco) troubleshooting commands:

- General troubleshooting commands
- Per-AS type troubleshooting commands, depending on which AS the router belongs to

![Troubleshooting](https://github.com/mintoo/networks/raw/master/Readme/troubleshooting.png)

## 3D display

There are 3 layers in NetDim: the physical layer (Ethernet and WDM fiber trunks), the logical layer ("routes", i.e logical links), and the traffic layer (traffic links).
In order to enhance network visualization, it is possible to have a per-layer view of the network.
Nodes are drawn at all 3 layers, and connected with a dashed line to further improve the display.

![AS Management](https://github.com/mintoo/networks/raw/master/Readme/3D-display.PNG)

## Capacity planning 

Once traffic links are created, they are routed on the trunks. The resulting traffic flow is computed for all for all interfaces. In the following example, the router load-balance the traffic on four equal-cost paths.

![Capacity planning](https://github.com/mintoo/networks/raw/master/Readme/capacity_planning.PNG)

## Failure simulation

It is possible to simulate the failure of one or several devices and see how it impacts the network routing and dimensioning. A trunk can be set "in failure" from the right-click menu.
For the failure to be considered, it is required to trigger the update of all routing tables, then route the traffic flows again. 
On the same example as above, we see that the router is now load-balancing the traffic on two paths only, and the total traffic flow is computed accordingly.

![Failure simulation](https://github.com/mintoo/networks/raw/master/Readme/failure_simulation.PNG)

## Advanced algorithms

The transportation problem consists in finding the best way to carry traffic flows through the network.
It has a number of variations (maximum flow, minimum-cost flow, traffic-demand constrained flow, etc).

Four methods were implemented to solve the maximum flow problem:

- Ford-Fulkerson algorithm
- Edmond-Karps algorithm
- Dinic algorithm
- Linear programming with GLPK

Two methods to solve the minimum-cost flow problem:

- Linear programming with GLPK
- Cycle-canceling algorithm (~ Klein algorithm)

Another recurrent problem in networking is to find the shortest link-disjoint paths. 
Four methods were implemented to find the K link-disjoint shortest paths:

- Constrained A*
- Bhandari algorithm
- Suurbale algorithm
- Linear programming with GLPK

To run these algorithms, go to the "Network routing" menu and click on the "Advanced algorithms" entry.
Select an algorithm, fill in all the associated fields, and confirm.

![Algorithm window](https://github.com/mintoo/networks/raw/master/Readme/algorithm_window.png)

## Wavelength allocation problem

In an optical-bypass enabled network, a wavelength can cross an optical switch without Optical-Electrical-Optical (OEO) conversion. While this is a step forward towards cheaper and "greener" networks, a trade-off is that there has to be an end-to-end "wavelength continuity": a wavelength stays the same from the source edge to the destination edge, and it cannot be used by different lightpaths on the same optical fiber.

![WA topology](https://github.com/mintoo/networks/raw/master/Readme/WA_problem1.png)

In the following example, there are 3 paths. If there is a transponder at "node2" to take care of the wavelength conversion, we need only two wavelengths overall: we can assign a wavelength M to traffic3, N to traffic4, and traffic5 will first use N from node1 to node2, then M from node2 to node3. However, in an optical-bypass enabled network, there can be no OEO conversion at node2: the number of wavelengths we need depends how we assign them.
If we assign M to traffic3 and N to traffic4, we will have to use a third wavelength for traffic5, since M and N are already used. However, we could assign M to both traffic3 and traffic4, which leaves N free to use for traffic5: the minimal number of wavelengths required is 2.

The wavelength allocation problem consists in finding the minimum number of wavelengths that are required, and how to allocate them to lightpaths.
Build an network with optical switches (OXCs) and traffic links (at most one per couple of OXC), then go to the "Network routing" and click on the "Wavelength assignment" entry.

![WA topology](https://github.com/mintoo/networks/raw/master/Readme/WA_problem2.png)

The first step is to trigger the graph transformation: type a name for the scenario and click on "Graph transformation".
Two methods were implemented to solve the wavelength assignment problem:

- Linear programming with GLPK
- "Largest degree first" heuristic

Choose one of them in the list and click on "Run algorithm": NetDim will find out how many wavelengths are needed.

# A simple use case: create an OSPF tessaract (4-hypercube)

## Create the tessaract

Go to the "Network routing" menu, and select the entry "Graph generation". Click on the "Hypercube" button, leave the dimension to 4 and click on "OK".

![Graph creation](https://github.com/mintoo/networks/raw/master/Readme/use_case_step1.PNG)

## Visualize the graph
When the graph is created, all nodes are colocated. Right-click on the canvas, and select the "Drawing > Both" entry. 
Nodes will first be randomly spread accross the canvas, after what the force-directed layout is applied.
The network is continuously drawing itself until you right-click again and select the "Stop drawing" entry.
You can use the mouse scroll wheel to center the display on the nodes.

![Graph visualization](https://github.com/mintoo/networks/raw/master/Readme/use_case_step2.PNG)

## Create the AS
Select all nodes and right-click on one of them. Click on "Create AS" and choose "OSPF" in the "Type" list, then click on "Create AS". The "Manage AS" panel pops up.

![AS creation](https://github.com/mintoo/networks/raw/master/Readme/use_case_step3.PNG)

## Add trunks to the AS
The AS was created as a set of nodes: it has no trunk yet. Click on the "Find trunks" button.
This will automatically add all trunks which both ends belong the AS.
Add a few edge nodes. Click on the "Create traffic" button: traffic links will be automatically created between all pairs of edge nodes.
This AS management panel also display the area topology. In our case, all nodes and trunks are part of the backbone, there is no other area.

![AS management](https://github.com/mintoo/networks/raw/master/Readme/use_case_step4.PNG)

## Assign IP address and look at the configuration panel
Right-click on the canvas, and select the "Calculate" entry. NetDim will perform the following actions:
- Update AS topology
- Interface allocation: assign Ethernet interfaces to all trunks: these interfaces are used to create the routing table of the attached routers, as well as for the configuration panel.
- IP addressing: assign IP addressing to all interfaces.
- Subnetwork allocation: compute a subnetwork address for all trunks. Subnetworks depend on the IP addresses of both interfaces of the trunk. For example, if the IP addresses are 10.0.0.1/24 and 10.0.0.2/24, the "subnetwork" advertised by the router will be 10.0.0.0/24.
- Create routing tables.
- Route traffic links: based on the routing tables that were created in the previous step, NetDim finds the path of each traffic flows and map the traffic on physical trunks, just like it's done in real-world networks.
- Refresh labels: update all label values.

From this point on, you can:
- Choose which label to display from the "Options" menu (IP address, interface, etc)
- Click on a route to see how the traffic is routed through the AS
- Access the configuration panel by right-clicking on a router, and select the "Configuration" entry.

![Routing](https://github.com/mintoo/networks/raw/master/Readme/use_case_step6.PNG)

## Multi-layer display
Finally, you can trigger the multi-layer display to dissociate traffic links from trunks and better assess the situation.

![Multi-layer display](https://github.com/mintoo/networks/raw/master/Readme/use_case_step7.PNG)

# To be done

## Algorithms
- [x] Kruskal algorithm to find the minimum spanning tree, Union Find structure
- [x] Ford-Fulkerson algorithm to find the maximum flow
- [x] Edmonds-Karp algorithm to find the maximum flow
- [x] Linear programming with GLPK to find the maximum flow
- [x] Dijkstra algorithm with constraints to find CSPF paths
- [x] Bellman-Ford to find the shortest path
- [x] BFS to find all loop-free paths
- [x] Floyd Warshall to find all SP length
- [x] Fruchterman-Reingold: make it work.
- [x] Graph drawing on the right-click for a selection of nodes
- [x] Shortest path with linear programming
- [x] Minimum-cost flow with linear programming
- [x] Shortest pair with A*
- [x] Bhandari algorithm to find the shortest edge-disjoint pair
- [x] Dinic algorithm to find the maximum flow
- [x] Suurbale algorithm to find the shortest edge-disjoint pair
- [x] Use LP to solve RWA simple version
- [x] Algorithm to determine link weight in order to optimize load sharing (is-is/ospf optimization)
- [ ] Improved Suurbale/Bhandari to find the K (maximally) edge/edge&nodes disjoint paths
- [ ] Prim algorithm to find the minimum spanning tree
- [ ] Minimum cut.
- [ ] Use a genetic algorithm to solve RWA, compare with LP
- [ ] Degree centrality. number of neighbor of each node (graph + make node size depend on it)
- [ ] Protection-based link dimensioning: IGP reconvergence, FRR, etc

## Links
- [x] Possibility to change the cost of a link (UD-metric)
- [x] Interface. Metrics depends on the interface for OSPF, RSTP, etc
- [x] Different type of physical link: WDM Fiber, ETH, etc. Color per type of link.

## Canvas-related tasks
- [x] Multiple selection: all nodes/links contained in a rectangle
- [x] Icons for devices instead of a tkinter oval
- [x] Multiple nodes/links deletion
- [x] Dijkstra must consider the cost of the links
- [x] Fix the zoom that doesn't work well (zooming and unzooming)
- [x] Left-clicking on an object updates the property window if it is deiconified
- [x] Hide/show display per type of objects
- [x] Draw an arc instead of a straigth line when there are several links between two nodes.
- [x] Per-layer 3D display with nodes duplication
- [x] When switching to simple oval display, keep track of the size of the object so that it is always the same.
- [x] Remove switch to creation button
- [x] Click on a node should select only the node (erase previous selection). Ctrl to add to selection
- [x] Radio button for nodes and link selection. Add to menu
- [ ] Add arrows on trunks for route highlight
- [ ] Change the mouse pointeur when going over an object
- [ ] Modified Dijkstra to find the longest path/widest path
- [ ] Generate text and shapes on the canvas
- [ ] Label position issue + label deletion for routes after calculate all
- [ ] Highlight should include the nodes too
- [ ] Upload icon with all possible colors and have a special folder for them
- [ ] Highlight the LL when highlighting the path
- [ ] Highlight recovery path with dash
- [ ] Highlight routes / traffic methods should depend on whether there is or not a link in failure.

## Routing
- [x] ISIS routing
- [x] OSPF routing. 
- [x] Traffic link routing. All nodes that belongs to an AS should be excluded.
- [ ] G8032 ring with RPL protection
- [ ] Ring AS with steering/wrapping protection mode
- [ ] Dimensioning with Maximally redundant tree
- [ ] OSPF options: route leaking, multi-ABR, multi-area links, etc (RFC 5086, ...)
- [ ] IS-IS improvement: route leaking option (RFC 2966)

## Protection
- [x] Failure simulation system to see where the traffic is going. Route's protection path highlight.
- [x] Protection by pruning the failed link(s): dimensioning considering IGP convergence
- [ ] FRR implementation for MPLS. A LSP can have a protection mode (Local Detour to Merge point, Local Detour to Destination, Next-Hop protection) or a user-defined back-up LSP.
- [ ] Highlight the protection path with a different color
- [ ] K-failure AS dimensioning

## AS
- [x] Add to/remove from AS should be done graphically only: no need for buttons.
- [ ] Highlight all elements of a domain
- [ ] Improve the AS management window. Button with arrows instead of add/remove edge
- [ ] Delete AS button. Rename AS. Delete area. Rename area.
- [ ] Interaction between rename an object and the AS management. 
- [ ] Find a way to make the network tree view work, by retrieving the name of the category
- [ ] Add AS properties in the model, NTV and ASm panel

## Tests
- [x] Add test for the maximum flow problem
- [x] Add tests for SP (Dijkstra, BF, all-paths BFS)
- [x] Add test for import export
- [x] Add test for IS-IS
- [x] Add test for OSPF
- [ ] Add test for AS creation, modification, renaming, deletion, etc + area management

## Other
- [x] Convert tk drop-down list into ttk combo box
- [x] Modify customlistbox to avoid the line to retrieve the index
- [x] Scenario system with multiple scenarii
- [x] Possibiliy to rename objects
- [x] Delete scenario
- [x] Merge Add to AS and Manage AS window
- [x] Use haversine formula to compute the distance of a link based on GPS coordinates
- [x] Add new devices: splitter, regenerator/amplifier
- [x] Graph generation: select the type of nodes
- [x] Remove AS from pn
- [x] Add switch
- [x] Dict reset from keys
- [x] IP address management on interface.
- [x] Menu for graph drawing: save all parameters
- [ ] Selection dict should include all type of link: trunk, route, traffic
- [ ] Check box in the frame to hide/show nodes
- [ ] Filter route display depending on whether a traffic link is using them
- [ ] Remove all Var() when not necessary (set, get can be used instead)
- [ ] Scenario duplication
- [ ] Drawing for a selection of nodes only
- [ ] Message window (display log) + error window: catch error
- [ ] Add regex for sanity checks in all user input entry boxes
- [ ] Network links/nodes statistics with plotlib: number of links per type, etc
- [ ] Save the default drawing parameters when modified. Update the window.
- [ ] compute the optimal pairwise distance for the spring length
- [ ] Help menu for links, nodes input
- [ ] Common top-level window for object property display to avoid having several windows at once
- [ ] Keyboard shortcut: Ctrl, Suppr, Ctrl Z/Y, etc
- [ ] Treeview to display the list of object of the network
- [ ] when clicking on a link, window displaying all routes / traffic link mapped on it
- [ ] Right-click of the tree view equivalent to a right-click on the canvas
- [ ] Menu to generate complex graph: hypercube, square tiling in a special window
- [ ] Make a clear distinction between class variable and init
- [ ] Rename objects bugs
- [ ] Property decorator to summarize routes param
- [ ] Vertical bars in RC menu to separate methods

## Config generation
- [x] Generate OSPF config
- [x] Generate RIP config
- [x] Have an "AS number" and an "area" number.
- [x] Generate IS-IS config
- [ ] Generate MPLS config
- [ ] Generate RSTP config 

## Import/Export/Save
- [x] Import and export the graph with CSV
- [x] Import and export the graph with excel
- [x] Import GML format and provide all files from the topology zoo
- [x] Allow to import the property of nodes, so that they can be efficiently modified in excel for a big graph
- [ ] Consider all scenario when saving/opening a saved project
- [ ] Save all scenario
- [ ] Import Export all scenario
- [ ] Import new and update mode