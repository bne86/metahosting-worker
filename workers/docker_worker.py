import ConfigParser
import logging

from docker import Client
from queue_managers import send_message, subscribe
from workers.common.dispatcher import Dispatcher
from workers.common.instance_management import add_local_instance, get_local_instance, update_instance_status
from workers.common.types_management import start_publishing_type, stop_publishing_type


settings = ConfigParser.ConfigParser()
settings.readfp(open('config.ini'))
instance_class = dict()
instance_class['name'] = settings.get('docker_worker', 'name')
instance_class['description'] = settings.get('docker_worker', 'description')
instance_class['image'] = settings.get('docker_worker', 'image')

instance_environment = []
for item in settings.items('docker_worker_env'):
    instance_environment.append(item[0].upper()+'='+item[1])


my_dispatcher = Dispatcher()

docker_version = settings.get('docker_worker', 'client_version')
docker = Client(version=docker_version)


def init():
    logging.debug('Initialize docker worker')
    subscribe(instance_class['name'], my_dispatcher.dispatch)
    # FIXME: this should be repeated periodically
    start_publishing_type(instance_class, send_message)


@my_dispatcher.callback('create_instance')
def create_instance(message):
    instance = message.copy()
    logging.debug('Creating instance (id=%s, environment=%s)' % (instance['id'], instance_environment))
    container = docker.create_container(instance_class['image'], environment=instance_environment)
    instance['status'] = 'creating'
    docker.start(container, publish_all_ports=True)
    add_local_instance(instance['id'], {'container-id': container['Id'], 'status': 'creating'})
    update_instance_status(instance['id'], instance)


@my_dispatcher.callback('delete_instance')
def delete_instance(message):
    instance = message.copy()
    logging.debug('Deleting instance (id: %s)' % instance['id'])
    try:
        instance_id, information = get_local_instance(instance['id'])
    except TypeError as err:
        logging.error('Instance not in local store, therefore not deleting it'+err.message)
        return
    container_id = information['container-id']
    container = docker.inspect_container({'Id': container_id})
    if not container:
        logging.debug('Container %s for instance %s not available, not stopping it'
                      % (container_id, instance['id']))
        return
    docker.stop(container)
    # update local store
    information['status'] = 'deleted'
    add_local_instance(instance_id, information)
    # update global store
    instance['status'] = 'deleting'
    update_instance_status(instance['id'], instance)


def stop():
    stop_publishing_type(instance_class)