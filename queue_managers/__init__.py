import copy
from config_manager import get_configuration
from queue_managers.rabbit import BlockingPikaManager


config = get_configuration('messaging')
managers = dict()

if config is None:
    config = {'host': 'localhost', 'port': 5672}


def get_manager(queue=None):
    if queue not in managers:
        managers[queue] = BlockingPikaManager(host=config['host'],
                                              port=int(config['port']),
                                              queue=queue)
    return managers[queue]


def send_message(routing_key, subject, message):
    msg = copy.copy(message)
    msg['subject'] = subject
    get_manager().publish(routing_key, msg)


def subscribe(routing_key, callback):
    get_manager(routing_key).subscribe(routing_key, callback)


def get_message_subject(message):
    if 'subject' not in message:
        return None
    return message.pop('subject')
