import logging
import time

from collections import namedtuple
from metahosting.common.config_manager import get_backend_class

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
        backend_store_class = get_backend_class(config)
        self._instances = backend_store_class(config=config)
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
