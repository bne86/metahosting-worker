import logging
import time

from collections import namedtuple

States = namedtuple('States', ['STARTING', 'DELETED', 'RUNNING', 'STOPPED',
                               'FAILED'])
INSTANCE_STATUS = States('starting', 'deleted', 'running', 'stopped', 'failed')


class PersistenceManager(object):
    """
    wrapper around a store (metahosting.stores) to store instance information
    for local management.
    """

    def __init__(self, config, backend, publish):
        """
        :param config: local_persistence part of the config
        :param send_method: method to access messaging for sending info
        :return: -
        """
        logging.info('Initializing instance manager')
        backend_store_class = backend
        self.instances = backend_store_class(config=config)
        self.publish = publish
        logging.info('Instances stored: %r', self.get_instances().keys())

    def get_instance(self, instance_id):
        return self.instances.get(instance_id)

    def get_instances(self):
        return self.instances.get_all()

    def set_instance(self, instance_id, instance):
        instance['ts'] = time.time()
        self.instances.update(instance_id, instance)

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
