from workers.manager.persistence import PersistenceManager
from unittest import TestCase


class TestLocalInstanceManager(TestCase):
    def setUp(self):
        self.persistence = PersistenceManager(
            config={'backend': 'stores.dict_store.Store'},
            send_method=self.foo())

    def tearDown(self):
        pass

    def foo(self):
        pass
    #
    # def test_get_instance(self):
    #     self.fail()
    #
    # def test_get_instances(self):
    #     self.fail()
    #
    # def test_set_instance(self):
    #     self.fail()
    #
    # def test_update_instance_status(self):
    #     self.fail()
    #
    # def test_publish_instance(self):
    #     self.fail()
