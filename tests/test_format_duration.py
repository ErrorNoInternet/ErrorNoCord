import unittest

import utils
import youtubedl


class TestFormatDuration(unittest.TestCase):
    def test_youtubedl(self):
        self.assertEqual(youtubedl.format_duration(0), "00:00")
        self.assertEqual(youtubedl.format_duration(0.5), "00:00")
        self.assertEqual(youtubedl.format_duration(60.5), "01:00")
        self.assertEqual(youtubedl.format_duration(1), "00:01")
        self.assertEqual(youtubedl.format_duration(60), "01:00")
        self.assertEqual(youtubedl.format_duration(60 + 30), "01:30")
        self.assertEqual(youtubedl.format_duration(60 * 60), "01:00:00")
        self.assertEqual(youtubedl.format_duration(60 * 60 + 30), "01:00:30")

    def test_utils(self):
        self.assertEqual(utils.format_duration(0), "")
        self.assertEqual(utils.format_duration(60 * 60 * 24 * 7), "1 week")
        self.assertEqual(utils.format_duration(60 * 60 * 24 * 21), "3 weeks")
        self.assertEqual(
            utils.format_duration((60 * 60 * 24 * 21) - 1),
            "2 weeks, 6 days, 23 hours, 59 minutes, 59 seconds",
        )
        self.assertEqual(utils.format_duration(60), "1 minute")
        self.assertEqual(utils.format_duration(60 * 2), "2 minutes")
        self.assertEqual(utils.format_duration(60 * 59), "59 minutes")
        self.assertEqual(utils.format_duration(60 * 60), "1 hour")
        self.assertEqual(utils.format_duration(60 * 60 * 2), "2 hours")
        self.assertEqual(utils.format_duration(1), "1 second")
        self.assertEqual(utils.format_duration(60 + 5), "1 minute, 5 seconds")
        self.assertEqual(utils.format_duration(60 * 60 + 30), "1 hour, 30 seconds")
        self.assertEqual(
            utils.format_duration(60 * 60 + 60 + 30), "1 hour, 1 minute, 30 seconds"
        )
        self.assertEqual(
            utils.format_duration(60 * 60 * 24 * 7 + 30), "1 week, 30 seconds"
        )

    def test_utils_natural(self):
        def format(seconds: int):
            return utils.format_duration(seconds, natural=True)

        self.assertEqual(format(0), "")
        self.assertEqual(format(60 * 60 * 24 * 7), "1 week")
        self.assertEqual(format(60 * 60 * 24 * 21), "3 weeks")
        self.assertEqual(
            format((60 * 60 * 24 * 21) - 1),
            "2 weeks, 6 days, 23 hours, 59 minutes and 59 seconds",
        )
        self.assertEqual(format(60), "1 minute")
        self.assertEqual(format(60 * 2), "2 minutes")
        self.assertEqual(format(60 * 59), "59 minutes")
        self.assertEqual(format(60 * 60), "1 hour")
        self.assertEqual(format(60 * 60 * 2), "2 hours")
        self.assertEqual(format(1), "1 second")
        self.assertEqual(format(60 + 5), "1 minute and 5 seconds")
        self.assertEqual(format(60 * 60 + 30), "1 hour and 30 seconds")
        self.assertEqual(format(60 * 60 + 60 + 30), "1 hour, 1 minute and 30 seconds")
        self.assertEqual(format(60 * 60 * 24 * 7 + 30), "1 week and 30 seconds")
