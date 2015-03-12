import json
import unittest
from urlbuilders import neo_builder


class RabbitTest(unittest.TestCase):
    def setUp(self):
        with open('neo4j.json') as ff:
            self.neo_container = json.load(ff)[0]
        print 'Neo4j container loaded %s' % self.neo_container

    def tearDown(self):
        pass

    def test_neo_builder(self):
        res = neo_builder(self.neo_container)
        print res
        self.assertEqual(res.host, '0.0.0.0')
        self.assertEqual(res.port, 49154)
        self.assertEqual(res.scheme, 'http')