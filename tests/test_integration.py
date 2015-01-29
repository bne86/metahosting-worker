from facade import get_facade

__author__ = 'jj'

import unittest


class IntegrationTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_noting(self):
        facade = get_facade()
        self.assertIsNotNone(facade)
