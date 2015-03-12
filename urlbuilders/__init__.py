from furl import furl


def get_port_mapping(container):
    return container['NetworkSettings']['Ports']


class GenericUrlBuilder(object):

    def __init__(self, container, url):
        self.target_url = furl(url)
        self.container = container

    def substitute_host(self, port, port_mapping):
        # {u'HostIp': u'0.0.0.0', u'HostPort': u'49154'}
        mp = port_mapping[port][0]
        self.target_url.port = int(mp['HostPort'])
        self.target_url.host = mp['HostIp']

    def convert_url(self):
        port = '%s/tcp' % self.target_url.port
        self.substitute_host(port, get_port_mapping(self.container))
        return self.target_url


def neo_builder(container):
    b = GenericUrlBuilder(container, 'http://localhost:7474')
    return b.convert_url()