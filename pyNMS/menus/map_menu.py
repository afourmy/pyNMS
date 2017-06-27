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

from pythonic_tkinter.preconfigured_widgets import *
from collections import OrderedDict

class MapMenu(Menu):
    
    def __init__(self, view, nodes):
        super().__init__(0)
        self.cs = view
        
        cmds = OrderedDict([
                    ('Update geographical coordinates with current position', 
                        lambda: self.cs.update_geographical_coordinates(*nodes)
                    ),
                    ('Update logical coordinates with current position', 
                        lambda: self.cs.update_logical_coordinates(*nodes)
                    ),
                    ('Move selected nodes to geographical coordinates', 
                        lambda: self.cs.move_to_geographical_coordinates(*nodes)
                    ),
                    ('Move selected nodes to logical coordinates', 
                        lambda: self.cs.move_to_logical_coordinates(*nodes)
                    ),
                    ('move to geo', lambda: self.cs.to_geo(*nodes)),
        ])
    
        for label, cmd in cmds.items():
            self.add_command(label=label, command=cmd)