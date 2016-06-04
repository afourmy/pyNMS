import unittest
import sys
from inspect import getsourcefile
from os.path import abspath

path_app = abspath(getsourcefile(lambda: 0))[:-7]
if path_app not in sys.path:
    sys.path.append(path_app)
    
import gui

def start_and_import(filename):
    def inner_decorator(function):
        def wrapper(self):
            self.netdim = gui.NetDim(path_app)
            path_test = path_app + "Tests\\"
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
        for extension in ("xls", "txt", "csv"):
            cls.netdim.export_graph(path_app + "Tests\\test_export." + extension)
        cls.netdim.destroy()
        
    def tearDown(self):
        self.netdim.destroy()
        
    def object_import(self, ext):
        self.netdim = gui.NetDim(path_app)
        self.netdim.import_graph(path_app + "Tests\\test_export." + ext)
        x_coord = set(map(lambda n: n.x, self.netdim.cs.ntw.pn["node"].values()))
        self.assertEqual(x_coord, {42, 24})
        trunk ,= self.netdim.cs.ntw.pn["trunk"].values()
        self.assertEqual(trunk.distance, 666)
        self.assertEqual(len(self.netdim.cs.ntw.pn["route"].values()), 1)
        
    def test_object_import_xls(self):
        self.object_import("xls")
        
    def test_object_import_txt(self):
        self.object_import("txt")
        
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
        
if __name__ == '__main__':
    unittest.main(warnings='ignore')  
    unittest.main()