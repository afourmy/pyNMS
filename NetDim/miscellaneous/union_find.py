# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3
        
class UnionFind:
    
    def __init__(self, nodes):
        self.up = {node: node for node in nodes}
        self.rank = {node: 0 for node in nodes}
        
    def find(self, node):
        if self.up[node] == node:
            return node
        else:
            self.up[node] = self.find(self.up[node])
            return self.up[node]
            
    def union(self, nA, nB):
        repr_nA = self.find(nA)
        repr_nB = self.find(nB)
        if repr_nA == repr_nB:
            return False
        if self.rank[repr_nA] >= self.rank[repr_nB]:
            self.up[repr_nB] = repr_nA
            if self.rank[repr_nA] == self.rank[repr_nB]:
                self.rank[repr_nA] += 1   
        else:
            self.up[repr_nA] == repr_nB
        return True
