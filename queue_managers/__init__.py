import logging
import ConfigParser
import os
from queue_managers.rabbit import BlockingPikaManager

# configuration defaults through ENV,
# allways more important then configuration files.
HOST = 'MESSAGING_PORT_5672_TCP_ADDR'
PORT = 'MESSAGING_PORT_5672_TCP_PORT'


# if ENV not set in a default way,
# try to get other variables or a configuration file.
if HOST not in os.environ or PORT not in os.environ:
    # maybe the environment is different, keep it configurable
    envvars = ConfigParser.ConfigParser()
    try:
        envvars.readfp(open('envvars.ini'))
        HOST = envvars.get('messaging', 'HOST_VARIABLE')
        PORT = envvars.get('messaging', 'PORT_VARIABLE')
    except IOError or ConfigParser.NoOptionError as err:
        logging.debug('Option file for environment variables not valid')
        logging.error(err)


# if new ENVs still not set, we should look for a configuration file,
# otherwise configure the messaging
if HOST not in os.environ or PORT not in os.environ:
    config = ConfigParser.ConfigParser()
    try:
        config.readfp(open('config.ini'))
        host = config.get('communication', 'host')
        port = int(config.get('communication', 'port'))
    except IOError or ConfigParser.NoOptionError as err:
        logging.debug('Establishing messaging not possible because both '
                      'env and config are not valid')
        logging.error(err)
        exit(1)
else:
    host = os.getenv(HOST, 'localhost')
    port = int(os.getenv(PORT, 5672))

logging.debug('Try to establish connection to messaging bus via '
              'host %s on port %s', host, port)
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
