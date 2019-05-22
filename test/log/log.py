import unittest

from pyanalysis.log.log import *
from pyanalysis.log import log_pool


class TestLogging(unittest.TestCase):
    def test_console_logger(self):
        # pass
        log = ConsoleLog("test", INFO)
        log_pool.add(log)
        try:
            1 / 0
        except BaseException as e:
            log_pool.get("test").error(e)
