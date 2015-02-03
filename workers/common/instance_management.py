import importlib
import logging
import time

from queue_managers import send_message


class LocalInstanceManagement:
    """
    wrapper around a store (metahosting.stores) to store instance information
    for local management.
    """

    def __init__(self, config):
        """
        :param config: dict containing at least backend to use and the required
                       config parameters per backend, e.g. url, database and
                       collection in case of Ming
        :return: -
        """
        logging.debug('Initialize local instance store.')

        class_path = config['local_instance_info']['backend'].split(".")
        module_path = ".".join(class_path[:-1])
        module = importlib.import_module(module_path)
        backend_class = getattr(module, class_path[-1])
        self._instances = backend_class(config=config['local_instance_info'])

        logging.debug('We already have \n%s\nstored',
                      self.get_instances())

    def get_instance(self, instance_id):
        return self._instances.get(instance_id)

    def get_instances(self):
        return self._instances.get_all()

    def set_instance(self, instance_id, instance):
        instance['ts'] = time.time()
        self._instances.update(instance_id, instance)

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
            send_message('info', 'instance_info', {'instance': instance})
