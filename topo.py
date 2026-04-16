from mininet.topo import Topo

class FlowTopo(Topo):
    def build(self):

        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')

        h1 = self.addHost('h1', mac='00:00:00:00:00:01')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')

        self.addLink(h1, s1)
        self.addLink(s1, s2)
        self.addLink(s2, s3)
        self.addLink(s3, h2)
        self.addLink(h3, s2)
        self.addLink(h4, s3)

topos = {'flowtopo': FlowTopo}
