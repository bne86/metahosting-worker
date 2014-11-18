from queue_managers import get_message_subject
import logging

__author__ = 'jj'


class Dispatcher(object):
    def __init__(self):
        self.callbacks = dict()

    def callback(self, subject):
        def decorator(f):
            logging.debug('Registering callback for %s: %s', subject,
                          f.__name__)
            self.callbacks[subject] = f
            return f

        return decorator

    def dispatch(self, message):
        subject = get_message_subject(message)

        if subject in self.callbacks:
            callback = self.callbacks[subject]
            callback(message)
        else:
            logging.error('No callback for %s found!', subject)