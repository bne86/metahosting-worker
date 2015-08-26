import logging
import time

from workers import Worker
from workers.manager.persistence import INSTANCE_STATUS


class DummyWorker(Worker):
    def __init__(self, config, persistence, messaging):
        """
        Call super-class constructor for common configuration items
        :return: -
        """
        logging.debug('DummyWorker initialization')
        super(DummyWorker, self).__init__(config=config,
                                          persistence=persistence,
                                          messaging=messaging)

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
