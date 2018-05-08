#!/usr/bin/python
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import RemoteController, Host
from mininet.topo import Topo
from mininet.util import irange


class VLANHost(Host):
    "Host connected to VLAN interface"

    def config(self, vlan=100, **params):
        """Configure VLANHost according to (optional) parameters:
           vlan: VLAN ID for default interface"""

        r = super(VLANHost, self).config(**params)

        intf = self.defaultIntf()
        # remove IP from default, "physical" interface
        self.cmd('ifconfig %s inet 0' % intf)
        # create VLAN interface
        self.cmd('vconfig add %s %d' % (intf, vlan))
        # assign the host's IP to the VLAN interface
        self.cmd('ifconfig %s.%d inet %s' % (intf, vlan, params['ip']))
        # update the intf name and host's intf map
        newName = '%s.%d' % (intf, vlan)
        # restore default gateway
        self.cmd('route add default gw %s' % params['gateway'])
        # update thee (Mininet) interface to refer to VLAN interface name
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
            switch = self.addSwitch('s%s' % i, protocols='OpenFlow13')
            for j in irange(lastHost + 1, hosts_per_switch + lastHost):

                ip = '10.0.0.%s/24' % j
                if opts['ip_map']:
                    ip = opts['ip_map']['h%s' % j][0]
                    gateway = opts['ip_map']['h%s' % j][1]
                    vlan = opts['ip_map']['h%s' % j][2]

                host = self.addHost('h%s' % j, cls=VLANHost, ip=ip, vlan=vlan, gateway=gateway)
                self.addLink(host, switch)
                lastHost = j

            if lastSwitch:
                self.addLink(switch, lastSwitch)
            lastSwitch = switch


def simpleTest():
    """Create and test a simple network"""
    ip_map = {'h1': ['172.16.10.10/24', '172.16.10.1', 2, '172.16.10.254'],
              'h2': ['172.16.10.11/24', '172.16.10.1', 110, '172.16.10.254'],
              'h3': ['192.168.30.10/24', '192.168.30.1', 2, '192.168.30.254'],
              'h4': ['192.168.30.11/24', '192.168.30.1', 110, '192.168.30.254'],
              'h5': ['172.16.20.10/24', '172.16.20.1', 2, '172.16.10.254'],
              'h6': ['172.16.20.11/24', '172.16.20.1', 110, '172.16.10.254']}

    topo = LinearTopo(switches=3, hosts_per_switch=2, ip_map=ip_map)
    net = Mininet(topo=topo, controller=RemoteController)
    net.start()
    CLI(net)
    net.stop()


if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    simpleTest()
