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

class TestFlow(unittest.TestCase):
 
    @start_and_import("test_flow1.xls")
    def setUp(self):
        self.source = self.netdim.cs.pn["node"]["s"]
        self.target = self.netdim.cs.pn["node"]["t"]
 
    def tearDown(self):
        self.netdim.destroy()
 
    def test_ford_fulkerson(self):
        ff_flow = self.netdim.cs.ford_fulkerson(self.source, self.target)
        self.assertEqual(ff_flow, 19)
        
    def test_edmonds_karp(self):
        ek_flow = self.netdim.cs.edmonds_karp(self.source, self.target)
        self.assertEqual(ek_flow, 19)   
    
    def test_LP_flow(self):
        LP_flow = self.netdim.cs.LP_MF_formulation(self.source, self.target)
        self.assertEqual(LP_flow, 19)   
        
class TestMST(unittest.TestCase):
 
    @start_and_import("test_mst1.xls")
    def setUp(self):
        pass
 
    def tearDown(self):
        self.netdim.destroy()
 
    def test_kruskal(self):
        mst = self.netdim.cs.kruskal(self.netdim.cs.pn["node"].values())
        mst_costs = set(map(lambda trunk: trunk.costSD, mst))
        self.assertEqual(mst_costs, {1, 2, 4})
        
if __name__ == '__main__':
    unittest.main(warnings='ignore')  
    unittest.main()