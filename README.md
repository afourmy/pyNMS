# Introduction

pyNMS is a network design and planning software.

![pyNMS](https://github.com/mintoo/networks/raw/master/Readme/pynms.png)

[Visit our website](http://www.pynms.fr)

Contact us: contact@pynms.fr

# Getting started

The following modules are used in pyNMS:
```
pyQT (mandatory: GUI framework)
shapely, shapefile, pyproj (mandatory: used for shapefile import)
xlrd, xlwt, yaml (desirable: used for saving projects)
numpy, cvxopt (optional: used for linear programming)
NAPALM (optional: used for network automation)
```

In order to use pyNMS, you need to run **main.py**.
```
python main.py
```

# Features

## Network GIS visualization

Maps can be displayed in pyNMS to draw all network
devices at their exact location (longitude and latitude),
using the mercator or azimuthal orthographic projections.

![Network GIS visualization](https://github.com/mintoo/networks/raw/master/Readme/gis_visualization.png)

## Interface to NAPALM

NAPALM is an automation framework that provides a set of functions to interact with different network device Operating Systems using a unified API. NAPALM can be used from within pyNMS to retrieve information about a device, and change the configuration.

A demonstration of how to use NAPALM from pyNMS is available here:
https://www.youtube.com/watch?v=c7ZG7IElgkw

![NAPALM](https://github.com/mintoo/networks/raw/master/Readme/napalm.png)

## Network algorithmic visualization

GIS visualization this can only be done if we have all GPS coordinates: it is not always the case.
Another way to visualize a network is use graph drawing algorithms to display the network.
Two spring-layout algorithms are implemented: 
- Eades algorithm
- Fructherman-Reingold algorithm

On a four-dimensional hypercube, the algorithm converges within a few milliseconds to a visually pleasing tree shape.

![Network force-based visualization](https://github.com/mintoo/networks/raw/master/Readme/visualization.png)

## Saving and import/export

Projects can be imported from / exported to an Excel or a YAML file. This allows to import an existing network into pyNMS.

![Excel project](https://github.com/mintoo/networks/raw/master/Readme/xls_import.PNG)

## AS Management

Autonomous systems can be created to keep track of which device runs which protocol (OSPF, IS-IS, BGP, etc).
Autonomous systems can be divided into multiple areas.

![AS Management](https://github.com/mintoo/networks/raw/master/Readme/AS_management.png)

## Automatic device configuration

pyNMS shows all Cisco commands required to properly configure a protocol on the device. 

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
  1. First, pyNMS automatically assigns IP addresses and interfaces to all routers.
  2. For each device, a switching / routing table is created to associate a destination address to an exit interface.

![Routing table](https://github.com/mintoo/networks/raw/master/Readme/routing_table.png)

## Troubleshooting commands

pyNMS also provides an help with troubleshooting, by listing the most useful commands depending on the protocol used in the simulation.

![Troubleshooting](https://github.com/mintoo/networks/raw/master/Readme/troubleshooting.png)

## Capacity planning 

Once traffic links are created, they are routed on the physical links. The resulting traffic flow is computed for all for all interfaces. In the following example, the router load-balance the traffic on four equal-cost paths.

![Capacity planning](https://github.com/mintoo/networks/raw/master/Readme/capacity_planning.PNG)

## Failure simulation

It is possible to simulate the failure of one or several devices and see how it impacts the network routing and dimensioning. 

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

Choose one of them in the list and click on "Run algorithm": pyNMS will find out how many wavelengths are needed.
