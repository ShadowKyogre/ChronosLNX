import ephem
import math
from datetime import datetime, timedelta, date
from dateutil.tz import *

def grab_moon_phase(date):
	moon=ephem.Moon(date)
	next_full_moon=ephem.localtime(ephem.next_full_moon(date)).replace(tzinfo=tzfile('/etc/localtime'))
	next_new_moon=ephem.localtime(ephem.next_new_moon(date)).replace(tzinfo=tzfile('/etc/localtime'))
	illumination="%.3f%% illuminated" % moon.phase
	if 97.0 <= moon.phase <= 100.0:
		return "Full moon: " + illumination
	if 0 <= moon.phase <= 1.0:
		return "New moon: " + illumination
	status="Waning"
	if next_new_moon - date > next_full_moon - date:
		status = "Waxing"
	if 1.0 <= moon.phase <= 50.0:
		return status + " crescent moon: " + illumination
	elif 50.0 <= moon.phase <= 75.0:
		if status == "Waxing":
			return "First quarter moon: " + illumination
		else:
			return "Last quarter moon: " + illumination
	elif 75.0 <= moon.phase <= 97.0:
		return status + " gibbous moon: " + illumination

def get_sunrise_and_sunset(date,latitude,longitude,elevation):
	home = ephem.Observer()
	# replace lat, long, and elevation to yours
	home.lat = str(latitude) #-is south
	home.long = str(longitude) #-is west
	home.elevation = elevation
	tomorrow="%i/%i/%i" %(date.year,date.month,date.day+1)
	today="%i/%i/%i" %(date.year,date.month,date.day)
	#print tomorrow
	sun = ephem.Sun()
	sunrise=ephem.localtime(home.next_rising(sun, start=today)).replace(tzinfo=tzfile('/etc/localtime'))
	sunset=ephem.localtime(home.next_setting(sun, start=tomorrow)).replace(tzinfo=tzfile('/etc/localtime'))
	next_sunrise=ephem.localtime(home.next_rising(sun, start=tomorrow)).replace(tzinfo=tzfile('/etc/localtime'))
	return sunrise,sunset,next_sunrise

def hours_for_day(date,latitude,longitude,elevation):
	day_type=int(date.strftime('%w'))
	needed_planet=get_planet_day(day_type)
	sunrise,sunset,next_sunrise=get_sunrise_and_sunset(date,latitude,longitude,elevation)
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
	  if day_of_year < 20 or 357 < day_of_year < 365:
		return "Capricorn"
	  elif 21 < day_of_year < 50:
		return "Aquarias"
	  elif 51 < day_of_year < 79:
		return "Pisces"
	  elif 80 < day_of_year < 111:
		return "Aries"
	  elif 112 < day_of_year < 141:
		return "Taurus"
	  elif 142 < day_of_year < 172:
		return "Gemini"
	  elif 173 < day_of_year < 202:
		return "Cancer"
	  elif 203 < day_of_year < 234:
		return "Leo"
	  elif 235 < day_of_year < 265:
		return "Virgo"
	  elif 266 < day_of_year < 295:
		return "Libra"
	  elif 296 < day_of_year < 326:
		return "Scorpio"
	  elif 326 < day_of_year < 356:
		return "Sagittarius"
	  else:
		return "- Error -"
	else:
	  if day_of_year < 20 or 358 < day_of_year < 366:
		return "Capricornus"
	  elif 21 < day_of_year < 50:
		return "Aquarias"
	  elif 51 < day_of_year < 80:
		return "Pisces"
	  elif 81 < day_of_year < 112:
		return "Aries"
	  elif 113 < day_of_year < 142:
		return "Taurus"
	  elif 143 < day_of_year < 173:
		return "Gemini"
	  elif 174 < day_of_year < 203:
		return "Cancer"
	  elif 204 < day_of_year < 235:
		return "Leo"
	  elif 236 < day_of_year < 266:
		return "Virgo"
	  elif 267 < day_of_year < 296:
		return "Libra"
	  elif 297 < day_of_year < 327:
		return "Scorpio"
	  elif 327 < day_of_year < 357:
		return "Sagittarius"
	  else:
		return "- Error -"

def get_ruling_constellations_for_date(date):
	sun=ephem.Sun(date)
	moon=ephem.Moon(date)
	mercury=ephem.Mercury(date)
	venus=ephem.Venus(date)
	mars=ephem.Mars(date)
	jupiter=ephem.Jupiter(date)
	saturn=ephem.Saturn(date)
	uranus=ephem.Uranus(date)
	neptune=ephem.Neptune(date)
	pluto=ephem.Pluto(date)

	data= {
	 'Sun' : ephem.constellation(sun),
	'Moon' : ephem.constellation(moon),
	'Mercury' : ephem.constellation(mercury),
	'Venus' : ephem.constellation(venus),
	'Mars' : ephem.constellation(mars),
	'Jupiter' : ephem.constellation(jupiter),
	'Saturn' : ephem.constellation(saturn),
	'Uranus' : ephem.constellation(uranus),
	'Neptune' : ephem.constellation(neptune),
	'Pluto' : ephem.constellation(pluto),
	}
	
	return data