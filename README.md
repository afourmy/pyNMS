# Introduction

Netdim is a network design and planning software.

A network in NetDim is made of:
- devices (router, optical switch, host machine or antenna)
- physical links (<a href="https://en.wikipedia.org/wiki/Link_aggregation">trunks</a>)
- routes
- traffic links
- [autonomous systems] (https://en.wikipedia.org/wiki/Autonomous_system_%28Internet%29) (AS)

A physical link in NetDim is called a trunk: it represents a set of physical links aggregated together.
An autonomous system is a set of devices exchanging routing and signalization messages to carry the incoming traffic.
The path of a traffic flow inside an AS depends on the [protocol] (https://en.wikipedia.org/wiki/Communications_protocol) used
in the AS.

# Features

## Graph visualization

The first step to network modelization is graph visualization. One way to visualize a network is to locate all devices on a map. However, this can only be done if we have all GPS coordinates: it is rarely the case. Instead, NetDim relies on graph visualization algorithms to display the network.
Two spring-layout algorithms are implemented: Eades and Fructherman-Reingold.

On a 5-layer deep tree which nodes are initially drawn at a random position on the canvas, the algorithm converges within a few seconds to a visually pleasing tree shape.

![Graph visualization](https://github.com/mintoo/networks/raw/master/Readme/visualization.PNG)

## Saving and import/export

Projects can be saved to an excel or a csv format. This is also a way to import an existing network into NetDim.

![Excel project](https://github.com/mintoo/networks/raw/master/Readme/xls_import.PNG)

It is also possible to import graphml files from the [Topology Zoo] (http://www.topology-zoo.org/). The Topology Zoo gathers information about existing networks. All files are provided in the Workspace Folder.
As an example, this is the topology of the BENESTRA network in Slovakia:

![Graphml Impport](https://github.com/mintoo/networks/raw/master/Readme/BenestraBB.PNG)

## Routing algorithms

Three shortest path algorithms are implemented to modelize network routing:
- Dijkstra algorithm
- Bellman-Ford algorithm
- Floyd-Warshall algorithm

Dijkstra algorithm (quasi-linear complexity) is used by default. Variations of Dijkstra algorithm were implemented to find the traffic path in an AS depending on the protocol.
The reason for using a specific algorithm is that multi-area configuration can lead to suboptimal routing:
- In IS-IS, an L1 router sends all traffic to the closest L1/L2 router, even though there could be a shorter path in terms of metric if there are multiple L1/L2 routers in the starting area.
- In OSPF, intra-area routes are always favored over inter-area routes, even when inter-area routes happen to be the shortest.

Clicking on a route or a traffic link highlights its path through the network:

![Route highlight](https://github.com/mintoo/networks/raw/master/Readme/routing.PNG)

## AS Management

Nodes and trunks can be added to the network by selecting them on the canvas, from the right-click menu. The AS topology is display in a specific window. The "AS Management" panel is also used to create and manage areas.
Routes are created between everry couple of "edge nodes".

![AS Management](https://github.com/mintoo/networks/raw/master/Readme/AS_management.PNG)

## 3D display

There are 3 layers in NetDim: the physical layers (trunks), the logical layer (routes), and the traffic layer (traffic link).
In order to improve the network visualization, it is possible to have a per-layer view of the network.
Nodes are draw at all 3 layers, and connected with a dashed line to further improve the display.

![AS Management](https://github.com/mintoo/networks/raw/master/Readme/3D-display.PNG)

## Capacity planning

Once traffic links are created, they are routed on the trunks outside an AS, and the routes to cross an AS. The resulting traffic flow is computed for each trunks. This is then used for trunk dimensioning and capacity planning.

![Capacity planning](https://github.com/mintoo/networks/raw/master/Readme/capacity_planning.PNG)

## Failure simulation

It is also possible to simulate the failure of a device and see how it impacts the network routing and dimensioning.
When highlighting a route's path, the recovery path is display.

![Failure simulation](https://github.com/mintoo/networks/raw/master/Readme/failure_simulation.PNG)

## Automatic device configuration

Netdim automatically assigns IP addresses and interfaces to all devices. After an AS is created, Netdim shows all Cisco commands required to configure the protocol on the device.

![Failure simulation](https://github.com/mintoo/networks/raw/master/Readme/config.PNG)

## Transportation problem

The transportation problem consists in finding the maximum flow that can transit through the network: it is a multi-source multi-destination maximum flow problem.
Three methods were implemented in NetDim to solve the transportation problem:

- Ford-Fulkerson algorithm
- Edmond-Karps algorithm
- Linear programming with GLPK

# A simple use case: OSPF domain creation and configuration (one area only)

## Create a full-meshed graph with 6 routers
Click on the full-mesh icon at the bottom of Netdim menu. A window pops up, asking for the number and the type of nodes.
Choose "router" in the drop-down list, and set the number of nodes to 6.
![Graph creation](https://github.com/mintoo/networks/raw/master/Readme/use_case_step1.PNG)

## Visualize the graph
When the graph is created, all nodes are colocated. Click on the selection button in the menu. Select all nodes by pressing the left-click button of the mouse. Right-click on the selected nodes, choose "Force-based layout" in the right-click menu. A window pops up: select "Random + Force-based drawing".
Nodes will first be randomly spread accross the canvas, after what the force-directed layout is applied.
You can use the mouse scroll wheel to center the display on the nodes.
![Graph visualization](https://github.com/mintoo/networks/raw/master/Readme/use_case_step2.PNG)

## Create the AS
Select all 6 nodes and right-click on one of them. Select "Create AS". The "Manage AS" panel pops up.
![AS creation](https://github.com/mintoo/networks/raw/master/Readme/use_case_step3.PNG)

## Add the trunk to the AS
The AS was created as a set of nodes: it has no trunk yet. Click on the "Find trunks" button.
This will automatically add all trunks which both ends are part of the AS.
Add a few edge nodes. Routes are only created between edge nodes.
This AS management panel also display the area topology. In this simple use case, all nodes and trunks are part of the backbone, there is no other area.
![AS management](https://github.com/mintoo/networks/raw/master/Readme/use_case_step4.PNG)

## Assign IP address and look at the configuration panel
Click on "Netdim" logo. This will trigger the assignment of IP addresses to all routers. It will also create "routes" between each pair of "edge nodes", and compute their path in accordance with the OSPF protocol (since there is only one area, it results in a simple shortest path).
You can access the configuration panel by right-clicking on a router, and click on "Configuration".
![AS management](https://github.com/mintoo/networks/raw/master/Readme/use_case_step5.PNG)

## Multi-layer display
Finally, you can trigger the multi-layer display to dissociate routes from trunks and better assess the situation.
Clicking on a route display its path in red. Since we created a full-mesh AS, the shortest path simply uses the trunk connecting each edge. You can delete a few trunks (use "link selection" instead of "node selection" in the menu, select a set of trunks and use the right-click menu to delete them) and see how that affects the routing.
![AS management](https://github.com/mintoo/networks/raw/master/Readme/use_case_step6.PNG)

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
- [ ] Minimum-cost flow with linear programming
- [ ] Shortest pair with A*
- [ ] Bhandari algorithm to compare with Suurbale
- [ ] Improved Suurbale/Bhandari to find the K (maximally) edge/edge&nodes disjoint paths
- [ ] Prim algorithm to find the minimum spanning tree
- [ ] Minimum cut. Useful to find the bottleneck of the network, and partition the graph before visualisation.
- [ ] K-means before graph drawing if the graph is too big.
- [ ] Dinic algorithm to find the maximum flow
- [ ] Loop detection algorithm with BFS
- [ ] K equal-cost links/links&amp;nodes-disjoint shortest paths with BFS
- [ ] Suurbale algorithm to find the shortest links/links&amp;nodes-disjoint pair
- [ ] Use LP to solve RWA simple version
- [ ] Use a genetic algorithm to find the maximum flow, compare with LP
- [ ] Use a genetic algorithm to solve RWA, compare with LP
- [ ] Degree centrality. number of neighbor of each node (graph + make node size depend on it)
- [ ] Algorithm to determine link weight in order to optimize load sharing (is-is/ospf optimization)
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
- [ ] Add arrows on trunks for route highlight
- [ ] Change the mouse pointeur when going over an object
- [ ] Modified Dijkstra to find the longest path/widest path
- [ ] Capacity label display: should be with an arrow
- [ ] Generate text and shapes on the canvas
- [ ] Label position issue + label deletion for routes after calculate all
- [ ] Highlight should include the nodes too
- [ ] Upload icon with all possible colors and have a special folder for them
- [ ] Radio button for nodes and link selection. Add to menu
- [ ] Center on view for one node and multiple node
- [ ] Highlight the LL when highlighting the path
- [ ] Drawing: choose between "random drawing, random + spring layout, draw at position, spring layout (warning if colocated nodes)
- [ ] Highlight recovery path with dash
- [ ] Highlight routes / traffic methods should depend on whether there is or not a link in failure.

## Routing
- [x] ISIS routing
- [x] OSPF routing. 
- [x] Traffic link routing. All nodes that belongs to an AS should be excluded.
- [ ] subnet and filtering system on routes/traffic link
- [ ] G8032 ring with RPL protection
- [ ] Ring AS with steering/wrapping protection mode
- [ ] Dimensioning with Maximally redundant tree
- [ ] OSPF options: route leaking, multi-ABR, multi-area links, etc (RFC 5086, ...)
- [ ] IS-IS improvement: route leaking option (RFC 2966)
- [ ] Load balancing for the edges of an AS.

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
- [ ] Use the K-shortest paths for load-balancing at the edge of an AS
- [ ] Delete AS button. Rename AS. Delete area. Rename area.
- [ ] Interaction between rename an object and the AS management. 
- [ ] Find a way to make the network tree view work, by retrieving the name of the category
- [ ] Add AS properties in the model, NTV and ASm panel

## Tests
- [x] Add tests for SP (Dijkstra, BF, all-paths BFS)
- [x] Add test for import export
- [x] Add test for AS creation, modification, renaming, deletion, etc + area management
- [x] Add test for IS-IS

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
- [ ] Menu for graph drawing: save all parameters
- [ ] Selection dict should include all type of link: trunk, route, traffic
- [ ] Check box in the frame to hide/show nodes
- [ ] Filter route display depending on whether a traffic link is using them
- [ ] Find a way to silence GLPK
- [ ] Remove all Var() when not necessary (set, get can be used instead)
- [ ] Scenario duplication
- [ ] Drawing for a selection of nodes only
- [ ] Message window (display log) + error window: catch error
- [ ] Dockable frame system
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
- [ ] __bool__ for link: means bw > 0
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