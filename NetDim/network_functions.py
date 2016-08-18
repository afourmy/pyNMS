BYTE = range(32, 0, -8)

def toip(ip):
    return sum(x << s - 8 for x, s in zip(map(int, ip.split(".")), BYTE))
    
def tostring(ip):
    return ".".join(str((ip & (1 << i) - 1) >> (i - 8)) for i in BYTE)

def compute_network(ip, mask):
    return tostring(toip(ip) & toip(mask))

def masktosubnet(ip):
    return "".join(map(bin, map(int, ip.split(".")))).count("1")