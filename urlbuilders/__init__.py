from furl import furl

NEO_URL_FORMAT = 'http://localhost:7474'
EXIST_URL_FORMAT = 'http://localhost:8080/exist/'


def get_port_mapping(container):
    return container['NetworkSettings']['Ports']


class GenericUrlBuilder(object):

    def __init__(self, url_formatting_string):
        self.target_url = furl(url_formatting_string)

    def substitute_host(self, port, port_mapping):
        # {u'HostIp': u'0.0.0.0', u'HostPort': u'49154'}
        mp = port_mapping[port][0]
        self.target_url.port = int(mp['HostPort'])
        self.target_url.host = mp['HostIp']

    def build(self, port_mapping):
        port = '%s/tcp' % self.target_url.port
        self.substitute_host(port, port_mapping)
        return '%s' % self.target_url


def neo_builder(container):
    b = GenericUrlBuilder(NEO_URL_FORMAT)
    return b.build(get_port_mapping(container))


def exist_builder(container):
    b = GenericUrlBuilder(EXIST_URL_FORMAT)
    return b.build(get_port_mapping(container))


def url_builder_filter(container, url_formatting_string=None):
    if url_formatting_string is None:
        return container
    url_builder = GenericUrlBuilder(url_formatting_string)
    container['url'] = url_builder.build(get_port_mapping(container))