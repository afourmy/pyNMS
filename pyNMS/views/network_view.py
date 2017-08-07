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

from .geographical_view import GeographicalView
from networks import main_network

class NetworkView(GeographicalView):

    def __init__(self, controller):
        self.network = main_network.MainNetwork(self)
        super().__init__(controller)
        
    def refresh_display(self):
        print('test1')
        # we draw everything except interface
        for type in set(self.network.pn) - {'interface'}:
            self.draw_objects(self.network.pn[type].values())
        