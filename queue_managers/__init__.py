import ConfigParser
import importlib

# TODO: is it sufficient for dynamically switch between different backends
# TODO: still have to inject the config file path or using command line
settings = ConfigParser.ConfigParser()
settings.readfp(open('config.ini'))

imports = settings.get('communication', 'backend').rsplit('.', 1)

manager_module = importlib.import_module(imports[0])
manager_class = getattr(manager_module, imports[1])()


def send_message(routing_key, subject, message):
    msg = message.copy()
    msg['subject'] = subject
    manager_class.publish(routing_key, msg)


def subscribe(routing_key, callback):
    manager_class.subscribe(routing_key, callback)


def get_message_subject(message):
    if 'subject' not in message:
        return None
    return message.pop('subject')
