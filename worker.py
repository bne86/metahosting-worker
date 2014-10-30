import time
from queue_manager import send_message, get_message_subject
from worker_helpers import run_in_background, start_publishing_class_type, \
    stop_publishing_class_type

instance_class = dict()
instance_class['name'] = 'service_a'
instance_class['description'] = 'service_a for doing lot of cool stuff'

my_instances = dict()


@run_in_background
def create_instance(message):
    global my_instances
    instance = message.copy()
    log('Creating instance (id=%s)' % instance['id'])
    time.sleep(5)
    instance['status'] = 'running'
    my_instances[instance['id']] = instance
    publish_instance_status(instance)


@run_in_background
def delete_instance(message):
    log('Deleting instance (id=%s)' % message['id'])
    instance = my_instances.pop(message['id'])
    instance['status'] = 'deleted'
    publish_instance_status(instance)


def listener(message):
    # queue(?)
    subject = get_message_subject(message)
    if subject == 'create_instance':
        create_instance(message)
    elif subject == 'delete_instance':
        delete_instance(message)
    else:
        log('Unknown message subject: %s' % subject)


def publish_instance_status(instance):
    send_message('info', 'instance_info', {'instance': instance})


def init(qm):
    # this should be repeated periodically as well, our msg "middleware"
    # can't cope with that at the moment
    qm.subscribe(instance_class['name'], listener)
    start_publishing_class_type(instance_class, send_message)


def stop():
    stop_publishing_class_type(instance_class)


def log(entry):
    print('[%sWorker] %s\n' % (instance_class['name'], entry))
