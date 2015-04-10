import json
import unittest
import os
from urlbuilders import GenericUrlBuilder

NEO_URL_FORMAT = 'http://localhost:7474;https://localhost:7473'
EXIST_URL_FORMAT = 'http://localhost:8080/exist'


def load_container(name):
    with open(os.path.join('containers', name)) as ff:
        container = json.load(ff)
    return container


class TestGenericUrlBuilder(unittest.TestCase):
    def setUp(self):
        self.neo_connection = \
            load_container('neo4j.json')['HostConfig']['PortBindings']
        self.exist_connection = \
            load_container('exist.json')['HostConfig']['PortBindings']

    def tearDown(self):
        pass

    def test_neo_url_builder(self):
        builder = GenericUrlBuilder(
            worker_conf={'formatting_string': NEO_URL_FORMAT})
        urls = builder.build(self.neo_connection)
        self.assertTrue(len(urls) == 2)

    def test_exist_url_builder(self):
        builder = GenericUrlBuilder(
            worker_conf={'formatting_string': EXIST_URL_FORMAT})
        urls = builder.build(self.exist_connection)
        self.assertTrue(len(urls) == 1)
        self.assertTrue('exist' in urls[0])
