"""
MySQL 模块集成测试

本测试文件使用真实的 MySQL 服务器进行测试，验证各组件在实际环境中的功能正确性。

配置方式（通过环境变量）：
    MYSQL_HOST      - MySQL 服务器地址（默认：localhost）
    MYSQL_PORT      - MySQL 服务器端口（默认：3306）
    MYSQL_USER      - MySQL 用户名（默认：root）
    MYSQL_PASSWORD  - MySQL 密码（默认：空）
    MYSQL_DATABASE  - 测试数据库名称（默认：test_pyanalysis）

运行方式：
    # 设置环境变量后运行
    export MYSQL_HOST=localhost
    export MYSQL_USER=root
    export MYSQL_PASSWORD=your_password
    python3 -m unittest test/mysql_integration.py

    # 或者一行命令
    MYSQL_HOST=localhost MYSQL_USER=root MYSQL_PASSWORD=password python3 -m unittest test/mysql_integration.py

测试覆盖：
- Pool: 连接池的创建、连接获取/归还
- Conn: 数据库连接的查询、执行、插入操作
- Trans: 事务的提交、回滚控制
"""

import os
import unittest
import decimal
import datetime

import pymysql

from pyanalysis.mysql import (
    Pool,
    Conn,
    Trans,
    add_pool,
    get_pool,
)
import pyanalysis.mysql as mysql_module

# 通过模块访问内部的 __pool 注册表（用于测试清理）
_pool_registry = mysql_module.__pool


def get_mysql_config():
    """从环境变量获取 MySQL 配置"""
    return {
        "host": os.environ.get("MYSQL_HOST", "localhost"),
        "port": int(os.environ.get("MYSQL_PORT", "3306")),
        "user": os.environ.get("MYSQL_USER", "root"),
        "password": os.environ.get("MYSQL_PASSWORD", ""),
        "database": os.environ.get("MYSQL_DATABASE", "test_pyanalysis"),
        "charset": "utf8mb4",
    }


def is_mysql_available():
    """检查 MySQL 服务器是否可用"""
    config = get_mysql_config()
    try:
        conn = pymysql.connect(
            host=config["host"],
            port=config["port"],
            user=config["user"],
            password=config["password"],
            charset=config["charset"],
        )
        conn.close()
        return True
    except Exception:
        return False


def setup_test_database():
    """创建测试数据库（如果不存在）"""
    config = get_mysql_config()
    conn = pymysql.connect(
        host=config["host"],
        port=config["port"],
        user=config["user"],
        password=config["password"],
        charset=config["charset"],
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{config['database']}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        conn.commit()
    finally:
        conn.close()


# 如果 MySQL 不可用，跳过所有测试
SKIP_TESTS = not is_mysql_available()
SKIP_REASON = "MySQL server is not available. Set MYSQL_* environment variables."


@unittest.skipIf(SKIP_TESTS, SKIP_REASON)
class TestPoolIntegration(unittest.TestCase):
    """
    连接池 Pool 类的集成测试
    """

    @classmethod
    def setUpClass(cls):
        """测试类开始前：创建测试数据库"""
        setup_test_database()
        cls.config = get_mysql_config()
        cls.pool_name = "test_pool_integration"

    def tearDown(self):
        """每个测试后清理：从全局注册表中移除测试连接池"""
        if self.pool_name in _pool_registry:
            del _pool_registry[self.pool_name]

    def test_pool_creation(self):
        """测试创建连接池：应成功创建指定大小的连接池"""
        pool = Pool(
            size=5,
            name=self.pool_name,
            host=self.config["host"],
            port=self.config["port"],
            user=self.config["user"],
            password=self.config["password"],
            database=self.config["database"],
            charset=self.config["charset"],
        )
        self.assertEqual(pool.size(), 5)
        self.assertEqual(pool.name, self.pool_name)

    def test_get_and_put_connection(self):
        """测试获取和归还连接：连接应能正常获取和归还"""
        pool = Pool(
            size=3,
            name=self.pool_name,
            host=self.config["host"],
            port=self.config["port"],
            user=self.config["user"],
            password=self.config["password"],
            database=self.config["database"],
            charset=self.config["charset"],
        )

        # 获取连接
        conn = pool.get_connection(timeout=5)
        self.assertIsNotNone(conn)
        self.assertEqual(pool.size(), 2)

        # 归还连接
        pool.put_connection(conn)
        self.assertEqual(pool.size(), 3)

    def test_connection_ping(self):
        """测试连接活性检查：获取连接时应自动进行 ping 检查"""
        pool = Pool(
            size=3,
            name=self.pool_name,
            host=self.config["host"],
            port=self.config["port"],
            user=self.config["user"],
            password=self.config["password"],
            database=self.config["database"],
            charset=self.config["charset"],
        )

        conn = pool.get_connection(timeout=5)
        # 连接应该是有效的
        conn.ping(reconnect=True)
        pool.put_connection(conn)

    def test_pool_registry(self):
        """测试连接池注册表：add_pool 和 get_pool 应正常工作"""
        pool = Pool(
            size=3,
            name=self.pool_name,
            host=self.config["host"],
            port=self.config["port"],
            user=self.config["user"],
            password=self.config["password"],
            database=self.config["database"],
            charset=self.config["charset"],
        )

        add_pool(pool)
        retrieved = get_pool(self.pool_name)
        self.assertEqual(retrieved, pool)


@unittest.skipIf(SKIP_TESTS, SKIP_REASON)
class TestConnIntegration(unittest.TestCase):
    """
    数据库连接 Conn 类的集成测试
    """

    @classmethod
    def setUpClass(cls):
        """测试类开始前：创建测试数据库和表"""
        setup_test_database()
        cls.config = get_mysql_config()
        cls.pool_name = "test_conn_integration"

        # 创建连接池
        pool = Pool(
            size=5,
            name=cls.pool_name,
            host=cls.config["host"],
            port=cls.config["port"],
            user=cls.config["user"],
            password=cls.config["password"],
            database=cls.config["database"],
            charset=cls.config["charset"],
        )
        add_pool(pool)

        # 创建测试表
        cls._create_test_table()

    @classmethod
    def _create_test_table(cls):
        """创建测试表"""
        conn = Conn(cls.pool_name)
        try:
            conn.execute("DROP TABLE IF EXISTS test_users")
            conn.execute("""
                CREATE TABLE test_users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100),
                    balance DECIMAL(10, 2) DEFAULT 0.00,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
        finally:
            conn.close()

    @classmethod
    def tearDownClass(cls):
        """测试类结束后：清理测试表和连接池"""
        # 先取出并关闭池中所有连接
        if cls.pool_name in _pool_registry:
            pool = _pool_registry[cls.pool_name]
            while pool.size() > 0:
                try:
                    conn = pool._pool.get_nowait()
                    conn._pool = None
                    pymysql.connections.Connection.close(conn)
                except Exception:
                    break
            del _pool_registry[cls.pool_name]

        # 使用直接连接删除表
        try:
            direct_conn = pymysql.connect(
                host=cls.config["host"],
                port=cls.config["port"],
                user=cls.config["user"],
                password=cls.config["password"],
                database=cls.config["database"],
                charset=cls.config["charset"],
            )
            try:
                with direct_conn.cursor() as cursor:
                    cursor.execute("DROP TABLE IF EXISTS test_users")
                direct_conn.commit()
            finally:
                direct_conn.close()
        except Exception:
            pass

    def setUp(self):
        """每个测试前：清空测试表数据"""
        # 使用直接连接避免连接池中的连接状态问题
        direct_conn = pymysql.connect(
            host=self.config["host"],
            port=self.config["port"],
            user=self.config["user"],
            password=self.config["password"],
            database=self.config["database"],
            charset=self.config["charset"],
        )
        try:
            with direct_conn.cursor() as cursor:
                cursor.execute("TRUNCATE TABLE test_users")
            direct_conn.commit()
        finally:
            direct_conn.close()

    def test_insert_and_query_one(self):
        """测试插入和单条查询：插入后应能查询到数据"""
        conn = Conn(self.pool_name)
        try:
            # 插入数据
            user_id = conn.insert(
                "INSERT INTO test_users (name, email) VALUES (?, ?)",
                ("张三", "zhangsan@example.com"),
            )
            self.assertIsNotNone(user_id)
            self.assertGreater(user_id, 0)

            # 查询数据
            result = conn.query_one(
                "SELECT * FROM test_users WHERE id = ?", (user_id,)
            )
            self.assertIsNotNone(result)
            self.assertEqual(result["name"], "张三")
            self.assertEqual(result["email"], "zhangsan@example.com")
        finally:
            conn.close()

    def test_query_multiple(self):
        """测试批量查询：应返回所有匹配的记录"""
        conn = Conn(self.pool_name)
        try:
            # 插入多条数据
            conn.insert(
                "INSERT INTO test_users (name, email) VALUES (?, ?)",
                ("用户1", "user1@example.com"),
            )
            conn.insert(
                "INSERT INTO test_users (name, email) VALUES (?, ?)",
                ("用户2", "user2@example.com"),
            )
            conn.insert(
                "INSERT INTO test_users (name, email) VALUES (?, ?)",
                ("用户3", "user3@example.com"),
            )

            # 查询所有数据
            results = conn.query("SELECT * FROM test_users ORDER BY id")
            self.assertEqual(len(results), 3)
            self.assertEqual(results[0]["name"], "用户1")
            self.assertEqual(results[1]["name"], "用户2")
            self.assertEqual(results[2]["name"], "用户3")
        finally:
            conn.close()

    def test_query_empty(self):
        """测试空查询结果：无匹配数据时应返回空列表"""
        conn = Conn(self.pool_name)
        try:
            results = conn.query("SELECT * FROM test_users WHERE id = 99999")
            self.assertEqual(len(results), 0)
        finally:
            conn.close()

    def test_query_one_empty(self):
        """测试单条空查询结果：无匹配数据时应返回 None"""
        conn = Conn(self.pool_name)
        try:
            result = conn.query_one("SELECT * FROM test_users WHERE id = 99999")
            self.assertIsNone(result)
        finally:
            conn.close()

    def test_execute_update(self):
        """测试执行更新语句：应返回受影响行数"""
        conn = Conn(self.pool_name)
        try:
            # 插入数据
            conn.insert(
                "INSERT INTO test_users (name, email) VALUES (?, ?)",
                ("测试用户", "test@example.com"),
            )

            # 更新数据
            affected = conn.execute(
                "UPDATE test_users SET name = ? WHERE email = ?",
                ("更新后的用户", "test@example.com"),
            )
            self.assertEqual(affected, 1)

            # 验证更新
            result = conn.query_one(
                "SELECT * FROM test_users WHERE email = ?", ("test@example.com",)
            )
            self.assertEqual(result["name"], "更新后的用户")
        finally:
            conn.close()

    def test_execute_delete(self):
        """测试执行删除语句：应返回受影响行数"""
        conn = Conn(self.pool_name)
        try:
            # 插入数据
            conn.insert(
                "INSERT INTO test_users (name, email) VALUES (?, ?)",
                ("待删除用户", "delete@example.com"),
            )

            # 删除数据
            affected = conn.execute(
                "DELETE FROM test_users WHERE email = ?", ("delete@example.com",)
            )
            self.assertEqual(affected, 1)

            # 验证删除
            result = conn.query_one(
                "SELECT * FROM test_users WHERE email = ?", ("delete@example.com",)
            )
            self.assertIsNone(result)
        finally:
            conn.close()

    def test_query_range(self):
        """测试分批查询：应通过生成器逐批返回所有结果"""
        conn = Conn(self.pool_name)
        try:
            # 插入多条数据
            for i in range(10):
                conn.insert(
                    "INSERT INTO test_users (name, email) VALUES (?, ?)",
                    (f"用户{i}", f"user{i}@example.com"),
                )

            # 分批查询（每批 3 条）
            results = list(
                conn.query_range("SELECT * FROM test_users ORDER BY id", size=3)
            )
            self.assertEqual(len(results), 10)

            # 验证顺序
            for i, result in enumerate(results):
                self.assertEqual(result["name"], f"用户{i}")
        finally:
            conn.close()

    def test_decimal_encoding(self):
        """测试 Decimal 类型编码：Decimal 应正确转换为 float"""
        conn = Conn(self.pool_name)
        try:
            # 插入带 Decimal 的数据
            conn.insert(
                "INSERT INTO test_users (name, balance) VALUES (?, ?)",
                ("余额测试", decimal.Decimal("123.45")),
            )

            # 查询并验证类型转换
            result = conn.query_one(
                "SELECT * FROM test_users WHERE name = ?", ("余额测试",)
            )
            self.assertIsNotNone(result)
            self.assertIsInstance(result["balance"], float)
            self.assertAlmostEqual(result["balance"], 123.45, places=2)
        finally:
            conn.close()

    def test_datetime_encoding(self):
        """测试 datetime 类型编码：datetime 应正确转换为字符串"""
        conn = Conn(self.pool_name)
        try:
            # 插入数据
            user_id = conn.insert(
                "INSERT INTO test_users (name, email) VALUES (?, ?)",
                ("时间测试", "time@example.com"),
            )

            # 查询并验证 datetime 转换
            result = conn.query_one(
                "SELECT * FROM test_users WHERE id = ?", (user_id,)
            )
            self.assertIsNotNone(result)
            # created_at 应被转换为字符串格式
            self.assertIsInstance(result["created_at"], str)
        finally:
            conn.close()


@unittest.skipIf(SKIP_TESTS, SKIP_REASON)
class TestTransIntegration(unittest.TestCase):
    """
    事务 Trans 类的集成测试
    """

    @classmethod
    def setUpClass(cls):
        """测试类开始前：创建测试数据库和表"""
        setup_test_database()
        cls.config = get_mysql_config()
        cls.pool_name = "test_trans_integration"

        # 创建连接池
        pool = Pool(
            size=5,
            name=cls.pool_name,
            host=cls.config["host"],
            port=cls.config["port"],
            user=cls.config["user"],
            password=cls.config["password"],
            database=cls.config["database"],
            charset=cls.config["charset"],
        )
        add_pool(pool)

        # 创建测试表
        cls._create_test_table()

    @classmethod
    def _create_test_table(cls):
        """创建测试表"""
        conn = Conn(cls.pool_name)
        try:
            conn.execute("DROP TABLE IF EXISTS test_accounts")
            conn.execute("""
                CREATE TABLE test_accounts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    balance DECIMAL(10, 2) DEFAULT 0.00
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
        finally:
            conn.close()

    @classmethod
    def tearDownClass(cls):
        """测试类结束后：清理测试表和连接池"""
        # 先取出并关闭池中所有连接
        if cls.pool_name in _pool_registry:
            pool = _pool_registry[cls.pool_name]
            while pool.size() > 0:
                try:
                    conn = pool._pool.get_nowait()
                    conn._pool = None
                    pymysql.connections.Connection.close(conn)
                except Exception:
                    break
            del _pool_registry[cls.pool_name]

        # 使用直接连接删除表
        try:
            direct_conn = pymysql.connect(
                host=cls.config["host"],
                port=cls.config["port"],
                user=cls.config["user"],
                password=cls.config["password"],
                database=cls.config["database"],
                charset=cls.config["charset"],
            )
            try:
                with direct_conn.cursor() as cursor:
                    cursor.execute("DROP TABLE IF EXISTS test_accounts")
                direct_conn.commit()
            finally:
                direct_conn.close()
        except Exception:
            pass

    def setUp(self):
        """每个测试前：清空测试表并插入初始数据"""
        # 使用直接连接避免连接池中的连接状态问题
        direct_conn = pymysql.connect(
            host=self.config["host"],
            port=self.config["port"],
            user=self.config["user"],
            password=self.config["password"],
            database=self.config["database"],
            charset=self.config["charset"],
        )
        try:
            with direct_conn.cursor() as cursor:
                cursor.execute("TRUNCATE TABLE test_accounts")
                cursor.execute(
                    "INSERT INTO test_accounts (name, balance) VALUES (%s, %s)",
                    ("账户A", 1000.00),
                )
                cursor.execute(
                    "INSERT INTO test_accounts (name, balance) VALUES (%s, %s)",
                    ("账户B", 500.00),
                )
            direct_conn.commit()
        finally:
            direct_conn.close()

    def test_transaction_commit(self):
        """测试事务提交：提交后数据应持久化"""
        trans = Trans(self.pool_name)
        try:
            # 模拟转账：A -> B 转 100
            trans.execute(
                "UPDATE test_accounts SET balance = balance - ? WHERE name = ?",
                (100, "账户A"),
            )
            trans.execute(
                "UPDATE test_accounts SET balance = balance + ? WHERE name = ?",
                (100, "账户B"),
            )
            trans.commit()
        finally:
            trans.close()

        # 验证数据已持久化
        conn = Conn(self.pool_name)
        try:
            account_a = conn.query_one(
                "SELECT * FROM test_accounts WHERE name = ?", ("账户A",)
            )
            account_b = conn.query_one(
                "SELECT * FROM test_accounts WHERE name = ?", ("账户B",)
            )

            self.assertAlmostEqual(account_a["balance"], 900.00, places=2)
            self.assertAlmostEqual(account_b["balance"], 600.00, places=2)
        finally:
            conn.close()

    def test_transaction_rollback(self):
        """测试事务回滚：回滚后数据应恢复原状"""
        trans = Trans(self.pool_name)
        try:
            # 模拟转账：A -> B 转 100
            trans.execute(
                "UPDATE test_accounts SET balance = balance - ? WHERE name = ?",
                (100, "账户A"),
            )
            trans.execute(
                "UPDATE test_accounts SET balance = balance + ? WHERE name = ?",
                (100, "账户B"),
            )
            # 回滚事务
            trans.rollback()
        finally:
            trans.close()

        # 验证数据未改变
        conn = Conn(self.pool_name)
        try:
            account_a = conn.query_one(
                "SELECT * FROM test_accounts WHERE name = ?", ("账户A",)
            )
            account_b = conn.query_one(
                "SELECT * FROM test_accounts WHERE name = ?", ("账户B",)
            )

            self.assertAlmostEqual(account_a["balance"], 1000.00, places=2)
            self.assertAlmostEqual(account_b["balance"], 500.00, places=2)
        finally:
            conn.close()

    def test_transaction_insert(self):
        """测试事务中插入：提交后应能查询到新数据"""
        trans = Trans(self.pool_name)
        try:
            new_id = trans.insert(
                "INSERT INTO test_accounts (name, balance) VALUES (?, ?)",
                ("账户C", decimal.Decimal("200.00")),
            )
            self.assertIsNotNone(new_id)
            self.assertGreater(new_id, 0)
            trans.commit()
        finally:
            trans.close()

        # 验证数据已插入
        conn = Conn(self.pool_name)
        try:
            account_c = conn.query_one(
                "SELECT * FROM test_accounts WHERE name = ?", ("账户C",)
            )
            self.assertIsNotNone(account_c)
            self.assertAlmostEqual(account_c["balance"], 200.00, places=2)
        finally:
            conn.close()

    def test_transaction_insert_rollback(self):
        """测试事务中插入后回滚：回滚后新数据应不存在"""
        trans = Trans(self.pool_name)
        try:
            trans.insert(
                "INSERT INTO test_accounts (name, balance) VALUES (?, ?)",
                ("账户D", decimal.Decimal("300.00")),
            )
            trans.rollback()
        finally:
            trans.close()

        # 验证数据未插入
        conn = Conn(self.pool_name)
        try:
            account_d = conn.query_one(
                "SELECT * FROM test_accounts WHERE name = ?", ("账户D",)
            )
            self.assertIsNone(account_d)
        finally:
            conn.close()


@unittest.skipIf(SKIP_TESTS, SKIP_REASON)
class TestConcurrentAccess(unittest.TestCase):
    """
    并发访问测试
    """

    @classmethod
    def setUpClass(cls):
        """测试类开始前：创建测试数据库和表"""
        setup_test_database()
        cls.config = get_mysql_config()
        cls.pool_name = "test_concurrent_integration"

        # 创建连接池
        pool = Pool(
            size=10,
            name=cls.pool_name,
            host=cls.config["host"],
            port=cls.config["port"],
            user=cls.config["user"],
            password=cls.config["password"],
            database=cls.config["database"],
            charset=cls.config["charset"],
        )
        add_pool(pool)

        # 创建测试表
        cls._create_test_table()

    @classmethod
    def _create_test_table(cls):
        """创建测试表"""
        conn = Conn(cls.pool_name)
        try:
            conn.execute("DROP TABLE IF EXISTS test_counter")
            conn.execute("""
                CREATE TABLE test_counter (
                    id INT PRIMARY KEY,
                    count INT DEFAULT 0
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            conn.insert("INSERT INTO test_counter (id, count) VALUES (?, ?)", (1, 0))
        finally:
            conn.close()

    @classmethod
    def tearDownClass(cls):
        """测试类结束后：清理测试表和连接池"""
        # 先取出并关闭池中所有连接
        if cls.pool_name in _pool_registry:
            pool = _pool_registry[cls.pool_name]
            while pool.size() > 0:
                try:
                    conn = pool._pool.get_nowait()
                    conn._pool = None  # 防止 close 时放回池中
                    pymysql.connections.Connection.close(conn)
                except Exception:
                    break
            del _pool_registry[cls.pool_name]

        # 使用直接连接删除表
        try:
            direct_conn = pymysql.connect(
                host=cls.config["host"],
                port=cls.config["port"],
                user=cls.config["user"],
                password=cls.config["password"],
                database=cls.config["database"],
                charset=cls.config["charset"],
            )
            try:
                with direct_conn.cursor() as cursor:
                    cursor.execute("DROP TABLE IF EXISTS test_counter")
                direct_conn.commit()
            finally:
                direct_conn.close()
        except Exception:
            pass

    def test_multiple_connections(self):
        """测试多个连接同时操作：应能正确处理并发访问"""
        import threading

        errors = []
        results = []

        def increment_counter():
            try:
                conn = Conn(self.pool_name)
                try:
                    conn.execute(
                        "UPDATE test_counter SET count = count + 1 WHERE id = ?", (1,)
                    )
                    result = conn.query_one(
                        "SELECT count FROM test_counter WHERE id = ?", (1,)
                    )
                    results.append(result["count"])
                finally:
                    conn.close()
            except Exception as e:
                errors.append(str(e))

        # 创建多个线程同时操作
        threads = []
        for _ in range(5):
            t = threading.Thread(target=increment_counter)
            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # 验证无错误发生
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")

        # 验证最终计数
        conn = Conn(self.pool_name)
        try:
            result = conn.query_one(
                "SELECT count FROM test_counter WHERE id = ?", (1,)
            )
            self.assertEqual(result["count"], 5)
        finally:
            conn.close()


if __name__ == "__main__":
    if SKIP_TESTS:
        print("=" * 60)
        print("WARNING: MySQL server is not available!")
        print("Please set the following environment variables:")
        print("  MYSQL_HOST     - MySQL server host (default: localhost)")
        print("  MYSQL_PORT     - MySQL server port (default: 3306)")
        print("  MYSQL_USER     - MySQL username (default: root)")
        print("  MYSQL_PASSWORD - MySQL password (default: empty)")
        print("  MYSQL_DATABASE - Test database name (default: test_pyanalysis)")
        print("=" * 60)
        print()

    unittest.main()
