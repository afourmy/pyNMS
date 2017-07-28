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

class Area(object):
    
    class_type = 'area'
    
    def __init__(self, name, id, AS, links, nodes):
        self.name = name
        self.id = int(id)
        self.AS = AS
        # it is important to write set(nodes) and not just nodes so that
        # both set are distinct in memory, and when we remove a node
        # (or physical link) from an area, it is not removed from the AS as well.
        self.pa = {'node': set(nodes), 'link': set(links)}
        # update the AS dict for all objects, so that they are aware they
        # belong to this new area
        for obj in nodes | links:
            obj.AS[self.AS].add(self)
        # update the area dict of the AS with the new area
        self.AS.areas[name] = self
        # add the area to the AS management panel area listbox
        self.AS.management.add_area(name, id)
        
    def __repr__(self):
        return self.name
        
    def add_to_area(self, *objects):
        for obj in objects:
            self.pa[obj.class_type].add(obj)
            obj.AS[self.AS].add(self)
            
    def remove_from_area(self, *objects):
        for obj in objects:
            self.pa[obj.class_type].discard(obj)
            obj.AS[self.AS].discard(self)
            
