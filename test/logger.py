import unittest
import logging

from pyanalysis.logger import DebugHandler
from pyanalysis.logger import ReleaseRotatingFileHandler
from pyanalysis.logger import ReleaseTimedRotatingFileHandler


class TestLogging(unittest.TestCase):
    def test_debug_handler_logger(self):
        debug_handler = DebugHandler()
        logger = logging.getLogger("debug")
        logger.addHandler(debug_handler)
        logger.setLevel(debug_handler.level)

        logger.debug("some log about debug! ")
        logger.info("some log about info! ")

        try:
            1 / 0
        except Exception as e:
            logger.exception(e)

    def test_release_rotating_file_logger(self):
        release_handler = ReleaseRotatingFileHandler("release.log")
        logger = logging.getLogger("release")
        logger.addHandler(release_handler)
        logger.setLevel(release_handler.level)

        logger.debug("some log about debug! ")
        logger.info("some log about info! ")
        try:
            1 / 0
        except Exception as e:
            logger.exception(e)

    def test_release_time_rotating_file_logger(self):
        release_handler = ReleaseTimedRotatingFileHandler("release-time-rotating.log")
        logger = logging.getLogger("release")
        logger.addHandler(release_handler)
        logger.setLevel(release_handler.level)

        logger.debug("some log about debug! ")
        logger.info("some log about info! ")
        try:
            1 / 0
        except Exception as e:
            logger.exception(e)

    # def test_alarm_smtp_logger(self):
    #     alarm_handler = AlarmSMTPHandler(
    #         host="smtp.qq.com",
    #         port=587,
    #         username="input your email username",
    #         password="input your email password",
    #         fromaddr="input your send email address",
    #         toaddrs="input your receive email address",
    #         subject="pyanalysis notify"
    #     )
    #
    #     logger = logging.getLogger("alarm")
    #     logger.addHandler(alarm_handler)
    #     logger.setLevel(alarm_handler.level)
    #
    #     logger.critical("hahahahahha")
