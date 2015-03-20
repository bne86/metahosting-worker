from furl import furl


class GenericUrlBuilder(object):

    def __init__(self, worker_conf):
        """
        use a url template to create services URLs based on the container
        networking config
        :param worker_conf: dict containing the worker config
        :return:
        """
        self.service_url = dict()
        if 'formatting_string' in worker_conf:
            for url in worker_conf['formatting_string'].split(';'):
                self.service_url[url] = furl(url)

    def build(self, port_mapping):
        """
        :param port_mapping: a docker port mapping(container[][], e.g.
        {u'15672/tcp': [{u'HostPort': u'7000', u'HostIp': u'192.168.59.103'}],
        u'5672/tcp': [{u'HostPort': u'7001', u'HostIp': u'192.168.59.103'}]}
        :return: list of urls
        """
        urls = list()
        for internal_port in port_mapping.keys():
            for index, unused in enumerate(port_mapping[internal_port]):
                endpoint = port_mapping[internal_port][index]
                port, proto = internal_port.split('/')
                tmp_url = None
                'if our internal url is part of a formatting template, use it'
                for item in self.service_url.keys():
                    if int(port) == self.service_url[item].port:
                        tmp_url = self.service_url[item].copy()
                        tmp_url.port = int(endpoint['HostPort'])
                        tmp_url.host = endpoint['HostIp']
                        break
                'otherwise we create a url with http(most often default?)'
                if not tmp_url:
                    tmp_url = furl('http://{}:{}'.format(
                        endpoint['HostIp'], endpoint['HostPort']))
                urls.append(str(tmp_url))
        return urls
