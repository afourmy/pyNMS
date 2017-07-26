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

import os
from PyQt5.QtWidgets import QMenu, QAction
from .selection_menu import SelectionMenu
from autonomous_system import AS
from objects.objects import *
import ip_networks.configuration as conf
import ip_networks.troubleshooting as ip_ts
import ip_networks.ping as ip_ping
import ip_networks.switching_table as switching_table
import ip_networks.arp_table as arp_table
import ip_networks.routing_table as ip_rt
import ip_networks.bgp_table as ip_bgpt
import graph_generation.multiple_objects as mobj
from miscellaneous import site_operations
from objects.object_management_window import ObjectManagementWindow, PropertyChanger
from collections import OrderedDict
from objects.interface_window import InterfaceWindow
                                
class NetworkSelectionMenu(SelectionMenu):
    
    def __init__(self, controller):
        super().__init__(controller)
        
        if self.no_shape:
            simulate_failure = QAction('&Simulate failure', self)        
            simulate_failure.triggered.connect(lambda: self.simulate_failure(*self.so))
            self.addAction(simulate_failure)
            remove_failure = QAction('&Remove failure', self)        
            remove_failure.triggered.connect(lambda: self.remove_failure(*self.so))
            self.addAction(remove_failure)
            self.addSeparator()

        self.addAction(self.align_action)
        self.addAction(self.drawing_action)
                
    def simulate_failure(self, *objects):
        self.view.simulate_failure(*objects)
        
    def remove_failure(self, *objects):
        self.view.remove_failure(*objects)
            