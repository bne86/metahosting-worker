from docker.client import Client
from docker.tls import TLSConfig
import docker.errors
import logging
from workers.manager.persistence import INSTANCE_STATUS
from workers import Worker


class DockerWorker(Worker):
    def __init__(self, worker_conf, worker_env,
                 local_persistence, send_method):
        """
        Call super-class constructor for common configuration items and
        then do the docker-specific setup
        :param worker_conf: dict containing the configuration
        :param worker_env: dict containing the configurable environment
        :param local_persistence: local instance manger
        :param send_method: messaging communication method
        :return: -
        """
        super(DockerWorker, self).__init__(worker_conf,
                                           worker_env,
                                           local_persistence,
                                           send_method)
        logging.debug('DockerWorker initialization')
        self.docker = Client(base_url=self.worker_conf['base_url'],
                             version=self.worker_conf['client_version'],
                             tls=_get_tls(worker_conf))
        self._image_ports = self._initialize_image()
        self._get_all_allocated_ports()

    @Worker._callback('create_instance')
    def create_instance(self, message):
        instance = message.copy()
        logging.info('Creating instance id: %s', instance['id'])
        environment = self._create_instance_env()
        ports = self.port_manager.acquire_ports(len(self._image_ports))
        if ports:
            port_mapping = dict(zip(self._image_ports, ports))
            container = self.docker.create_container(self.worker['image'],
                                                     environment=environment,
                                                     ports=self._image_ports)
            self.docker.start(container, port_bindings=port_mapping)
            instance['container_id'] = container['Id']
            instance['environment'] = environment
            self._set_networking(instance=instance)
            self.local_persistence.update_instance_status(
                instance=instance,
                status=INSTANCE_STATUS.STARTING)
        else:
            self.local_persistence.update_instance_status(
                instance=instance,
                status=INSTANCE_STATUS.FAILED)

    @Worker._callback('delete_instance')
    def delete_instance(self, message):
        msg = message.copy()
        instance = self.local_persistence.get_instance(msg['id'])
        if instance['status'] == INSTANCE_STATUS.RUNNING:
            logging.info('Deleting instance id: %s', msg['id'])
            container = self._get_container(
                container_id=instance['container_id'])
            if not container:
                logging.debug('Container does not exist, not stopping it')
                return
            free_ports = self._get_container_ports(instance['container_id'])
            self.docker.stop(container)
            self.port_manager.release_ports(free_ports)
            self.docker.remove_container(container)
            self.local_persistence.update_instance_status(
                instance=instance,
                status=INSTANCE_STATUS.DELETED)
        else:
            self.local_persistence.update_instance_status(
                instance=instance,
                status=INSTANCE_STATUS.DELETED)

    def _initialize_image(self):
        """
        download a docker image and get the ports that we have to link
        :return: list of ports(str)
        """
        logging.info('Initializing image %s', self.worker_conf['image'])
        self.worker['image'] = self.worker_conf['image']
        tmp = self.worker['image'].split(':')
        if len(tmp) == 2:
            self.docker.import_image(image=tmp[0], tag=tmp[1])
        else:
            self.docker.import_image(image=tmp)
        logging.debug('Extracting ports from image')
        ports = []
        docker_image = self.docker.inspect_image(self.worker['image'])
        for port in docker_image[u'ContainerConfig'][u'ExposedPorts'].keys():
            ports.append(port.split('/')[0])
        return ports

    def _get_all_allocated_ports(self):
        """
        get all containers, that have not been stopped, they may have been
        started from outside of the workers scope.
        :return: array with ports to use, None if not enough ports available
        """
        used_ports = set()
        containers = self.docker.containers()
        for container in containers:
            for port in self._get_container_ports(container['Id']):
                used_ports.add(port)
        self.port_manager.update_used_ports(used_ports)

    def _get_container(self, container_id):
        """
        get docker-py s container description
        :param container_id: string, id for the container
        :return: dict, containing the container
        """
        try:
            return self.docker.inspect_container({'Id': container_id})
        except docker.errors.APIError:
            logging.debug('Not able to get container %s', container_id)
            return None

    def _get_container_networking(self, container_id):
        """
        return a dict with the container networking, using the appropriate
        worker ip
        :param container_id: id of the container
        :return: dict with the Ports section of the container representation
        """
        try:
            networking = self._get_container(
                container_id)['NetworkSettings']['Ports']
            if 'ip' in self.worker_conf.keys():
                for port in networking:
                    for index, unused in enumerate(networking[port]):
                        networking[port][index][u'HostIp'] = \
                            unicode(self.worker_conf['ip'])
            return networking
        except TypeError:
            logging.error('Cannot get ports for container_id %s', container_id)
            return None

    def _get_container_ports(self, container_id):
        """
        return a list of the concrete container ports that are used
        :param container_id: id of the container
        :return: list of integers
        """
        networking = self._get_container_networking(container_id)
        ports = list()
        if networking:
            for port in networking.keys():
                for index, unused in enumerate(networking[port]):
                    ports.append(int(networking[port][index][u'HostPort']))
        return ports

    def _publish_updates(self):
        instances = self.local_persistence.get_instances()
        for instance_id in instances.keys():
            if instances[instance_id]['status'] is INSTANCE_STATUS.DELETED:
                continue
            elif instances[instance_id]['status'] is INSTANCE_STATUS.FAILED:
                self.local_persistence.publish_instance(instance_id)
                continue

            container_id = instances[instance_id]['container_id']
            container = self._get_container(container_id)
            if not container_id or not container or not _is_running(container):
                instances[instance_id].pop('connection', None)
                instances[instance_id].pop('urls', None)
                self.local_persistence.update_instance_status(
                    instances[instance_id],
                    INSTANCE_STATUS.STOPPED)
                continue
            elif _is_running(container):
                self._set_networking(instances[instance_id])
                self.local_persistence.update_instance_status(
                    instances[instance_id],
                    INSTANCE_STATUS.RUNNING)
            else:
                logging.error("error while publishing updates")
        self._get_all_allocated_ports()

    def _set_networking(self, instance):
        instance['connection'] = \
            self._get_container_networking(instance['container_id'])
        instance['urls'] = self.url_builder.build(instance['connection'])


def _is_running(container):
    if 'State' not in container or 'Running' not in container['State']:
        return False
    return container['State']['Running']


def _get_tls(config):
    keys = config.keys()
    if 'client_cert' in keys and 'client_key' in keys \
            and 'tls_verify' in keys:
        if config['tls_verify'] == 'True':
            verify = True
        else:
            verify = False
        return TLSConfig(client_cert=(
            config['client_cert'], config['client_key'],), verify=verify)
