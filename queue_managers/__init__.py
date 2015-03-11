import copy
from config_manager import get_configuration
from queue_managers.rabbit import BlockingPikaManager


manager = None


def set_manager(queue=None):
    config = get_configuration('messaging') or {'host': 'localhost',
                                                'port': 5672,
                                                'user': 'guest',
                                                'pass': 'guest'}
    global manager
    if not manager:
        manager = BlockingPikaManager(host=config['host'],
                                      port=int(config['port']),
                                      user=config['user'],
                                      password=config['pass'],
                                      queue=queue)


def get_manager():
    global manager
    if not manager:
        set_manager()
    return manager


def send_message(routing_key, subject, message):
    msg = copy.copy(message)
    msg['subject'] = subject
    get_manager().publish(routing_key, msg)


def get_message_subject(message):
    if 'subject' not in message:
        return None
    return message.pop('subject')


def subscribe(routing_key, callback):
    get_manager().subscribe(routing_key, callback)