import logging
import random
import string

from abc import ABCMeta, abstractmethod
from time import sleep, ctime

from metahosting.common import get_uuid
from metahosting.common.messaging import get_message_subject
from urlbuilders import GenericUrlBuilder
from workers.manager.persistence import PersistenceManager
from workers.manager.port import PortManager


def get_random_key(length=16):
    return ''.join(
        random.SystemRandom().choice(string.ascii_letters + string.digits)
        for _ in range(length))

callbacks = dict()


def callback(subject):
    def decorator(f):
        logging.debug('Registering callback for %s: %s', subject, f.__name__)
        global callbacks
        callbacks[subject] = f
        return f
    return decorator


class Worker(object):
    __metaclass__ = ABCMeta

    def __init__(self, config, persistence, messaging):
        """
        Worker skeleton
        :param worker_conf: dict containing the configuration
        :param worker_env: dict containing the configurable environment
        :param local_persistence: local instance manger
        :param send_method: messaging communication method
        :return: -
        """
        logging.debug('Worker initialization')

        if 'disable_https_warnings' in config['worker']:
            import requests.packages.urllib3
            requests.packages.urllib3.disable_warnings()

        self.running = False
        self.config = config

        self.worker = dict()
        self.worker['name'] = self.config['worker']['name']
        self.worker['uuid'] = get_uuid(self.config['worker']['uuid_source'])
        self.worker['description'] = self.config['worker']['description']
        self.worker['environment'] = \
            _load_instance_env(self.config['instance'])
        self.port_manager = PortManager(self.config['worker'])
        self.url_builder = GenericUrlBuilder(self.config['worker'])

        self.publish_manager = messaging(
            config=self.config['messaging'],
            queue='info')
        self.publish = self.publish_manager.publish
        self.subscribe_manager = messaging(config=self.config['messaging'],
                                           queue=self.worker['name'])
        self.local_persistence = PersistenceManager(
            config=self.config['persistence'],
            backend=persistence,
            publish=self.publish)

    def start(self):
        """
        start thread that is sending all information to the queue and at the
        same time subscribe for create_instance messages on own queue
        :return:
        """
        self.running = True
        logging.info('Worker starting at %s', ctime())
        self.worker['available'] = True
        self.worker['status'] = 'Worker available'
        self.subscribe_manager.subscribe(self.worker['name'], self._dispatch)
        while self.running:
            logging.info('Publishing type and status updates: %s',
                         self.worker['name'])
            self._publish_updates()
            self._publish_type()
            sleep(10)
        logging.info('Worker stopped at %s', ctime())

    def stop(self, signal, stack):
        """
        try to catch a SIGTERM signal in main thread and stop.
        :param signal:
        :param stack:
        :return:
        """
        self.worker['available'] = False
        self.worker['status'] = 'Worker not available'
        self._publish_type()
        self.publish_manager.disconnect()
        self.running = False
        logging.info('Worker stopping with signal %s', signal)

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
        logging.error('WORKER_ENV: %s', worker_env)
        instance_env = []
        for key in worker_env.keys():
            if worker_env[key] == '':
                instance_env.append(key + '=' + get_random_key())
            else:
                instance_env.append(key + '=' + worker_env[key])
        logging.debug('Current environment for VM: %s', instance_env)

        logging.error('INSTANCE_ENV: %s', instance_env)
        return instance_env


def _load_instance_env(instance_env=None):
    environment = dict()
    if instance_env:
        for item in instance_env.keys():
            environment[item.upper()] = instance_env[item]
    return environment
