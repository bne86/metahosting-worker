
import ConfigParser
import importlib
import logging

logging.basicConfig(format='[%(filename)s] %(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    level=logging.DEBUG)


settings = ConfigParser.ConfigParser()
settings.readfp(open('config.ini'))
worker = importlib.import_module(settings.get('worker', 'backend'))


if __name__ == "__main__":
    logging.debug('Starting worker...')
    worker.init()
    raw_input('Press any key to stop...')
    worker.stop()
