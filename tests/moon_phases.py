import unittest

from dateutil import tz

from datetime import datetime

import chronoslnxlib
from chronoslnxlib.core.moon_phases import predict_phase

class TestMoonPhases(unittest.TestCase):
    NEW_MOON_KEY      = (0, 0)
    FIRST_QUARTER_KEY = (0, -90)
    FULL_MOON_KEY     = (0, 180)
    LAST_QUARTER_KEY  = (1, 90)

    def setUp(self):
        self.test_cases = {
            datetime(1900, 1, 1, 13, 52, tzinfo=tz.gettz('UTC')): {
                (0, 0):   datetime(1900, 1,  1, 13, 52, tzinfo=tz.gettz('UTC')),
                (0, -90): datetime(1900, 1,  8,  5, 40, tzinfo=tz.gettz('UTC')),
                (0, 180): datetime(1900, 1, 15, 19,  7, tzinfo=tz.gettz('UTC')),
                (1, 90):  datetime(1900, 1, 23, 23, 53, tzinfo=tz.gettz('UTC')),
            },
            datetime(2015, 9, 23, 13, 52, 58, tzinfo=tz.gettz('UTC')): {
                (0, 0):   datetime(2015, 9, 13,  6, 41, tzinfo=tz.gettz('UTC')),
                (0, -90): datetime(2015, 9, 21,  8, 59, tzinfo=tz.gettz('UTC')),
                (0, 180): datetime(2015, 9, 28,  2, 50, tzinfo=tz.gettz('UTC')),
                (1, 90):  datetime(2015,10,  4, 21,  6, tzinfo=tz.gettz('UTC')),
            },
            datetime(2015, 6, 1, 12, 0, 0, tzinfo=tz.gettz('UTC')): {
                (0, 0):   datetime(2015, 5, 18,  4, 13, tzinfo=tz.gettz('UTC')),
                (0, -90): datetime(2015, 5, 25, 17, 19, tzinfo=tz.gettz('UTC')),
                (0, 180): datetime(2015, 6,  2, 16, 19, tzinfo=tz.gettz('UTC')),
                (1, 90):  datetime(2015, 6,  9, 15, 42, tzinfo=tz.gettz('UTC')),
            },
        }

    def compare_to_the_minute(self, date1, date2):
        date1 = date1.astimezone(tz.gettz('UTC'))
        date2 = date2.astimezone(tz.gettz('UTC'))

        date1_tup = (
            date1.year,
            date1.month,
            date1.day,
            date1.hour,
            date1.minute + round(date1.second/60),
        )
        date2_tup = (
            date2.year,
            date2.month,
            date2.day,
            date2.hour,
            date2.minute + round(date2.second/60),
        )
        return date1_tup == date2_tup

    def test_new_moon(self):
        for date in self.test_cases:
            answer = self.test_cases[date][TestMoonPhases.NEW_MOON_KEY]
            computed_answer = predict_phase(date, offset=TestMoonPhases.NEW_MOON_KEY[0], 
                target_angle=TestMoonPhases.NEW_MOON_KEY[1])
            print(date, TestMoonPhases.NEW_MOON_KEY, answer, computed_answer, sep='\t')
            self.assertTrue(self.compare_to_the_minute(answer, computed_answer))

    def test_first_quarter(self):
        for date in self.test_cases:
            answer = self.test_cases[date][TestMoonPhases.FIRST_QUARTER_KEY]
            computed_answer = predict_phase(date, offset=TestMoonPhases.FIRST_QUARTER_KEY[0], 
                target_angle=TestMoonPhases.FIRST_QUARTER_KEY[1])
            print(date, TestMoonPhases.FIRST_QUARTER_KEY, answer, computed_answer, sep='\t')
            self.assertTrue(self.compare_to_the_minute(answer, computed_answer))

    def test_full_moon(self):
        for date in self.test_cases:
            answer = self.test_cases[date][TestMoonPhases.FULL_MOON_KEY]
            computed_answer = predict_phase(date, offset=TestMoonPhases.FULL_MOON_KEY[0], 
                target_angle=TestMoonPhases.FULL_MOON_KEY[1])
            print(date, TestMoonPhases.FULL_MOON_KEY, answer, computed_answer, sep='\t')
            self.assertTrue(self.compare_to_the_minute(answer, computed_answer))

    def test_last_quarter(self):
        for date in self.test_cases:
            answer = self.test_cases[date][TestMoonPhases.LAST_QUARTER_KEY]
            computed_answer = predict_phase(date, offset=TestMoonPhases.LAST_QUARTER_KEY[0], 
                target_angle=TestMoonPhases.LAST_QUARTER_KEY[1])
            print(date, TestMoonPhases.LAST_QUARTER_KEY, answer, computed_answer, sep='\t')
            self.assertTrue(self.compare_to_the_minute(answer, computed_answer))

if __name__ == '__main__':
    unittest.main()
