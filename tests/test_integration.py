from facade import get_facade

__author__ = 'jj'

import unittest


class IntegrationTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_nothing(self):
        # this is just a stupid test if it is possible to get the
        # whole glued version of the facade
        facade = get_facade()
        self.assertIsNotNone(facade)
