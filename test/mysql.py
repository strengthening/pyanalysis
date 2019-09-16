import unittest
import logging

from pyanalysis.handler import DebugHandler

from pyanalysis import mysql_pool


class TestMysqlPool(unittest.TestCase):
    def test_mysql_pool(self):

        debug_handler = DebugHandler()
        logger = logging.getLogger("debug")
        logger.addHandler(debug_handler)
        logger.setLevel(debug_handler.level)

        mysql_pool.logger = logger
        p = mysql_pool.ConnectionPool(
            size=1,
            name="localhost",
            host="localhost",
            user="root",
            password="123456",
            database="ghost",
            autocommit=True,
            charset="utf8",
        )
        mysql_pool.add(p)
        conn = mysql_pool.Conn("localhost")
        item = conn.query_one(
            "SELECT * FROM account_future WHERE id = ? LIMIT 1",
            (1,)
        )
        # print(item)
        # int(time.time()*1000000)


