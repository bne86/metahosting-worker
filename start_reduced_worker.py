
import logging
from workers import reduced_worker as worker

logging.basicConfig(format='[%(filename)s] %(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    level=logging.DEBUG)



if __name__ == "__main__":
    logging.debug('Starting worker...')
    worker.init()
    raw_input('Press any key to stop...')
