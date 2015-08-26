import unittest

from mock import Mock

from metahosting.common import config_manager
from workers.dummy_worker import DummyWorker
from workers.manager.persistence import INSTANCE_STATUS
from workers.manager.persistence import PersistenceManager


class DummyWorkerTest(unittest.TestCase):
    def setUp(self):
        self.instance_manager = Mock()
        self.messaging = Mock()
        config = dict()
        config['persistence'] = config_manager.get_configuration('persistence')
        config['messaging'] = config_manager.get_configuration('messaging')
        config['worker'] = config_manager.get_configuration('worker')
        config['instance'] = \
            config_manager.get_instance_configuration('instance_environment')
        self.worker = DummyWorker(config=config,
                                  persistence=self.instance_manager,
                                  messaging=self.messaging)

    def tearDown(self):
        pass

    def test_create_instance(self):
        instance = {'id': '1121', 'foo': 'bar'}
        PersistenceManager.update_instance_status = Mock()
        self.worker.create_instance(instance)
        PersistenceManager.update_instance_status.assert_called_with(
            instance,
            INSTANCE_STATUS.STARTING)

    def test_delete_instance(self):
        message = {'id': '71'}
        PersistenceManager.get_instance = Mock(return_value=None)
        self.worker.delete_instance(message)
        PersistenceManager.get_instance.assert_called_with('71')

        instance = {'id': '71', 'foo': 'bar'}
        PersistenceManager.get_instance = Mock(return_value=instance)
        self.worker.delete_instance(message)
        PersistenceManager.get_instance.assert_called_with('71')
        PersistenceManager.update_instance_status.assert_called_with(
            instance, INSTANCE_STATUS.DELETED)
