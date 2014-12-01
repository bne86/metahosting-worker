import logging
import time

from common.instance_management import get_local_instance, update_instance_status
from queue_managers import get_message_subject, send_message, subscribe
from workers.common.types_management import start_publishing_type, \
    stop_publishing_type
from workers.common.thread_management import run_in_background


# template for service creation
instance_type = dict()
instance_type['name'] = 'service_a'
instance_type['description'] = 'service_a for doing lot of cool stuff'

my_instances = dict()


def init():
    # this should be repeated periodically as well, our msg "middleware"
    # can't cope with that at the moment, or we can use the publish method
    # for that.
    logging.debug('Worker init')
    subscribe(instance_type['name'], dispatcher)
    start_publishing_type(instance_type, send_message)


def dispatcher(message):
    subject = get_message_subject(message)
    logging.debug('Dispatching message: %s', subject)
    if subject == 'create_instance':
        create_instance(message)
    elif subject == 'delete_instance':
        delete_instance(message)
    else:
        logging.error('Unknown message subject: %s', subject)


@run_in_background
def create_instance(message):
    instance = message.copy()
    logging.debug('Creating instance id: %s', instance['id'])
    time.sleep(5)
    instance['status'] = 'running'
    update_instance_status(instance['id'], instance)


@run_in_background
def delete_instance(message):
    instance_id = message['id']
    logging.debug('Deleting instance (id=%s)', instance_id)
    instance = get_instance(instance_id)
    if instance is None:
        return
    instance['status'] = 'deleted'
    update_instance_status(instance_id, instance)


# it smells
def stop():
    stop_publishing_type(instance_type)
