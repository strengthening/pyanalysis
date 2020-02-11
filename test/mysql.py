import unittest
import logging
import time

from pyanalysis.logger import DebugHandler
from pyanalysis import mysql


class TestMysqlPool(unittest.TestCase):
    def test_mysql_pool(self):

        debug_handler = DebugHandler()
        logger = logging.getLogger("debug")
        logger.addHandler(debug_handler)
        logger.setLevel(debug_handler.level)

        mysql.logger = logger
        p = mysql.Pool(
            size=3,
            name="localhost",
            host="localhost",
            user="root",
            password="123456",
            database="ghost_etl",
            autocommit=True,
            charset="utf8",
        )
        mysql.add_pool(p)

        conn = mysql.Conn("localhost")
        items = conn.query_range(
            "SELECT * FROM spot_kline_btc_usd ORDER BY id",
        )

        start_time = time.time()
        print(start_time)

        for item in items:
            pass

        end_time = time.time()
        print(end_time)