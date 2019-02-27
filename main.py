import logging

from tqdm import tqdm


class TqdmHandler(logging.StreamHandler):
    def __init__(self):
        logging.StreamHandler.__init__(self)

    def emit(self, record):
        msg = self.format(record)
        tqdm.write(msg)


logging_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('Web-Scraper')

tqdm_handler = TqdmHandler()
tqdm_handler.setFormatter(logging_formatter)
logger.addHandler(tqdm_handler)
logger.setLevel(logging.INFO)


