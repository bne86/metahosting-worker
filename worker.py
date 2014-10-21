import time
import threading
import random
from queue_manager import qm, send_message, get_message_subject

instance_class = dict()
instance_class['name'] = 'service_a'
instance_class['description'] = 'service_a for doing lot of cool stuff'

my_instances = dict()

# how often instance type information should be published (will become global)
INTERVAL = 3600
publishing_thread = threading.Timer(0, lambda: None)


def run_in_background(func):
    def background_runner(*args, **kwargs):
        th = threading.Thread(target=func, args=args, kwargs=kwargs)
        th.start()
    return background_runner


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


def publish_class_type():
    # qm.publish('info', {'msg': 'instance_type', 'class': instance_class})
    send_message('info', 'instance_type', {'class': instance_class})
    global publishing_thread
    publishing_thread = threading.Timer(INTERVAL + jitter(INTERVAL),
                                        publish_class_type)
    publishing_thread.start()


def publish_instance_status(instance):
    send_message('info', 'instance_info', {'instance': instance})


def stop():
    global publishing_thread
    publishing_thread.cancel()


def init():
    # this should be repeated periodically as well, our msg "middleware"
    # can't cope with that at the moment
    qm.subscribe(instance_class['name'], listener)
    publish_class_type()


def jitter(interval):
    return random.random() * interval * 0.3


def log(entry):
    print('[%sWorker] %s\n' % (instance_class['name'], entry))
