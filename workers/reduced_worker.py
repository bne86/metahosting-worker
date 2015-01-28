import logging
import time

from workers.worker import Worker


class ReducedWorker(Worker):
    def __init__(self, config, local_instances):
        """
        Call super-class constructor for common configuration items and
        then do the docker-specific setup
        :param config: dict containing the configuration
        :param local_instances: storage backend for worker-local instances
        :return: -
        """
        logging.debug('Initialize reduced worker')
        super(ReducedWorker, self).__init__(config, local_instances)

    @Worker.callback('create_instance')
    def create_instance(self, message):
        instance = message.copy()
        logging.debug('Creating instance (id=%s)', instance['id'])
        time.sleep(5)
        instance['status'] = 'running'
        self.instances.set_instance(instance['id'], instance)
        self.instances.publish_instance(instance['id'], instance)

    @Worker.callback('delete_instance')
    def delete_instance(self, message):
        instance_id = message['id']
        logging.debug('Deleting instance id: %s', instance_id)
        instance = self.instances.get_instance(instance_id)
        if instance is None:
            return
        instance['status'] = 'deleted'
        self.instances.publish_instance(instance_id, instance)
