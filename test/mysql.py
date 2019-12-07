import unittest
import logging

from pyanalysis.log_handler import DebugHandler
from pyanalysis import mysql


class TestMysqlPool(unittest.TestCase):
    def test_mysql_pool(self):

        debug_handler = DebugHandler()
        logger = logging.getLogger("debug")
        logger.addHandler(debug_handler)
        logger.setLevel(debug_handler.level)

        mysql.logger = logger
        p = mysql.Pool(
            size=1,
            name="localhost",
            host="localhost",
            user="root",
            password="123456",
            database="ghost",
            autocommit=True,
            charset="utf8",
        )
        mysql.add_pool(p)
        conn = mysql.Conn("localhost")
        item = conn.query_one(
            "SELECT * FROM account_future WHERE id = ? LIMIT 1",
            (1,)
        )
        print(item)
