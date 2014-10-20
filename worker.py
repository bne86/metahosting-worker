import time
import threading
import random
from queue_manager import qm

instance_class = dict()
instance_class['name'] = 'service_a'
instance_class['description'] = 'service_a for doing lot of cool stuff'

# how often instance type information should be published (will become global)
INTERVAL = 3600
publishing_thread = threading.Timer(0, {})


def create_instance(msg):
    log('Creating %s instance (id=%s)' % (instance_class['name'], msg['id']))
    time.sleep(5)
    msg['status'] = 'running'
    qm.publish('info', {'msg': 'instance_info', 'instance': msg})


def listener(message):
    # queue(?) + dispatcher here
    create_instance(message)


def publish_class_type():
    qm.publish('info', {'msg': 'instance_type', 'class': instance_class})
    global publishing_thread
    publishing_thread = threading.Timer(INTERVAL + jitter(INTERVAL),
                                        publish_class_type)
    publishing_thread.start()


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

