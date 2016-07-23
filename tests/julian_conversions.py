from datetime import datetime, timedelta

from dateutil import tz
import swisseph

import chronoslnxlib
from chronoslnxlib.core import revjul_to_datetime, datetime_to_julian

ACCEPTABLE_DIFF_DAYS = 1E-6
ACCEPTABLE_DIFF_DAYS_DT = timedelta(ACCEPTABLE_DIFF_DAYS)

test_cases = (
    (
        datetime(1900, 1, 1, 13, 52, tzinfo=tz.gettz('UTC')),
        2415021.077778,
    ),
    (
        datetime(2015, 9, 23, 13, 52, 58, tzinfo=tz.gettz('UTC')),
        2457289.078449,
    ),
    (
        datetime(2015, 6, 1, 12, 0, 0, tzinfo=tz.gettz('UTC')),
        2457175.000000,
    ),
)

def test_to_julian():
    for date, jul in test_cases:
        assert abs(jul - datetime_to_julian(date)) <= ACCEPTABLE_DIFF_DAYS

def test_revjul():
    for date, jul in test_cases:
        rev_dt = revjul_to_datetime(swisseph.revjul(jul))
        assert abs(date - rev_dt) <= ACCEPTABLE_DIFF_DAYS_DT
