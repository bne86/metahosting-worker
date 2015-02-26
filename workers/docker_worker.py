from docker.client import Client
from docker.tls import TLSConfig
import docker.errors
import logging
from workers.instance_management import INSTANCE_STATUS
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
        environment = self._create_container_environment()
        container = self.docker.create_container(self.worker_info['image'],
                                                 environment=environment)
        self.docker.start(container, publish_all_ports=True)
        instance['local'] = container
        instance['environment'] = environment
        instance['connection'] = self._get_connection_details(container['Id'])
        self.instances.update_instance_status(instance=instance,
                                              status=INSTANCE_STATUS.STARTING)

    @Worker.callback('delete_instance')
    def delete_instance(self, message):
        instance = message.copy()
        logging.info('Deleting instance id: %s', instance['id'])
        container_id = self._get_container_id(instance_id=instance['id'])
        container = self._get_container(container_id=container_id)
        if not container:
            logging.error('Container does not exist, not stopping it')
        # we could view the container['State']['Running'] value here

        self.docker.stop(container)
        instance_local = self.instances.get_instance(instance['id'])
        self.instances.update_instance_status(instance=instance_local,
                                              status=INSTANCE_STATUS.DELETED)

    def _initialize_image(self):
        self.worker_info['image'] = self.config['worker']['image']
        logging.info('Importing image %s', self.worker_info['image'])
        # status update
        self.docker.import_image(image=self.worker_info['image'])

    def _get_container(self, container_id):
        return self.docker.inspect_container({'Id': container_id})

    def _get_container_id(self, instance_id):
        try:
            instance_local = self.instances.get_instance(instance_id)
            return instance_local['local']['Id']
        except TypeError as err:
            logging.error('Instance %s not found %s', instance_id, err.message)
            return False

    def _get_connection_details(self, container_id):
        container = self._get_container(container_id=container_id)
        if not container:
            return False
        return self._extract_connection(container)

    def publish_updates(self):
        """
        updates instance status to docker status.
        :return:
        """
        instances = self.instances.get_instances()
        for instance_id in instances.keys():
            container_id = instances[instance_id]['local']['Id']

            try:
                container = self._get_container(container_id)
            except docker.errors.APIError as error:
                logging.error('Container not available, set to stopped  %s',
                              error)
                instances[instance_id].pop('connection', None)
                self.instances.update_instance_status(instances
                                                      [instance_id],
                                                      INSTANCE_STATUS.STOPPED)
                continue

            if DockerWorker._is_running(container):  # and status not running?
                connection_details = \
                    DockerWorker._extract_connection(container)
                instances[instance_id]['connection'] = connection_details
                self.instances.update_instance_status(instances
                                                      [instance_id],
                                                      INSTANCE_STATUS.RUNNING)
            else:
                instances[instance_id].pop('connection', None)
                self.instances.update_instance_status(instances
                                                      [instance_id],
                                                      INSTANCE_STATUS.STOPPED)
                return

    # do static method make any sense at all in python?
    @staticmethod
    def _is_running(container):
        if 'State' not in container or 'Running' not in container['State']:
            return False
        return container['State']['Running']

    @staticmethod
    def _get_tls(config):
        keys = config['worker'].keys()
        if 'client_cert' in keys and 'client_key' in keys \
                and 'tls_verify' in keys:
            if config['worker']['tls_verify'] == 'True':
                verify = True
            else:
                verify = False
            return TLSConfig(client_cert=
                             (config['worker']['client_cert'],
                              config['worker']['client_key'],),
                             verify=verify)
        return False

    @staticmethod
    def _extract_connection(container):
        return container['NetworkSettings']['Ports']
