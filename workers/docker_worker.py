import logging
import time

from queue_managers import get_message_subject, send_message, subscribe
from workers.common.types_management import start_publishing_type, \
    stop_publishing_type


# template for service creation
from workers.common.thread_management import run_in_background

instance_type = dict()
instance_type['name'] = 'service_a'
instance_type['description'] = 'service_a for doing lot of cool stuff'

my_instances = dict()


def init():
    # this should be repeated periodically as well, our msg "middleware"
    # can't cope with that at the moment, or we can use the publish method
    # for that.
    logging.debug('Init')
    subscribe(instance_type['name'], dispatcher)
    start_publishing_type(instance_type, send_message)


def dispatcher(message):
    # queue(?)
    subject = get_message_subject(message)
    if subject == 'create_instance':
        create_instance(message)
    elif subject == 'delete_instance':
        delete_instance(message)
    else:
        logging.error('Unknown message subject: %s', subject)


@run_in_background
def create_instance(message):
    instance = message.copy()
    logging.debug('Creating instance (id=%s)', instance['id'])
    time.sleep(5)
    instance['status'] = 'running'
    update_instance_status(instance['id'], instance)


@run_in_background
def delete_instance(message):
    instance_id = message['id']
    logging.debug('Deleting instance id: %s', instance_id)
    instance = get_instance(instance_id)
    if instance is None:
        return
    instance['status'] = 'deleted'
    update_instance_status(instance_id, instance)


# it smells
def stop():
    stop_publishing_type(instance_type)


def get_instance(instance_id):
    if instance_id not in my_instances:
        return None
    return my_instances[instance_id].copy()


def update_instance_status(instance_id, instance):
    global my_instances
    instance['id'] = instance_id
    instance['ts'] = time.time()
    my_instances[instance_id] = instance
    publish_instance_status(instance_id)


def publish_instance_status(instance_id):
    instance = get_instance(instance_id)
    if instance is not None:
        send_message('info', 'instance_info', {'instance': instance})
