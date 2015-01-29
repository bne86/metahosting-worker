from copy import copy
import unittest
from facade.facade import Facade
from autho import RemoteAuthorizer
from mock import Mock
from stores.dict_store import Store


class FacadeTest(unittest.TestCase):
    def setUp(self):
        self.author = RemoteAuthorizer('', '', '')
        self.instance_store = Store()
        self.type_store = Store()

        def send(routing_key, subject, message):
            pass

        self.facade = Facade(authorization=self.author,
                             instance_store=self.instance_store,
                             type_store=self.type_store,
                             send_method=send)

        self.service_name2 = 'service1'
        self.service_name1 = 'eXistNeo'
        self.non_existing_type = 'mAtriX'

        self.facade.add_type(self.service_name1, 'description')
        self.facade.add_type(self.service_name2, 'description')

        self.user_id = 'foo'
        self.unauthorized_user = 'bar'
        self.instances = list()
        self.author.make_owner = Mock(return_value=True)
        self.instances.append(self.facade.create_instance(
            uid=self.user_id,
            instance_type=self.service_name1))
        self.instances.append(self.facade.create_instance(
            uid=self.user_id,
            instance_type=self.service_name1))
        self.instances.append(self.facade.create_instance(
            uid=self.user_id,
            instance_type=self.service_name2))

    def tearDown(self):
        pass

    def test_get_types(self):
        types = self.facade.get_types()
        self.assertIsNotNone(types)
        self.assertTrue(self.service_name1 in types)
        self.assertTrue(self.service_name2 in types)
        self.assertEqual(len(types), 2)

    def test_create_instance(self):
        # not possible to start an instance of unknown type
        result = self.facade.create_instance(
            instance_type=self.non_existing_type,
            uid=self.user_id)
        self.assertIsNone(result)

        self.author.make_owner = Mock(return_value=True)
        result = self.facade.create_instance(instance_type=self.service_name1,
                                             uid=self.user_id)
        self.assertIsNotNone(result)
        self.author.make_owner.assert_called_with(self.user_id, result['id'])

        # expect following fields:
        self.assertEqual(result['type'], self.service_name1)
        self.assertTrue('ts' in result)
        self.assertTrue('id' in result)
        self.assertTrue('status' in result)

        ts1 = result['ts']
        result = self.facade.create_instance(instance_type=self.service_name1,
                                             uid=self.user_id)
        self.author.make_owner.assert_called_with(self.user_id, result['id'])
        self.assertIsNotNone(result)
        self.assertTrue('ts' in result)
        # time runs, timestamp increases
        self.assertGreater(result['ts'], ts1)

    def test_get_instance(self):
        # non-existing instances
        self.author.is_user_instance = Mock(return_value=True)
        self.assertIsNone(self.facade.get_instance(instance_id='33322211',
                                                   uid=self.user_id))
        self.assertIsNone(self.facade.get_instance(instance_id='333222111',
                                                   uid=self.user_id))

        # not authorized
        self.author.is_user_instance = Mock(return_value=False)
        self.assertIsNone(self.facade.get_instance(
            instance_id=1,
            uid=self.unauthorized_user))

        # authorized
        self.author.is_user_instance = Mock(return_value=True)
        for instance in self.instances:
            self.instance_store.get = Mock(return_value=instance)
            result = self.facade.get_instance(instance_id=instance['id'],
                                              uid=self.user_id)
            self.author.is_user_instance.assert_called_with(instance['id'],
                                                            self.user_id)
            self.instance_store.get.assert_called_with(instance['id'])
            self.assertIsNotNone(result)
            self.assertTrue('id' in result)
            self.assertEqual(result['id'], instance['id'])
            self.assertTrue('ts' in result)
            self.assertTrue('status' in result)

    def test_get_all_instances(self):
        self.author.get_user_instances = Mock(return_value=set())
        instances = self.facade.get_all_instances(uid=self.unauthorized_user)
        self.assertIsNotNone(instances)
        self.assertEquals(0, len(instances))

        id_list = list()
        for instance in self.instances:
            id_list.append(instance['id'])

        self.author.get_user_instances = Mock(return_value=copy(id_list))
        self.author.is_user_instance = Mock(return_value=True)
        self.instance_store.get = Mock(return_value={'id': '1121'})
        instances = self.facade.get_all_instances(uid=self.user_id)
        self.assertIsNotNone(instances)
        self.assertEqual(len(instances), len(id_list))
        for inst_id in id_list:
            self.assertTrue(inst_id in instances)

    def test_get_instances_of_type(self):
        # non-existing type
        result = self.facade.get_instances_of_type(self.non_existing_type,
                                                   self.user_id)
        self.assertIsNotNone(result)
        self.assertEquals(0, len(result))

        # not-authorized
        self.author.get_user_instances = Mock(return_value=set())
        instances = self.facade.get_instances_of_type(self.service_name1,
                                                      self.unauthorized_user)
        self.assertIsNotNone(result)
        self.assertEquals(0, len(result))

        # authorized:
        user_instances = set()
        for instance in self.instances:
            user_instances.add(instance['id'])

        self.instance_store.update(self.instances[0]['id'], self.instances[0])
        self.instance_store.update(self.instances[1]['id'], self.instances[1])

        self.author.get_user_instances = Mock(return_value=user_instances)
        instances = self.facade.get_instances_of_type(self.service_name1,
                                                      self.user_id)
        self.assertIsNotNone(instances)

        self.assertEquals(2, len(instances))
        self.assertTrue(self.instances[0]['id'] in instances)
        self.assertTrue(self.instances[1]['id'] in instances)

        self.instance_store.update(self.instances[2]['id'], self.instances[2])
        instances = self.facade.get_instances_of_type(self.service_name2,
                                                      self.user_id)
        self.assertIsNotNone(instances)
        self.assertEquals(1, len(instances))
        self.assertTrue(self.instances[2]['id'] in instances)

    def test_delete_instance(self):
        # delete non existing:
        r = self.facade.delete_instance(instance_id=71121, uid=self.user_id)
        self.assertFalse(r)

        # delete unauthorized
        self.author.is_user_instance = Mock(return_value=False)
        self.instance_store.get = Mock(return_value=self.instances[0])
        r = self.facade.delete_instance(instance_id=self.instances[0]['id'],
                                        uid=self.unauthorized_user)
        self.assertFalse(r)
        self.instance_store.get.assert_called_with(self.instances[0]['id'])
        self.author.is_user_instance.assert_called_with(
            instance_id=self.instances[0]['id'],
            user_id=self.unauthorized_user)

        # delete:
        self.author.is_user_instance = Mock(return_value=True)
        self.author.revoke_ownership = Mock(return_value=True)
        r = self.facade.delete_instance(instance_id=self.instances[0]['id'],
                                        uid=self.user_id)
        self.assertTrue(r)
        self.author.is_user_instance.assert_called_with(
            instance_id=self.instances[0]['id'],
            user_id=self.user_id)

        # delete:
        r = self.facade.delete_instance(instance_id=self.instances[0]['id'],
                                        uid=self.user_id)
        self.assertTrue(r)

    def test_outdated_autho(self):
        # authorization service returns some non-existing ids:
        self.author.get_user_instances = Mock(return_value={'1', '2'})
        v = self.facade.get_all_instances(self.user_id)
        self.assertIsNotNone(v)
        self.assertEqual(len(v), 0)
