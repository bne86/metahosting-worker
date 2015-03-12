import logging
import time
from workers.manager.persistence import INSTANCE_STATUS
from workers import Worker


class DummyWorker(Worker):
    def __init__(self, worker_conf, worker_env,
                 local_persistence, send_method):
        """
        Call super-class constructor for common configuration items and
        then do the docker-specific setup
        :param worker_conf: dict containing the configuration
        :param worker_env: dict containing the configurable environment
        :param local_persistence: storage backend for worker-local instances
        :return: -
        """
        logging.debug('DummyWorker initialization')
        super(DummyWorker, self).__init__(worker_conf,
                                          worker_env,
                                          local_persistence,
                                          send_method)

    @Worker._callback('create_instance')
    def create_instance(self, message):
        instance = message.copy()
        logging.info('Creating instance id: %s', instance['id'])
        time.sleep(5)
        self.local_persistence.update_instance_status(
            instance, INSTANCE_STATUS.STARTING)

    @Worker._callback('delete_instance')
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
