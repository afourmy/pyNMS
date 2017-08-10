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

from .base_view import BaseView
from graphical_objects.graphical_link import GraphicalLink
from right_click_menus.network_general_menu import NetworkGeneralMenu
from math import sqrt
from miscellaneous.decorators import overrider
from networks import main_network
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from random import randint

class NetworkView(BaseView):

    def __init__(self, controller):
        super().__init__(controller)
        
    ## Drawing functions
        
    def refresh_display(self):
        # we draw everything except interface
        for type in set(self.network.pn) - {'interface'}:
            self.draw_objects(*self.network.pn[type].values())
            
    @overrider(BaseView)
    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if self.controller.mode == 'creation':
            if self.is_node(item) and event.buttons() == Qt.LeftButton:
                self.start_node = item
                self.start_position = pos = self.mapToScene(event.pos())
                self.temp_line = QGraphicsLineItem(QLineF(pos, pos))
                self.temp_line.setZValue(2)
                self.scene.addItem(self.temp_line)
        super(NetworkView, self).mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        item = self.itemAt(event.pos())
        if hasattr(self, 'temp_line') and self.temp_line:
            if self.is_node(item):
                self.end_node = item
                GraphicalLink(self)
                # we made the start node unselectable and unmovable to enable
                # the creation of links, in the press binding of GraphicalNode: 
                # we revert this change at link creation
                self.start_node.setFlag(QGraphicsItem.ItemIsSelectable, True)
                self.start_node.setFlag(QGraphicsItem.ItemIsMovable, True)
            self.scene.removeItem(self.temp_line)
            self.temp_line = None
        if event.button() == Qt.RightButton and self.trigger_menu:
            if not self.is_node(item) and not self.is_link(item): 
                menu = NetworkGeneralMenu(event, self.controller)
                menu.exec_(event.globalPos())
        super(NetworkView, self).mouseReleaseEvent(event)
        
    ## Object deletion
    
    def remove_objects(self, *items):
        for item in items:
            obj = item.object
            self.scene.removeItem(item)
            # remove it from all AS it belongs to
            if hasattr(obj, 'AS'):
                for AS in list(obj.AS):
                    AS.management.remove_from_AS(obj)
            # remove it from all sites it belongs to
            for site in set(obj.sites):
                site.view.remove_from_site(obj)
            # remove it from the scene and the network model
            if self.is_node(item):
                for link in self.network.remove_node(obj):
                    self.remove_objects(link.glink[self])
            else:
                self.network.remove_link(obj)
        
    ## Force-directed layout algorithms
    
    def distance(self, p, q): 
        return sqrt(p*p + q*q)
    
    ## 1) Eades algorithm (spring layout)
    
    # We use the following constants:
    # - k is the spring constant (stiffness of the spring)
    # - L0 is the equilibrium length
    # - cf is the Coulomb factor (repulsive force factor)
    # - sf is the speed factor
    
    def coulomb_force(self, dx, dy, distance, cf):
        c = distance and cf/distance**3
        return (-c*dx, -c*dy)
        
    def hooke_force(self, dx, dy, distance, L0, k):
        const = distance and k*(distance - L0)/distance
        return (const*dx, const*dy)
            
    def spring_layout(self, cf, k, sf, L0):
        for nodeA in self.node_selection:
            Fx = Fy = 0
            for nodeB in self.node_selection:
                if nodeA != nodeB:
                    dx, dy = nodeB.x - nodeA.x, nodeB.y - nodeA.y
                    distance = self.distance(dx, dy)
                    F_hooke = (0,)*2
                    if self.network.is_connected(nodeA.node, nodeB.node, 'plink'):
                        F_hooke = self.hooke_force(dx, dy, distance, L0, k)
                    F_coulomb = self.coulomb_force(dx, dy, distance, cf)
                    Fx += F_hooke[0] + F_coulomb[0]
                    Fy += F_hooke[1] + F_coulomb[1]
            nodeA.vx = max(-100, min(100, 0.5 * nodeA.vx + 0.2 * Fx))
            nodeA.vy = max(-100, min(100, 0.5 * nodeA.vy + 0.2 * Fy))
    
        for node in self.node_selection:
            node.x, node.y = node.x + node.vx*sf, node.y + node.vy*sf
            
    ## 2) Fruchterman-Reingold algorithm
    
    def fa(self, d, k):
        return (d**2)/k
    
    def fr(self, d, k):
        return -(k**2)/d
        
    def fruchterman_reingold_layout(self, limit=False, opd=0):
        t = 1
        if not opd:
            try:
                opd = sqrt(500*500/len(self.node_selection))
            except ZeroDivisionError:
                return
        for nodeA in self.node_selection:
            nodeA.vx, nodeA.vy = 0, 0
            for nodeB in self.node_selection:
                if nodeA != nodeB:
                    dx, dy = nodeA.x - nodeB.x, nodeA.y - nodeB.y
                    distance = self.distance(dx, dy)
                    if distance:
                        nodeA.vx += (dx*opd**2)/distance**2
                        nodeA.vy += (dy*opd**2)/distance**2
                    
        for link in self.network.plinks.values():
            source, destination = link.source.gnode[self], link.destination.gnode[self]
            dx, dy = source.x - destination.x, source.y - destination.y
            distance = self.distance(dx, dy)
            if distance:
                link.source.gnode[self].vx -= distance*dx/opd
                link.source.gnode[self].vy -= distance*dy/opd
                link.destination.gnode[self].vx += distance*dx/opd
                link.destination.gnode[self].vy += distance*dy/opd
            
        for node in self.node_selection:
            distance = self.distance(node.vx, node.vy)
            node.x += node.vx/sqrt(distance)
            node.y += node.vy/sqrt(distance)
            
        t *= 0.95
        
    def igraph_test(self):
        pass
        #TODO later: networkx + igraph drawing algorithms
        # import igraph
        # g = igraph.Graph.Tree(127, 2)
        # b = igraph.BoundingBox(0, 0, 1000, 1000)
        # layout = g.layout("kamada_kawai")
        # for row in layout:
        #     print(row)
        
    def timerEvent(self, event):
        if self.drawing_algorithm =='Spring-based layout':
            parameters = self.controller.spring_layout_parameters_window.get_values()
            self.spring_layout(*parameters)
        else:
            self.fruchterman_reingold_layout()

    def stop_timer(self):
        self.killTimer(self.timer)
        
    ## Drawing functions
        
    def random_layout(self):
        for gnode in self.node_selection:
            gnode.x = randint(int(gnode.x) - 500, int(gnode.x) + 500)
            gnode.y = randint(int(gnode.y) - 500, int(gnode.y) + 500)
        