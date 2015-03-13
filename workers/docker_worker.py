from docker.client import Client
from docker.tls import TLSConfig
import docker.errors
import logging
from urlbuilders import GenericUrlBuilder
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

        if 'disable_https_warnings' in worker_conf \
                and 'https' in worker_conf['base_url']:
            import requests.packages.urllib3

            requests.packages.urllib3.disable_warnings()

        self.docker = Client(base_url=self.worker_conf['base_url'],
                             version=self.worker_conf['client_version'],
                             tls=_get_tls(worker_conf))
        self._initialize_image()
        self._get_associated_ports()

        if 'formatting_string' in self.worker_conf:
            self.url_builder = GenericUrlBuilder(self.worker_conf[
                'formatting_string'])
        else:
            self.url_builder = None

    @Worker._callback('create_instance')
    def create_instance(self, message):
        instance = message.copy()
        logging.info('Creating instance id: %s', instance['id'])
        environment = self._create_instance_env()
        ports_required = self._get_image_ports(self.worker['image'])
        ports = self.port_manager.acquire_ports(len(ports_required))
        if ports:
            port_mapping = dict(zip(ports_required, ports))
            container = self.docker.create_container(self.worker['image'],
                                                     environment=environment,
                                                     ports=ports_required)

            self.docker.start(container, port_bindings=port_mapping)
            instance['local'] = container
            instance['environment'] = environment
            instance['connection'] = \
                self._get_container_connectivity(container)
            url = self._get_url(container)
            if url:
                instance['url'] = url

            self.local_persistence.update_instance_status(
                instance=instance,
                status=INSTANCE_STATUS.STARTING)
        else:
            self.local_persistence.update_instance_status(
                instance=instance,
                status=INSTANCE_STATUS.FAILED)

    @Worker._callback('delete_instance')
    def delete_instance(self, message):
        instance = message.copy()
        logging.info('Deleting instance id: %s', instance['id'])
        container_id = self._get_container_id(instance_id=instance['id'])
        container = self._get_container(container_id=container_id)
        if not container:
            logging.debug('Container does not exist, not stopping it')
            return
        self.docker.stop(container)
        freed_ports = _container_used_ports(container)
        self.port_manager.release_ports(freed_ports)
        self.docker.remove_container(container)
        instance_local = self.local_persistence.get_instance(instance['id'])
        self.local_persistence.update_instance_status(
            instance=instance_local,
            status=INSTANCE_STATUS.DELETED)

    def _initialize_image(self):
        logging.info('Initializing image %s', self.worker_conf['image'])
        self.worker['image'] = self.worker_conf['image']
        tmp = self.worker['image'].split(':')
        if len(tmp) == 2:
            self.docker.import_image(image=tmp[0], tag=tmp[1])
        else:
            self.docker.import_image(image=tmp)

    def _get_container_id(self, instance_id):
        try:
            return \
                self.local_persistence.get_instance(instance_id)['local']['Id']
        except (KeyError, TypeError):
            logging.debug('Container for instance %s not found', instance_id)
            return False

    def _get_container(self, container_id):
        try:
            return self.docker.inspect_container({'Id': container_id})
        except docker.errors.APIError:
            logging.debug('Not able to get container %s', container_id)
            return False

    def _get_container_connectivity(self, container):
        ports = container['NetworkSettings']['Ports']
        if ports:
            if 'ip' in self.worker_conf.keys():
                for port in ports:
                    ports[port][0][u'HostIp'] = unicode(self.worker_conf['ip'])
            return ports
        else:
            return False

    def _get_url(self, container):
        if self.url_builder is None:
            return None
        return self.url_builder.build(
            self._get_container_connectivity(container))

    def _publish_updates(self):
        instances = self.local_persistence.get_instances()
        for instance_id in instances.keys():
            if instances[instance_id]['status'] in [INSTANCE_STATUS.DELETED,
                                                    INSTANCE_STATUS.FAILED]:
                self.local_persistence.publish_instance(instance_id)
                continue

            container_id = self._get_container_id(instance_id)
            container = self._get_container(container_id)
            if not container_id or not container:
                instances[instance_id].pop('connection', None)
                self.local_persistence.update_instance_status(
                    instances[instance_id],
                    INSTANCE_STATUS.STOPPED)
                continue

            if _is_running(container):
                connection_details = \
                    self._get_container_connectivity(container)
                instances[instance_id]['connection'] = connection_details
                url = self._get_url(container)
                if url:
                    instances[instance_id]['url'] = url

                self.local_persistence.update_instance_status(
                    instances[instance_id],
                    INSTANCE_STATUS.RUNNING)
            else:
                instances[instance_id].pop('connection', None)
                self.local_persistence.update_instance_status(
                    instances[instance_id],
                    INSTANCE_STATUS.STOPPED)

    def _get_image_ports(self, image):
        logging.debug('Extracting ports from image')
        ports = []
        docker_image = self.docker.inspect_image(image)
        for port in docker_image[u'ContainerConfig'][u'ExposedPorts'].keys():
            ports.append(port.split('/')[0])
        return ports

    def _get_associated_ports(self):
        """
        get all containers, that have not been stopped, they may have been
        started from outside of the workers scope.
        :return: array with ports to use, None if not enough ports available
        """
        used_ports = set()
        containers = self.docker.containers()
        for container in containers:
            tmp = self._get_container(container['Id'])
            for port in _container_used_ports(tmp):
                used_ports.add(port)
        self.port_manager.update_used_ports(used_ports)


def _container_used_ports(container):
    container_ports = container[u'HostConfig'][u'PortBindings']
    ports = set()
    for container_port in container_ports.keys():
        for item in container_ports[container_port]:
            ports.add(int(item[u'HostPort']))
    return ports


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
