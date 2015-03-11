from abc import ABCMeta, abstractmethod
import logging
import random
import string
from time import sleep
from queue_managers import get_message_subject, set_manager, subscribe

_shutdown_worker = False


def get_random_key(length=16):
    return ''.join(
        random.SystemRandom().choice(string.ascii_letters + string.digits)
        for _ in range(length))


class Worker(object):
    __metaclass__ = ABCMeta
    callbacks = dict()
    PUBLISHING_INTERVAL = 15

    def __init__(self, worker_conf, worker_env, instance_manager, send_method):
        logging.debug('Worker initialization')

        self.send = send_method
        self.worker_conf = worker_conf
        self.worker_env = worker_env
        self.instances = instance_manager
        self.worker_info = dict()
        self.worker_info['name'] = worker_conf['name']
        self.worker_info['description'] = worker_conf['description']

        self.worker_info['environment'] = dict()
        if worker_env:
            for item in self.worker_env.keys():
                self.worker_info['environment'][item.upper()] \
                    = self.worker_env[item]

    def start(self):
        """
        start thread that is sending all information to the queue and at the
        same time subscribe for create_instance messages on own queue
        :return:
        """
        logging.debug('Worker started')
        self.worker_info['available'] = True
        set_manager(queue=['info', self.worker_info['name']])
        subscribe(self.worker_info['name'], self._dispatch)
        self._publish_information()

    def stop(self, signal, stack):
        """
        try to catch a SIGTERM signal in main thread and stop, not working.
        :param signal:
        :param stack:
        :return:
        """
        logging.debug('Worker stopped with signal %s', signal)
        self.worker_info['available'] = False
        self.publish_type()
        global _shutdown_worker
        _shutdown_worker = True

    def _publish_information(self):
        while not _shutdown_worker:
            logging.info('Publishing type and status updates: %s',
                         self.worker_info['name'])
            self.publish_type()
            self.publish_updates()
            sleep(self.PUBLISHING_INTERVAL)

    def publish_type(self):
        self.send('info', 'instance_type', {'type': self.worker_info})

    @staticmethod
    def callback(subject):
        def decorator(f):
            logging.debug('Registering callback for %s: %s', subject,
                          f.__name__)
            Worker.callbacks[subject] = f
            return f

        return decorator

    def _dispatch(self, message):
        subject = get_message_subject(message)

        if subject in self.callbacks:
            callback = Worker.callbacks[subject]
            callback(self, message)
        else:
            logging.error('No callback for %s found!', subject)

    def _create_container_environment(self):
        """
        Merge the build_parameters configured for the worker and gotten from
        the facade.
        :rtype : list
        Policy: Only override worker-local parameters. If a parameter is empty,
        generate a value using lowercase, uppercase and digits.
        :return: list containing key=value pairs send to docker
        """
        if 'environment' in self.worker_info.keys():
            local_parameters = self.worker_info['environment']
        else:
            local_parameters = dict()
        environment = []
        for key in local_parameters.keys():
            if local_parameters[key] == '':
                environment.append(key + '=' + get_random_key())
            else:
                environment.append(key + '=' + local_parameters[key])
        logging.debug('Current environment for VM: %s', environment)
        return environment

    @abstractmethod
    def publish_updates(self):
        pass
