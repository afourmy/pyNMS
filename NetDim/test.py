# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import unittest
import sys
from inspect import getsourcefile
from os.path import abspath, pardir, join

path_app = abspath(getsourcefile(lambda: 0))[:-7]
if path_app not in sys.path:
    sys.path.append(path_app)
path_parent = abspath(join(path_app, pardir))

import gui

def start_and_import(filename):
    def inner_decorator(function):
        def wrapper(self):
            self.netdim = gui.NetDim(path_app)
            path_test = path_parent + "\\Tests\\"
            self.netdim.import_graph(path_test + filename)
            function(self)
        return wrapper
    return inner_decorator

class TestExportImport(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        super(TestExportImport, cls).setUpClass()
        cls.netdim = gui.NetDim(path_app)
        src = cls.netdim.cs.ntw.nf(name="s")
        dest = cls.netdim.cs.ntw.nf(name="d")
        dest.x, src.x = 42, 24
        trunk = cls.netdim.cs.ntw.lf(name="t", s=src, d=dest)
        trunk.distance = 666
        route = cls.netdim.cs.ntw.lf(link_type="route", s=src, d=dest)
        # export in all 3 format: excel, text and csv
        path = "\\Tests\\test_export."
        for extension in ("xls", "csv"):
            cls.netdim.export_graph("".join((path_parent, path, extension)))
        cls.netdim.destroy()
        
    def tearDown(self):
        self.netdim.destroy()
        
    def object_import(self, ext):
        self.netdim = gui.NetDim(path_app)
        self.netdim.import_graph(path_parent + "\\Tests\\test_export." + ext)
        x_coord = set(map(lambda n: n.x, self.netdim.cs.ntw.pn["node"].values()))
        self.assertEqual(x_coord, {42, 24})
        trunk ,= self.netdim.cs.ntw.pn["trunk"].values()
        self.assertEqual(trunk.distance, 666)
        self.assertEqual(len(self.netdim.cs.ntw.pn["route"].values()), 1)
        
    def test_object_import_xls(self):
        self.object_import("xls")
        
    def test_object_import_csv(self):
        self.object_import("csv")

class TestFlow(unittest.TestCase):
 
    @start_and_import("test_flow1.xls")
    def setUp(self):
        self.source = self.netdim.cs.ntw.pn["node"]["s"]
        self.target = self.netdim.cs.ntw.pn["node"]["t"]
 
    def tearDown(self):
        self.netdim.destroy()
 
    def test_ford_fulkerson(self):
        ff_flow = self.netdim.cs.ntw.ford_fulkerson(self.source, self.target)
        self.assertEqual(ff_flow, 19)
        
    def test_edmonds_karp(self):
        ek_flow = self.netdim.cs.ntw.edmonds_karp(self.source, self.target)
        self.assertEqual(ek_flow, 19)  
        
    def test_dinic(self):
        _, dinic_flow = self.netdim.cs.ntw.dinic(self.source, self.target)
        self.assertEqual(dinic_flow, 19)  
    
    def test_LP_flow(self):
        LP_flow = self.netdim.cs.ntw.LP_MF_formulation(self.source, self.target)
        self.assertEqual(LP_flow, 19)   
        
class TestMST(unittest.TestCase):
 
    @start_and_import("test_mst1.xls")
    def setUp(self):
        pass
 
    def tearDown(self):
        self.netdim.destroy()
 
    def test_kruskal(self):
        mst = self.netdim.cs.ntw.kruskal(self.netdim.cs.ntw.pn["node"].values())
        mst_costs = set(map(lambda trunk: trunk.costSD, mst))
        self.assertEqual(mst_costs, {1, 2, 4})
        
class TestSP(unittest.TestCase):
    
    results = (
    ["trunk1", "trunk3", "trunk5"], 
    ["trunk1", "trunk7"],
    ["trunk1", "trunk3"]
    )
 
    @start_and_import("test_SP.xls")
    def setUp(self):
        self.route9 = self.netdim.cs.ntw.pn["route"]["route9"]
        self.route10 = self.netdim.cs.ntw.pn["route"]["route10"]
        self.route11 = self.netdim.cs.ntw.pn["route"]["route11"]
        self.netdim.cs.ntw.calculate_all()
 
    def tearDown(self):
        self.netdim.destroy()
 
    def test_A_star(self):
        for i, r in enumerate((self.route9, self.route10, self.route11)):
            self.assertEqual(list(map(str, r.path)), self.results[i])
        
    def test_bellman_ford(self):
        for i, r in enumerate((self.route9, self.route10, self.route11)):
            _, path = self.netdim.cs.ntw.bellman_ford(r.source, r.destination)
            self.assertEqual(list(map(str, path)), self.results[i])
        
    def test_floyd_warshall(self):
        cost_trunk = lambda trunk: trunk.costSD
        all_length = self.netdim.cs.ntw.floyd_warshall()
        for r in (self.route9, self.route10, self.route11):
            path_length = all_length[r.source][r.destination]
            self.assertEqual(sum(map(cost_trunk, r.path)), path_length)
            
    def test_LP(self):
        for i, r in enumerate((self.route9, self.route10, self.route11)):
            path = self.netdim.cs.ntw.LP_SP_formulation(r.source, r.destination)
            self.assertEqual(list(map(str, path)), self.results[i])
            
class TestMCF(unittest.TestCase):
    
    results = (
    ("trunk1", 5),
    ("trunk2", 7),
    ("trunk3", 3),
    ("trunk4", 10),
    ("trunk5", 2)
    )
    
    @start_and_import("test_mcf.xls")
    def setUp(self):
        source = self.netdim.cs.ntw.pn["node"]["node1"]
        target = self.netdim.cs.ntw.pn["node"]["node4"]
        self.netdim.cs.ntw.LP_MCF_formulation(source, target, 12)
 
    def tearDown(self):
        self.netdim.destroy()
 
    def test_MCF(self):
        for trunk_name, flow in self.results:
            trunk = self.netdim.cs.ntw.pn["trunk"][trunk_name]
            self.assertEqual(trunk.flowSD, flow)
        
class TestISIS(unittest.TestCase):
    
    results = (
    ("node5->node0", ["trunk5","trunk3","trunk2"]),
    ("node0->node5", ["trunk1","trunk0","trunk4","trunk5"])
    )
 
    @start_and_import("test_ISIS.xls")
    def setUp(self):
        self.netdim.cs.ntw.calculate_all()
 
    def tearDown(self):
        self.netdim.destroy()
 
    def test_ISIS(self):
        self.assertEqual(len(self.netdim.cs.ntw.pn["route"]), 2)
        for route, path in self.results:
            # we retrieve the actual route from its name in pn
            route = self.netdim.cs.ntw.pn["route"][route]
            # we check that the path is conform to IS-IS protocol
            self.assertEqual(list(map(str, route.path)), path)
            
class TestOSPF(unittest.TestCase):
    
    results = (
    ("node8->node1", ["trunk11", "trunk6", "trunk1"]),
    ("node1->node8", ["trunk5", "trunk12", "trunk9", "trunk10", "trunk11"])
    )
 
    @start_and_import("test_ospf.xls")
    def setUp(self):
        self.netdim.cs.ntw.calculate_all()
 
    def tearDown(self):
        self.netdim.destroy()
 
    def test_OSPF(self):
        self.assertEqual(len(self.netdim.cs.ntw.pn["route"]), 2)
        for route, path in self.results:
            # we retrieve the actual route from its name in pn
            route = self.netdim.cs.ntw.pn["route"][route]
            # we check that the path is conform to OSPF protocol
            self.assertEqual(list(map(str, route.path)), path)
            
class TestCSPF(unittest.TestCase):
    
    results = (
    ["trunk13", "trunk3", "trunk5", "trunk8", "trunk9", "trunk11"],
    ["trunk14", "trunk15", "trunk15", "trunk14", "trunk13", "trunk3", "trunk5", 
    "trunk8", "trunk9", "trunk11"],
    ["trunk13", "trunk3", "trunk3", "trunk13", "trunk14", "trunk15", "trunk15", 
    "trunk14", "trunk13", "trunk3", "trunk5", "trunk8", "trunk9", "trunk11"],
    ["trunk14", "trunk15", "trunk1", "trunk4", "trunk3", "trunk5", "trunk8", 
    "trunk9", "trunk11"],
    ["trunk14", "trunk15", "trunk2", "trunk5", "trunk8", "trunk9", "trunk11"],
    []
    )
 
    @start_and_import("test_cspf.xls")
    def setUp(self):
        pass
 
    def tearDown(self):
        self.netdim.destroy()
 
    def test_CSPF(self):
        node1 = self.netdim.cs.ntw.nf(name="node1")
        node2 = self.netdim.cs.ntw.nf(name="node2")
        node3 = self.netdim.cs.ntw.nf(name="node3")
        node4 = self.netdim.cs.ntw.nf(name="node4")
        node6 = self.netdim.cs.ntw.nf(name="node6")
        node7 = self.netdim.cs.ntw.nf(name="node7")
        # trunk between node4 and node6
        trunk13 = self.netdim.cs.ntw.lf(name="trunk13")
        # trunk between node2 and node5
        trunk15 = self.netdim.cs.ntw.lf(name="trunk15")
        
        _, path = self.netdim.cs.ntw.A_star(node6, node7)
        self.assertEqual(list(map(str, path)), self.results[0])
        _, path = self.netdim.cs.ntw.A_star(node6, node7, 
                                                    path_constraints=[node2])
        self.assertEqual(list(map(str, path)), self.results[1])
        _, path = self.netdim.cs.ntw.A_star(node6, node7, 
                                            path_constraints=[node3, node2])
        self.assertEqual(list(map(str, path)), self.results[2])                  
        _, path = self.netdim.cs.ntw.A_star(node6, node7, 
                                                    excluded_trunks={trunk13})
        self.assertEqual(list(map(str, path)), self.results[3])
        _, path = self.netdim.cs.ntw.A_star(node6, node7, 
                            excluded_trunks={trunk13}, excluded_nodes={node1})
        self.assertEqual(list(map(str, path)), self.results[4])
        _, path = self.netdim.cs.ntw.A_star(node6, node7, 
                            excluded_trunks={trunk15}, excluded_nodes={node4})
        self.assertEqual(list(map(str, path)), self.results[5])
        
class TestRWA(unittest.TestCase):
     
    @start_and_import("test_RWA.xls")
    def setUp(self):
        pass
 
    def tearDown(self):
        self.netdim.destroy()
        
    def test_RWA(self):
        sco_new_graph = self.netdim.cs.ntw.RWA_graph_transformation()
        self.assertEqual(sco_new_graph.ntw.LP_RWA_formulation(), 3)
        
if __name__ == '__main__':
    unittest.main(warnings='ignore')  
    unittest.main()