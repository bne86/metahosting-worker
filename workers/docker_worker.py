from docker.client import Client
from docker.tls import TLSConfig
import docker.errors
import logging
import random
import string
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
        environment = self._create_container_environment(instance)
        logging.debug('Creating instance (id=%s)', instance['id'])
        container = self.docker.create_container(self.worker_info['image'],
                                                 environment=environment)
        self.docker.start(container, publish_all_ports=True)
        instance['status'] = 'starting'
        instance['local'] = container
        instance['environment'] = environment
        self.instances.set_instance(instance['id'], instance)
        self.instances.publish_instance(instance['id'])

    @Worker.callback('delete_instance')
    def delete_instance(self, message):
        instance = message.copy()
        logging.debug('Deleting instance (id: %s)', instance['id'])
        try:
            instance_local = self.instances.get_instance(instance['id'])
        except TypeError as err:
            logging.error('Instance not in local store, '
                          'therefore not deleting it' + err.message)
            return
        container_id = instance_local['local']['Id']
        try:
            container = self.docker.inspect_container({'Id': container_id})
        except docker.errors.APIError as error:
            logging.error('Container %s for instance %s not available, not '
                          'stopping it', container_id, instance['id'], error)
            return
        if not container:
            logging.debug(
                'Container %s for instance %s not available, not stopping it',
                container_id, instance['id'])
            return
        self.docker.stop(container)
        # update local store
        instance_local['status'] = 'deleted'
        self.instances.set_instance(instance['id'], instance_local)
        # update global store
        self.instances.publish_instance(instance['id'],
                                        ['local', 'environment'])

    def _create_container_environment(self, message):
        """
        Merge the build_parameters configured for the worker and gotten from
        the facade.
        :rtype : list
        Policy: Only override worker-local parameters. If a parameter is empty,
        generate a value using lowercase, uppercase and digits.
        :param message: dict containing the message gotten from the bus
        :return: list containing key=value pairs send to docker
        """
        if 'environment' in message.keys():
            injected_parameters = message['environment']
        else:
            injected_parameters = dict()
        if 'environment' in self.worker_info.keys():
            local_parameters = self.worker_info['environment']
        else:
            local_parameters = dict()
        environment = []
        for key in local_parameters.keys():
            if key in injected_parameters.keys():
                environment.append(key + '=' + injected_parameters[key])
            else:
                if local_parameters[key] == '':
                    environment.append(key + '=' + ''.join(
                        random.SystemRandom().choice(
                            string.ascii_lowercase +
                            string.ascii_uppercase +
                            string.digits)
                        for _ in range(16)))
                else:
                    environment.append(key + '=' + local_parameters[key])
        logging.debug('Current environment for VM: %s', environment)
        return environment

