import copy
from config_manager import get_configuration
from queue_managers.rabbit import BlockingPikaManager


managers = dict()


def managed(queue):
    if queue not in managers:
        config = get_configuration('messaging') or {'host': 'localhost',
                                                    'port': 5672,
                                                    'user': 'guest',
                                                    'pass': 'guest'}

        managers[queue] = BlockingPikaManager(host=config['host'],
                                              port=int(config['port']),
                                              user=config['user'],
                                              password=config['pass'],
                                              queue=queue)
    return managers[queue]


def send_message(routing_key, subject, message):
    msg = copy.copy(message)
    msg['subject'] = subject
    managed(routing_key).publish(routing_key, msg)


def get_message_subject(message):
    if 'subject' not in message:
        return None
    return message.pop('subject')


def subscribe(routing_key, callback):
    managed(routing_key).subscribe(routing_key, callback)