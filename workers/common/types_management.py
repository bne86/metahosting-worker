import random
import threading

# stores True for each type that should be published (we could store
# threads as well)
publishing_active = dict()
# how often instance type information should be published
INTERVAL = 0

# options:
# 1) publishing thread
# 2) many threads stored in dict (to stop selectively)


def publish_type(send_message_function, type_description):
    send_message_function('info', 'instance_type', {'type': type_description})
    if publishing_active[type_description['name']]:
        func = lambda: publish_type(send_message_function, type_description)
        timer = threading.Timer(INTERVAL + jitter(INTERVAL), func)
        timer.start()


def stop_publishing_type(type_description):
    global publishing_active
    publishing_active[type_description['name']] = False


def start_publishing_type(type_description, send_message_function):
    global publishing_active
    publishing_active[type_description['name']] = (INTERVAL > 0)
    publish_type(send_message_function, type_description)


def jitter(interval):
    return random.random() * interval * 0.3
