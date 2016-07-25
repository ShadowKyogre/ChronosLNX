from itertools import product, chain

from datetime import datetime
from dateutil import tz
import pytest

from chronoslnxlib.core import Observer
from chronoslnxlib.core.hours import AstrologicalDay

POLAR_LATITUDE = 70
STEP = 5

polar_latitudes = chain(
    range(-90, -POLAR_LATITUDE-1, STEP),
    range(POLAR_LATITUDE, 90, STEP)
)

semipolar_latitudes = chain(
    range(-POLAR_LATITUDE, -POLAR_LATITUDE + 10 + 1, STEP),
    range(POLAR_LATITUDE - 10, POLAR_LATITUDE + 1, STEP),
)
latitudes = range(-POLAR_LATITUDE + 10, POLAR_LATITUDE - 10 + 1, STEP)
longitudes = range(-180, 181, STEP * 3)

all_hours = range(24)
all_minutes = range(0, 51, 10)

noon_tpl = datetime(2016, 7, 23, 12, 0, 0, tzinfo=tz.gettz('UTC'))

all_times = (
    datetime(2016, 7, 23, h, m, 0, tzinfo=tz.gettz('UTC'))
    for h, m in product(all_hours, all_minutes)
)

def test_circumpolar_error():
    all_possibilities = product(polar_latitudes, (0,), (noon_tpl,))

    for latitude, longitude, date in all_possibilities:
        observer = Observer(lat=latitude, lng=longitude)
        date = date.replace(tzinfo=observer.timezone)

        print(">>>", "testing if circumpolar is bad", "<<<")
        print(">>>", observer)
        print(">>>", date)

        with pytest.raises(ValueError):
            astro_day = AstrologicalDay.day_for_ref_point(observer, dt=date)

def test_nonpolar_sunset_before_sunrise():
    all_possibilities = product(latitudes, (0,), all_times)

    for latitude, longitude, date in all_possibilities:
        observer = Observer(lat=latitude, lng=longitude)
        date = date.replace(tzinfo=observer.timezone)

        print(">>>", "testing whether it's the right day - nonpolar", "<<<")
        print(">>>", observer)
        print(">>>", date)

        astro_day = AstrologicalDay.day_for_ref_point(observer, dt=date)
        print(">>>", "Result", "<<<")
        print(">>>", astro_day.sunrise)
        print(">>>", astro_day.sunset)
        print(">>>", astro_day.next_sunrise)

        day_hour_check = (astro_day.sunrise <= date <= astro_day.sunset)
        night_hour_check = (astro_day.sunset <= date <= astro_day.next_sunrise)

        assert day_hour_check or night_hour_check
        assert astro_day.sunrise < astro_day.sunset < astro_day.next_sunrise

def test_semipolar_sunset_before_sunrise():
    all_possibilities = product(semipolar_latitudes, (0,), all_times)

    for latitude, longitude, date in all_possibilities:
        observer = Observer(lat=latitude, lng=longitude)
        date = date.replace(tzinfo=observer.timezone)

        print(">>>", "testing whether it's the right day - semipolar", "<<<")
        print(">>>", observer)
        print(">>>", date)

        astro_day = AstrologicalDay.day_for_ref_point(observer, dt=date)
        print(">>>", "Result", "<<<")
        print(">>>", astro_day.sunrise)
        print(">>>", astro_day.sunset)
        print(">>>", astro_day.next_sunrise)

        day_hour_check = (astro_day.sunrise <= date <= astro_day.sunset)
        night_hour_check = (astro_day.sunset <= date <= astro_day.next_sunrise)

        assert day_hour_check or night_hour_check
        assert astro_day.sunrise < astro_day.sunset < astro_day.next_sunrise
