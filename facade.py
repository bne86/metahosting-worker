import time
import uuid
from queue_manager import get_message_subject

instance_types = dict()
instances = dict()
send_message = lambda x, y, z: None


def init(qm, send_message_method):
    global send_message
    send_message = send_message_method
    qm.subscribe('info', facade_listener)


# worker method
def register_instance_type(instance_type):
    if is_proper_instance_type(instance_type):
        name = instance_type['name']
        instance_type['ts'] = time.time()
        log('Registering class: %s' % name)
        global instance_types
        instance_types[name] = instance_type


# client method
def get_instance_types():
    return instance_types.copy()


# client method
def create_instance(instance_type_name):
    if instance_type_name in instance_types:
        log('Creating instance for %s' % instance_type_name)
        instance = dict()
        instance['id'] = generate_id()
        instance['status'] = 'starting'
        instance['class'] = instance_types[instance_type_name]
        update_instance(instance['id'], instance)
        send_message(instance_type_name, 'create_instance', instance)
        return instance
    else:
        log('Unknown instance type: ' % instance_type_name)


# client method
def get_all_instances():
    # are the shallow copies enough?
    return instances.copy()


# client method
def get_instances_of_type(instance_type_name):
    def filter_function(x):
        return x[1]['class']['name'] == instance_type_name

    return filter(filter_function, get_all_instances().iteritems())


# client method
def get_instance(instance_id):
    if instance_id in instances:
        return instances[instance_id]
    else:
        log('Instance %s does not exist' % instance_id)


# client and worker method
def update_instance(instance_id, instance):
    log('Instance %s updated' % instance_id)
    global instances
    instances[instance_id] = instance


# msg receiver
def facade_listener(message):
    msg_subject = get_message_subject(message)
    if msg_subject is None:
        print('Invalid message format')
        return

    if msg_subject == 'instance_type':
        register_instance_type(message['class'])
    elif msg_subject == 'instance_info':
        instance = message['instance'].copy()
        instance['last_info'] = time.time()
        update_instance(instance['id'], instance)
    else:
        log('Unknown message subject: %s' % msg_subject)


# helpers
def is_proper_instance_type(instance_type):
    return 'name' in instance_type


def generate_id():
    return uuid.uuid1().hex


def log(msg):
    print('[facade] %s' % msg)
