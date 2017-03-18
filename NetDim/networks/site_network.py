# NetDim
# Copyright (C) 2017 Antoine Fourmy (contact@netdim.fr)
# Released under the GNU General Public License GPLv3

from .base_network import BaseNetwork

class SiteNetwork(BaseNetwork):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)