import unittest

from datetime import datetime
from pyanalysis.moment import moment


class TestMoment(unittest.TestCase):
    def test_switch_timezone(self):
        now = moment.now().to("utc").to("Asia/Shanghai")
        now_utc = moment.utcnow().to("Asia/Shanghai")
        fmt_now = now.format("YYYY-MM-DD HH:mm:ss ZZ")
        fmt_utc = now_utc.format("YYYY-MM-DD HH:mm:ss ZZ")
        if fmt_now != fmt_utc:
            raise RuntimeError()

    def test_from_timestamp(self):
        m = moment.get(1568585483123)
        print(m.format("YYYY-MM-DD HH:mm:ss.SSSSSS ZZ"))

    def test_get_none(self):
        m = moment.get().to("Asia/Shanghai")
        print(m.format("YYYY-MM-DD HH:mm:ss.SSSSSS ZZ"))

    def test_get_datetime(self):
        m = moment.get(datetime(2019, 9, 10), "Asia/Shanghai")
        print(m.format("YYYY-MM-DD HH:mm:ss"))

    def test_get_datetime_fmt(self):
        m = moment.get("2019-09-10 00:00:00", "YYYY-MM-DD HH:mm:ss")
        print(m.format("YYYY-MM-DD HH:mm:ss"))

    def test_get_xxxxxsecond(self):
        m = moment.now()
        second_timestamp = m.second_timestamp
        millisecond = m.millisecond_timestamp
        microsecond = m.microsecond_timestamp

        print("second: " + str(second_timestamp))
        print("millisecond: " + str(millisecond))
        print("microsecond: " + str(microsecond))

    def test_get_floor(self):
        m = moment.now().to("Asia/Shanghai")
        print(m.floor("hour"))

