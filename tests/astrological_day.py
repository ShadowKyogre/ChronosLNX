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

latitudes = range(-POLAR_LATITUDE, POLAR_LATITUDE, STEP)
longitudes = range(-180, 181, STEP)

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

        print(observer, date, "testing if circumpolar is bad")

        with pytest.raises(ValueError):
            astro_day = AstrologicalDay(observer, date)

def test_sunset_always_before_sunrise():
    all_possibilities = product(latitudes, longitudes, all_times)

    for latitude, longitude, date in all_possibilities:
        observer = Observer(lat=latitude, lng=longitude)
        date = date.replace(tzinfo=observer.timezone)

        print(observer, date, "testing whether it's the right day")

        astro_day = AstrologicalDay(observer, date)
        assert astro_day.sunrise <= date <= astro_day.next_sunrise
        assert astro_day.sunrise < astro_day.sunset < astro_day.next_sunrise
