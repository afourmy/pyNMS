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
 
    def test_dijkstra(self):
        for i, r in enumerate((self.route9, self.route10, self.route11)):
            self.assertEqual(list(map(str, r.path)), self.results[i])
        
    def test_bellman_ford(self):
        for i, r in enumerate((self.route9, self.route10, self.route11)):
            _, path = self.netdim.cs.ntw.bellman_ford(r.source, r.destination)
            self.assertEqual(list(map(str, path)), self.results[i])
        
    def test_floyd_warshall(self):
        cost_trunk = lambda trunk: getattr(trunk, "costSD")
        all_length = self.netdim.cs.ntw.floyd_warshall()
        for r in (self.route9, self.route10, self.route11):
            path_length = all_length[r.source][r.destination]
            self.assertEqual(sum(map(cost_trunk, r.path)), path_length)
            
    def test_LP(self):
        source = self.netdim.cs.ntw.nf(name="node0")
        destination = self.netdim.cs.ntw.nf(name="node3")
        path_sum = self.netdim.cs.ntw.LP_SP_formulation(source, destination)
        self.assertEqual(path_sum, 2)
        
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
    ("node8->node1", ["trunk11", "trunk7", "trunk12", "trunk5"]),
    ("node1->node8", ["trunk5", "trunk3", "trunk6", "trunk11"])
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
        
if __name__ == '__main__':
    unittest.main(warnings='ignore')  
    unittest.main()