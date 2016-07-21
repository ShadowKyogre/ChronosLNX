from dateutil import tz
import swisseph

from datetime import datetime, timedelta
import math

from .. import zonetab

SOLAR_YEAR_DAYS = 365.2421934027778

LUNAR_MONTH_DAYS = 29.53058868
LAST_NM = 2415021.077777778

SECS_TO_DAYS=86400.0

class Observer:
    def __init__(self, lat=0, lng=0, elevation=0, dt=None):
        self.lat = lat
        self.lng = lng
        self.elevation = elevation
        self.obvdate = dt
    def set_dt(self, new_dt):
        if new_dt is None:
            self._dt = None
            return
        if new_dt.tzinfo is None:
            #assume the new fixed dt is given in system's localtime
            #if it is naive
            ndt = new_dt.replace(tzinfo=tz.gettz())
        else:
            ndt = new_dt
        #then convert it to the timezone for the observer
        self._dt = ndt.astimezone(self.timezone)
    def get_dt(self):
        if self._dt is None:
            return self.dt_now()
        return self._dt
    @property
    def timezone(self):
         zt = zonetab.nearest_tz(self.lat, self.lng, zonetab.timezones())[2]
         #print(zt)
         return tz.gettz(zt)
    def dt_now(self):
        utcdt = datetime.now(tz=tz.gettz('UTC'))
        return utcdt.astimezone(self.timezone)
    def average(self, other):
        new_lat = (other.lat+self.lat)/2
        new_lng = (other.lng+self.lng)/2
        new_elevation = (other.elevation + self.elevation)/2
        utc_dt = timezone_to_utc(self.obvdate)
        other_utc_dt = timezone_to_utc(other.obvdate)
        dt_delta = (utc_dt-other_utc_dt)/2
        if dt_delta < timedelta(0):
            new_dt = utc_dt+dt_delta
        else:
            new_dt = other_utc_dt+dt_delta
        new_obv = Observer(lat=new_lat, lng=new_lng, elevation=new_elevation)
        new_obv.obvdate = new_dt
        return new_obv
    def __str__(self):
        return self.obvdate.strftime("%Y-%m-%d/%H:%M:%S@{0},{1},{2}")\
               .format(self.lat, self.lng, self.elevation)
    def __repr__(self):
        return "Observer(lat={0}, lng={1}, elevation={2}, dt={3})" \
               .format(repr(self.lat), repr(self.lng), repr(self.elevation), repr(self._dt))
    obvdate = property(get_dt, set_dt)

def compare_to_the_second(date, hour, minute, second):
    return hour == date.hour and minute == date.minute and second == date.second

def revjul_to_datetime(revjul):
    hours = int(math.modf(revjul[3])[1])
    minutedouble = math.modf(revjul[3])[0]*60
    minutes = int(minutedouble)
    seconds = int(math.modf(minutedouble)[0]*60)
    utc = datetime(
        int(revjul[0]), int(revjul[1]), int(revjul[2]), 
        hour=hours, minute=minutes, second=seconds,
        tzinfo=tz.gettz('UTC')
    )
    return utc

def datetime_to_julian(date):
    utc = date.utctimetuple()
    total_hour = utc.tm_hour*1.0+utc.tm_min/60.0+utc.tm_sec/3600.0
    day = swisseph.julday(utc.tm_year, utc.tm_mon, utc.tm_mday, hour=total_hour)
    swisseph.close()
    return day

def timezone_to_utc(date):
    return date.astimezone(tz.gettz('UTC'))

#takes a UTC without UTC set
def utc_to_timezone(date, target_tz=tz.gettz()):
    dateutc = date.replace(tzinfo=tz.gettz('UTC'))
    datenow = dateutc.astimezone(target_tz)
    return datenow

def average(first, second):
    return (first+second)/2

def zipped_func(first_list, second_list, func=average):
    output=[]
    for f, b in zip(first_list, second_list):
        output.append(func(f, b))
    return output

def angle_average(first, second):
    rfirst = math.radians(first)
    rsecond = math.radians(second)
    sin_sum = math.sin(rfirst) + math.sin(rsecond)
    cos_sum = math.cos(rfirst) + math.cos(rsecond)
    avg_angle = math.degrees(math.atan2(sin_sum/2, cos_sum/2))
    if avg_angle < 0:
        avg_angle += 360.
    return avg_angle

def angle_sub(target, source):
    diff = (target-source)
    if diff > 180:
        diff -= 360
    elif diff < -180:
        diff += 360
    return diff

def date_to_solar_cycles(forecast_date, orig_date):
    end_point = datetime_to_julian(forecast_date)
    if type(orig_date) == float:
        start_point = orig_date
    else:
        start_point =  datetime_to_julian(orig_date) 
    cycle_with_part = (end_point-start_point)/SOLAR_YEAR_DAYS
    return cycle_with_part

def date_to_moon_cycles(forecast_date, orig_date=LAST_NM):
    days_since_nm = datetime_to_julian(forecast_date)-orig_date
    cycle_with_part = days_since_nm/LUNAR_MONTH_DAYS
    return cycle_with_part

def solar_cycles_to_jul(cycles, orig_date):
    day = cycles*SOLAR_YEAR_DAYS+orig_date
    return day

def moon_cycles_to_jul(cycles, orig_date=LAST_NM):
    day = cycles*LUNAR_MONTH_DAYS+orig_date
    return day
