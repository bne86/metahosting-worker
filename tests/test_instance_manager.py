from mock import Mock
from workers.instance_management import LocalInstanceManager, InstanceStatus
from stores.dict_store import Store
import unittest


class LocalStoreTest(unittest.TestCase):
    def setUp(self):
        self.store = Store()
        self.send_method = Mock()
        self.manager = LocalInstanceManager(instance_store=self.store,
                                            send_method=self.send_method)

    def tearDown(self):
        pass

    def test_get_instance(self):
        self.store.get = Mock(return_value=None)
        ret = self.manager.get_instance(instance_id=1)
        self.assertIsNone(ret)
        self.store.get.assert_called_with(1)

    def test_get_instances(self):
        self.store.get_all = Mock(return_value=None)
        ret = self.manager.get_instances()
        self.assertIsNone(ret)
        self.store.get_all.assert_called_with()

    def test_set_instance(self):
        self.store.update = Mock(return_value=None)
        instance = dict()
        instance['id'] = 12
        instance['name'] = 'not important'
        self.manager.set_instance(12, instance)
        self.assertTrue('ts' in instance)
        self.store.update.assert_called_with(12, instance)

    def test_publish_instance(self):
        instance = {'name': 'foo', 'id': 'bar', 'local': 'foobar'}
        self.store.get = Mock(return_value=instance)
        self.manager.publish_instance(instance_id=6)
        self.store.get.assert_called_with(6)
        self.send_method.assert_called_with(
            'info',
            'instance_info',
            {'instance': {'name': 'foo', 'id': 'bar'}})

    def test_update_instance_status(self):
        self.store.update = Mock()
        instance = {'id': '123', 'some info': 'additional'}
        self.assertFalse('status' in instance)
        self.manager.update_instance_status(instance=instance,
                                            status=InstanceStatus.STARTING,
                                            publish=False)
        self.assertTrue('status' in instance)
        self.assertEqual(instance['status'], InstanceStatus.STARTING)
        self.store.update.assert_called_with('123', instance)

        self.manager.update_instance_status(instance=instance,
                                            status=InstanceStatus.DELETED,
                                            publish=False)
        self.assertTrue('status' in instance)
        self.assertEqual(instance['status'], InstanceStatus.DELETED)
        self.store.update.assert_called_with('123', instance)

        self.store.get = Mock(return_value=instance)
        self.manager.update_instance_status(instance=instance,
                                            status=InstanceStatus.STARTING,
                                            publish=True)
        self.assertTrue('status' in instance)
        self.assertEqual(instance['status'], InstanceStatus.STARTING)
        self.store.update.assert_called_with('123', instance)
        self.store.get.assert_called_with('123')
        self.send_method.assert_called_with('info', 'instance_info',
                                            {'instance': instance})

    def test_remove_fields(self):
        # remove_fields(instance, filter_fields)
        instance = {'name': 'foo', 'id': 'bar'}
        fields = {'name'}
        self.assertTrue('name' in instance)
        LocalInstanceManager.remove_fields(instance=instance,
                                           filter_fields=fields)
        self.assertFalse('name' in instance)
        self.assertTrue('id' in instance)

        instance = {'name': 'foo', 'id': 'bar'}
        fields = {'bar'}
        LocalInstanceManager.remove_fields(instance=instance,
                                           filter_fields=fields)
        self.assertTrue('name' in instance)
        self.assertTrue('id' in instance)

        instance = {'name': 'foo', 'id': 'bar'}
        fields = {'name', 'id'}
        LocalInstanceManager.remove_fields(instance=instance,
                                           filter_fields=fields)
        self.assertFalse('name' in instance)
        self.assertFalse('id' in instance)
        self.assertDictEqual(instance, {})
