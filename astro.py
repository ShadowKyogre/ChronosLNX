import ephem
import math
import re
from datetime import timedelta
#from dateutil.tz import *
from datetimetz import *

#zodiac = 'AR TA GE CN LE VI LI SC SG CP AQ PI'.split()
zodiac = 'Aries Taurus Gemini Cancer Leo Virgo Libra Scorpio Sagittarius Capricorn Aquarius Pisces'.split()
bodies=[ephem.Sun(), ephem.Moon(), ephem.Mercury(), ephem.Venus(), ephem.Mars(), ephem.Jupiter(), \
	  ephem.Saturn(), ephem.Uranus(), ephem.Neptune(), ephem.Pluto()]
#http://stackoverflow.com/questions/5881897/how-to-calculate-longitude-using-pyephem
def format_zodiacal_longitude(longitude):
	l = math.degrees(longitude.norm)
	degrees = int(l % 30)
	sign = zodiac[int(l / 30)]
	minutes = int(round((l % 1) * 60))
	return degrees, sign, minutes
	#return '{0:02}{1}{2:02}'.format(degrees, sign, minutes)

def format_angle_as_time(a):
	a = math.degrees(a) / 15.0
	hours = int(a)
	minutes = int((a % 1) * 60)
	seconds = int(((a * 60) % 1) * 60)
	return '{0:02}:{1:02}:{2:02}'.format(hours, minutes, seconds)

def clone_observer(observer):
	copy=ephem.Observer()
	copy.lat=observer.lat
	copy.long=observer.long
	copy.elevation=copy.elevation
	return copy

#check work:http://www.skyviewzone.com/astrology/retrogradeplanets.htm
def get_signs(date, observer):
	date_ephem = ephem.Date(date)
	using=clone_observer(observer)
	using2=clone_observer(observer)
	using.date=date_ephem
	using2.date=ephem.Date(date-timedelta(days=1))
	entries={}

	for b in bodies:
		b.compute(using)
		#last entry used for retrograde check
		degrees,sign,minutes=format_zodiacal_longitude(ephem.Ecliptic(b).lon)
		angle="%s*%s'" %(degrees, minutes)
		lat=ephem.Ecliptic(b).lat
		b.compute(using2)
		lat2=ephem.Ecliptic(b).lat
		latdelta=lat2-lat
		print lat2,lat
		if b.name == "Sun" or b.name == "Moon":
			retrograde=str('Not Applicable')
		else:
			retrograde=str(latdelta<0)
		entries[b.name]=[sign, angle, retrograde, "Change in latitude was %.3f over a day" %(latdelta)]
	return entries

#end copypaste#
def compare_to_the_second(date, hour, minute, second):
	return hour == date.hour and \
		minute == date.minute and \
		second == date.second

def grab_moon_phase(date):
	moon=ephem.Moon(date)
	next_full_moon=ephem.localtime(ephem.next_full_moon(date)).replace(tzinfo=LocalTimezone())
	next_new_moon=ephem.localtime(ephem.next_new_moon(date)).replace(tzinfo=LocalTimezone())
	illumination="%.3f%% illuminated" % moon.phase
	if 99.0 <= moon.phase <= 100.0:
		return "Full moon: " + illumination
	if 0 <= moon.phase <= 4.0:
		return "New moon: " + illumination
	status="Waning"
	if next_new_moon - date > next_full_moon - date:
		status = "Waxing"
	if 4.0 <= moon.phase <= 47.0:
		return status + " crescent moon: " + illumination
	elif 47.0 <= moon.phase <= 52.0:
		if status == "Waxing":
			return "First quarter moon: " + illumination
		else:
			return "Last quarter moon: " + illumination
	elif 52.0 <= moon.phase <= 99.0:
		return status + " gibbous moon: " + illumination

def get_moon_cycle(date):
	prev_new=ephem.localtime(ephem.previous_new_moon(date)).replace(tzinfo=LocalTimezone())
	full=ephem.localtime(ephem.next_full_moon(date)).replace(tzinfo=LocalTimezone())
	new_m=ephem.localtime(ephem.next_new_moon(date)).replace(tzinfo=LocalTimezone())
	length = (new_m - prev_new) / 29
	moon_phase=[]
	for i in range (0,30):
		cycling=prev_new + length * i
		state_line=grab_moon_phase(cycling)
		state=re.split(":",state_line)
		percent=re.split(" ",state[1])
		moon_phase.append([cycling, state[0], percent[1]])
	return moon_phase

#adjust for polar circles (+-66)
def get_sunrise_and_sunset(date,observer):
	tomorrow="%i/%i/%i" %(date.year,date.month,date.day+1)
	today="%i/%i/%i" %(date.year,date.month,date.day)
	#print tomorrow
	ob=clone_observer(observer)
	sun = ephem.Sun()
	sunrise=ephem.localtime(observer.next_rising(sun, start=today)).replace(tzinfo=LocalTimezone())
	sunset=ephem.localtime(observer.next_setting(sun, start=tomorrow)).replace(tzinfo=LocalTimezone())
	next_sunrise=ephem.localtime(observer.next_rising(sun, start=tomorrow)).replace(tzinfo=LocalTimezone())
	return sunrise,sunset,next_sunrise

def hours_for_day(date,observer):
	day_type=int(date.strftime('%w'))
	needed_planet=get_planet_day(day_type)
	sunrise,sunset,next_sunrise=get_sunrise_and_sunset(date,observer)
	day_length=sunset - sunrise
	night_length=next_sunrise - sunset
	dayhour_length=day_length/12
	nighthour_length=night_length/12
	hours=[]
	for i in range(0,12):
		hours.append([(sunrise+ i * dayhour_length), progression_check(needed_planet, i), True])
	for j in range(0,12):
		hours.append([(sunset + j * nighthour_length), progression_check(needed_planet, j+12), False])
	return hours

def get_planet_day(day_type):
  day_sequence=["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
  return day_sequence[day_type]

def progression_check(needed_planet, hour):
	hour_sequence=["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]
	offset=hour_sequence.index(needed_planet)
	progress=(hour % 7) + offset
	while progress>=7:
		progress -= 7
	return hour_sequence[int(math.fabs(progress))]

def calculate_sign(date):
	#sign_sequence=[Aquarias, Pisces, Aries,  Taurus, Gemini, Cancer, Leo, Virgo, Libra, Scorpio,  Sagittarius, Capricorn]
	day_of_year = date.timetuple().tm_yday
	leapyear = date.year % 4
	if leapyear > 0:
	  if day_of_year < 21 or 357 <= day_of_year < 365:
		return "Capricorn"
	  elif 21 <= day_of_year < 51:
		return "Aquarius"
	  elif 51 <= day_of_year < 80:
		return "Pisces"
	  elif 80 <= day_of_year < 112:
		return "Aries"
	  elif 112 <= day_of_year < 142:
		return "Taurus"
	  elif 142 <= day_of_year < 173:
		return "Gemini"
	  elif 173 <= day_of_year < 203:
		return "Cancer"
	  elif 203 <= day_of_year < 235:
		return "Leo"
	  elif 235 <= day_of_year < 266:
		return "Virgo"
	  elif 266 <= day_of_year < 296:
		return "Libra"
	  elif 296 <= day_of_year < 326:
		return "Scorpio"
	  elif 326 <= day_of_year < 357:
		return "Sagittarius"
	  else:
		return "- Error -"
	else:
	  if day_of_year < 21 or 358 <= day_of_year < 367:
		return "Capricorn"
	  elif 21 <= day_of_year < 51:
		return "Aquarius"
	  elif 51 <= day_of_year < 81:
		return "Pisces"
	  elif 81 <= day_of_year < 113:
		return "Aries"
	  elif 113 <= day_of_year < 143:
		return "Taurus"
	  elif 143 <= day_of_year < 174:
		return "Gemini"
	  elif 174 <= day_of_year < 204:
		return "Cancer"
	  elif 204 <= day_of_year < 236:
		return "Leo"
	  elif 236 <= day_of_year < 267:
		return "Virgo"
	  elif 267 <= day_of_year < 297:
		return "Libra"
	  elif 297 <= day_of_year < 327:
		return "Scorpio"
	  elif 327 <= day_of_year < 358:
		return "Sagittarius"
	  else:
		return "- Error -"