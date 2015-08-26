from metahosting.common import config_manager
from pymongo import MongoClient
from stores.mongo_store import MongoStore

import unittest


class MongoStoreTest(unittest.TestCase):
    def setUp(self):
        self.config = config_manager.get_configuration(
            section_name='local_persistence')
        self.config['database'] = 'metahosting_tests'
        self.store = MongoStore(config=self.config)

    def tearDown(self):
        MongoClient(host=self.config['host'],
                    port=int(self.config['port']))\
            .drop_database('metahosting_tests')

    def test_update(self):
        self.assertIsNone(self.store.get('name'))
        self.store.update('name', 'value')
        self.assertIsNotNone(self.store.get('name'))
        self.store.update('name', 'new_value')
        self.assertEqual(self.store.get('name'), 'new_value')

    def test_get(self):
        self.assertIsNone(self.store.get('foo'))
        self.store.update('foo', 'bar')
        self.assertIsNotNone(self.store.get('foo'))
        self.assertEqual('bar', self.store.get('foo'))

    def test_get_all(self):
        ret = self.store.get_all()
        self.assertDictEqual({}, ret)
        a = dict()
        a['foo'] = 'bar'
        a['foo2'] = 'bar2'
        a[1] = 'some'
        a['foo3'] = 21211
        for key, value in a.iteritems():
            self.store.update(key, value)

        self.assertDictEqual(a, self.store.get_all())

    def test_update_with_dict(self):
        simple_dict = dict()
        simple_dict['a'] = {'foo': 'bar'}
        self.store.update('foo', simple_dict)
        simple_dict['a'] = {'ooo': 'barr'}
        ret = self.store.get('foo')
        self.assertTrue('a' in ret)
        self.assertFalse('b' in ret)
        ret['c'] = {'foo': 'ba'}
        ret2 = self.store.get('foo')
        self.assertFalse('c' in ret2)
