import logging
import ConfigParser
import os
import copy
from queue_managers.rabbit import BlockingPikaManager

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 5672

var_config = ConfigParser.SafeConfigParser(
    {'HOST_VARIABLE': 'MESSAGING_PORT_5672_TCP_ADDR',
     'PORT_VARIABLE': 'MESSAGING_PORT_5672_TCP_PORT'})
var_config.read('envvars.ini')
HOST = var_config.get('messaging', 'HOST_VARIABLE')
PORT = var_config.get('messaging', 'PORT_VARIABLE')

if HOST not in os.environ or PORT not in os.environ:
    config = ConfigParser.SafeConfigParser(
        {'host': DEFAULT_HOST, 'port': DEFAULT_PORT}
    )
    config.read('config.ini')
    host = config.get('messaging', 'host')
    port = int(config.get('messaging', 'port'))
else:
    host = os.getenv(HOST, DEFAULT_HOST)
    port = int(os.getenv(PORT, DEFAULT_PORT))

logging.info('Connecting to messaging on %s:%s', host, port)
manager = BlockingPikaManager(host=host, port=port)


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
