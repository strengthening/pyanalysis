import os
import pymysql
import warnings
import queue
import logging
import threading
import datetime
import decimal

from pymysql.cursors import SSDictCursor

__all__ = ["Pool", "Conn", "Trans"]
__pool = {}

# set the logger to show the debug or online log
warnings.filterwarnings("error", category=pymysql.err.Warning)
logger = logging.getLogger(__name__)


# logger.addHandler(logging.NullHandler)


def add_pool(pool):
    if not isinstance(pool, Pool):
        raise RuntimeError("you must add a connection pool object! ")
    __pool[pool.name] = pool


def get_pool(pool_name):
    if not (pool_name in __pool):
        raise RuntimeError("can not find the pool named {}. ".format(pool_name))
    return __pool[pool_name]


def no_warning(func):
    def wrapper(*args, **kw):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return func(*args, **kw)

    return wrapper


class _Connection(pymysql.connections.Connection):
    """
    Return a connection object with or without connection_pool feature.
    This is all the same with pymysql.connections.Connection instance except that with connection_pool feature:
        the __exit__() method additionally put the connection back to it's pool
    """
    _pool = None
    _reusable_exception = (
        pymysql.err.ProgrammingError,
        pymysql.err.IntegrityError,
        pymysql.err.NotSupportedError,
    )

    def __init__(self, *args, **kwargs):
        pymysql.connections.Connection.__init__(self, *args, **kwargs)
        self.args = args
        self.kwargs = kwargs
        self._last_use_datetime = datetime.datetime.now()

    def __exit__(self, exc, value, traceback):
        """
        Overwrite the __exit__() method of pymysql.connections.Connection
        Base action: on successful exit, commit. On exception, rollback
        With pool additional action: put connection back to pool
        """
        pymysql.connections.Connection.__exit__(self, exc, value, traceback)
        if self._pool:
            if not exc or exc in self._reusable_exception:
                """reusable connection. """
                self._pool.put_connection(self)
            else:
                """no reusable connection, close it and create a new one then put it to the pool. """
                self._pool.put_connection(self._recreate(*self.args, **self.kwargs))
                self._pool = None
                try:
                    self.close()
                    logger.warning("close not reusable connection from pool(%s) caused by %s", self._pool.name, value)
                except Exception:
                    pass

    def _recreate(self, *args, **kwargs):
        conn = _Connection(*args, **kwargs)
        logger.debug("create new connection due to pool(%s) lacking", self._pool.name)
        return conn

    # if the connection idle too long, ping with reconnect the connection
    def ping(self, reconnect=True):
        expire_datetime = self._last_use_datetime + datetime.timedelta(days=1)
        now = datetime.datetime.now()
        if now > expire_datetime:
            self._last_use_datetime = now
            super().ping(reconnect=True)

    def close(self):
        """
        Overwrite the close() method of pymysql.connections.Connection
        With pool, put connection back to pool;
        Without pool, send the quit message and close the socket
        """
        if self._pool:
            self._pool.put_connection(self)
        else:
            pymysql.connections.Connection.close(self)


class Pool:
    """
    Return connection_pool object, which has method can get connection from a pool with timeout and retry feature;
    put a reusable connection back to the pool, etc; also we can create different instance of this class that represent
    different pool of different DB Server or different user
    """
    _MAX_SIZE_LIMIT = 100
    _MIN_SIZE_LIMIT = 3
    _THREAD_LOCAL = threading.local()
    _THREAD_LOCAL.retry_counter = 0  # a counter used for debug get_connection() method

    def __init__(self, size=5, name=None, *args, **kwargs):
        if size > self._MAX_SIZE_LIMIT:
            size = self._MAX_SIZE_LIMIT
            logger.warning(
                "can not set the pool size to %d, the max pool size is %d.",
                size,
                self._MAX_SIZE_LIMIT,
            )

        if size < self._MIN_SIZE_LIMIT:
            size = self._MIN_SIZE_LIMIT
            logger.warning(
                "The pool size is too small. the min pool size is %d",
                self._MIN_SIZE_LIMIT,
            )
        self._pool = queue.Queue(self._MAX_SIZE_LIMIT)
        self.name = name if name else '-'.join(
            [kwargs.get('host', 'localhost'), str(kwargs.get('port', 3306)),
             kwargs.get('user', ''), kwargs.get('database', '')])

        for _ in range(size):
            conn = _Connection(*args, **kwargs)
            conn._pool = self
            self._pool.put(conn)

    def get_connection(self, timeout=1, retry_num=2):
        """
        timeout: timeout of get a connection from pool, should be a int(0 means return or raise immediately)
        retry_num: how many times will retry to get a connection
        """
        try:
            conn = self._pool.get(timeout=timeout) if timeout > 0 else self._pool.get_nowait()
            conn.ping()
            logger.debug("get connection from pool(%s)", self.name)
            return conn
        except queue.Empty:
            if retry_num > 0:
                self._THREAD_LOCAL.retry_counter += 1
                logger.debug(
                    "retry get connection from pool(%s), the %d times",
                    self.name,
                    self._THREAD_LOCAL.retry_counter,
                )
                retry_num -= 1
                return self.get_connection(timeout, retry_num)
            else:
                total_times = self._THREAD_LOCAL.retry_counter + 1
                self._THREAD_LOCAL.retry_counter = 0
                raise GetConnectionFromPoolError(
                    "can't get connection from pool({}) within {}*{} second(s)".format(
                        self.name,
                        timeout,
                        total_times,
                    )
                )

    def put_connection(self, conn):
        if not conn._pool:
            conn._pool = self
        conn.cursor().close()
        try:
            self._pool.put_nowait(conn)
            logger.debug("put connection back to pool(%s)", self.name)
        except queue.Full:
            logger.warning("put connection to pool(%s) error, pool is full, size:%d", self.name, self.size())
        # except Exception as e:
        #     raise e

    def size(self):
        return self._pool.qsize()


class Conn(object):
    def __init__(self, db_name):
        self._conn = get_pool(db_name).get_connection()

    @staticmethod
    def _encode_input(row):
        for key in row:
            value = row[key]
            if isinstance(value, decimal.Decimal):
                row[key] = float(value)
                continue
            if isinstance(value, datetime.datetime):
                row[key] = value.strftime("%Y-%m-%d %H:%M:%S")
                continue
        return row

    @staticmethod
    def _format_sql(sql):
        return sql.replace("?", "%s")

    @no_warning
    def query_one(self, sql=None, args=()):
        result = None
        # use the SSDictCursor, cause it's no need to buffer here.
        with self._conn.cursor(cursor=SSDictCursor) as cursor:
            cursor.execute(self._format_sql(sql), args)
            if logger.level <= logging.DEBUG:
                logger.info(cursor.mogrify(self._format_sql(sql), args))

            row = cursor.fetchone()
            if row:
                result = self._encode_input(row)
        return result

    @no_warning
    def query(self, sql=None, args=()):
        result = []

        with self._conn.cursor() as cursor:
            cursor.execute(self._format_sql(sql), args)
            if logger.level <= logging.DEBUG:
                logger.info(cursor.mogrify(self._format_sql(sql), args))

            rows = cursor.fetchall()
            if rows:
                result = [self._encode_input(row) for row in rows]
        return result

    @no_warning
    def query_range(self, sql=None, args=(), size=100):

        # use the SSDictCursor, cause it's no need to buffer here.
        with self._conn.cursor(cursor=SSDictCursor) as cursor:
            cursor.execute(self._format_sql(sql), args)
            if logger.level <= logging.DEBUG:
                logger.info(cursor.mogrify(self._format_sql(sql), args))

            while True:
                rows = cursor.fetchmany(size=size)
                if not rows:
                    break

                for row in rows:
                    yield self._encode_input(row)
                if len(rows) < size:
                    break

    @no_warning
    def execute(self, sql=None, args=()):
        result = -1

        with self._conn.cursor() as cursor:
            if logger.level <= logging.DEBUG:
                logger.info(cursor.mogrify(self._format_sql(sql), args))

            result = cursor.execute(self._format_sql(sql), args)
            self._conn.commit()
        return result

    @no_warning
    def insert(self, sql=None, args=()):
        result = -1

        with self._conn.cursor() as cursor:
            if logger.level <= logging.DEBUG:
                logger.info(cursor.mogrify(self._format_sql(sql), args))

            cursor.execute(self._format_sql(sql), args)
            result = cursor.lastrowid
            self._conn.commit()
        return result

    def get_native_conn(self):
        return self._conn

    # 手动关闭链接
    def close(self):
        self.__close()

    def __del__(self):
        # 析构并不是立刻进行
        self.__close()

    def __close(self):
        if os and os.getpid() and self._conn:
            self._conn.close()
            self._conn = None


class Trans(Conn):
    def __init__(self, db_name):
        super().__init__(db_name)
        self._conn.begin()

    # tran 将 commit 和 rollback的机会交给调用方
    @no_warning
    def execute(self, sql=None, args=()):
        result = -1
        if logger.level <= logging.DEBUG:
            logger.info(self._conn.mogrify(self._format_sql(sql), args))

        try:
            with self._conn.cursor() as cursor:
                result = cursor.execute(self._format_sql(sql), args)
        except Exception as e:
            print(e)
        finally:
            return result

    @no_warning
    def insert(self, sql=None, args=()):
        result = -1
        if logger.level <= logging.DEBUG:
            logger.info(self._conn.mogrify(self._format_sql(sql), args))

        with self._conn.cursor() as cursor:
            cursor.execute(self._format_sql(sql), args)
            result = cursor.lastrowid
        return result

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()


class GetConnectionFromPoolError(Exception):
    """Exception related can't get connection from pool within timeout seconds."""
