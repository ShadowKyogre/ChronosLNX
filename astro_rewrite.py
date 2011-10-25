#!/usr/bin/python
import swisseph
from dateutil import tz
from datetime import datetime, timedelta
import math
#http://www.astro.com/swisseph/swephprg.htm#_Toc283735418
#http://packages.python.org/pyswisseph/
#http://www.astrologyzine.com/what-is-a-house-cusp.shtml

#ascmc[0] =      Ascendant
#ascmc[1] =     MC
#ascmc[2] =     ARMC
#ascmc[3] =     Vertex
#ascmc[4] =     "equatorial ascendant"
#ascmc[5] =     "co-ascendant" (Walter Koch)
#ascmc[6] =     "co-ascendant" (Michael Munkasey)
#ascmc[7] =     "polar ascendant" (M. Munkasey)
zodiac = 'Aries Taurus Gemini Cancer Leo Virgo Libra Scorpio Sagittarius Capricorn Aquarius Pisces'.split()
def format_zodiacal_longitude(l):
	degrees = int(l % 30)
	sign = zodiac[int(l / 30)]
	minutes = int(round((l % 1) * 60))
	return degrees, sign, minutes

def next_full_moon(date, planet):
	day=datetime_to_julian(date)-1
	#2455860.500000
	#2455859.500000
	while True:
		if 97.0 <= swisseph.pheno_ut(day, planet)[1] * 100 <= 100.0:
			return revjul_to_datetime(swisseph.revjul(day))
		else:
			day=day-1

def previous_new_moon(date, planet):
	day=datetime_to_julian(date)-1
	#2455860.500000
	#2455859.500000
	while True:
		if 0 <= swisseph.pheno_ut(day, planet)[1] * 100 <= 2.0:
			return revjul_to_datetime(swisseph.revjul(day))
		else:
			day=day-1
	
	
def next_full_moon(date, planet):
	day=datetime_to_julian(date)
	#2455860.500000
	#2455859.500000
	while True:
		if 97.0 <= swisseph.pheno_ut(day, planet)[1] * 100 <= 100.0:
			return revjul_to_datetime(swisseph.revjul(day))
		else:
			day=day+1
	
def next_new_moon(date, planet):
	day=datetime_to_julian(date)
	#2455860.500000
	#2455859.500000
	while True:
		if 0 <= swisseph.pheno_ut(day, planet)[1] * 100 <= 2.0:
			return revjul_to_datetime(swisseph.revjul(day))
		else:
			day=day+1

def is_retrograde(planet, date):
	day=datetime_to_julian(date)
	# lat.speed < 0, then retrograde (source: openastro.org)
	return (swisseph.calc_ut(day,planet)[3] < 0)

def get_house(planet, observer, date):
	day=datetime_to_julian(date)
	#longitude, latitude, distance, [long. speed], lat. speed, dist. speed
	obliquity=swisseph.calc_ut(day,swisseph.ECL_NUT)[0]
	objlon=swisseph.calc_ut(day,planet)[0]
	oblt=swisseph.calc_ut(day,planet)[1]
	#float[12],#float[8]
	cusps=swisseph.houses_ex(day, observer.lat, observer.long)[0]
	asmc=swisseph.houses_ex(day, observer.lat, observer.long)[1]
	hom=swisseph.house_pos(asmc[2], observer.lat, obliquity, objlon, objlat=oblt)
	return hom,format_zodiacal_longitude(objlon)

def get_signs(date, observer):
	entries={}
	for i in xrange(10):
		house,info=get_house(i, observer, date)
		degrees,sign,minutes=info
		angle="%s*%s'" %(degrees, minutes)
		if i == swisseph.SUN or i == swisseph.MOON:
			retrograde=str('Not Applicable')
		else:
			retrograde=str(is_retrograde(i,date))
		entries[swisseph.get_planet_name(i)]=[sign, angle, retrograde,str(int(house))]
	return entries

def grab_phase(planet, date):
	day=datetime_to_julian(date)
	next_full=next_full_moon(date,planet)
	next_new=next_new_moon(date,planet)
	phase=swisseph.pheno_ut(day,planet)[1]*100
	if 97.0 <= phase <= 100.0:
		illumination="Full"
	elif 0 <= phase <= 2.0:
		illumination="New"
	elif 2.0 <= phase <= 47.0:
		illumination="Crescent"
	elif 47.0 <= phase <= 52.0:
		illumination="Quarter"
	else:
		illumination="Gibbous"
	status="Waning"
	if next_new - date > next_full - date:
		status = "Waxing"
	return status,illumination,"%.3f%%" %(phase)

	#attr[0] = phase angle (earth-planet-sun)
	#attr[1] = phase (illumined fraction of disc)
	#attr[2] = elongation of planet
	#attr[3] = apparent diameter of disc
	#attr[4] = apparent magnitude

def state_to_string(state_line, planet):
	name=swisseph.get_planet_name(planet)
	if state_line[1] == "New" or state_line[1] == "Full":
		state="%s %s" %(state_line[1], name)
	elif state_line[1] == "Quarter":
		if state_line[0] == "Waning":
			state="Last %s %s" %(state_line[1], name)
		else:
			state="First %s %s" %(state_line[1], name)
	else:
		state="%s %s %s" %(state_line[0], state_line[1], name)
	return state

def datetime_to_julian(date):
	utc=date.utctimetuple()
	day=swisseph.julday(utc.tm_year, utc.tm_mon, utc.tm_mday, hour=utc.tm_hour*1.0)
	return day

def timezone_to_utc(date):
	return date.astimezone(tz.gettz('UTC'))

#takes a UTC without UTC set
def utc_to_timezone(date):
	dateutc=date.replace(tzinfo=tz.gettz('UTC'))
	datenow=dateutc.astimezone(tz.gettz())
	return datenow

def get_moon_cycle(date):
	prev_new=previous_new_moon(date, swisseph.MOON)
	full=next_full_moon(date, swisseph.MOON)
	new_m=next_new_moon(date, swisseph.MOON)
	length = (new_m - prev_new) / 29
	moon_phase=[]
	for i in range (0,30):
		cycling=prev_new + length * i
		state_line=grab_phase(swisseph.MOON, cycling)
		state=state_to_string(state_line, swisseph.MOON)
		moon_phase.append([cycling, state, state_line[2]])
	return moon_phase

def revjul_to_datetime(revjul):
	hours=int(math.modf(revjul[3])[1])
	minutes=int(math.modf(revjul[3])[0]*60)
	seconds=int(math.modf(minutes)[0]*60)
	utc=datetime(int(revjul[0]), int(revjul[1]), int(revjul[2]), hour=hours,minute=minutes,second=seconds)
	return utc_to_timezone(utc)

def get_sunrise_and_sunset(date,observer):
	utc=timezone_to_utc(date)
	precise_hour=utc.hour+float(utc.minute)/60+float(utc.second)/3600
	day=swisseph.julday(utc.year,utc.month,utc.day, hour=precise_hour)

	sunrise=revjul_to_datetime(swisseph.revjul(swisseph.rise_trans(day-1, \
			swisseph.SUN, observer.long, observer.lat, alt=observer.elevation, \
			rsmi=swisseph.CALC_RISE)[1][0]))

	sunset=revjul_to_datetime(swisseph.revjul(swisseph.rise_trans(day, \
			swisseph.SUN, observer.long, observer.lat, observer.elevation, \
			rsmi=swisseph.CALC_SET)[1][0]))

	next_sunrise=revjul_to_datetime(swisseph.revjul(swisseph.rise_trans(day,
			swisseph.SUN, observer.long, observer.lat, observer.elevation, \
			rsmi=swisseph.CALC_RISE)[1][0]))

	return sunrise,sunset,next_sunrise

def compare_to_the_second(date, hour, minute, second):
	return hour == date.hour and \
		minute == date.minute and \
		second == date.second

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

def get_sun_sign(date, observer):
	return get_house(swisseph.SUN, observer, date)[1][1]
