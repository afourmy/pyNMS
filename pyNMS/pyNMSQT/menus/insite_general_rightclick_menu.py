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

import tkinter as tk
from graph_generation.multiple_objects import MultipleNodes
from pythonic_tkinter.preconfigured_widgets import Menu

class InSiteGeneralRightClickMenu(Menu):
    def __init__(self, event, view):
        super().__init__(tearoff=0)
        self.cs = view
        x, y = self.cs.cvs.canvasx(event.x), self.cs.cvs.canvasy(event.y)
                
        # remove all failures if there is at least one
        if self.cs.ns.ntw.failed_obj | self.cs.site.ps['node'] | self.cs.site.ps['link']:
            self.add_command(label='Remove all failures',
                    command=lambda: self.remove_all_failures())
            self.add_separator()
                   
        # multiple nodes creation
        self.add_command(label='Create multiple nodes', 
                command=lambda: MultipleNodes(self.cs, x, y))
                
        # make the menu appear    
        self.tk_popup(event.x_root, event.y_root)

    def remove_all_failures(self):
        self.cs.remove_failures()
        self.destroy()
        
    def refresh(self):
        self.cs.ms.refresh()
        self.destroy()