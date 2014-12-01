import ConfigParser
import time

from queue_managers import send_message
from stores import get_instance as local_instance_store


settings = ConfigParser.ConfigParser()
settings.readfp(open('config.ini'))
my_instances = local_instance_store(settings, 'local_instance_store')


def get_local_instance(instance_id):
    return my_instances.get(instance_id)


def add_local_instance(instance_id, instance):
    my_instances.update(instance_id, instance)


def publish_instance_status(instance_id):
    instance = get_local_instance(instance_id)
    if instance is not None:
        send_message('info', 'instance_info', {'instance': instance})


def update_instance_status(instance_id, instance):
    instance['id'] = instance_id
    instance['ts'] = time.time()
    send_message('info', 'instance_info', {'instance': instance})
