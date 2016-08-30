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

def masktosubnet(ip):
    return "".join(map(bin, map(int, ip.split(".")))).count("1")
    
def mac_incrementer(mac_address, nb):
    return "{:012X}".format(int(mac_address, 16) + nb)
    
def ip_incrementer(ip_address, nb):
    return tostring(toip(ip_address) + nb)