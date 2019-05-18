import os
import warnings
import decimal
import datetime

from pyanalysis.database import mysql_pool

mysql_pool.logger.setLevel("ERROR")

__all__ = ["Conn", "Trans"]

__pool = {}


def add(pool):
    __pool[pool.name] = pool


def get(pool_name):
    return __pool[pool_name]


def no_warning(func):
    def wrapper(*args, **kw):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return func(*args, **kw)

    return wrapper


class Conn(object):
    def __init__(self, db_name):
        self._conn = get[db_name].get_connection()

    @no_warning
    def query_one(self, sql=None, args=None):
        result = None
        with self._conn.cursor() as cursor:
            cursor.execute(sql, args)
            row = cursor.fetchone()
            if row:
                result = dict(zip([desc[0] for desc in cursor.description], self._encode_row(row)))
        return result

    @no_warning
    def query(self, sql=None, args=None):
        result = []
        with self._conn.cursor() as cursor:
            cursor.execute(sql, args)
            rows = cursor.fetchall()
            if rows:
                columns = [desc[0] for desc in cursor.description]
                result = [dict(zip(columns, self._encode_row(row))) for row in rows]
        return result

    @staticmethod
    def _encode_row(row):
        encoded_row = []
        for i in range(len(row)):
            if isinstance(row[i], decimal.Decimal):
                encoded_row.append(float(row[i]))
            elif isinstance(row[i], datetime.datetime):
                encoded_row.append(row[i].strftime("%Y-%m-%d %H:%M:%S"))
            else:
                encoded_row.append(row[i])
        return encoded_row

    @no_warning
    def execute(self, sql=None, args=None):
        result = -1
        with self._conn.cursor() as cursor:
            result = cursor.execute(sql, args)
            self._conn.commit()
        return result

    @no_warning
    def insert(self, sql=None, args=None):
        result = -1
        with self._conn.cursor() as cursor:
            cursor.execute(sql, args)
            result = cursor.lastrowid
            self._conn.commit()
        return result

    def __del__(self):
        # 析构并不是立刻进行
        self._conn.close()


class Trans(Conn):
    def __init__(self, db_name):
        super().__init__(db_name)
        self._conn.begin()

    # tran 将 commit 和 rollback的机会交给调用方
    @no_warning
    def execute(self, sql=None, args=None):
        result = -1
        try:
            with self._conn.cursor() as cursor:
                result = cursor.execute(sql, args)
        except Exception as e:
            print(e)
        finally:
            return result

    @no_warning
    def insert(self, sql=None, args=None):
        result = -1
        with self._conn.cursor() as cursor:
            cursor.execute(sql, args)
            result = cursor.lastrowid
        return result

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()
