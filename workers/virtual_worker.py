import logging
import time

from workers.worker import Worker


class VirtualWorker(Worker):
    def __init__(self, config, instances):
        """
        Call super-class constructor for common configuration items and
        then do the docker-specific setup
        :param config: dict containing the configuration
        :param instances: storage backend for worker-local instances
        :return: -
        """
        logging.debug('Initialize reduced worker')
        super(VirtualWorker, self).__init__(config, instances)

    @Worker.callback('create_instance')
    def create_instance(self, message):
        instance = message.copy()
        logging.error('Creating instance (id=%s)', instance)
        time.sleep(5)
        instance['status'] = 'starting'
        self.instances.set_instance(instance['id'], instance)
        self.instances.publish_instance(instance['id'])

    @Worker.callback('delete_instance')
    def delete_instance(self, message):
        instance = message.copy()
        logging.error('Deleting instance id: %s', instance['id'])
        instance = self.instances.get_instance(instance['id'])
        if instance is None:
            return
        instance['status'] = 'deleted'
        instance = self.instances.set_instance(instance['id'], instance)
        self.instances.publish_instance(instance['id'])
