"""
MySQL 模块单元测试

本测试文件使用 Mock 技术对 pyanalysis.mysql 模块进行单元测试，
无需连接真实数据库即可验证各组件的功能正确性。

测试覆盖：
- Pool: 连接池的创建、连接获取/归还、超时重试机制
- Conn: 数据库连接的查询、执行、插入操作
- Trans: 事务的开始、提交、回滚控制
- 连接池注册表: add_pool/get_pool 全局函数
- no_warning 装饰器
"""

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

# 通过模块访问内部的 __pool 注册表（用于测试清理）
_pool_registry = mysql_module.__pool


class TestPool(unittest.TestCase):
    """
    连接池 Pool 类的单元测试

    测试连接池的核心功能：
    - 连接池大小限制（最大100，最小3）
    - 连接池名称生成规则
    - 从池中获取连接（包括超时和重试机制）
    - 将连接归还到池中
    """

    def setUp(self):
        """测试前准备：设置测试用的连接池名称"""
        self.pool_name = "test_pool"

    def tearDown(self):
        """测试后清理：从全局注册表中移除测试连接池"""
        if self.pool_name in _pool_registry:
            del _pool_registry[self.pool_name]

    @patch("pyanalysis.mysql._Connection")
    def test_pool_size_limit_max(self, mock_conn_class):
        """测试连接池大小上限：设置超过100时应被限制为100"""
        pool = Pool(size=150, name=self.pool_name, host="localhost")
        self.assertEqual(pool.size(), Pool._MAX_SIZE_LIMIT)

    @patch("pyanalysis.mysql._Connection")
    def test_pool_size_limit_min(self, mock_conn_class):
        """测试连接池大小下限：设置小于3时应被限制为3"""
        pool = Pool(size=1, name=self.pool_name, host="localhost")
        self.assertEqual(pool.size(), Pool._MIN_SIZE_LIMIT)

    @patch("pyanalysis.mysql._Connection")
    def test_pool_normal_size(self, mock_conn_class):
        """测试正常范围内的连接池大小：应保持设置值不变"""
        pool = Pool(size=5, name=self.pool_name, host="localhost")
        self.assertEqual(pool.size(), 5)

    @patch("pyanalysis.mysql._Connection")
    def test_pool_name_generation(self, mock_conn_class):
        """测试连接池名称自动生成：未指定名称时应根据host-port-user-database生成"""
        pool = Pool(host="localhost", port=3306, user="test", database="testdb")
        self.assertIn("localhost", pool.name)
        self.assertIn("3306", pool.name)
        self.assertIn("test", pool.name)
        self.assertIn("testdb", pool.name)

    @patch("pyanalysis.mysql._Connection")
    def test_get_connection_success(self, mock_conn_class):
        """测试成功获取连接：应返回连接对象并调用ping检查连接有效性"""
        mock_conn = MagicMock()
        mock_conn_class.return_value = mock_conn

        pool = Pool(size=3, name=self.pool_name, host="localhost")
        conn = pool.get_connection(timeout=1, retry_num=0)

        self.assertIsNotNone(conn)
        mock_conn.ping.assert_called_once()

    @patch("pyanalysis.mysql._Connection")
    def test_get_connection_timeout(self, mock_conn_class):
        """测试获取连接超时：池中无可用连接且不重试时应抛出异常"""
        mock_conn = MagicMock()
        mock_conn_class.return_value = mock_conn

        pool = Pool(size=3, name=self.pool_name, host="localhost")

        # 取走池中所有连接
        pool.get_connection(timeout=0)
        pool.get_connection(timeout=0)
        pool.get_connection(timeout=0)

        # 再次获取应抛出异常
        with self.assertRaises(GetConnectionFromPoolError) as context:
            pool.get_connection(timeout=0, retry_num=0)

        self.assertIn("can't get connection from pool", str(context.exception))

    @patch("pyanalysis.mysql._Connection")
    def test_get_connection_retry(self, mock_conn_class):
        """测试获取连接重试机制：前两次失败后第三次成功应返回连接"""
        mock_conn = MagicMock()
        mock_conn_class.return_value = mock_conn

        pool = Pool(size=1, name=self.pool_name, host="localhost")

        # 取走唯一的连接
        pool.get_connection(timeout=0)

        # 模拟前两次获取失败，第三次成功
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
        """测试归还连接：取出后归还，池大小应恢复且连接的_pool属性应指向池"""
        mock_conn = MagicMock()
        mock_conn._pool = None
        mock_conn_class.return_value = mock_conn

        pool = Pool(size=3, name=self.pool_name, host="localhost")
        initial_size = pool.size()

        # 取出一个连接，池大小减1
        conn = pool.get_connection(timeout=0)
        self.assertEqual(pool.size(), initial_size - 1)

        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        # 归还连接，池大小恢复
        pool.put_connection(conn)
        self.assertEqual(pool.size(), initial_size)
        self.assertEqual(conn._pool, pool)

    @patch("pyanalysis.mysql._Connection")
    def test_put_connection_pool_accepts_extra(self, mock_conn_class):
        """测试归还额外连接：池可以接受超过初始大小的连接（边界情况）"""
        mock_conn = MagicMock()
        mock_conn._pool = None
        mock_conn_class.return_value = mock_conn

        pool = Pool(size=3, name=self.pool_name, host="localhost")

        # 创建一个不属于池的额外连接
        extra_conn = MagicMock()
        mock_cursor = MagicMock()
        extra_conn.cursor.return_value = mock_cursor
        extra_conn._pool = None

        # 归还额外连接，池大小增加
        pool.put_connection(extra_conn)
        self.assertEqual(pool.size(), 4)
        self.assertEqual(extra_conn._pool, pool)


class TestConn(unittest.TestCase):
    """
    数据库连接 Conn 类的单元测试

    测试 Conn 类的核心功能：
    - SQL 格式化（? 占位符转换为 %s）
    - 输入数据编码（Decimal 转 float，datetime 转字符串）
    - 单条查询 query_one
    - 批量查询 query
    - 分批查询 query_range（生成器方式）
    - 执行语句 execute
    - 插入语句 insert
    - 获取原生连接和关闭连接
    """

    def setUp(self):
        """测试前准备：创建 mock 连接池并注册到全局注册表"""
        self.pool_name = "test_conn_db"
        self.mock_pool = MagicMock()
        self.mock_conn = MagicMock()
        self.mock_pool.get_connection.return_value = self.mock_conn
        _pool_registry[self.pool_name] = self.mock_pool

    def tearDown(self):
        """测试后清理：从全局注册表中移除测试连接池"""
        if self.pool_name in _pool_registry:
            del _pool_registry[self.pool_name]

    def test_format_sql(self):
        """测试 SQL 格式化：? 占位符应转换为 pymysql 使用的 %s"""
        conn = Conn(self.pool_name)
        sql = "SELECT * FROM users WHERE id = ? AND name = ?"
        formatted = conn._format_sql(sql)
        self.assertEqual(formatted, "SELECT * FROM users WHERE id = %s AND name = %s")

    def test_encode_input_decimal(self):
        """测试输入编码 - Decimal 类型：应转换为 float"""
        conn = Conn(self.pool_name)
        row = {"price": decimal.Decimal("10.99"), "name": "test"}
        result = conn._encode_input(row)
        self.assertIsInstance(result["price"], float)
        self.assertEqual(result["price"], 10.99)

    def test_encode_input_datetime(self):
        """测试输入编码 - datetime 类型：应转换为格式化字符串"""
        conn = Conn(self.pool_name)
        dt = datetime.datetime(2023, 1, 1, 12, 30, 45)
        row = {"created_at": dt, "name": "test"}
        result = conn._encode_input(row)
        self.assertEqual(result["created_at"], "2023-01-01 12:30:45")

    def test_query_one_success(self):
        """测试单条查询成功：应返回包含数据的字典"""
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
        """测试单条查询无结果：应返回 None"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        self.mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        conn = Conn(self.pool_name)
        result = conn.query_one("SELECT * FROM users WHERE id = ?", (999,))

        self.assertIsNone(result)

    def test_query_success(self):
        """测试批量查询成功：应返回包含多条记录的列表"""
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
        """测试批量查询无结果：应返回空列表"""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        self.mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        conn = Conn(self.pool_name)
        result = conn.query("SELECT * FROM users")

        self.assertEqual(len(result), 0)

    def test_query_range(self):
        """测试分批查询：应通过生成器逐批返回所有结果"""
        mock_cursor = MagicMock()
        # 模拟分三批返回数据：2条、2条、空（结束）
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
        """测试分批查询自定义批次大小：fetchmany 应使用指定的 size 参数"""
        mock_cursor = MagicMock()
        mock_cursor.fetchmany.side_effect = [[{"id": 1}], [{"id": 2}], []]
        self.mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        conn = Conn(self.pool_name)
        results = list(conn.query_range("SELECT * FROM users", size=1))

        self.assertEqual(len(results), 2)
        mock_cursor.fetchmany.assert_called_with(size=1)

    def test_execute_success(self):
        """测试执行语句成功：应返回受影响行数并自动提交事务"""
        mock_cursor = MagicMock()
        mock_cursor.execute.return_value = 5
        self.mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        conn = Conn(self.pool_name)
        result = conn.execute("UPDATE users SET name = ?", ("new_name",))

        self.assertEqual(result, 5)
        self.mock_conn.commit.assert_called_once()

    def test_insert_success(self):
        """测试插入语句成功：应返回新插入行的 ID 并自动提交事务"""
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 100
        self.mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        conn = Conn(self.pool_name)
        result = conn.insert("INSERT INTO users (name) VALUES (?)", ("test",))

        self.assertEqual(result, 100)
        self.mock_conn.commit.assert_called_once()

    def test_get_native_conn(self):
        """测试获取原生连接：应返回底层的 pymysql 连接对象"""
        conn = Conn(self.pool_name)
        native = conn.get_native_conn()
        self.assertEqual(native, self.mock_conn)

    def test_close(self):
        """测试关闭连接：应调用底层连接的 close 方法"""
        conn = Conn(self.pool_name)
        conn.close()
        self.mock_conn.close.assert_called_once()


class TestTrans(unittest.TestCase):
    """
    事务 Trans 类的单元测试

    测试 Trans 类的核心功能：
    - 创建事务时自动开启事务（调用 begin）
    - execute/insert 不自动提交（与 Conn 不同）
    - 手动提交 commit
    - 手动回滚 rollback
    """

    def setUp(self):
        """测试前准备：创建 mock 连接池并注册到全局注册表"""
        self.pool_name = "test_trans_db"
        self.mock_pool = MagicMock()
        self.mock_conn = MagicMock()
        self.mock_pool.get_connection.return_value = self.mock_conn
        _pool_registry[self.pool_name] = self.mock_pool

    def tearDown(self):
        """测试后清理：从全局注册表中移除测试连接池"""
        if self.pool_name in _pool_registry:
            del _pool_registry[self.pool_name]

    def test_trans_begin_transaction(self):
        """测试事务初始化：创建 Trans 对象时应自动调用 begin 开启事务"""
        trans = Trans(self.pool_name)
        self.assertIsNotNone(trans)
        self.mock_conn.begin.assert_called_once()

    def test_trans_execute_no_commit(self):
        """测试事务中执行语句：应返回受影响行数但不自动提交"""
        mock_cursor = MagicMock()
        mock_cursor.execute.return_value = 3
        self.mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        trans = Trans(self.pool_name)
        result = trans.execute("UPDATE users SET name = ?", ("new_name",))

        self.assertEqual(result, 3)
        # 关键断言：事务中不应自动提交
        self.mock_conn.commit.assert_not_called()

    def test_trans_insert_no_commit(self):
        """测试事务中插入语句：应返回新行 ID 但不自动提交"""
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 200
        self.mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        trans = Trans(self.pool_name)
        result = trans.insert("INSERT INTO users (name) VALUES (?)", ("test",))

        self.assertEqual(result, 200)
        # 关键断言：事务中不应自动提交
        self.mock_conn.commit.assert_not_called()

    def test_trans_commit(self):
        """测试手动提交事务：调用 commit 应提交底层连接的事务"""
        trans = Trans(self.pool_name)
        trans.commit()
        self.mock_conn.commit.assert_called_once()

    def test_trans_rollback(self):
        """测试手动回滚事务：调用 rollback 应回滚底层连接的事务"""
        trans = Trans(self.pool_name)
        trans.rollback()
        self.mock_conn.rollback.assert_called_once()


class TestPoolRegistry(unittest.TestCase):
    """
    连接池全局注册表的单元测试

    测试 add_pool 和 get_pool 全局函数：
    - add_pool: 将连接池注册到全局注册表
    - add_pool: 传入非 Pool 对象时应抛出异常
    - get_pool: 根据名称获取已注册的连接池
    - get_pool: 获取不存在的连接池时应抛出异常
    """

    def setUp(self):
        """测试前准备：设置测试用的连接池名称"""
        self.pool_name = "test_registry"

    def tearDown(self):
        """测试后清理：从全局注册表中移除测试连接池"""
        if self.pool_name in _pool_registry:
            del _pool_registry[self.pool_name]

    @patch("pyanalysis.mysql._Connection")
    def test_add_pool(self, mock_conn_class):
        """测试添加连接池：应成功注册到全局注册表"""
        mock_conn = MagicMock()
        mock_conn_class.return_value = mock_conn

        pool = Pool(size=3, name=self.pool_name, host="localhost")
        add_pool(pool)

        self.assertIn(self.pool_name, _pool_registry)
        self.assertEqual(_pool_registry[self.pool_name], pool)

    def test_add_pool_invalid_object(self):
        """测试添加非法对象：传入非 Pool 对象应抛出 RuntimeError"""
        with self.assertRaises(RuntimeError) as context:
            add_pool("not a pool")

        self.assertIn("must add a connection pool object", str(context.exception))

    @patch("pyanalysis.mysql._Connection")
    def test_get_pool(self, mock_conn_class):
        """测试获取连接池：应返回之前注册的连接池对象"""
        mock_conn = MagicMock()
        mock_conn_class.return_value = mock_conn

        pool = Pool(size=3, name=self.pool_name, host="localhost")
        add_pool(pool)

        retrieved = get_pool(self.pool_name)
        self.assertEqual(retrieved, pool)

    def test_get_pool_not_found(self):
        """测试获取不存在的连接池：应抛出 RuntimeError"""
        with self.assertRaises(RuntimeError) as context:
            get_pool("nonexistent_pool")

        self.assertIn("can not find the pool", str(context.exception))


class TestNoWarningDecorator(unittest.TestCase):
    """
    no_warning 装饰器的单元测试

    测试装饰器功能：
    - 被装饰的函数执行时应抑制警告信息
    - 函数返回值应正常传递
    """

    @patch("pyanalysis.mysql.warnings")
    def test_no_warning_decorator(self, mock_warnings):
        """测试 no_warning 装饰器：应调用 catch_warnings 上下文管理器抑制警告"""
        @mysql_module.no_warning
        def function_with_warning():
            warnings.warn("test warning")
            return "success"

        result = function_with_warning()
        self.assertEqual(result, "success")
        mock_warnings.catch_warnings.assert_called_once()


if __name__ == "__main__":
    unittest.main()
