#!/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import irange
from mininet.log import setLogLevel
from mininet.node import RemoteController, Host, Switch, Link
from mininet.cli import CLI

class LinearTopo(Topo):
    """Linear topology of k switches, with one host per switch."""

    def __init__(self, switches=3, hosts_per_switch=1, **opts):
        """ In it.
            switches: number of switches (and hosts)
            hosts_per_switch: number of hosts per switch """

        super(LinearTopo, self).__init__(**opts)
        self.k = switches

        lastSwitch = None
        lastHost = 0
        for i in irange(1, switches):
            switch = self.addSwitch('s%s' % i)
            for j in irange(lastHost + 1, hosts_per_switch + lastHost):
                host = self.addHost('h%s' % j, ip='11.0.0.%s' % j)
                self.addLink(host, switch)
                lastHost = j

            if lastSwitch:
                self.addLink(switch, lastSwitch)
            lastSwitch = switch


def simpleTest():
    """Create and test a simple network"""
    topo = LinearTopo(switches=3, hosts_per_switch=2)
    net = Mininet(topo=topo, controller=RemoteController)
    net.start()
    CLI(net)
    net.stop()


if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    simpleTest()
