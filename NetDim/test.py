# NetDim (contact@netdim.fr)

import unittest
import sys
from inspect import stack
from os.path import abspath, dirname, pardir, join

# prevent python from writing *.pyc files / __pycache__ folders
sys.dont_write_bytecode = True

path_app = dirname(abspath(stack()[0][1]))

if path_app not in sys.path:
    sys.path.append(path_app)
    
path_parent = abspath(join(path_app, pardir))
    
import controller
from autonomous_system.AS_operations import ASCreation
from graph_generation.network_dimension import NetworkDimension

from ip_networks.arp_table import ARPTable
from ip_networks.bgp_table import BGPTable
from ip_networks.configuration import RouterConfiguration
from ip_networks.ping import Ping
from ip_networks.routing_table import RoutingTable
from ip_networks.switching_table import SwitchingTable
from ip_networks.troubleshooting import Troubleshooting

def start_netdim(function):
    def wrapper(self):
            self.ct = controller.Controller(path_app)
            self.pj = self.ct.current_project
            self.vw = self.pj.current_view
            self.nk = self.vw.network
            function(self)
    return wrapper
    
# @start_netdim_and_import_project(name of the file to be imported)
# starting a project and importing a file: used for tests
def start_netdim_and_import_project(filename):
    def inner_decorator(function):
        @start_netdim
        def wrapper(self):
            path_test = path_parent + '\\Tests\\'
            self.pj.import_project(path_test + filename)
            function(self)
        return wrapper
    return inner_decorator

class TestExportImport(unittest.TestCase):
    
    @start_netdim
    def setUp(self):
        src = self.nk.nf(name='s')
        dest = self.nk.nf(name='d')
        dest.x, src.x = 42, 24
        plink = self.nk.lf(
                            name = 't', 
                            source = src, 
                            destination = dest
                            )
        plink.distance = 666
        route = self.nk.lf(
                            subtype = 'routed traffic',
                            source = src, 
                            destination = dest
                            )
        # export in excel and csv
        path = '\\Tests\\test_export.'
        self.pj.export_project(''.join((path_parent, path, 'xls')))
        self.ct.destroy()
                
    def tearDown(self):
        self.ct.destroy()
        
    def object_import(self, ext):
        self.pj.import_project(path_parent + '\\Tests\\test_export.' + ext)
        x_coord = set(map(lambda n: n.x, self.nk.pn['node'].values()))
        self.assertEqual(x_coord, {42, 24})
        plink ,= self.nk.pn['plink'].values()
        self.assertEqual(plink.distance, 666)
        self.assertEqual(len(self.nk.pn['traffic'].values()), 1)
        
    @start_netdim
    def test_object_import_xls(self):
        self.object_import('xls')

class TestFlow(unittest.TestCase):
 
    @start_netdim_and_import_project('test_flow1.xls')
    def setUp(self):
        self.source = self.nk.pn['node'][self.nk.name_to_id['s']]
        self.target = self.nk.pn['node'][self.nk.name_to_id['t']]
 
    def tearDown(self):
        self.ct.destroy()
 
    def test_ford_fulkerson(self):
        ff_flow = self.nk.ford_fulkerson(self.source, self.target)
        self.assertEqual(ff_flow, 19)
        
    def test_edmonds_karp(self):
        ek_flow = self.nk.edmonds_karp(self.source, self.target)
        self.assertEqual(ek_flow, 19)  
        
    def test_dinic(self):
        _, dinic_flow = self.nk.dinic(self.source, self.target)
        self.assertEqual(dinic_flow, 19)  
    
    def test_LP_flow(self):
        LP_flow = self.nk.LP_MF_formulation(self.source, self.target)
        self.assertEqual(LP_flow, 19)   
        
class TestMST(unittest.TestCase):
 
    @start_netdim_and_import_project('test_mst.xls')
    def setUp(self):
        pass
 
    def tearDown(self):
        self.ct.destroy()
 
    def test_kruskal(self):
        mst = self.nk.kruskal(self.nk.pn['node'].values())
        mst_costs = set(map(lambda plink: plink.costSD, mst))
        self.assertEqual(mst_costs, {1, 2, 4})
        
class TestSP(unittest.TestCase):
    
    results = (
    ['ethernet link1', 'ethernet link3', 'ethernet link5'], 
    ['ethernet link1', 'ethernet link7'],
    ['ethernet link1', 'ethernet link3']
    )
 
    @start_netdim_and_import_project('test_SP.xls')
    def setUp(self):
        get_node = lambda node_name: self.nk.pn['node'][self.nk.name_to_id[node_name]]
        self.route9 = (get_node('node0'), get_node('node4'))
        self.route10 = (get_node('node0'), get_node('node5'))
        self.route11 = (get_node('node0'), get_node('node3'))
 
    def tearDown(self):
        self.ct.destroy()
 
    def test_A_star(self):
        for i, r in enumerate((self.route9, self.route10, self.route11)):
            _, path = self.nk.A_star(r[0], r[1])
            self.assertEqual(list(map(str, path)), self.results[i])
        
    def test_bellman_ford(self):
        for i, r in enumerate((self.route9, self.route10, self.route11)):
            _, path = self.nk.bellman_ford(r[0], r[1])
            self.assertEqual(list(map(str, path)), self.results[i])
        
    def test_floyd_warshall(self):
        cost_plink = lambda plink: plink.costSD
        all_length = self.nk.floyd_warshall()
        for i, r in enumerate((self.route9, self.route10, self.route11)):
            path_length = all_length[r[0]][r[1]]
            _, path = self.nk.A_star(r[0], r[1])
            self.assertEqual(sum(map(cost_plink, path)), path_length)
            
    def test_LP(self):
        for i, r in enumerate((self.route9, self.route10, self.route11)):
            path = self.nk.LP_SP_formulation(r[0], r[1])
            self.assertEqual(list(map(str, path)), self.results[i])
            
class TestMCF(unittest.TestCase):
    
    results = (
    ('ethernet link1', 5),
    ('ethernet link2', 7),
    ('ethernet link3', 3),
    ('ethernet link4', 10),
    ('ethernet link5', 2)
    )
    
    @start_netdim_and_import_project('test_mcf.xls')
    def setUp(self):
        source = self.nk.pn['node'][self.nk.name_to_id['node1']]
        target = self.nk.pn['node'][self.nk.name_to_id['node4']]
        self.nk.LP_MCF_formulation(source, target, 12)
 
    def tearDown(self):
        self.ct.destroy()
 
    def test_MCF(self):
        for plink_name, flow in self.results:
            plink = self.nk.pn['plink'][self.nk.name_to_id[plink_name]]
            self.assertEqual(plink.flowSD, flow)
        
class TestISIS(unittest.TestCase):
    
    results = (
    ('routed traffic link16', {
    'ethernet link1', 
    'ethernet link2', 
    'ethernet link6', 
    'ethernet link7',
    'router5',
    'router4',
    'router3',
    'router2',
    'router6'
    }),
    
    ('routed traffic link15', {
    'ethernet link1', 
    'ethernet link3', 
    'ethernet link4',
    'ethernet link5',
    'ethernet link7',
    'router5',
    'router0',
    'router1',
    'router4',
    'router2',
    'router6'
    }))
 
    @start_netdim_and_import_project('test_ISIS.xls')
    def setUp(self):
        self.pj.refresh()
 
    def tearDown(self):
        self.ct.destroy()
 
    def test_ISIS(self):
        self.assertEqual(len(self.nk.pn['traffic']), 2)
        for traffic, path in self.results:
            # we retrieve the actual route from its name in pn
            traffic_link = self.nk.pn['traffic'][self.nk.name_to_id[traffic]]
            # we check that the path is conform to IS-IS protocol
            self.assertEqual(set(map(str, traffic_link.path)), path)
            
class TestOSPF(unittest.TestCase):
    
    results = (
    ('routed traffic0', {
    'ethernet link1', 
    'ethernet link2', 
    'ethernet link9', 
    'ethernet link10', 
    'ethernet link11', 
    'ethernet link12',
    'ethernet link13',
    'router9',
    'router7',
    'router5',
    'router4',
    'router6',
    'router3',
    'router1',
    'router0'
    }),
    
    ('routed traffic1', {
    'ethernet link1', 
    'ethernet link2', 
    'ethernet link9', 
    'ethernet link8',  
    'ethernet link12',
    'ethernet link13',
    'router9',
    'router7',
    'router5',
    'router4',
    'router3',
    'router1',
    'router0'
    }))
 
    @start_netdim_and_import_project('test_ospf.xls')
    def setUp(self):
        self.pj.refresh()
 
    def tearDown(self):
        self.ct.destroy()
 
    def test_OSPF(self):
        self.assertEqual(len(self.nk.pn['traffic']), 2)
        for traffic_link, path in self.results:
            # we retrieve the actual route from its name in pn
            traffic_link = self.nk.pn['traffic'][self.nk.name_to_id[traffic_link]]
            # we check that the path is conform to OSPF protocol
            self.assertEqual(set(map(str, traffic_link.path)), path)
            
class TestCSPF(unittest.TestCase):
    
    results = (
    ['plink13', 'plink3', 'plink5', 'plink8', 'plink9', 'plink11'],
    ['plink14', 'plink15', 'plink15', 'plink14', 'plink13', 'plink3', 'plink5', 
    'plink8', 'plink9', 'plink11'],
    ['plink13', 'plink3', 'plink3', 'plink13', 'plink14', 'plink15', 'plink15', 
    'plink14', 'plink13', 'plink3', 'plink5', 'plink8', 'plink9', 'plink11'],
    ['plink14', 'plink15', 'plink1', 'plink4', 'plink3', 'plink5', 'plink8', 
    'plink9', 'plink11'],
    ['plink14', 'plink15', 'plink2', 'plink5', 'plink8', 'plink9', 'plink11'],
    []
    )
 
    @start_netdim_and_import_project('test_cspf.xls')
    def setUp(self):
        pass
 
    def tearDown(self):
        self.ct.destroy()
 
    def test_CSPF(self):
        node1 = self.nk.nf(name='node1')
        node2 = self.nk.nf(name='node2')
        node3 = self.nk.nf(name='node3')
        node4 = self.nk.nf(name='node4')
        node6 = self.nk.nf(name='node6')
        node7 = self.nk.nf(name='node7')
        # plink between node4 and node6
        plink13 = self.nk.lf(name='plink13')
        # plink between node2 and node5
        plink15 = self.nk.lf(name='plink15')
        
        _, path = self.nk.A_star(node6, node7)
        self.assertEqual(list(map(str, path)), self.results[0])
        _, path = self.nk.A_star(node6, node7, 
                                                    path_constraints=[node2])
        self.assertEqual(list(map(str, path)), self.results[1])
        _, path = self.nk.A_star(node6, node7, 
                                            path_constraints=[node3, node2])
        self.assertEqual(list(map(str, path)), self.results[2])                  
        _, path = self.nk.A_star(node6, node7, 
                                                    excluded_plinks={plink13})
        self.assertEqual(list(map(str, path)), self.results[3])
        _, path = self.nk.A_star(node6, node7, 
                            excluded_plinks={plink13}, excluded_nodes={node1})
        self.assertEqual(list(map(str, path)), self.results[4])
        _, path = self.nk.A_star(node6, node7, 
                            excluded_plinks={plink15}, excluded_nodes={node4})
        self.assertEqual(list(map(str, path)), self.results[5])
        
class TestRWA(unittest.TestCase):
     
    @start_netdim_and_import_project('test_RWA.xls')
    def setUp(self):
        pass
 
    def tearDown(self):
        self.ct.destroy()
        
    def test_RWA(self):
        project_new_graph = self.nk.RWA_graph_transformation()
        self.assertEqual(project_new_graph.network.LP_RWA_formulation(), 3)

## Graph generation and IGP simulation

class TestHypercubeOSPF(unittest.TestCase):
     
    @start_netdim
    def setUp(self):
        pass
 
    def tearDown(self):
        self.ct.destroy()
        
    def test_HypercubeOSPF(self):
        dimension_window = NetworkDimension('hypercube', self.ct)
        dimension_window.entry_dimension.text = 4
        dimension_window.node_type_list.text = 'router'
        dimension_window.create_graph()
        
        # we created a 4-dimensional hypercube: the network shoud have 16 nodes
        self.assertEqual(len(self.nk.pn['node']), 16)
        
        # we select all nodes and set the type of AS to OSPF (AS Creation window)
        self.vw.highlight_objects(*self.nk.pn['node'].values())
        as_creation = ASCreation(set(self.vw.so['node']), set(), self.ct)
        as_creation.AS_type_list.text = 'OSPF'
        as_creation.create_AS()
        
        # find all links
        ospf_as ,= self.nk.pnAS.values()
        ospf_as.management.find_links()
        
        # tick the address allocation box and trigger all routing functions
        self.ct.routing_menu.action_booleans[2].set(True)
        self.ct.routing_menu.refresh()
        
        # pick a router and check its routing table / configuration 
        for router in self.nk.pn['node'].values():
            break
        self.assertEqual(len(router.rt), 32)
        
        # generate the configuration
        configuration = RouterConfiguration(router, self.ct)
        self.assertEqual(len(tuple(configuration.build_config(router))), 27)
        
        # generate the ARP, routing and BGP tables
        arp_table = ARPTable(router, self.ct)
        bgp_table = BGPTable(router, self.ct)
        routing_table = RoutingTable(router, self.ct)
        
        # generate the ping and troubleshooting tab
        troubleshooting = Troubleshooting(router, self.ct)
        ping = Ping(router, self.ct)
        
class TestSquareTilingISIS(unittest.TestCase):
     
    @start_netdim
    def setUp(self):
        pass
 
    def tearDown(self):
        self.ct.destroy()
        
    def test_SquareTilingISIS(self):
        dimension_window = NetworkDimension('square-tiling', self.ct)
        dimension_window.entry_dimension.text = 8
        dimension_window.node_type_list.text = 'router'
        dimension_window.create_graph()
        
        # we created a 4-dimensional hypercube: the network shoud have 16 nodes
        self.assertEqual(len(self.nk.pn['node']), 81)
        
        # we select all nodes and set the type of AS to OSPF (AS Creation window)
        self.vw.highlight_objects(*self.nk.pn['node'].values())
        as_creation = ASCreation(set(self.vw.so['node']), set(), self.ct)
        as_creation.AS_type_list.text = 'ISIS'
        as_creation.create_AS()
        
        # find all links
        ospf_as ,= self.nk.pnAS.values()
        ospf_as.management.find_links()
        
        # tick the address allocation box and trigger all routing functions
        self.ct.routing_menu.action_booleans[2].set(True)
        self.ct.routing_menu.refresh()
        
        # pick a router and check its routing table / configuration 
        for router in self.nk.pn['node'].values():
            break
        self.assertEqual(len(router.rt), 144)
        
        # generate the configuration
        configuration = RouterConfiguration(router, self.ct)
        self.assertEqual(len(tuple(configuration.build_config(router))), 23)
        
        # generate the ARP, routing and BGP tables
        arp_table = ARPTable(router, self.ct)
        bgp_table = BGPTable(router, self.ct)
        routing_table = RoutingTable(router, self.ct)
        
        # generate the ping and troubleshooting tab
        troubleshooting = Troubleshooting(router, self.ct)
        ping = Ping(router, self.ct)
        
class TestFullMeshRIP(unittest.TestCase):
     
    @start_netdim
    def setUp(self):
        pass
 
    def tearDown(self):
        self.ct.destroy()
        
    def test_FullMeshRIP(self):
        dimension_window = NetworkDimension('full-mesh', self.ct)
        dimension_window.entry_dimension.text = 5
        dimension_window.node_type_list.text = 'router'
        dimension_window.create_graph()
        
        # we created a 4-dimensional hypercube: the network shoud have 16 nodes
        self.assertEqual(len(self.nk.pn['node']), 5)
        
        # we select all nodes and set the type of AS to OSPF (AS Creation window)
        self.vw.highlight_objects(*self.nk.pn['node'].values())
        as_creation = ASCreation(set(self.vw.so['node']), set(), self.ct)
        as_creation.AS_type_list.text = 'RIP'
        as_creation.create_AS()
        
        # find all links
        ospf_as ,= self.nk.pnAS.values()
        ospf_as.management.find_links()
        
        # tick the address allocation box and trigger all routing functions
        self.ct.routing_menu.action_booleans[2].set(True)
        self.ct.routing_menu.refresh()
        
        # pick a router and check its routing table / configuration 
        for router in self.nk.pn['node'].values():
            break
        self.assertEqual(len(router.rt), 10)
        
        # generate the configuration
        configuration = RouterConfiguration(router, self.ct)
        self.assertEqual(len(tuple(configuration.build_config(router))), 27)
        
        # generate the ARP, routing and BGP tables
        arp_table = ARPTable(router, self.ct)
        bgp_table = BGPTable(router, self.ct)
        routing_table = RoutingTable(router, self.ct)
        
        # generate the ping and troubleshooting tab
        troubleshooting = Troubleshooting(router, self.ct)
        ping = Ping(router, self.ct)

from graph_generation.multiple_objects import MultipleNodes
from graph_generation.multiple_objects import MultipleLinks
        
class TestMultipleObjectGeneration(unittest.TestCase):
     
    @start_netdim
    def setUp(self):
        pass
 
    def tearDown(self):
        self.ct.destroy()
        
    def test_ObjectGeneration(self):
        # we created 10 nodes with the multiple nodes window
        multiple_nodes = MultipleNodes(0, 0, self.ct)
        multiple_nodes.entry_nodes.text = 10
        multiple_nodes.node_type_list.text = 'switch'
        multiple_nodes.create_nodes()
        
        self.assertEqual(len(self.nk.pn['node']), 10)
        
        # we create multiple links from a switch to all other switches
        for switch in self.nk.nodes.values():
            break
            
        multiple_links = MultipleLinks({switch}, self.ct)
        multiple_links.listbox.selection_set(0, 'end')
        multiple_links.create_links()
        
        # there should be 9 links in total
        self.assertEqual(len(self.nk.pn['plink']), 9)

        
                
        
if str.__eq__(__name__, '__main__'):
    unittest.main(warnings='ignore')  
    unittest.main()