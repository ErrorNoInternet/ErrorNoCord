import unittest

import utils
import youtubedl


class TestFormatDuration(unittest.TestCase):
    def test_youtubedl(self):
        def f(s):
            return youtubedl.format_duration(s)

        self.assertEqual(f(0), "00:00")
        self.assertEqual(f(0.5), "00:00")
        self.assertEqual(f(60.5), "01:00")
        self.assertEqual(f(1), "00:01")
        self.assertEqual(f(60), "01:00")
        self.assertEqual(f(60 + 30), "01:30")
        self.assertEqual(f(60 * 60), "01:00:00")
        self.assertEqual(f(60 * 60 + 30), "01:00:30")

    def test_utils(self):
        def f(s):
            return utils.format_duration(s)

        self.assertEqual(f(0), "")
        self.assertEqual(f(60 * 60 * 24 * 7), "1 week")
        self.assertEqual(f(60 * 60 * 24 * 21), "3 weeks")
        self.assertEqual(
            f((60 * 60 * 24 * 21) - 1),
            "2 weeks, 6 days, 23 hours, 59 minutes, 59 seconds",
        )
        self.assertEqual(f(60), "1 minute")
        self.assertEqual(f(60 * 2), "2 minutes")
        self.assertEqual(f(60 * 59), "59 minutes")
        self.assertEqual(f(60 * 60), "1 hour")
        self.assertEqual(f(60 * 60 * 2), "2 hours")
        self.assertEqual(f(1), "1 second")
        self.assertEqual(f(60 + 5), "1 minute, 5 seconds")
        self.assertEqual(f(60 * 60 + 30), "1 hour, 30 seconds")
        self.assertEqual(f(60 * 60 + 60 + 30), "1 hour, 1 minute, 30 seconds")
        self.assertEqual(f(60 * 60 * 24 * 7 + 30), "1 week, 30 seconds")

    def test_utils_natural(self):
        def f(s):
            return utils.format_duration(s, natural=True)

        self.assertEqual(f(0), "")
        self.assertEqual(f(60 * 60 * 24 * 7), "1 week")
        self.assertEqual(f(60 * 60 * 24 * 21), "3 weeks")
        self.assertEqual(
            f((60 * 60 * 24 * 21) - 1),
            "2 weeks, 6 days, 23 hours, 59 minutes and 59 seconds",
        )
        self.assertEqual(f(60), "1 minute")
        self.assertEqual(f(60 * 2), "2 minutes")
        self.assertEqual(f(60 * 59), "59 minutes")
        self.assertEqual(f(60 * 60), "1 hour")
        self.assertEqual(f(60 * 60 * 2), "2 hours")
        self.assertEqual(f(1), "1 second")
        self.assertEqual(f(60 + 5), "1 minute and 5 seconds")
        self.assertEqual(f(60 * 60 + 30), "1 hour and 30 seconds")
        self.assertEqual(f(60 * 60 + 60 + 30), "1 hour, 1 minute and 30 seconds")
        self.assertEqual(f(60 * 60 * 24 * 7 + 30), "1 week and 30 seconds")

    def test_utils_short(self):
        def f(s):
            return utils.format_duration(s, short=True)

        self.assertEqual(f(0), "")
        self.assertEqual(f(60 * 60 * 24 * 7), "1w")
        self.assertEqual(f(60 * 60 * 24 * 21), "3w")
        self.assertEqual(
            f((60 * 60 * 24 * 21) - 1),
            "2w 6d 23h 59m 59s",
        )
        self.assertEqual(f(60), "1m")
        self.assertEqual(f(60 * 2), "2m")
        self.assertEqual(f(60 * 59), "59m")
        self.assertEqual(f(60 * 60), "1h")
        self.assertEqual(f(60 * 60 * 2), "2h")
        self.assertEqual(f(1), "1s")
        self.assertEqual(f(60 + 5), "1m 5s")
        self.assertEqual(f(60 * 60 + 30), "1h 30s")
        self.assertEqual(f(60 * 60 + 60 + 30), "1h 1m 30s")
        self.assertEqual(f(60 * 60 * 24 * 7 + 30), "1w 30s")

    def test_utils_natural_short(self):
        def f(s):
            return utils.format_duration(s, natural=True, short=True)

        self.assertEqual(f(0), "")
        self.assertEqual(f(60 * 60 * 24 * 7), "1w")
        self.assertEqual(f(60 * 60 * 24 * 21), "3w")
        self.assertEqual(
            f((60 * 60 * 24 * 21) - 1),
            "2w 6d 23h 59m and 59s",
        )
        self.assertEqual(f(60), "1m")
        self.assertEqual(f(60 * 2), "2m")
        self.assertEqual(f(60 * 59), "59m")
        self.assertEqual(f(60 * 60), "1h")
        self.assertEqual(f(60 * 60 * 2), "2h")
        self.assertEqual(f(1), "1s")
        self.assertEqual(f(60 + 5), "1m and 5s")
        self.assertEqual(f(60 * 60 + 30), "1h and 30s")
        self.assertEqual(f(60 * 60 + 60 + 30), "1h 1m and 30s")
        self.assertEqual(f(60 * 60 * 24 * 7 + 30), "1w and 30s")
