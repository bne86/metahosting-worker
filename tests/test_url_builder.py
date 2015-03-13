import json
import unittest
from urlbuilders import neo_builder, exist_builder, url_builder_filter, \
    NEO_URL_FORMAT, EXIST_URL_FORMAT
import os
from furl import furl

def load_container(name):
    with open(os.path.join('./containers', name)) as ff:
        container = json.load(ff)[0]
    print '%s container loaded' % name
    return container


class RabbitTest(unittest.TestCase):
    def setUp(self):
        self.neo_container = load_container('neo4j.json')
        self.exist_container = load_container('exist.json')

    def tearDown(self):
        pass

    def test_neo_builder(self):
        res = furl(neo_builder(self.neo_container))
        self.assertEqual(res.host, '0.0.0.0')
        self.assertEqual(res.port, 49154)
        self.assertEqual(res.scheme, 'http')

    def test_exist_builder(self):
        res = furl(exist_builder(self.exist_container))
        self.assertEqual(res.host, '0.0.0.0')
        self.assertEqual(res.port, 49153)
        self.assertEqual(res.scheme, 'http')
        self.assertEqual(res.path, '/exist/')

    def test_url_builder_filter_neo(self):
        self.assertFalse('url' in self.neo_container)
        res = url_builder_filter(self.neo_container, NEO_URL_FORMAT)
        self.assertTrue('url' in self.neo_container)
        url = furl(self.neo_container['url'])
        self.assertEqual(url.host, '0.0.0.0')
        self.assertEqual(url.port, 49154)
        self.assertEqual(url.scheme, 'http')

    def test_url_builder_filter_exist(self):
        self.assertFalse('url' in self.exist_container)
        res = url_builder_filter(self.exist_container, EXIST_URL_FORMAT)
        self.assertTrue('url' in self.exist_container)
        url = furl(self.exist_container['url'])
        self.assertEqual(url.host, '0.0.0.0')
        self.assertEqual(url.port, 49153)
        self.assertEqual(url.scheme, 'http')
        self.assertEqual(url.path, '/exist/')