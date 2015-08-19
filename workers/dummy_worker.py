import logging
import time

from workers.manager.persistence import INSTANCE_STATUS
from workers import Worker


class DummyWorker(Worker):
    def __init__(self, worker_conf, instance_env,
                 local_persistence, send_method):
        """
        Call super-class constructor for common configuration items
        :param worker_conf: dict containing the configuration
        :param worker_env: dict containing the configurable environment
        :param local_persistence: local instance manger
        :param send_method: messaging communication method
        :return: -
        """
        logging.debug('DummyWorker initialization')
        super(DummyWorker, self).__init__(worker_conf=worker_conf,
                                          instance_env=instance_env,
                                          local_persistence=local_persistence,
                                          send_method=send_method)

    def create_instance(self, message):
        instance = message.copy()
        logging.info('Creating instance id: %s', instance['id'])
        time.sleep(5)
        self.local_persistence.update_instance_status(
            instance, INSTANCE_STATUS.STARTING)

    def delete_instance(self, message):
        instance_id = message['id']
        logging.info('Deleting instance id: %s', instance_id)
        instance = self.local_persistence.get_instance(instance_id)
        if instance is None:
            return
        self.local_persistence.update_instance_status(
            instance, INSTANCE_STATUS.DELETED)

    def _publish_updates(self):
        """
        dummy instances always change state from STARTING to RUNNING
        :return:
        """
        instances = self.local_persistence.get_instances()
        for instance_name in instances.keys():
            if instances[instance_name]['status'] == INSTANCE_STATUS.STARTING:
                self.local_persistence.update_instance_status(
                    instances[instance_name], INSTANCE_STATUS.RUNNING)
