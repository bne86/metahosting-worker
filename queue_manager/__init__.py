import ConfigParser
import importlib

#TODO: decide whether this is a appropriate way to dynamically switch between different queue backends
#TODO:  still have to inject the config file path or using command line
settings = ConfigParser.ConfigParser()
settings.readfp(open('config.ini'))

qmmodule = importlib.import_module(settings.get('communication', 'backend'))
qm = qmmodule.QueueManager()


def send_message(routing_key, subject, message):
    msg = message.copy()
    msg['subject'] = subject
    qm.publish(routing_key, msg)


def subscribe(routing_key, callback):
    qm.subscribe(routing_key, callback)


def get_message_subject(message):
    if 'subject' not in message:
        return None
    return message.pop('subject')