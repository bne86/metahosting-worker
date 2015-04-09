import json
import unittest
import os
from furl import furl

NEO_URL_FORMAT = 'http://localhost:7474'
EXIST_URL_FORMAT = 'http://localhost:8080/exist'
RABBIT_URL_FORMAT = 'amqp://localhost:5672;http://localhost:15672'


def load_container(name):
    with open(os.path.join('tests/containers', name)) as ff:
        container = json.load(ff)
    return container


class TestGenericUrlBuilder(unittest.TestCase):
    def setUp(self):
        self.neo_container = load_container('neo4j.json')
        self.exist_container = load_container('exist.json')
        self.rabbit_container = load_container('rabbit.json')

    def tearDown(self):
        pass

    def test_neo_builder(self):
        self.fail()
        res = furl(neo_builder(self.neo_container))
        self.assertEqual(res.host, '0.0.0.0')
        self.assertEqual(res.port, 49154)
        self.assertEqual(res.scheme, 'http')

    def test_exist_builder(self):
        self.fail()
        res = furl(exist_builder(self.exist_container))
        self.assertEqual(res.host, '0.0.0.0')
        self.assertEqual(res.port, 49153)
        self.assertEqual(res.scheme, 'http')
        self.assertEqual(res.path, '/exist/')

    def test_url_builder_filter_neo(self):
        self.fail()
        self.assertFalse('url' in self.neo_container)
        res = url_builder_filter(self.neo_container, NEO_URL_FORMAT)
        self.assertTrue('url' in self.neo_container)
        url = furl(self.neo_container['url'])
        self.assertEqual(url.host, '0.0.0.0')
        self.assertEqual(url.port, 49154)
        self.assertEqual(url.scheme, 'http')
