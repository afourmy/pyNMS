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

from collections import OrderedDict, defaultdict
from napalm_base import get_network_driver
from threading import Thread

napalm_actions = OrderedDict([
('ARP table', 'get_arp_table'),
('Interfaces counters', 'get_interfaces_counters'),
('Facts', 'get_facts'),
('Environment', 'get_environment'),
('Configuration', 'get_config'),
('Interfaces', 'get_interfaces'),
('Interface IP', 'get_interfaces_ip'),
('LLDP neighbors', 'get_lldp_neighbors'),
('LLDP neighbors detail', 'get_lldp_neighbors_detail'),
('MAC address', 'get_mac_address_table'),
('ARP table', 'get_arp_table'),
('NTP servers', 'get_ntp_servers'),
('NTP statistics', 'get_ntp_stats'),
('Transceivers', 'get_optics'),
('SNMP', 'get_snmp_information'),
# ('Users', 'get_users'), # not implemented
# ('Network instances (VRF)', 'get_network_instances'), # not implemented
# ('NTP peers', 'get_ntp_peers'), # not implemented
# ('BGP configuration', 'get_bgp_config'), # not implemented
# ('Traceroute', 'traceroute'), # need argument
# ('BGP neighbors', 'get_bgp_neighbors'), # bug when no neighbors
# ('Routing table', 'get_route_to') # need argument
])

def napalm_update(*nodes):
    for node in nodes:
        driver = get_network_driver('ios')
        device = driver(
                        hostname = node.ipaddress, 
                        username = 'cisco', 
                        password = 'cisco', 
                        optional_args = {'secret': 'cisco'}
                        )
        device.open()
        for action, function in napalm_actions.items():
            node.napalm_data[action] = getattr(device, function)()
        node.napalm_data['Configuration']['compare'] = device.compare_config()
        device.close()
        
def napalm_action(action, *nodes):
    for node in nodes:
        driver = get_network_driver('ios')
        device = driver(
                        hostname = node.ipaddress, 
                        username = 'cisco', 
                        password = 'cisco', 
                        optional_args = {'secret': 'cisco'}
                        )
        device.open()
        if action in ('commit', 'discard'):
            function = {
                        'commit': device.commit_config,
                        'discard': device.discard_config,
                        }[action]()
        else:
            config = node.napalm_data['Configuration']['candidate']
            function = {
                        'load_merge_candidate': device.load_merge_candidate,
                        'load_replace_candidate': device.load_replace_candidate
                        }[action](config=config)
        device.close()
