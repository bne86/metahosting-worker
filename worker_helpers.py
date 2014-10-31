import random
import threading


def run_in_background(func):
    def background_runner(*args, **kwargs):
        th = threading.Thread(target=func, args=args, kwargs=kwargs)
        th.start()
    return background_runner

# stores True for each class type that should be published (we could store
# threads as well
publishing_active = dict()
# how often instance type information should be published (will become global)
INTERVAL = 3600


def publish_class_type(send_message, class_type_description):
    send_message('info', 'instance_type', {'class': class_type_description})
    if publishing_active[class_type_description['name']]:
        func = lambda: publish_class_type(send_message, class_type_description)
        th = threading.Timer(INTERVAL + jitter(INTERVAL), func)
        th.start()


def stop_publishing_class_type(class_type_description):
    global publishing_active
    publishing_active[class_type_description['name']] = True


def start_publishing_class_type(class_type_description, send_message_function):
    global publishing_active
    publishing_active[class_type_description['name']] = True
    publish_class_type(send_message_function, class_type_description)


def jitter(interval):
    return random.random() * interval * 0.3
