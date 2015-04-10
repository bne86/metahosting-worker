from collections import namedtuple
import importlib
import logging
import time

States = namedtuple('States', ['STARTING', 'DELETED', 'RUNNING', 'STOPPED',
                               'FAILED'])
INSTANCE_STATUS = States('starting', 'deleted', 'running', 'stopped', 'failed')


class PersistenceManager:
    """
    wrapper around a store (metahosting.stores) to store instance information
    for local management.
    """

    def __init__(self, config, send_method):
        """
        :param config: local_persistence part of the config
        :param send_method: method to access messaging for sending info
        :return: -
        """
        logging.info('Initializing instance manager')
        self._instances = get_instance_store(config)
        self.publish = send_method
        logging.info('Instances stored: %r', self.get_instances().keys())

    def get_instance(self, instance_id):
        return self._instances.get(instance_id)

    def get_instances(self):
        return self._instances.get_all()

    def set_instance(self, instance_id, instance):
        instance['ts'] = time.time()
        self._instances.update(instance_id, instance)

    def update_instance_status(self, instance, status, publish=True):
        instance['status'] = status
        self.set_instance(instance['id'], instance)
        if publish:
            self.publish_instance(instance['id'])

    def publish_instance(self, instance_id):
        """
        Send information of the corresponding instance to the messaging system
        :param instance_id: id of the instance that we publish information for
        :return: -
        """
        instance = self.get_instance(instance_id)
        if instance is not None:
            self.publish('info', 'instance_info', {'instance': instance})


def get_instance_store(config):
    """
    :param config:dict containing the storage backend configuration
    :return: backend for instance store
    """
    class_path = config['backend'].split(".")
    module = importlib.import_module(".".join(class_path[:-1]))
    backend_class = getattr(module, class_path[-1])
    return backend_class(config=config)
