import logging
import os
from queue_managers.rabbit import BlockingPikaManager

HOST = 'MESSAGING_PORT_5672_TCP_ADDR'
PORT = 'MESSAGING_PORT_5672_TCP_PORT'

if HOST not in os.environ or PORT not in os.environ:
    logging.warning('Using default messaging connection details. Set [%s, '
                    '%s].',
                    HOST, PORT)

host = os.getenv(HOST, 'localhost')
port = int(os.getenv(PORT, 5672))

manager = BlockingPikaManager(host=host, port=port)


def send_message(routing_key, subject, message):
    msg = message.copy()
    msg['subject'] = subject
    manager.publish(routing_key, msg)


def subscribe(routing_key, callback):
    manager.subscribe(routing_key, callback)


def get_message_subject(message):
    if 'subject' not in message:
        return None
    return message.pop('subject')
