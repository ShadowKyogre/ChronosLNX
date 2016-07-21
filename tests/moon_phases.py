import unittest

from dateutil import tz

from datetime import datetime

import chronoslnxlib
from chronoslnxlib.core.moon_phases import predict_phase

def tuplify(date):
    date = date.astimezone(tz.gettz('UTC'))

    date_tup = (
        date.year,
        date.month,
        date.day,
        date.hour,
        date.minute + round(date.second/60),
    )
    return date_tup

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

    def test_new_moon(self):
        moon_phase_key = TestMoonPhases.NEW_MOON_KEY
        for date in self.test_cases:
            with self.subTest(date=date, moon_phase=moon_phase_key):
                answer = self.test_cases[date][moon_phase_key]
                computed_answer = predict_phase(
                    date,
                    offset=moon_phase_key[0], 
                    target_angle=moon_phase_key[1]
                )
                answer_tup = tuplify(answer)
                computed_answer_tup = tuplify(computed_answer)
                self.assertEqual(answer_tup, computed_answer_tup)

    def test_first_quarter(self):
        moon_phase_key = TestMoonPhases.FIRST_QUARTER_KEY
        for date in self.test_cases:
            with self.subTest(date=date, moon_phase=moon_phase_key):
                answer = self.test_cases[date][moon_phase_key]
                computed_answer = predict_phase(
                    date,
                    offset=moon_phase_key[0], 
                    target_angle=moon_phase_key[1]
                )
                answer_tup = tuplify(answer)
                computed_answer_tup = tuplify(computed_answer)
                self.assertEqual(answer_tup, computed_answer_tup)

    def test_full_moon(self):
        moon_phase_key = TestMoonPhases.FULL_MOON_KEY
        for date in self.test_cases:
            with self.subTest(date=date, moon_phase=moon_phase_key):
                answer = self.test_cases[date][moon_phase_key]
                computed_answer = predict_phase(
                    date,
                    offset=moon_phase_key[0], 
                    target_angle=moon_phase_key[1]
                )
                answer_tup = tuplify(answer)
                computed_answer_tup = tuplify(computed_answer)
                self.assertEqual(answer_tup, computed_answer_tup)

    def test_last_quarter(self):
        moon_phase_key = TestMoonPhases.LAST_QUARTER_KEY
        for date in self.test_cases:
            with self.subTest(date=date, moon_phase=moon_phase_key):
                answer = self.test_cases[date][moon_phase_key]
                computed_answer = predict_phase(
                    date,
                    offset=moon_phase_key[0], 
                    target_angle=moon_phase_key[1]
                )
                answer_tup = tuplify(answer)
                computed_answer_tup = tuplify(computed_answer)
                self.assertEqual(answer_tup, computed_answer_tup)

if __name__ == '__main__':
    unittest.main()
