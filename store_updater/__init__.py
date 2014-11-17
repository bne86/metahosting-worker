import logging
from queue_managers import subscribe
from store_updater.methods import dispatcher

__author__ = 'jj'


def init():
    logging.debug('Initializing...')
    subscribe('info', dispatcher)


if __name__ == '__main__':
    init()
