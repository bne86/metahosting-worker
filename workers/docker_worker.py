from docker.client import Client
from docker.tls import TLSConfig
import docker.errors
import logging
from workers.instance_management import InstanceStatus
from workers.worker import Worker


class DockerWorker(Worker):
    def __init__(self, config, instance_manager, send_method):
        """
        Call super-class constructor for common configuration items and
        then do the docker-specific setup
        :param config: dict containing the configuration
        :param instance_manager: local instance manger
        :param send_method: messaging communication method
        :return: -
        """
        super(DockerWorker, self).__init__(config,
                                           instance_manager,
                                           send_method)
        logging.debug('DockerWorker initialization')
        self.docker = Client(base_url=self.config['worker']['base_url'],
                             version=self.config['worker']['client_version'],
                             tls=DockerWorker._get_tls(config))
        self._initialize_image()


    @Worker.callback('create_instance')
    def create_instance(self, message):
        instance = message.copy()
        logging.info('Creating instance id: %s', instance['id'])
        environment = self._create_container_environment(instance)
        container = self.docker.create_container(self.worker_info['image'],
                                                 environment=environment)
        self.docker.start(container, publish_all_ports=True)
        instance['local'] = container
        instance['environment'] = environment
        self.instances.update_instance_status(instance=instance,
                                              status=InstanceStatus.STARTING)

    @Worker.callback('delete_instance')
    def delete_instance(self, message):
        instance = message.copy()
        logging.info('Deleting instance (id: %s)', instance['id'])
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
        self.docker.stop(container)
        self.instances.update_instance_status(instance=instance_local,
                                              status=InstanceStatus.DELETED,
                                              publish=True)


    @staticmethod
    def _get_tls(config):
        if config['worker']['tls_verify'] == 'True':
            verify = True
        else:
            verify = False

        keys = config['worker'].keys()
        if 'client_cert' in keys and 'client_key' in keys \
                and 'tls_verify' in keys:
            return TLSConfig(client_cert=
                             (config['worker']['client_cert'],
                              config['worker']['client_key'],),
                             verify=verify)
        return False

    def _initialize_image(self):
        self.worker_info['image'] = self.config['worker']['image']
        logging.debug('Importing image %s', self.worker_info['image'])
        self.docker.import_image(image=self.worker_info['image'])

    def _get_container(self, container_id):
        try:
            return self.docker.inspect_container({'Id': container_id})
        except docker.errors.APIError as error:
            logging.error('Unable to retrieve container %s (%s)', container_id,
                          error)
            return False
