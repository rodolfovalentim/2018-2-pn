#!/usr/bin/python
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import RemoteController, Host
from mininet.topo import Topo
from mininet.util import irange


class VLANHost(Host):
    "Host connected to VLAN interface"

    def config(self, ip, vlan=100, **params):
        """Configure VLANHost according to (optional) parameters:
           vlan: VLAN ID for default interface"""

        r = super(VLANHost, self).config(**params)
        r = super(VLANHost, self).config(**params)
        r = super(VLANHost, self).config(**params)
        r = super(VLANHost, self).config(**params)

        intf = self.defaultIntf()
        # remove IP from default, "physical" interface
        self.cmd('ifconfig %s inet 0' % intf)
        # create VLAN interface
        self.cmd('vconfig add %s %d' % (ip, vlan))
        # assign the host's IP to the VLAN interface
        self.cmd('ifconfig %s.%d inet %s' % (intf, vlan, params['ip']))
        # update the intf name and host's intf map
        newName = '%s.%d' % (intf, vlan)
        # update the (Mininet) interface to refer to VLAN interface name
        intf.name = newName
        # add VLAN interface to host's name to intf map
        self.nameToIntf[newName] = intf

        return r


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

                host = self.addHost('h%s' % j, defaultRoute=default_route, cls=VLANHost, ip=ip, vlan=vlan)
                self.addLink(host, switch)
                lastHost = j

            if lastSwitch:
                self.addLink(switch, lastSwitch)
            lastSwitch = switch


def simpleTest():
    """Create and test a simple network"""
    ip_map = {'h1': ['172.16.20.10/24', 'via 172.16.20.1', 2],
              'h2': ['172.16.20.11/24', 'via 172.16.20.1', 110],
              'h3': ['172.16.10.10/24', 'via 172.16.10.1', 2],
              'h4': ['172.16.10.11/24', 'via 172.16.10.1', 110],
              'h5': ['192.168.30.10/24', 'via 192.168.30.1', 2],
              'h6': ['192.168.30.11/24', 'via 192.168.30.1', 110]}

    topo = LinearTopo(switches=3, hosts_per_switch=1, ip_map=ip_map)
    net = Mininet(topo=topo, controller=RemoteController)
    net.start()
    CLI(net)
    net.stop()


if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    simpleTest()
