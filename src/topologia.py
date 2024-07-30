from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink

def topologiaSDN():
    net = Mininet(topo=None, build=False, link=TCLink)

    info('*** Adicionando o controlador remoto\n')
    net.addController(name='c0',
                      controller=RemoteController,
                      ip='127.0.0.1',
                      port=6633)

    info('*** Adicionando switches\n')
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    s3 = net.addSwitch('s3')

    info('*** Adicionando sistemas finais\n')
    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')
    h3 = net.addHost('h3', ip='10.0.0.3')
    h4 = net.addHost('h4', ip='10.0.0.4')
    h5 = net.addHost('h5', ip='10.0.0.5')
    h6 = net.addHost('h6', ip='10.0.0.6')

    info('*** Adicionando enlaces\n')
    net.addLink(s1, h1)
    net.addLink(s1, h2)
    net.addLink(s1, s2)
    net.addLink(s2, h3)
    net.addLink(s2, h4)
    net.addLink(s2, h5)
    net.addLink(s2, s3)
    net.addLink(s3, h6)
    net.addLink(s3, s1)

    info('*** Iniciando a rede\n')
    net.build()
    net.start()

    info('*** Executando CLI\n')
    CLI(net)

    info('*** Parando a rede\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topologiaSDN()
