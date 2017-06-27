# Copyright (C) 2017 Antoine Fourmy <antoine dot fourmy at gmail dot com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
        
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
