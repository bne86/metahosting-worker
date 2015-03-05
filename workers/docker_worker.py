from docker.client import Client
from docker.tls import TLSConfig
import docker.errors
import logging
from workers.instance_management import INSTANCE_STATUS
from workers.worker import Worker


class DockerWorker(Worker):
    def __init__(self, worker_conf, worker_env, instance_manager, send_method):
        """
        Call super-class constructor for common configuration items and
        then do the docker-specific setup
        :param worker_conf: dict containing the configuration
        :param worker_env: dict containing the configurable environment
        :param instance_manager: local instance manger
        :param send_method: messaging communication method
        :return: -
        """
        super(DockerWorker, self).__init__(worker_conf,
                                           worker_env,
                                           instance_manager,
                                           send_method)
        logging.debug('DockerWorker initialization')
        self.docker = Client(base_url=self.worker_conf['base_url'],
                             version=self.worker_conf['client_version'],
                             tls=DockerWorker._get_tls(worker_conf))
        self._initialize_image()

        self.allowed_ports = []
        for item in range(int(self.worker_conf['portrange_count'])):
            self.allowed_ports.append(int(self.worker_conf['portrange_start'])
                                      + item)
        self.allowed_ports = frozenset(self.allowed_ports)

    @Worker.callback('create_instance')
    def create_instance(self, message):
        instance = message.copy()
        logging.info('Creating instance id: %s', instance['id'])
        environment = self._create_container_environment()
        ports_required = self._get_image_ports(self.worker_info['image'])
        ports = self._get_available_ports(ports_required)
        if ports:
            port_mapping = dict(zip(ports_required, ports))
            container = self.docker.create_container(self.worker_info['image'],
                                                     environment=environment,
                                                     ports=ports_required)

            self.docker.start(container, port_bindings=port_mapping)
            instance['local'] = container
            instance['environment'] = environment
            instance['connection'] = self._get_connection_details(
                container['Id'])
            self.instances.update_instance_status(instance=instance,
                                                  status=
                                                  INSTANCE_STATUS.STARTING)
        else:
            self.instances.update_instance_status(instance=instance,
                                                  status=
                                                  INSTANCE_STATUS.FAILED)

    @Worker.callback('delete_instance')
    def delete_instance(self, message):
        instance = message.copy()
        logging.info('Deleting instance id: %s', instance['id'])
        container_id = self._get_container_id(instance_id=instance['id'])
        container = self._get_container(container_id=container_id)
        if not container:
            logging.error('Container does not exist, not stopping it')
            return
        # we could view the container['State']['Running'] value here

        self.docker.stop(container)
        self.docker.remove_container(container)
        instance_local = self.instances.get_instance(instance['id'])
        self.instances.update_instance_status(instance=instance_local,
                                              status=INSTANCE_STATUS.DELETED)

    def _initialize_image(self):
        self.worker_info['image'] = self.worker_conf['image']
        logging.info('Importing image %s', self.worker_info['image'])
        self.docker.import_image(image=self.worker_info['image'])

    def _get_container(self, container_id):
        try:
            container = self.docker.inspect_container({'Id': container_id})
        except docker.errors.APIError as error:
            logging.error('Not able to get requested container %s, ettot %s',
                          container_id, error)
            return False
        return container

    def _get_container_id(self, instance_id):
        try:
            instance_local = self.instances.get_instance(instance_id)
            return instance_local['local']['Id']
        except KeyError or TypeError as err:
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
            container_id = self._get_container_id(instance_id)
            container = self._get_container(container_id)
            if not container_id or not container:
                logging.error('Container not available, set to stopped: %s',
                              container_id)
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

    def _get_image_ports(self, image):
        logging.debug('Extracting ports from image')
        ports = []
        docker_image = self.docker.inspect_image(image)
        for port in docker_image[u'ContainerConfig'][u'ExposedPorts'].keys():
            ports.append(port.split('/')[0])
        return ports

    def _get_available_ports(self, ports):
        """
        get all containers, that have not been stopped, they may have been
        started from outside of the workers scope.
        :param ports: ports for the new container
        :return: array with ports to use, None if not enough ports available
        """
        count = len(ports)
        used_ports = set()
        containers = self.docker.containers()
        for container in containers:
            for port in container['Ports']:
                used_ports.add(port['PublicPort'])
        available_ports = set(self.allowed_ports.difference(used_ports))
        if count <= len(available_ports):
            ports = []
            for item in range(0, count):
                ports.append(available_ports.pop())
            return ports
        else:
            return False

    # do static method make any sense at all in python?
    @staticmethod
    def _is_running(container):
        if 'State' not in container or 'Running' not in container['State']:
            return False
        return container['State']['Running']

    @staticmethod
    def _get_tls(config):
        keys = config.keys()
        if 'client_cert' in keys and 'client_key' in keys \
                and 'tls_verify' in keys:
            if config['tls_verify'] == 'True':
                verify = True
            else:
                verify = False
            return TLSConfig(client_cert=
                             (config['client_cert'],
                              config['client_key'],),
                             verify=verify)
        return False

    @staticmethod
    def _extract_connection(container):
        return container['NetworkSettings']['Ports']


