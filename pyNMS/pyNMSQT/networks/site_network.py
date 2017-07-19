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

from .base_network import BaseNetwork
from views.insite_view import InSiteView
from objects.objects import *

def overrider(interface_class):
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider

class SiteNetwork(BaseNetwork):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    # 'nf' is the node factory. Creates or retrieves any type of nodes
    @overrider(BaseNetwork)
    def nf(self, node_type='router', id=None, **kwargs):
        if not id:
            if 'name' not in kwargs:
                name = node_type + str(len(list(self.ftr('node', node_type))))
                kwargs['name'] = name
            else:
                if kwargs['name'] in self.name_to_id:
                    return self.nodes[self.name_to_id[kwargs['name']]]
            id = self.cpt_node
            kwargs['id'] = id
            self.nodes[id] = node_class[node_type](**kwargs)
            self.nodes[id].view = InSiteView(
                                             self.nodes[id], 
                                             kwargs['name'],
                                             self.view.controller,
                                             )
            self.name_to_id[kwargs['name']] = id
            self.cpt_node += 1
        return self.nodes[id]