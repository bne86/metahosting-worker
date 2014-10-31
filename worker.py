import time
from queue_manager import get_message_subject
from worker_helpers import run_in_background, start_publishing_class_type, \
    stop_publishing_class_type

instance_class = dict()
instance_class['name'] = 'service_a'
instance_class['description'] = 'service_a for doing lot of cool stuff'

my_instances = dict()
send_message = lambda: None


def init(qm, send_message_method):
    # this should be repeated periodically as well, our msg "middleware"
    # can't cope with that at the moment, or we can use the publish method
    # for that.
    qm.subscribe(instance_class['name'], listener)
    global send_message
    send_message = send_message_method
    start_publishing_class_type(instance_class, send_message)


def listener(message):
    # queue(?)
    subject = get_message_subject(message)
    if subject == 'create_instance':
        create_instance(message)
    elif subject == 'delete_instance':
        delete_instance(message)
    else:
        log('Unknown message subject: %s' % subject)


@run_in_background
def create_instance(message):
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


def publish_instance_status(instance):
    send_message('info', 'instance_info', {'instance': instance})


def stop():
    stop_publishing_class_type(instance_class)


def log(entry):
    print('[%sWorker] %s\n' % (instance_class['name'], entry))
