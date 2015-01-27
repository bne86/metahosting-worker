import copy
from config_manager import get_configuration
from queue_managers.rabbit import BlockingPikaManager


config = get_configuration('messaging')
manager = BlockingPikaManager(host=config['host'], port=int(config['port']))


def send_message(routing_key, subject, message):
    msg = copy.copy(message)
    msg['subject'] = subject
    manager.publish(routing_key, msg)


def subscribe(routing_key, callback):
    manager.subscribe(routing_key, callback)


def get_message_subject(message):
    if 'subject' not in message:
        return None
    return message.pop('subject')
