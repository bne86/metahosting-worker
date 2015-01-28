import uuid
from time import time
from queue_managers import send_message
import logging


class Facade(object):
    def __init__(self, authorization, type_store, instance_store):
        self.authorization = authorization
        self._types = type_store
        self._instances = instance_store

    def get_types(self):
        return self._types.get_all()

    def add_type(self, name, description):
        self._types.update(name, description)

    def create_instance(self, instance_type, uid, environment=None):
        logging.debug('Creating instance of %s', instance_type)
        if instance_type not in self.get_types():
            return None

        instance = self._prepare_instance(status='starting',
                                          instance_type=instance_type,
                                          environment=environment)
        # return value ignored?
        self.authorization.make_owner(uid, instance['id'])
        # self._instances.update(instance['id'], instance.copy())run
        send_message(instance_type, 'create_instance', instance)
        send_message('info', 'instance_info', {'instance': instance})
        return instance

    def delete_instance(self, instance_id, uid):
        logging.debug('Delete instance is not yet implemented %s', instance_id)
        if not self._instances.get(instance_id) or not \
                self.authorization.is_user_instance(instance_id=instance_id,
                                                    user_id=uid):
            return False
        instance = self._instances.get(instance_id)
        # this will not work properly as we don't use broadcast
        send_message(instance['type'], 'delete_instance', instance)
        instance['status'] = 'deleted'
        send_message('info', 'instance_info', {'instance': instance})
        # self._instances.remove(instance_id)
        return self.authorization.revoke_ownership(user_id=uid,
                                                   instance_id=instance_id)

    def get_instances_of_type(self, instance_type_name, uid):
        if instance_type_name not in self.get_types():
            return {}
        return {iid: desc
                for iid, desc in self.get_all_instances(uid).iteritems()
                if desc['type'] == instance_type_name}

    def get_instance(self, instance_id, uid):
        if not self.authorization.is_user_instance(instance_id, uid):
            return None

        return self._instances.get(instance_id)

    def get_all_instances(self, uid):
        user_instances = self.authorization.get_user_instances(uid)
        return {instanceId: self._instances.get(instanceId) for instanceId in
                user_instances if self._instances.get(instanceId)}

    @staticmethod
    def _generate_id():
        return uuid.uuid1().hex

    @staticmethod
    def _prepare_instance(status, instance_type, environment):
        instance = dict()
        instance['id'] = Facade._generate_id()
        instance['status'] = status
        instance['type'] = instance_type
        instance['ts'] = time()
        if environment:
            instance['environment'] = environment

        return instance
