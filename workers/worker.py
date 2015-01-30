from abc import ABCMeta
import logging
from queue_managers import get_message_subject, send_message, subscribe
import random
import string
from workers.common.types_management import start_publishing_type, \
    stop_publishing_type


class Worker(object):
    __metaclass__ = ABCMeta
    callbacks = dict()

    def __init__(self, config, instances):
        logging.debug('Initialize general worker')

        self.config = config
        self.instances = instances
        self.worker_info = dict()
        self.worker_info['name'] = config['worker']['name']
        self.worker_info['description'] = config['worker']['description']
        self.worker_info['environment'] = dict()
        if 'configurable_env' in self.config:
            for item in self.config['configurable_env'].keys():
                self.worker_info['environment'][item.upper()] \
                    = self.config['configurable_env'][item]

    def start(self):
        self.worker_info['available'] = True
        subscribe(self.worker_info['name'], self.dispatch)
        start_publishing_type(self.worker_info, send_message)

    def stop(self):
        self.worker_info['available'] = False
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

    def _create_container_environment(self, message):
        """
        Merge the build_parameters configured for the worker and gotten from
        the facade.
        :rtype : list
        Policy: Only override worker-local parameters. If a parameter is empty,
        generate a value using lowercase, uppercase and digits.
        :param message: dict containing the message gotten from the bus
        :return: list containing key=value pairs send to docker
        """
        if 'environment' in message.keys():
            injected_parameters = message['environment']
        else:
            injected_parameters = dict()
        if 'environment' in self.worker_info.keys():
            local_parameters = self.worker_info['environment']
        else:
            local_parameters = dict()
        environment = []
        for key in local_parameters.keys():
            if key in injected_parameters.keys():
                environment.append(key + '=' + injected_parameters[key])
            else:
                if local_parameters[key] == '':
                    environment.append(key + '=' + ''.join(
                        random.SystemRandom().choice(
                            string.ascii_lowercase +
                            string.ascii_uppercase +
                            string.digits)
                        for _ in range(16)))
                else:
                    environment.append(key + '=' + local_parameters[key])
        logging.debug('Current environment for VM: %s', environment)
        return environment
