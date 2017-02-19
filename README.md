# Introduction

NetDim is a network design and planning software.

[Visit our website] (http://www.netdim.fr)

Contact us: contact@netdim.fr

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
Right-click on the canvas, and select the "Refresh" entry. NetDim will perform the following actions:
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