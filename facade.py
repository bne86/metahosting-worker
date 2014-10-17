import time
import uuid
from queue_manager import qm

instanceTypes = dict()
instances = dict()


# worker method
def register_instance_type(instance_type):
    global instanceTypes
    if is_proper_instance_type(instance_type):
        name = instance_type['name']
        instance_type['ts'] = time.time()
        log('Registering class: %s' % name)
        instanceTypes[name] = instance_type


# client method
def get_instance_types():
    global instanceTypes
    return instanceTypes.copy()


# client method
def create_instance(instance_type_name):
    global instanceTypes
    global instances
    if instance_type_name in instanceTypes:
        log('Creating instance for %s' % instance_type_name)
        instance = dict()
        instance['id'] = generate_id()
        instance['status'] = 'starting'
        instance['class'] = instanceTypes[instance_type_name]
        instances[instance['id']] = instance
        # send create message?
        qm.publish(instance_type_name, instance)
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
    global instances
    if instance_id in instances:
        return instances[instance_id]
    else:
        log('Instance %s does not exist' % instance_id)


# client and worker method
def update_instance(instance_id, instance):
    global instances
    log('Instance %s updated' % instance_id)
    instances[instance_id] = instance


# helpers
def is_proper_instance_type(instance_type):
    return 'name' in instance_type


def generate_id():
    return uuid.uuid1().hex


def log(msg):
    print('[facade] %s\n' % msg)
