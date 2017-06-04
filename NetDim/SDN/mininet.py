from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import DefaultController, RemoteController
net = Mininet()
h1 = net.addHost('h1')
net.start()
CLI(net)
