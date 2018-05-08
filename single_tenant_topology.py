#!/usr/bin/python
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import RemoteController, Host
from mininet.topo import Topo
from mininet.util import irange


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
            switch = self.addSwitch('s%s' % i, protocols='OpenFlow13', address='172.16.20.1/24')
            for j in irange(lastHost + 1, hosts_per_switch + lastHost):

                ip = '10.0.0.%s/24' % j
                if opts['ip_map']:
                    ip = opts['ip_map']['h%s' % j][0]
                    default_route = opts['ip_map']['h%s' % j][1]
                    vlan = opts['ip_map']['h%s' % j][2]

                host = self.addHost('h%s' % j, defaultRoute=default_route, ip=ip)
                self.addLink(host, switch)
                lastHost = j

            if lastSwitch:
                self.addLink(switch, lastSwitch)
            lastSwitch = switch


def simpleTest(e):
    """Create and test a simple network"""
    ip_map = {'h1': ['172.16.20.10/24', 'via 172.16.20.1'],
              'h2': ['172.16.10.10/24', 'via 172.16.10.1'],
              'h3': ['192.168.30.10/24', 'via 192.168.30.1']}

    topo = LinearTopo(switches=3, hosts_per_switch=1, ip_map=ip_map)
    net = Mininet(topo=topo, controller=RemoteController)
    net.start()
    CLI(net)
    net.stop()


if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    simpleTest()
