import logging
import time

from common.instance_management import get_local_instance, update_instance_status
from queue_managers import send_message, subscribe
from workers.common.types_management import start_publishing_type
from workers.common.dispatcher import Dispatcher

# FIXME: template for service creation, common management
instance_type = dict()
instance_type['name'] = 'service_ooa'
instance_type['description'] = 'service_a for doing less cool stuff'

my_dispatcher = Dispatcher()


def init():
    logging.debug('Init')
    subscribe(instance_type['name'], my_dispatcher.dispatch)
    # FIXME: this should be repeated periodically
    start_publishing_type(instance_type, send_message)


@my_dispatcher.callback('create_instance')
def create_instance(message):
    instance = message.copy()
    logging.debug('Creating instance (id=%s)', instance['id'])
    time.sleep(5)
    instance['status'] = 'running'
    update_instance_status(instance['id'], instance)


@my_dispatcher.callback('delete_instance')
def delete_instance(message):
    instance_id = message['id']
    logging.debug('Deleting instance id: %s', instance_id)
    instance = get_instance(instance_id)
    if instance is None:
        return
    instance['status'] = 'deleted'
    update_instance_status(instance_id, instance)
