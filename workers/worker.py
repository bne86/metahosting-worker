from abc import ABCMeta
import logging
from queue_managers import get_message_subject, send_message, subscribe
from workers.common.types_management import start_publishing_type, \
    stop_publishing_type


class Worker(object):
    __metaclass__ = ABCMeta
    callbacks = dict()

    def __init__(self, config, local_instances):
        logging.debug('Initialize general worker')

        self.config = config
        self.instances = local_instances
        self.worker_info = dict()
        self.worker_info['name'] = config['worker']['name']
        self.worker_info['description'] = config['worker']['description']
        self.worker_info['environment'] = dict()
        if 'configurable_env' in self.config:
            for item in self.config['configurable_env'].keys():
                self.worker_info['environment'][item.upper()] \
                    = self.config['configurable_env'][item]

    def start(self):
        subscribe(self.worker_info['name'], self.dispatch)
        start_publishing_type(self.worker_info, send_message)

    def stop(self):
        stop_publishing_type(self.worker_info)

    @staticmethod
    def callback(subject):
        def decorator(f):
            logging.debug('Registering callback for %s: %s', subject,
                          f.__name__)
            Worker.callbacks[subject] = f
            return f

        return decorator

    def dispatch(self, message):
        subject = get_message_subject(message)

        if subject in self.callbacks:
            callback = Worker.callbacks[subject]
            callback(self, message)
        else:
            logging.error('No callback for %s found!', subject)
