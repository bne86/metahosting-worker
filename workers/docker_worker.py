from docker.client import Client
from docker.tls import TLSConfig
import logging
from workers.worker import Worker


class DockerWorker(Worker):
    def __init__(self, config, local_instances):
        """
        Call super-class constructor for common configuration items and
        then do the docker-specific setup
        :param config: dict containing the configuration
        :param local_instances: storage backend for worker-local instances
        :return: -
        """
        super(DockerWorker, self).__init__(config, local_instances)
        logging.debug('Initialize docker worker')

        self.worker_info['image'] = self.config['worker']['image']
        if self.config['worker']['tls_verify'] == 'True':
            verify = True
        else:
            verify = False
        keys = self.config['worker'].keys()
        # docker is remote or SSL used locally:
        if 'client_cert' in keys and 'client_key' in keys \
                and 'tls_verify' in keys:
            tls_config = TLSConfig(client_cert=
                                   (self.config['worker']['client_cert'],
                                    self.config['worker']['client_key'],),
                                   verify=verify)
            self.docker = Client(base_url=self.config['worker']['base_url'],
                                 version=self.config['worker'][
                                     'client_version'],
                                 tls=tls_config)
        else:
            self.docker = Client(base_url=self.config['worker']['base_url'],
                                 version=self.config['worker'][
                                     'client_version'])
        # load image if its not already available
        self.docker.import_image(image=self.worker_info['image'])

    @Worker.callback('create_instance')
    def create_instance(self, message):
        instance = message.copy()
        logging.debug('Creating instance (id=%s, environment=%s)',
                      instance['id'],
                      self.build_parameters)
        container = self.docker.create_container(
            self.worker_info['image'],
            environment=self.build_parameters)
        instance['status'] = 'creating'
        self.docker.start(container, publish_all_ports=True)
        self.instances.add_local_instance(instance['id'],
                                          {'container-id': container['Id'],
                                           'status': 'creating'})
        self.instances.update_instance_status(instance['id'], instance)

    @Worker.callback('delete_instance')
    def delete_instance(self, message):
        instance = message.copy()
        logging.debug('Deleting instance (id: %s)', instance['id'])
        try:
            instance_id, information = self.instances.get_local_instance(
                instance['id'])
        except TypeError as err:
            logging.error(
                'Instance not in local store, '
                'therefore not deleting it' + err.message)
            return
        container_id = information['container-id']
        container = self.docker.inspect_container({'Id': container_id})
        if not container:
            logging.debug(
                'Container %s for instance %s not available, not stopping it',
                container_id, instance['id'])
            return
        self.docker.stop(container)
        # update local store
        information['status'] = 'deleted'
        self.instances.add_local_instance(instance_id, information)
        # update global store
        instance['status'] = 'deleting'
        self.instances.update_instance_status(instance['id'], instance)
