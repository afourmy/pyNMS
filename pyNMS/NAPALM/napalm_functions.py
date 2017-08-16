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

def open_device(node):
    driver = get_network_driver('ios')
    device = driver(
                    hostname = node.ip_address, 
                    username = 'cisco', 
                    password = 'cisco', 
                    optional_args = {'secret': 'cisco'}
                    )
    device.open()
    return device

def napalm_update(device, node):
    for action, function in napalm_actions.items():
        node.napalm_data[action] = getattr(device, function)()
    node.napalm_data['Configuration']['compare'] = device.compare_config()
    node.napalm_data['cli'] = device.cli(['show logging'])

def standalone_napalm_update(*nodes):
    for node in nodes:
        device = open_device(node)
        # napalm_update(device, node)
        device.close()
        
def napalm_commit(*nodes):
    for node in nodes:
        device = open_device(node)
        device.commit_config()
        napalm_update(device, node)
        device.close()
        
def napalm_discard(*nodes):
    for node in nodes:
        device = open_device(node)
        device.discard_config()
        napalm_update(device, node)
        device.close()
        
def napalm_load_merge(*nodes):
    for node in nodes:
        device = open_device(node)
        config = node.napalm_data['Configuration']['candidate']
        device.load_merge_candidate(config=config)
        napalm_update(device, node)
        device.close()
        
def napalm_load_merge_commit(*nodes):
    for node in nodes:
        device = open_device(node)
        config = node.napalm_data['Configuration']['candidate']
        device.load_merge_candidate(config=config)
        device.commit_config()
        napalm_update(device, node)
        device.close()
        
def napalm_load_replace(*nodes):
    for node in nodes:
        device = open_device(node)
        config = node.napalm_data['Configuration']['candidate']
        device.load_replace_candidate(config=config)
        napalm_update(device, node)
        device.close()
        
def napalm_load_replace_commit(*nodes):
    for node in nodes:
        device = open_device(node)
        config = node.napalm_data['Configuration']['candidate']
        device.load_replace_candidate(config=config)
        device.commit_config()
        napalm_update(device, node)
        device.close()
        