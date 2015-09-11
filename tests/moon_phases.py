import unittest

from dateutil.tz import tzfile

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
			datetime(1900, 1, 1, 5, 52, tzinfo=tzfile('/etc/localtime')): {
				(0, 0):   datetime(1900, 1,  1, 5,  52, tzinfo=tzfile('/etc/localtime')),
				(0, -90): datetime(1900, 1,  7, 21, 40, tzinfo=tzfile('/etc/localtime')),
				(0, 180): datetime(1900, 1, 15, 11,  7, tzinfo=tzfile('/etc/localtime')),
				(1, 90):  datetime(1900, 1, 23, 15, 53, tzinfo=tzfile('/etc/localtime')),
			},
			datetime(2015, 9, 23, 5, 52, 58, tzinfo=tzfile('/etc/localtime')): {
				(0, 0):   datetime(2015, 9, 12, 23, 41, tzinfo=tzfile('/etc/localtime')),
				(0, -90): datetime(2015, 9, 21,  1, 59, tzinfo=tzfile('/etc/localtime')),
				(0, 180): datetime(2015, 9, 27, 19, 50, tzinfo=tzfile('/etc/localtime')),
				(1, 90):  datetime(2015,10,  4, 14,  6, tzinfo=tzfile('/etc/localtime')),
			},
			datetime(2015, 6, 1, 12, 0, 0, tzinfo=tzfile('/etc/localtime')): {
				(0, 0):   datetime(2015, 5, 17, 21, 13, tzinfo=tzfile('/etc/localtime')),
				(0, -90): datetime(2015, 5, 25, 10, 19, tzinfo=tzfile('/etc/localtime')),
				(0, 180): datetime(2015, 6,  2,  9, 19, tzinfo=tzfile('/etc/localtime')),
				(1, 90):  datetime(2015, 6,  9,  8, 42, tzinfo=tzfile('/etc/localtime')),
			},
		}

	def compare_to_the_minute(self, date1, date2):
		return date1.year == date2.year and date1.month == date2.month \
		    and date1.day == date2.day and \
		    date1.hour == date2.hour and \
		    (date1.minute + round(date1.second/60)) == (date2.minute + round(date2.second/60))

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
