import unittest

from datetime import tzinfo
from datetime import datetime
from pyanalysis.moment import *


class TestMoment(unittest.TestCase):

    def test_switch_timezone(self):
        now = moment.now().to('utc')
        now_utc = moment.utcnow()
        fmt_now = now.format("YYYY-MM-DD HH:mm:ss ZZ")
        fmt_utc = now_utc.format("YYYY-MM-DD HH:mm:ss ZZ")
        if fmt_now != fmt_utc:
            raise RuntimeError()

    def test_from_timestamp(self):
        m = moment.get(1568585483.123000, 'Asia/Shanghai')
        print(m.format("YYYY-MM-DD HH:mm:ss.SSSSSS ZZ"))

    def test_get(self):
        m = moment.get().to('Asia/Shanghai')
        print(m.format("YYYY-MM-DD HH:mm:ss.SSSSSS ZZ"))

    def test_get_datetime(self):
        m = moment.get(datetime(2019, 9, 10), "Asia/Shanghai")
        print(m.format("YYYY-MM-DD HH:mm:ss"))
