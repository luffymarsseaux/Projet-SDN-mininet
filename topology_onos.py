#!/usr/bin/env python3
import os
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel, info

# L'IP d'ONOS est fournie par start-sdn.sh (variable d'environnement)
ONOS_IP = os.environ.get('ONOS_IP', '172.17.0.2')


def topology():
    net = Mininet(controller=RemoteController, switch=OVSSwitch,
                  link=TCLink, autoSetMacs=True)

    info('*** Ajout du controleur ONOS (%s)\n' % ONOS_IP)
    c0 = net.addController('c0', controller=RemoteController,
                           ip=ONOS_IP, port=6653)

    info('*** Ajout des 3 switches OpenFlow 1.3\n')
    s1 = net.addSwitch('s1', protocols='OpenFlow13')
    s2 = net.addSwitch('s2', protocols='OpenFlow13')
    s3 = net.addSwitch('s3', protocols='OpenFlow13')

    info('*** Ajout des hotes\n')
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    h3 = net.addHost('h3', ip='10.0.0.3/24')
    h4 = net.addHost('h4', ip='10.0.0.4/24')
    h5 = net.addHost('h5', ip='10.0.0.5/24')
    h6 = net.addHost('h6', ip='10.0.0.6/24')

    info('*** Liens hotes - switches\n')
    net.addLink(h1, s1, bw=10)
    net.addLink(h2, s1, bw=10)
    net.addLink(h3, s2, bw=10)
    net.addLink(h4, s2, bw=10)
    net.addLink(h5, s3, bw=10)
    net.addLink(h6, s3, bw=10)

    info('*** Liens inter-switch (topologie lineaire, sans boucle)\n')
    net.addLink(s1, s2, bw=100)
    net.addLink(s2, s3, bw=100)

    info('*** Demarrage du reseau\n')
    net.build()
    c0.start()
    s1.start([c0])
    s2.start([c0])
    s3.start([c0])

    info('*** Reseau demarre. Lancement du CLI Mininet.\n')
    CLI(net)

    info('*** Arret du reseau\n')
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()
