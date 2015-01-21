from stores.dict_store import Store

__author__ = 'jj'

import unittest


class LocalStoreTest(unittest.TestCase):
    def setUp(self):
        self.store = Store()

    def tearDown(self):
        pass

    def test_update(self):
        store = Store()
        self.assertIsNone(store.get('name'))
        store.update('name', 'value')
        self.assertIsNotNone(store.get('name'))
        store.update('name', 'new_value')
        self.assertEqual(store.get('name'), 'new_value')

    def test_get(self):
        store = Store()
        self.assertIsNone(store.get('foo'))
        store.update('foo', 'bar')
        self.assertIsNotNone(store.get('foo'))
        self.assertEqual('bar', store.get('foo'))

    def test_get_all(self):
        store = Store()
        ret = store.get_all()
        self.assertDictEqual({}, ret)
        a = dict()
        a['foo'] = 'bar'
        a['foo2'] = 'bar2'
        a[1] = 'some'
        a['foo3'] = 21211
        for key, value in a.iteritems():
            store.update(key, value)

        self.assertDictEqual(a, store.get_all())

    def test_update_with_dict(self):
        store = Store()
        simple_dict = dict()
        simple_dict['a'] = {'foo': 'bar'}
        store.update('foo', simple_dict)
        simple_dict['a'] = {'ooo': 'barr'}
        ret = store.get('foo')
        self.assertTrue('a' in ret)
        self.assertFalse('b' in ret)
        ret['c'] = {'foo': 'ba'}
        ret2 = store.get('foo')
        self.assertFalse('c' in ret2)

    def test_remove(self):
        store = Store()
        self.assertIsNone(store.get('foo'))
        store.remove('foo')
        self.assertIsNone(store.get('foo'))
        store.update('foo', 'bar')
        store.remove('foo')
        self.assertIsNone(store.get('foo'))
