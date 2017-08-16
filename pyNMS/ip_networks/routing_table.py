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

from miscellaneous.decorators import update_paths
from operator import itemgetter
from pyQT_widgets.Q_console_edit import QConsoleEdit
from PyQt5.QtWidgets import QWidget, QTextEdit, QGridLayout

# protocol to Administrative Distances
AD = {
'S': 1,
'O': 110,
'i': 115,
'R': 120
}

class RoutingTable(QWidget):
    
    @update_paths(True)
    def __init__(self, node, controller):
        super().__init__()
        self.setWindowTitle('Switching table')
        self.setMinimumSize(600, 800)
        
        config_edit = QConsoleEdit()

        codes = '''
Codes: C - connected, S - static, R - RIP, M - mobile, B - BGP
        D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area
        N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2
        E1 - OSPF external type 1, E2 - OSPF external type 2
        i - IS-IS, su - IS-IS summary, L1 - IS-IS level-1, L2 - IS-IS level-2
        ia - IS-IS inter area, * - candidate default, U - per-user static route
        o - ODR, P - periodic downloaded static route\n\n'''
        
        config_edit.insertPlainText(codes)
        
        gateway = 'Gateway of last resort is not set\n\n'
        config_edit.insertPlainText(gateway)
                
        list_RT = sorted(node.rt.items(), key=itemgetter(1))
        for sntw, routes in list_RT:
            if len(routes) - 1:
                for idx, route in enumerate(routes):
                    rtype, ex_ip, ex_int, cost, *_ ,= route
                    rtype = rtype + ' '*(8 - len(rtype))
                    if not idx:
                        line = '{rtype}{sntw} [{AD}/{cost}] via {ex_ip}, {ex_int}\n'\
                                                    .format(
                                                            cost = int(cost), 
                                                            rtype = rtype, 
                                                            sntw = sntw, 
                                                            AD = AD[rtype[0]],
                                                            ex_ip = ex_ip.ip_addr, 
                                                            ex_int = ex_int
                                                            )
                    else:
                        spaces = ' '*(len(rtype) + len(sntw))
                        line = '{spaces} [{AD}/{cost}] via {ex_ip}, {ex_int}\n'\
                                                    .format(
                                                            spaces = spaces,
                                                            AD = AD[rtype[0]],
                                                            cost = int(cost),
                                                            ex_ip = ex_ip.ip_addr,
                                                            ex_int = ex_int
                                                            )
                    config_edit.insertPlainText(line)
                        
            else:
                route ,= routes
                rtype, ex_ip, ex_int, cost, *_ ,= route
                rtype = rtype + ' '*(8 - len(rtype))
                if rtype[0] in ('O', 'i', 'R'):
                    route = '{rtype}{sntw} [{AD}/{cost}] via {ex_ip}, {ex_int}\n'\
                                                .format(
                                                        cost = int(cost),
                                                        rtype = rtype, 
                                                        sntw = sntw,
                                                        AD = AD[rtype[0]],
                                                        ex_ip = ex_ip.ip_addr,
                                                        ex_int = ex_int
                                                        )
                elif rtype[0] == 'S':
                    route = '{rtype}{sntw} [{AD}/{cost}] via {ex_ip}\n'\
                                                .format(
                                                        cost = int(cost),
                                                        rtype = rtype, 
                                                        sntw = sntw,
                                                        AD = AD[rtype[0]],
                                                        ex_ip = ex_ip.ip_addr, 
                                                        )
                else:
                    route = '{rtype}{sntw} is directly connected, {ex_int}\n'\
                        .format(rtype=rtype, sntw=sntw, ex_int=ex_int)
                config_edit.insertPlainText(route)
                                        
        layout = QGridLayout()
        layout.addWidget(config_edit, 0, 0, 1, 1)
        self.setLayout(layout)
                                            