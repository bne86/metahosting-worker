import time
from queue_manager import get_message_subject
from worker_helpers import run_in_background, start_publishing_class_type, \
    stop_publishing_class_type

instance_class = dict()
instance_class['name'] = 'service_a'
instance_class['description'] = 'service_a for doing lot of cool stuff'

my_instances = dict()
send_message = lambda x, y, z: None

def init(qm, send_message_method):
    # this should be repeated periodically as well, our msg "middleware"
    # can't cope with that at the moment, or we can use the publish method
    # for that.
    qm.subscribe(instance_class['name'], dispatcher)
    global send_message
    send_message = send_message_method
    start_publishing_class_type(instance_class, send_message)


def dispatcher(message):
    # queue(?)
    subject = get_message_subject(message)
    if subject == 'create_instance':
        create_instance(message)
    elif subject == 'delete_instance':
        delete_instance(message)
    elif subject == 'instance_status':
        publish_instance_status(message['id'])
    else:
        log('Unknown message subject: %s' % subject)


@run_in_background
def create_instance(message):
    instance = message.copy()
    log('Creating instance (id=%s)' % instance['id'])
    time.sleep(5)
    instance['status'] = 'running'
    update_instance_status(instance['id'], instance)


@run_in_background
def delete_instance(message):
    instance_id = message['id']
    log('Deleting instance (id=%s)' % instance_id)
    instance = get_instance(instance_id)
    if instance is None:
        return
    instance['status'] = 'deleted'
    update_instance_status(instance_id, instance)

# it smells
def stop():
    stop_publishing_class_type(instance_class)


def get_instance(instance_id):
    global my_instances
    if instance_id not in my_instances:
        return None
    return my_instances[instance_id]


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


def log(entry):
    print('[%sWorker] %s\n' % (instance_class['name'], entry))
