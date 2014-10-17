import time
import uuid


instanceTypes = dict()
instances = dict()


# worker method
def register_instance_type(instance_type):
    global instanceTypes
    if is_proper_instance(instance_type):
        name = instance_type['name']
        instance_type['ts'] = time.time()
        print('Registering class: %s' % name)
        instanceTypes[name] = instance_type


# client method
def get_instance_types():
    global instanceTypes
    return instanceTypes


# client method
def create_instance(instance_type):
    global instanceTypes
    global instances
    if instance_type['name'] in instanceTypes:
        print('Creating instance for %s' % instance_type['name'])
        instance = dict()
        instance['id'] = generate_id()
        instance['status'] = 'starting'
        instance['class'] = instance_type
        instances[instance['id']] = instance
        # send create message?
        return instance
    else:
        print('Unknown instance type: ' % instance_type['name'])


# client method
def get_instance(instance_id):
    global instances
    if instance_id in instances:
        return instances[instance_id]
    else:
        print('Instance %s does not exist' % instance_id)


# client and worker method
def update_instance(instance_id, instance):
    global instances
    print('Instance %s updated' % instance_id)
    instances[instance_id] = instance


# helpers
def is_proper_instance(instance_type):
    return 'name' in instance_type


def generate_id():
    return uuid.uuid1().hex



