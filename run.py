#!/usr/bin/env python

import argparse
from config_manager import get_configuration
import importlib
import logging
import signal
from workers.instance_management import LocalInstanceManager, \
    get_instance_store
from queue_managers import send_message

def _get_backend_class(config):
    """
    :param config: worker configuration (inifile parsed to dict)
    :return: worker backend class
    """
    class_data = config['backend'].split(".")
    module_path = ".".join(class_data[:-1])
    module = importlib.import_module(module_path)
    class_str = class_data[-1]
    return getattr(module, class_str)


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="get debug output",
                        action="store_true")
    parser.add_argument("--envfile",
                        help="provide a file that tells which not-default "
                             "environment variables to use")
    parser.add_argument("--config", help="provide a config file")
    args = parser.parse_args()
    logger = logging.getLogger()
    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    if args.config:
        config_file = args.config
    else:
        config_file = 'config.ini'

    instance_store = get_instance_store(config=get_configuration(
            'local_instance_store', config_file=config_file))
    instance_manager = LocalInstanceManager(instance_store=instance_store,
                                            send_method=send_message)

    worker_config = get_configuration('worker', config_file=config_file)
    worker_env = get_configuration('configurable_env', config_file=config_file)
    worker_class = _get_backend_class(worker_config)
    worker = worker_class(worker_config,
                          worker_env,
                          instance_manager,
                          send_message)
    # try to exit gracefully
    signal.signal(signal.SIGTERM, worker.stop)
    signal.signal(signal.SIGHUP, worker.stop)
    worker.start()

if __name__ == "__main__":
    run()
