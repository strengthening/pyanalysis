import unittest

from pyanalysis.log import logging


class TestLogging(unittest.TestCase):
    def test_console_logger(self):
        pass
        log = logging.ConsoleLog("test", logging.INFO)
        logging.add(log)
        try:
            1 / 0
        except BaseException as e:
            logging.get("test").error(e)
