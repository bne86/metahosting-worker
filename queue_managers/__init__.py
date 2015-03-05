from contextlib import contextmanager
import copy
from config_manager import get_configuration
from queue_managers.rabbit import BlockingPikaManager


@contextmanager
def managed(queue):
    config = get_configuration('messaging') or {'host': 'localhost',
                                                'port': 5672,
                                                'user': 'guest',
                                                'pass': 'guest'}

    manager = BlockingPikaManager(host=config['host'],
                                  port=int(config['port']),
                                  user=config['user'],
                                  password=config['pass'],
                                  queue=queue)
    yield manager
    manager.disconnect()


def send_message(routing_key, subject, message):
    msg = copy.copy(message)
    msg['subject'] = subject
    with managed(routing_key) as manager:
        manager.publish(routing_key, msg)


def get_message_subject(message):
    if 'subject' not in message:
        return None
    return message.pop('subject')


def subscribe(routing_key, callback):
    with managed(routing_key) as manager:
        manager.subscribe(routing_key, callback)