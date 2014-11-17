import logging
import uuid
from stores import instance_store, type_store
from queue_managers import send_message


def get_types():
    return type_store.get_all()


def create_instance(instance_type):
    types = get_types()
    if instance_type not in types:
        logging.debug('Unknown instance type: %s', instance_type)

    logging.debug('Creating instance for: %s', instance_type)
    instance = dict()
    instance['id'] = generate_id()
    instance['status'] = 'starting'
    instance['type'] = types[instance_type]
    send_message(instance_type, 'create_instance', instance)
    send_message('info', 'instance_info', {'instance': instance})
    return instance


def get_instance(instance_id):
    return instance_store.get(instance_id)


def get_all_instances():
    return instance_store.get_all()


def get_instances_of_type(instance_type_name):
    def filter_function(x):
        return x[1]['type']['name'] == instance_type_name
    return filter(filter_function, get_all_instances().iteritems())


def generate_id():
    return uuid.uuid1().hex
