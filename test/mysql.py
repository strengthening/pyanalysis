import unittest
from unittest.mock import Mock, patch, MagicMock
import datetime
import decimal
import queue
import warnings

import pyanalysis.mysql as mysql_module
from pyanalysis.mysql import (
    Pool,
    Conn,
    Trans,
    GetConnectionFromPoolError,
    add_pool,
    get_pool,
)

# Access the internal __pool registry through the module
_pool_registry = mysql_module.__pool


class TestPool(unittest.TestCase):
    def setUp(self):
        self.pool_name = "test_pool"

    def tearDown(self):
        if self.pool_name in _pool_registry:
            del _pool_registry[self.pool_name]

    @patch("pyanalysis.mysql._Connection")
    def test_pool_size_limit_max(self, mock_conn_class):
        pool = Pool(size=150, name=self.pool_name, host="localhost")
        self.assertEqual(pool.size(), Pool._MAX_SIZE_LIMIT)

    @patch("pyanalysis.mysql._Connection")
    def test_pool_size_limit_min(self, mock_conn_class):
        pool = Pool(size=1, name=self.pool_name, host="localhost")
        self.assertEqual(pool.size(), Pool._MIN_SIZE_LIMIT)

    @patch("pyanalysis.mysql._Connection")
    def test_pool_normal_size(self, mock_conn_class):
        pool = Pool(size=5, name=self.pool_name, host="localhost")
        self.assertEqual(pool.size(), 5)

    @patch("pyanalysis.mysql._Connection")
    def test_pool_name_generation(self, mock_conn_class):
        pool = Pool(host="localhost", port=3306, user="test", database="testdb")
        self.assertIn("localhost", pool.name)
        self.assertIn("3306", pool.name)
        self.assertIn("test", pool.name)
        self.assertIn("testdb", pool.name)

    @patch("pyanalysis.mysql._Connection")
    def test_get_connection_success(self, mock_conn_class):
        mock_conn = MagicMock()
        mock_conn_class.return_value = mock_conn

        pool = Pool(size=3, name=self.pool_name, host="localhost")
        conn = pool.get_connection(timeout=1, retry_num=0)

        self.assertIsNotNone(conn)
        mock_conn.ping.assert_called_once()

    @patch("pyanalysis.mysql._Connection")
    def test_get_connection_timeout(self, mock_conn_class):
        mock_conn = MagicMock()
        mock_conn_class.return_value = mock_conn

        pool = Pool(size=3, name=self.pool_name, host="localhost")

        pool.get_connection(timeout=0)
        pool.get_connection(timeout=0)
        pool.get_connection(timeout=0)

        with self.assertRaises(GetConnectionFromPoolError) as context:
            pool.get_connection(timeout=0, retry_num=0)

        self.assertIn("can't get connection from pool", str(context.exception))

    @patch("pyanalysis.mysql._Connection")
    def test_get_connection_retry(self, mock_conn_class):
        mock_conn = MagicMock()
        mock_conn_class.return_value = mock_conn

        pool = Pool(size=1, name=self.pool_name, host="localhost")

        pool.get_connection(timeout=0)

        original_get = pool._pool.get
        call_count = [0]

        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] <= 2:
                raise queue.Empty()
            return original_get(*args, **kwargs)

        pool._pool.get = Mock(side_effect=side_effect)
        conn = pool.get_connection(timeout=0, retry_num=2)
        self.assertIsNotNone(conn)

    @patch("pyanalysis.mysql._Connection")
    def test_put_connection(self, mock_conn_class):
        mock_conn = MagicMock()
        mock_conn._pool = None
        mock_conn_class.return_value = mock_conn

        pool = Pool(size=3, name=self.pool_name, host="localhost")
        initial_size = pool.size()

        conn = pool.get_connection(timeout=0)
        self.assertEqual(pool.size(), initial_size - 1)

        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        pool.put_connection(conn)
        self.assertEqual(pool.size(), initial_size)
        self.assertEqual(conn._pool, pool)

    @patch("pyanalysis.mysql._Connection")
    def test_put_connection_pool_accepts_extra(self, mock_conn_class):
        mock_conn = MagicMock()
        mock_conn._pool = None
        mock_conn_class.return_value = mock_conn

        pool = Pool(size=3, name=self.pool_name, host="localhost")

        extra_conn = MagicMock()
        mock_cursor = MagicMock()
        extra_conn.cursor.return_value = mock_cursor
        extra_conn._pool = None

        pool.put_connection(extra_conn)
        self.assertEqual(pool.size(), 4)
        self.assertEqual(extra_conn._pool, pool)


class TestConn(unittest.TestCase):
    def setUp(self):
        self.pool_name = "test_conn_db"
        self.mock_pool = MagicMock()
        self.mock_conn = MagicMock()
        self.mock_pool.get_connection.return_value = self.mock_conn
        _pool_registry[self.pool_name] = self.mock_pool

    def tearDown(self):
        if self.pool_name in _pool_registry:
            del _pool_registry[self.pool_name]

    def test_format_sql(self):
        conn = Conn(self.pool_name)
        sql = "SELECT * FROM users WHERE id = ? AND name = ?"
        formatted = conn._format_sql(sql)
        self.assertEqual(formatted, "SELECT * FROM users WHERE id = %s AND name = %s")

    def test_encode_input_decimal(self):
        conn = Conn(self.pool_name)
        row = {"price": decimal.Decimal("10.99"), "name": "test"}
        result = conn._encode_input(row)
        self.assertIsInstance(result["price"], float)
        self.assertEqual(result["price"], 10.99)

    def test_encode_input_datetime(self):
        conn = Conn(self.pool_name)
        dt = datetime.datetime(2023, 1, 1, 12, 30, 45)
        row = {"created_at": dt, "name": "test"}
        result = conn._encode_input(row)
        self.assertEqual(result["created_at"], "2023-01-01 12:30:45")

    def test_query_one_success(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"id": 1, "name": "test"}
        self.mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        conn = Conn(self.pool_name)
        result = conn.query_one("SELECT * FROM users WHERE id = ?", (1,))

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], 1)
        self.assertEqual(result["name"], "test")
        mock_cursor.execute.assert_called_once()

    def test_query_one_empty(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        self.mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        conn = Conn(self.pool_name)
        result = conn.query_one("SELECT * FROM users WHERE id = ?", (999,))

        self.assertIsNone(result)

    def test_query_success(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {"id": 1, "name": "test1"},
            {"id": 2, "name": "test2"},
        ]
        self.mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        conn = Conn(self.pool_name)
        result = conn.query("SELECT * FROM users")

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], 1)
        self.assertEqual(result[1]["id"], 2)

    def test_query_empty(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        self.mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        conn = Conn(self.pool_name)
        result = conn.query("SELECT * FROM users")

        self.assertEqual(len(result), 0)

    def test_query_range(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchmany.side_effect = [
            [{"id": 1}, {"id": 2}],
            [{"id": 3}, {"id": 4}],
            [],
        ]
        self.mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        conn = Conn(self.pool_name)
        results = list(conn.query_range("SELECT * FROM users", size=2))

        self.assertEqual(len(results), 4)
        self.assertEqual([r["id"] for r in results], [1, 2, 3, 4])

    def test_query_range_custom_size(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchmany.side_effect = [[{"id": 1}], [{"id": 2}], []]
        self.mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        conn = Conn(self.pool_name)
        results = list(conn.query_range("SELECT * FROM users", size=1))

        self.assertEqual(len(results), 2)
        mock_cursor.fetchmany.assert_called_with(size=1)

    def test_execute_success(self):
        mock_cursor = MagicMock()
        mock_cursor.execute.return_value = 5
        self.mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        conn = Conn(self.pool_name)
        result = conn.execute("UPDATE users SET name = ?", ("new_name",))

        self.assertEqual(result, 5)
        self.mock_conn.commit.assert_called_once()

    def test_insert_success(self):
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 100
        self.mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        conn = Conn(self.pool_name)
        result = conn.insert("INSERT INTO users (name) VALUES (?)", ("test",))

        self.assertEqual(result, 100)
        self.mock_conn.commit.assert_called_once()

    def test_get_native_conn(self):
        conn = Conn(self.pool_name)
        native = conn.get_native_conn()
        self.assertEqual(native, self.mock_conn)

    def test_close(self):
        conn = Conn(self.pool_name)
        conn.close()
        self.mock_conn.close.assert_called_once()


class TestTrans(unittest.TestCase):
    def setUp(self):
        self.pool_name = "test_trans_db"
        self.mock_pool = MagicMock()
        self.mock_conn = MagicMock()
        self.mock_pool.get_connection.return_value = self.mock_conn
        _pool_registry[self.pool_name] = self.mock_pool

    def tearDown(self):
        if self.pool_name in _pool_registry:
            del _pool_registry[self.pool_name]

    def test_trans_begin_transaction(self):
        trans = Trans(self.pool_name)
        self.assertIsNotNone(trans)
        self.mock_conn.begin.assert_called_once()

    def test_trans_execute_no_commit(self):
        mock_cursor = MagicMock()
        mock_cursor.execute.return_value = 3
        self.mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        trans = Trans(self.pool_name)
        result = trans.execute("UPDATE users SET name = ?", ("new_name",))

        self.assertEqual(result, 3)
        self.mock_conn.commit.assert_not_called()

    def test_trans_insert_no_commit(self):
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 200
        self.mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        trans = Trans(self.pool_name)
        result = trans.insert("INSERT INTO users (name) VALUES (?)", ("test",))

        self.assertEqual(result, 200)
        self.mock_conn.commit.assert_not_called()

    def test_trans_commit(self):
        trans = Trans(self.pool_name)
        trans.commit()
        self.mock_conn.commit.assert_called_once()

    def test_trans_rollback(self):
        trans = Trans(self.pool_name)
        trans.rollback()
        self.mock_conn.rollback.assert_called_once()


class TestPoolRegistry(unittest.TestCase):
    def setUp(self):
        self.pool_name = "test_registry"

    def tearDown(self):
        if self.pool_name in _pool_registry:
            del _pool_registry[self.pool_name]

    @patch("pyanalysis.mysql._Connection")
    def test_add_pool(self, mock_conn_class):
        mock_conn = MagicMock()
        mock_conn_class.return_value = mock_conn

        pool = Pool(size=3, name=self.pool_name, host="localhost")
        add_pool(pool)

        self.assertIn(self.pool_name, _pool_registry)
        self.assertEqual(_pool_registry[self.pool_name], pool)

    def test_add_pool_invalid_object(self):
        with self.assertRaises(RuntimeError) as context:
            add_pool("not a pool")

        self.assertIn("must add a connection pool object", str(context.exception))

    @patch("pyanalysis.mysql._Connection")
    def test_get_pool(self, mock_conn_class):
        mock_conn = MagicMock()
        mock_conn_class.return_value = mock_conn

        pool = Pool(size=3, name=self.pool_name, host="localhost")
        add_pool(pool)

        retrieved = get_pool(self.pool_name)
        self.assertEqual(retrieved, pool)

    def test_get_pool_not_found(self):
        with self.assertRaises(RuntimeError) as context:
            get_pool("nonexistent_pool")

        self.assertIn("can not find the pool", str(context.exception))


class TestNoWarningDecorator(unittest.TestCase):
    @patch("pyanalysis.mysql.warnings")
    def test_no_warning_decorator(self, mock_warnings):
        @mysql_module.no_warning
        def function_with_warning():
            warnings.warn("test warning")
            return "success"

        result = function_with_warning()
        self.assertEqual(result, "success")
        mock_warnings.catch_warnings.assert_called_once()


if __name__ == "__main__":
    unittest.main()
