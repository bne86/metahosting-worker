#!/usr/bin/env python

import signal

from metahosting.common import \
    argument_parsing, logging_setup, config_manager as cm


def run():
    arguments = argument_parsing()
    logging_setup(arguments=arguments)

    if arguments.config:
        cm._CONFIG_FILE = arguments.config
    if arguments.envfile:
        cm._VARIABLES_FILE = arguments.envfile

    config = dict()
    config['persistence'] = cm.get_configuration('persistence')
    config['messaging'] = cm.get_configuration('messaging')
    config['worker'] = cm.get_configuration('worker')
    config['instance'] = cm.get_instance_configuration('instance_environment')
    persistence = cm.get_backend_class(config=config['persistence'],
                                       key='backend')
    messaging = cm.get_backend_class(config=config['messaging'],
                                     key='backend')

    worker_class = cm.get_backend_class(config=config['worker'], key='backend')
    worker = worker_class(config=config,
                          persistence=persistence,
                          messaging=messaging)

    signal.signal(signal.SIGTERM, worker.stop)
    signal.signal(signal.SIGHUP, worker.stop)
    signal.signal(signal.SIGINT, worker.stop)
    worker.start()

if __name__ == "__main__":
    run()
