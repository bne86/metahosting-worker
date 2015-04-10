from abc import ABCMeta, abstractmethod
from collections import namedtuple
import logging
import random
import string
from time import sleep
from queue_managers import get_message_subject, set_manager, subscribe
from urlbuilders import GenericUrlBuilder
from workers.manager.port import PortManager


def get_random_key(length=16):
    return ''.join(
        random.SystemRandom().choice(string.ascii_letters + string.digits)
        for _ in range(length))

callbacks = dict()


def callback(subject):
    def decorator(f):
        logging.debug('Registering callback for %s: %s', subject,
                      f.__name__)
        global callbacks
        callbacks[subject] = f
        return f

    return decorator


class Worker(object):
    __metaclass__ = ABCMeta
    PUBLISHING_INTERVAL = 10

    def __init__(self, worker_conf, worker_env,
                 local_persistence, send_method):
        """
        Worker skeleton
        :param worker_conf: dict containing the configuration
        :param worker_env: dict containing the configurable environment
        :param local_persistence: local instance manger
        :param send_method: messaging communication method
        :return: -
        """
        logging.debug('Worker initialization')

        if 'disable_https_warnings' in worker_conf \
                and 'base_url' in worker_conf \
                and 'https' in worker_conf['base_url']:
            import requests.packages.urllib3
            requests.packages.urllib3.disable_warnings()

        self.shutdown = False
        self.publish = send_method
        self.worker_conf = worker_conf
        self.worker_env = worker_env
        self.local_persistence = local_persistence
        self.worker = dict()
        self.worker['name'] = worker_conf['name']
        self.worker['description'] = worker_conf['description']
        self.worker['environment'] = _create_worker_env(worker_env)
        self.port_manager = PortManager(worker_conf)
        self.url_builder = GenericUrlBuilder(worker_conf)

    def start(self):
        """
        start thread that is sending all information to the queue and at the
        same time subscribe for create_instance messages on own queue
        :return:
        """
        logging.debug('Worker started')
        self.worker['available'] = True
        self.worker['status'] = 'Worker available'
        subscribe(self.worker['name'], self._dispatch)
        self.run()

    def stop(self, signal, stack):
        """
        try to catch a SIGTERM signal in main thread and stop.
        :param signal:
        :param stack:
        :return:
        """
        logging.debug('Worker stopped with signal %s, %s', signal, stack)
        self.worker['available'] = False
        self.worker['status'] = 'Worker not available'
        self._publish_type()
        self.shutdown = True

    @callback('create_instance')
    def create(self, message):
        self.create_instance(message)

    @callback('delete_instance')
    def delete(self, message):
        self.delete_instance(message)

    @abstractmethod
    def create_instance(self, message):
        pass

    @abstractmethod
    def delete_instance(self, message):
        pass

    @abstractmethod
    def _publish_updates(self):
        pass

    def run(self):
        while not self.shutdown:
            logging.info('Publishing type and status updates: %s',
                         self.worker['name'])
            self._publish_updates()
            self._publish_type()
            sleep(self.PUBLISHING_INTERVAL)

    def _publish_type(self):
        self.publish('info', 'instance_type', {'type': self.worker})

    def _dispatch(self, message):
        subject = get_message_subject(message)
        global callbacks
        if subject in callbacks:
            callbacks[subject](self, message)
        else:
            logging.error('No callback for %s found!', subject)

    def _create_instance_env(self):
        """
        Merge the worker env with the incarnation of the instance
        :return: list containing key=value pairs send to instance
        """
        worker_env = self.worker['environment']
        instance_env = []
        for key in worker_env.keys():
            if worker_env[key] == '':
                instance_env.append(key + '=' + get_random_key())
            else:
                instance_env.append(key + '=' + worker_env[key])
        logging.debug('Current environment for VM: %s', instance_env)
        return instance_env


def _create_worker_env(worker_env=None):
    environment = dict()
    if worker_env:
        for item in worker_env.keys():
            environment[item.upper()] = worker_env[item]
    return environment
