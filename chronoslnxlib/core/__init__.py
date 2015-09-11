from dateutil import tz
import swisseph

from datetime import datetime, timedelta
import math

from .. import zonetab

SOLAR_YEAR_SECONDS = 31556925.51 #source openastro.org
SOLAR_DEGREE_SECOND = 1.1407955438685572e-05
SOLAR_DEGREE_MS = 1.1407955438685574e-08
SOLAR_YEAR_DAYS = 365.2421934027778

LUNAR_MONTH_SECONDS = 2551442.8619520003
LUNAR_DEGREE_SECOND = 0.00014109663413139473
LUNAR_DEGREE_MS = 1.4109663413139472e-07
LUNAR_DEGREE_NS = 1.410966341313947e-10
LUNAR_MONTH_DAYS = 29.53058868
LMONTH_IN_SYEAR = 12.368266591655964
LMONTH_TO_MONTH = 0.9702248824500268
LAST_NM = 2415021.077777778

SECS_TO_DAYS=86400.0

class Observer:
	def __init__(self, lat=0, lng=0, elevation=0, dt=None):
		self.lat = lat
		self.lng = lng
		self.elevation = elevation
		self._dt = None
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
	obvdate = property(get_dt, set_dt)

def compare_to_the_second(date, hour, minute, second):
	return hour == date.hour and minute == date.minute and second == date.second

def revjul_to_datetime(revjul):
	hours = int(math.modf(revjul[3])[1])
	minutedouble = math.modf(revjul[3])[0]*60
	minutes = int(minutedouble)
	seconds = int(math.modf(minutedouble)[0]*60)
	utc = datetime(int(revjul[0]), int(revjul[1]), int(revjul[2]), 
	               hour=hours, minute=minutes, second=seconds)
	return utc_to_timezone(utc)

def datetime_to_julian(date):
	utc = date.utctimetuple()
	total_hour = utc.tm_hour*1.0+utc.tm_min/60.0+utc.tm_sec/3600.0
	day = swisseph.julday(utc.tm_year, utc.tm_mon, utc.tm_mday, hour=total_hour)
	swisseph.close()
	return day

def timezone_to_utc(date):
	return date.astimezone(tz.gettz('UTC'))

#takes a UTC without UTC set
def utc_to_timezone(date):
	dateutc = date.replace(tzinfo=tz.gettz('UTC'))
	datenow = dateutc.astimezone(tz.gettz())
	return datenow
