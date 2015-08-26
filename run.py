#!/usr/bin/env python

import argparse
import config_manager
import logging
import signal
from config_manager import get_backend_class
from workers.manager.persistence import PersistenceManager
from queue_managers import send_message


def argument_parsing():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug",
                        help="get debug output",
                        action="store_true")
    parser.add_argument("--logstash",
                        help="log everything (in addition) to logstash "
                             ", give host:port")
    parser.add_argument("--envfile",
                        help="provide a file that tells which not-default "
                        "environment variables to use")
    parser.add_argument("--config",
                        help="provide a config file")
    return parser.parse_args()


def logging_setup(arguments):
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler())
    if arguments.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    if arguments.logstash:
        import logstash
        host, port = arguments.logstash.split(':')
        logger.addHandler(logstash.TCPLogstashHandler(host=host,
                                                      port=int(port),
                                                      version=1))


def run():
    arguments = argument_parsing()
    logging_setup(arguments=arguments)

    if arguments.config:
        config_manager._CONFIG_FILE = arguments.config

    local_persistence = PersistenceManager(
        config=config_manager.get_configuration('local_persistence'),
        send_method=send_message)

    worker_config = config_manager.get_configuration('worker')
    instance_env = config_manager.\
        get_instance_configuration('instance_environment')
    worker_class = get_backend_class(worker_config)
    worker = worker_class(worker_conf=worker_config,
                          instance_env=instance_env,
                          local_persistence=local_persistence,
                          send_method=send_message)

    signal.signal(signal.SIGTERM, worker.stop)
    signal.signal(signal.SIGHUP, worker.stop)
    signal.signal(signal.SIGINT, worker.stop)
    worker.start()

if __name__ == "__main__":
    run()
