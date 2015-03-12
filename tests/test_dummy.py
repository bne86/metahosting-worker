from mock import Mock
from workers.dummy_worker import DummyWorker
import unittest
from workers.instance_management import INSTANCE_STATUS


class DummyWorkerTest(unittest.TestCase):
    def setUp(self):
        self.instance_manager = Mock()
        self.send_method = Mock()
        config = {'worker': {'name': 'dummyTest',
                             'description': 'foo bar bar'}}
        self.worker = DummyWorker(
            worker_conf=config, worker_env=None,
            instance_manager=self.instance_manager,
            send_method=self.send_method)

    def tearDown(self):
        pass

    def test_create_instance(self):
        instance = {'id': '1121', 'foo': 'bar'}
        self.instance_manager.update_instance_status = Mock()
        self.worker.create_instance(instance)
        self.instance_manager.update_instance_status.assert_called_with(
            instance,
            INSTANCE_STATUS.STARTING)

    def test_delete_instance(self):
        message = {'id': '71'}
        self.instance_manager.get_instance = Mock(return_value=None)
        self.worker.delete_instance(message)
        self.instance_manager.get_instance.assert_called_with('71')

        instance = {'id': '71', 'foo': 'bar'}
        self.instance_manager.get_instance = Mock(return_value=instance)
        self.instance_manager.update_instance_status = Mock()
        self.worker.delete_instance(message)
        self.instance_manager.get_instance.assert_called_with('71')
        self.instance_manager.update_instance_status.assert_called_with(
            instance, INSTANCE_STATUS.DELETED)
