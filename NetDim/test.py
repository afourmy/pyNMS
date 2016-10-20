# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

import unittest
import sys
from inspect import getsourcefile
from os.path import abspath, pardir, join

# prevent python from writing *.pyc files / __pycache__ folders
sys.dont_write_bytecode = True

path_app = abspath(getsourcefile(lambda: 0))[:-7]

if path_app not in sys.path:
    sys.path.append(path_app)
path_parent = abspath(join(path_app, pardir))

import gui

def start_and_import(filename):
    def inner_decorator(function):
        def wrapper(self):
            self.netdim = gui.NetDim(path_app)
            self.ntw = self.netdim.cs.ntw
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
        route = cls.netdim.cs.ntw.lf(subtype="static route", s=src, d=dest)
        # export in excel and csv
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
        self.source = self.ntw.pn["node"][self.ntw.name_to_id["s"]]
        self.target = self.ntw.pn["node"][self.ntw.name_to_id["t"]]
 
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
 
    @start_and_import("test_mst1.xls")
    def setUp(self):
        pass
 
    def tearDown(self):
        self.netdim.destroy()
 
    def test_kruskal(self):
        mst = self.ntw.kruskal(self.ntw.pn["node"].values())
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
        get_node = lambda node_name: self.ntw.pn["node"][self.ntw.name_to_id[node_name]]
        self.route9 = (get_node("node0"), get_node("node4"))
        self.route10 = (get_node("node0"), get_node("node5"))
        self.route11 = (get_node("node0"), get_node("node3"))
 
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
        cost_trunk = lambda trunk: trunk.costSD
        all_length = self.ntw.floyd_warshall()
        for i, r in enumerate((self.route9, self.route10, self.route11)):
            path_length = all_length[r[0]][r[1]]
            _, path = self.ntw.A_star(r[0], r[1])
            self.assertEqual(sum(map(cost_trunk, path)), path_length)
            
    def test_LP(self):
        for i, r in enumerate((self.route9, self.route10, self.route11)):
            path = self.ntw.LP_SP_formulation(r[0], r[1])
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
        source = self.ntw.pn["node"][self.ntw.name_to_id["node1"]]
        target = self.ntw.pn["node"][self.ntw.name_to_id["node4"]]
        self.ntw.LP_MCF_formulation(source, target, 12)
 
    def tearDown(self):
        self.netdim.destroy()
 
    def test_MCF(self):
        for trunk_name, flow in self.results:
            trunk = self.ntw.pn["trunk"][self.ntw.name_to_id[trunk_name]]
            self.assertEqual(trunk.flowSD, flow)
        
class TestISIS(unittest.TestCase):
    
    results = (
    ("traffic9", {"trunk0", "trunk1", "trunk4", "trunk5"}),
    ("traffic10", {"trunk2", "trunk3", "trunk5"})
    )
 
    @start_and_import("test_ISIS.xls")
    def setUp(self):
        self.ntw.calculate_all()
 
    def tearDown(self):
        self.netdim.destroy()
 
    def test_ISIS(self):
        self.assertEqual(len(self.ntw.pn["traffic"]), 2)
        for traffic, path in self.results:
            # we retrieve the actual route from its name in pn
            traffic_link = self.ntw.pn["traffic"][self.ntw.name_to_id[traffic]]
            # we check that the path is conform to IS-IS protocol
            self.assertEqual(set(map(str, traffic_link.path)), path)
            
class TestOSPF(unittest.TestCase):
    
    results = (
    ("traffic16", {"trunk14", "trunk2", "trunk3", "trunk6", "trunk8", "trunk15"}),
    ("traffic15", {"trunk14", "trunk2", "trunk4", "trunk5", "trunk6", "trunk8", "trunk15"})
    )
 
    @start_and_import("test_ospf.xls")
    def setUp(self):
        self.ntw.calculate_all()
 
    def tearDown(self):
        self.netdim.destroy()
 
    def test_OSPF(self):
        self.assertEqual(len(self.ntw.pn["traffic"]), 2)
        for traffic_link, path in self.results:
            # we retrieve the actual route from its name in pn
            traffic_link = self.ntw.pn["traffic"][self.ntw.name_to_id[traffic_link]]
            # we check that the path is conform to OSPF protocol
            self.assertEqual(set(map(str, traffic_link.path)), path)
            
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
        node1 = self.ntw.nf(name="node1")
        node2 = self.ntw.nf(name="node2")
        node3 = self.ntw.nf(name="node3")
        node4 = self.ntw.nf(name="node4")
        node6 = self.ntw.nf(name="node6")
        node7 = self.ntw.nf(name="node7")
        # trunk between node4 and node6
        trunk13 = self.ntw.lf(name="trunk13")
        # trunk between node2 and node5
        trunk15 = self.ntw.lf(name="trunk15")
        
        _, path = self.ntw.A_star(node6, node7)
        self.assertEqual(list(map(str, path)), self.results[0])
        _, path = self.ntw.A_star(node6, node7, 
                                                    path_constraints=[node2])
        self.assertEqual(list(map(str, path)), self.results[1])
        _, path = self.ntw.A_star(node6, node7, 
                                            path_constraints=[node3, node2])
        self.assertEqual(list(map(str, path)), self.results[2])                  
        _, path = self.ntw.A_star(node6, node7, 
                                                    excluded_trunks={trunk13})
        self.assertEqual(list(map(str, path)), self.results[3])
        _, path = self.ntw.A_star(node6, node7, 
                            excluded_trunks={trunk13}, excluded_nodes={node1})
        self.assertEqual(list(map(str, path)), self.results[4])
        _, path = self.ntw.A_star(node6, node7, 
                            excluded_trunks={trunk15}, excluded_nodes={node4})
        self.assertEqual(list(map(str, path)), self.results[5])
        
class TestRWA(unittest.TestCase):
     
    @start_and_import("test_RWA.xls")
    def setUp(self):
        pass
 
    def tearDown(self):
        self.netdim.destroy()
        
    def test_RWA(self):
        sco_new_graph = self.ntw.RWA_graph_transformation()
        self.assertEqual(sco_new_graph.ntw.LP_RWA_formulation(), 3)
        
if __name__ == '__main__':
    unittest.main(warnings='ignore')  
    unittest.main()