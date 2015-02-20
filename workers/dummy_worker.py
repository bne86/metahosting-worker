import logging
import time
from workers.instance_management import InstanceStatus

from workers.worker import Worker


class DummyWorker(Worker):
    def __init__(self, config, instance_manager, send_method):
        """
        Call super-class constructor for common configuration items and
        then do the docker-specific setup
        :param config: dict containing the configuration
        :param instance_manager: storage backend for worker-local instances
        :return: -
        """
        logging.debug('DummyWorker initialization')
        super(DummyWorker, self).__init__(config,
                                          instance_manager,
                                          send_method)

    @Worker.callback('create_instance')
    def create_instance(self, message):
        instance = message.copy()
        logging.info('Creating instance id: %s', instance['id'])
        time.sleep(5)
        self.instances.update_instance_status(instance,
                                              InstanceStatus.STARTING)

    @Worker.callback('delete_instance')
    def delete_instance(self, message):
        instance_id = message['id']
        logging.info('Deleting instance id: %s', instance_id)
        instance = self.instances.get_instance(instance_id)
        if instance is None:
            return
        self.instances.update_instance_status(instance,
                                              InstanceStatus.DELETED)

    def publish_updates(self):
        """
        dummy instances always change state from STARTING to ACTIVE
        :return:
        """
        instances = self.instances.get_instances()
        for instance_name in instances.keys():
            if instances[instance_name]['status'] == InstanceStatus.STARTING:
                self.instances.update_instance_status(instances[instance_name],
                                                      InstanceStatus.ACTIVE)
