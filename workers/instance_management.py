from collections import namedtuple
import importlib
import logging
import time

States = namedtuple('States', ['STARTING', 'DELETED', 'RUNNING', 'STOPPED'])
INSTANCE_STATUS = States('starting', 'deleted', 'running', 'stopped')


def get_instance_store(config):
    """
    :param config:dict containing at least backend to use and the required
         config parameters per backend, e.g. url, database and
         collection in case of Ming
    :return: backend for instance store
    """
    class_path = config['local_instance_info']['backend'].split(".")
    module_path = ".".join(class_path[:-1])
    module = importlib.import_module(module_path)
    backend_class = getattr(module, class_path[-1])
    return backend_class(config=config['local_instance_info'])


class LocalInstanceManager:
    """
    wrapper around a store (metahosting.stores) to store instance information
    for local management.
    """

    def __init__(self, instance_store, send_method):
        """
        :param instance_store: where to store instances
        :param send_method: method to access messaging for sending info
        :return: -
        """
        logging.info('Initializing instance manager')
        self._instances = instance_store
        self.send = send_method
        logging.info('Instances stored: %r', self.get_instances())

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
        Do not send 'local' tagged information from the local storage backend

        :param instance_id: id of the instance that we publish information for
        publish, default = local
        :return: -
        """
        instance = self.get_instance(instance_id)
        if instance is not None:
            # jj: was there a reason not to remove it? the functionality was
            # previously there
            instance.pop('local', None)
            self.send('info', 'instance_info', {'instance': instance})
