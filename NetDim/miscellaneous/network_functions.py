# NetDim
# Copyright (C) 2016 Antoine Fourmy (antoine.fourmy@gmail.com)
# Released under the GNU General Public License GPLv3

BYTE = range(32, 0, -8)

# ranges of private MAC addresses
# x2-xx-xx-xx-xx-xx
# x6-xx-xx-xx-xx-xx
# xA-xx-xx-xx-xx-xx
# xE-xx-xx-xx-xx-xx
START_MAC = "020000000000"

def toip(ip):
    return sum(x << s - 8 for x, s in zip(map(int, ip.split(".")), BYTE))
    
def tostring(ip):
    return ".".join(str((ip & (1 << i) - 1) >> (i - 8)) for i in BYTE)

def compute_network(ip, mask):
    return tostring(toip(ip) & toip(mask))

def tosubnet(ip):
    # convert a subnet mask to a subnet
    # ex: tosubnet("255.255.255.252") = 30
    return "".join(map(bin, map(int, ip.split(".")))).count("1")
    
def wildcard(ip):
    # convert a subnet mask to a wildcard mask or the other way around
    # ex: towildcard("255.255.255.252") = "0.0.0.3"
    #     towildcard("0.0.0.3") = "255.255.255.252"
    return ".".join(map(lambda i: str(255 - int(i)), ip.split(".")))

def tomask(subnet):
    # convert a subnet to a subnet mask
    # ex: tomask(30) = "255.255.255.252"
    return tostring(int("1"*subnet + "0"*(32 - subnet), 2))
    
def mac_incrementer(mac_address, nb):
    # increment a mac address by "nb"
    return "{:012X}".format(int(mac_address, 16) + nb)
    
def ip_incrementer(ip_address, nb):
    # increment an ip address by "nb"
    return tostring(toip(ip_address) + nb)