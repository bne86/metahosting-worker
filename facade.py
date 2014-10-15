import time
import uuid


instanceTypes = dict()
instances = dict()


# worker method
def register_instance_type(instanceType):
    global instanceTypes
    if is_proper_instance(instanceType):
        name = instanceType['name']
        instanceType['ts'] = time.time()
        print 'Registering class: ', name
        instanceTypes[name] = instanceType


# client method
def get_instance_types():
    global instanceTypes
    return instanceTypes


# client method
def create_instance(instanceType):
    global instanceTypes
    global instances
    if instanceType['name'] in instanceTypes:
        print 'Creating instance for ', instanceType['name']
        instance = dict()
        instance['id'] = generate_id(instanceType)
        instance['status'] = 'starting'
        instance['class'] = instanceType
        instances[instance['id']] = instance
        # send create message?
        return instance
    else:
        print 'Unknown instance type: ', instanceType['name']


# client method
def get_instance(instance_id):
    global instances
    if instance_id in instances:
        return instances[instance_id]
    else:
        print 'Instance ', instance_id, ' does not exist'


# client and worker method
def update_instance(instance_id, instance):
    global instances
    print 'Instance ', instance_id, ' updated'
    instances[instance_id] = instance


# helpers
def is_proper_instance(instanceType):
    return 'name' in instanceType


def generate_id(instanceType):
    return uuid.uuid1().hex
