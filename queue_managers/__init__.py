import copy
from config_manager import get_configuration
from queue_managers.rabbit import BlockingPikaManager


manager = dict()


def set_manager(queues=None):
    config = get_configuration('messaging') or {'host': 'localhost',
                                                'port': 5672,
                                                'user': 'guest',
                                                'pass': 'guest'}
    global manager
    for item in queues:
        manager[item] = BlockingPikaManager(host=config['host'],
                                            port=int(config['port']),
                                            user=config['user'],
                                            password=config['pass'],
                                            queue=item)


def get_manager(queue=None):
    global manager
    if not manager:
        set_manager(queues=queue)
    return manager[queue]


def send_message(routing_key, subject, message):
    msg = copy.copy(message)
    msg['subject'] = subject
    get_manager(queue=routing_key).publish(routing_key, msg)


def get_message_subject(message):
    if 'subject' not in message:
        return None
    return message.pop('subject')


def subscribe(routing_key, callback):
    get_manager(queue=routing_key).subscribe(routing_key, callback)
