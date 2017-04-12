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

def start_and_import(filename):
    def inner_decorator(function):
        def wrapper(self):
            self.netdim = controller.Controller(path_app)
            self.ntw = self.netdim.cs.ntw
            path_test = path_parent + '\\Tests\\'
            self.netdim.import_graph(path_test + filename)
            function(self)
        return wrapper
    return inner_decorator

class TestExportImport(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        super(TestExportImport, cls).setUpClass()
        cls.netdim = controller.Controller(path_app)
        src = cls.netdim.cs.ntw.nf(name='s')
        dest = cls.netdim.cs.ntw.nf(name='d')
        dest.x, src.x = 42, 24
        plink = cls.netdim.cs.ntw.lf(
                                     name = 't', 
                                     source = src, 
                                     destination = dest
                                     )
        plink.distance = 666
        route = cls.netdim.cs.ntw.lf(
                                     subtype = 'routed traffic',
                                     source = src, 
                                     destination = dest
                                     )
        # export in excel and csv
        path = '\\Tests\\test_export.'
        cls.netdim.export_graph(''.join((path_parent, path, 'xls')))
        cls.netdim.destroy()
        
    def tearDown(self):
        self.netdim.destroy()
        
    def object_import(self, ext):
        self.netdim = controller.Controller(path_app)
        self.netdim.import_graph(path_parent + '\\Tests\\test_export.' + ext)
        x_coord = set(map(lambda n: n.x, self.netdim.cs.ntw.pn['node'].values()))
        self.assertEqual(x_coord, {42, 24})
        plink ,= self.netdim.cs.ntw.pn['plink'].values()
        self.assertEqual(plink.distance, 666)
        self.assertEqual(len(self.netdim.cs.ntw.pn['traffic'].values()), 1)
        
    def test_object_import_xls(self):
        self.object_import('xls')

class TestFlow(unittest.TestCase):
 
    @start_and_import('test_flow1.xls')
    def setUp(self):
        self.source = self.ntw.pn['node'][self.ntw.name_to_id['s']]
        self.target = self.ntw.pn['node'][self.ntw.name_to_id['t']]
 
    def tearDown(self):
        self.netdim.destroy()
 
    def test_ford_fulkerson(self):
        ff_flow = self.ntw.ford_fulkerson(self.source, self.target)
        self.assertEqual(ff_flow, 19)
        
    def test_edmonds_karp(self):
        ek_flow = self.ntw.edmonds_karp(self.source, self.target)
        self.assertEqual(ek_flow, 19)  
        
    def test_dinic(self):
        _, dinic_flow = self.ntw.dinic(self.source, self.target)
        self.assertEqual(dinic_flow, 19)  
    
    def test_LP_flow(self):
        LP_flow = self.ntw.LP_MF_formulation(self.source, self.target)
        self.assertEqual(LP_flow, 19)   
        
class TestMST(unittest.TestCase):
 
    @start_and_import('test_mst.xls')
    def setUp(self):
        pass
 
    def tearDown(self):
        self.netdim.destroy()
 
    def test_kruskal(self):
        mst = self.ntw.kruskal(self.ntw.pn['node'].values())
        mst_costs = set(map(lambda plink: plink.costSD, mst))
        self.assertEqual(mst_costs, {1, 2, 4})
        
class TestSP(unittest.TestCase):
    
    results = (
    ['ethernet link1', 'ethernet link3', 'ethernet link5'], 
    ['ethernet link1', 'ethernet link7'],
    ['ethernet link1', 'ethernet link3']
    )
 
    @start_and_import('test_SP.xls')
    def setUp(self):
        get_node = lambda node_name: self.ntw.pn['node'][self.ntw.name_to_id[node_name]]
        self.route9 = (get_node('node0'), get_node('node4'))
        self.route10 = (get_node('node0'), get_node('node5'))
        self.route11 = (get_node('node0'), get_node('node3'))
 
    def tearDown(self):
        self.netdim.destroy()
 
    def test_A_star(self):
        for i, r in enumerate((self.route9, self.route10, self.route11)):
            _, path = self.ntw.A_star(r[0], r[1])
            self.assertEqual(list(map(str, path)), self.results[i])
        
    def test_bellman_ford(self):
        for i, r in enumerate((self.route9, self.route10, self.route11)):
            _, path = self.ntw.bellman_ford(r[0], r[1])
            self.assertEqual(list(map(str, path)), self.results[i])
        
    def test_floyd_warshall(self):
        cost_plink = lambda plink: plink.costSD
        all_length = self.ntw.floyd_warshall()
        for i, r in enumerate((self.route9, self.route10, self.route11)):
            path_length = all_length[r[0]][r[1]]
            _, path = self.ntw.A_star(r[0], r[1])
            self.assertEqual(sum(map(cost_plink, path)), path_length)
            
    def test_LP(self):
        for i, r in enumerate((self.route9, self.route10, self.route11)):
            path = self.ntw.LP_SP_formulation(r[0], r[1])
            self.assertEqual(list(map(str, path)), self.results[i])
            
class TestMCF(unittest.TestCase):
    
    results = (
    ('ethernet link1', 5),
    ('ethernet link2', 7),
    ('ethernet link3', 3),
    ('ethernet link4', 10),
    ('ethernet link5', 2)
    )
    
    @start_and_import('test_mcf.xls')
    def setUp(self):
        source = self.ntw.pn['node'][self.ntw.name_to_id['node1']]
        target = self.ntw.pn['node'][self.ntw.name_to_id['node4']]
        self.ntw.LP_MCF_formulation(source, target, 12)
 
    def tearDown(self):
        self.netdim.destroy()
 
    def test_MCF(self):
        for plink_name, flow in self.results:
            plink = self.ntw.pn['plink'][self.ntw.name_to_id[plink_name]]
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
 
    @start_and_import('test_ISIS.xls')
    def setUp(self):
        self.netdim.refresh()
 
    def tearDown(self):
        self.netdim.destroy()
 
    def test_ISIS(self):
        self.assertEqual(len(self.ntw.pn['traffic']), 2)
        for traffic, path in self.results:
            # we retrieve the actual route from its name in pn
            traffic_link = self.ntw.pn['traffic'][self.ntw.name_to_id[traffic]]
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
 
    @start_and_import('test_ospf.xls')
    def setUp(self):
        self.netdim.refresh()
 
    def tearDown(self):
        self.netdim.destroy()
 
    def test_OSPF(self):
        self.assertEqual(len(self.ntw.pn['traffic']), 2)
        for traffic_link, path in self.results:
            # we retrieve the actual route from its name in pn
            traffic_link = self.ntw.pn['traffic'][self.ntw.name_to_id[traffic_link]]
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
 
    @start_and_import('test_cspf.xls')
    def setUp(self):
        pass
 
    def tearDown(self):
        self.netdim.destroy()
 
    def test_CSPF(self):
        node1 = self.ntw.nf(name='node1')
        node2 = self.ntw.nf(name='node2')
        node3 = self.ntw.nf(name='node3')
        node4 = self.ntw.nf(name='node4')
        node6 = self.ntw.nf(name='node6')
        node7 = self.ntw.nf(name='node7')
        # plink between node4 and node6
        plink13 = self.ntw.lf(name='plink13')
        # plink between node2 and node5
        plink15 = self.ntw.lf(name='plink15')
        
        _, path = self.ntw.A_star(node6, node7)
        self.assertEqual(list(map(str, path)), self.results[0])
        _, path = self.ntw.A_star(node6, node7, 
                                                    path_constraints=[node2])
        self.assertEqual(list(map(str, path)), self.results[1])
        _, path = self.ntw.A_star(node6, node7, 
                                            path_constraints=[node3, node2])
        self.assertEqual(list(map(str, path)), self.results[2])                  
        _, path = self.ntw.A_star(node6, node7, 
                                                    excluded_plinks={plink13})
        self.assertEqual(list(map(str, path)), self.results[3])
        _, path = self.ntw.A_star(node6, node7, 
                            excluded_plinks={plink13}, excluded_nodes={node1})
        self.assertEqual(list(map(str, path)), self.results[4])
        _, path = self.ntw.A_star(node6, node7, 
                            excluded_plinks={plink15}, excluded_nodes={node4})
        self.assertEqual(list(map(str, path)), self.results[5])
        
class TestRWA(unittest.TestCase):
     
    @start_and_import('test_RWA.xls')
    def setUp(self):
        pass
 
    def tearDown(self):
        self.netdim.destroy()
        
    def test_RWA(self):
        sco_new_graph = self.ntw.RWA_graph_transformation()
        self.assertEqual(sco_new_graph.ntw.LP_RWA_formulation(), 3)
        
if str.__eq__(__name__, '__main__'):
    unittest.main(warnings='ignore')  
    unittest.main()