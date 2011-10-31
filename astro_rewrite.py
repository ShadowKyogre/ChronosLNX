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
zodiac =['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
zodiac_element = ['fire','earth','air','water','fire','earth','air','water','fire','earth','air','water']
aspects = { 'conjunction': 0.0,
	    'semi-sextile':30.0,
	    'semi=square':45.0,
	    'sextile':60.0,
	    'quintile':72.0,
	    'square':90.0,
	    'trine':120.0,
	    'sesiquadrate':135.0,
	    'biquintile':144.0,
	    'inconjunct':150.0,
	    'opposition':180.0,
	  }
special_aspects = { 'grand trine':((1,120),(2,120)),
		    'grand cross':((1,90),(3,90)),
		    'yod':((1,150),(2,60)),
		    'stellium':((1,0),(2,0)),
		    't square':((2,180),(1,90)),
		  }
					  ##Formalhaut
#stars=["Aldebaran", "Regulus", "Antares", "Fomalhaut", \#major stars
#"Alpheratz" , "Baten Kaitos", \#Aries stars
				###Caput Algol
#"Mirach", "Hamal", "Almach", "Algol", "Alcyone", \#Taurus stars
#"Hyades"
#]

def format_zodiacal_longitude(l):
	split=math.modf(l)
	degrees = int(split[1] % 30)
	sign = zodiac[int(split[1] / 30)]
	minutes = int(split[0] * 60)
	second = int(math.modf(split[0] * 60)[0] * 60)
	return degrees, sign, minutes, second

def parse_zodiacal_longitude(sign, degree, minute, second):
	degrees=zodiac.index(sign)*30.0
	return degrees+degree+minute/60.0+second/3600

def check_distance(degrees, orb, zodiacal1, zodiacal2):
	true_measurement=parse_zodiacal_longitude(zodiacal1[0], \
			  zodiacal1[1], zodiacal1[2])
	true_measurement2=parse_zodiacal_longitude(zodiacal2[0], \
			  zodiacal2[1], zodiacal2[2])
	return degrees - orb <= \
		math.fabs(true_measurement-true_measurement2) \
		<= degrees + orb

def create_aspect_table(zodiac,natal_data,orbs):
	print "To do"

def solar_return(date,year,data): #data contains the angular information, date is for a reasonable baseline
	day=datetime_to_julian(date.replace(year=year))
	origday=day
	while math.fabs(origday-day) <= 30:#
		this_degree=format_zodiacal_longitude(swisseph.calc_ut(day,swisseph.SUN)[0])
		swisseph.close()
		same_sign=this_degree[1]==data[1]
		delta_degrees=this_degree[0]-data[0]
		delta_minutes=this_degree[2]-data[2]
		delta_seconds=this_degree[3]-data[3]
		if same_sign:
			if delta_degrees < 0:
				day=day+0.0013020833
			elif delta_degrees > 0:
				day=day-0.0013020833
			else:
				if delta_minutes < 0:
					day=day+0.00065104169
				elif delta_minutes > 0:
					day=day-0.00065104169
				else:
					if delta_seconds < 0: #move forward
						if math.fabs(delta_seconds) <= 5:
							day=day+0.000081380211
						elif math.fabs(delta_seconds) <= 10:
							day=day+0.00016276042
						else:
							day=day+0.00032552084
					elif delta_seconds > 0:
						if math.fabs(delta_seconds) <= 5:
							day=day-0.000081380211
						elif math.fabs(delta_seconds) <= 10:
							day=day-0.00016276042
						else:
							day=day-0.00032552084
					else:
						return revjul_to_datetime(swisseph.revjul(day))
		else:
			if zodiac.index(this_degree[1]) < zodiac.index(data[1]) or \
				this_degree[1]=="Aries" and data[1]=="Pisces":
				day=day+30 #we're not even in the same month
			else:
				day=day-30 #we're not even in the same month

#off by +-10ish seconds for now
def lunar_return(date,month,year,data): #data contains the angular information, date is for a reasonable baseline
	start_of_last_lunar_cycle=previous_new_moon(date)
	this_month=date.replace(month=month,year=year, day=20)
	#if month==1:
		#this_month=date.replace(month=12,year=year-1)
	#else:
		#this_month=date.replace(month=month-1,year=year)
	time_elapsed=date-start_of_last_lunar_cycle #get the progress of the cycle
	start_of_month_lunar_cycle=previous_new_moon(this_month) #get the cycle for this month
	day=datetime_to_julian(start_of_month_lunar_cycle+time_elapsed)
	origday=day
	while math.fabs(origday-day) <= 30:#
		this_degree=format_zodiacal_longitude(swisseph.calc_ut(day,swisseph.MOON)[0])
		swisseph.close()
		same_sign=this_degree[1]==data[1]
		delta_degrees=this_degree[0]-data[0]
		delta_minutes=this_degree[2]-data[2]
		delta_seconds=this_degree[3]-data[3]
		if same_sign:
			if delta_degrees < 0: #move forward
				day=day+0.00032552084
			elif delta_degrees > 0: #move backward
				day=day-0.00032552084
			else:
				if delta_minutes < 0:
					day=day+0.00016276042
				elif delta_minutes > 0:
					day=day-0.00016276042
				else:
					if delta_seconds < 0: #move forward
						if math.fabs(delta_seconds) <= 3:
							day=day+0.000010172526
						elif math.fabs(delta_seconds) <= 5:
							day=day+0.000020345053
						elif math.fabs(delta_seconds) <= 10:
							day=day+0.000040690105
						else:
							day=day+0.000081380211
					elif delta_seconds > 0:
						if math.fabs(delta_seconds) <= 3:
							day=day-0.000010172526
						if math.fabs(delta_seconds) <= 5:
							day=day-0.000020345053
						elif math.fabs(delta_seconds) <= 10:
							day=day-0.000040690105
						else:
							day=day-0.000081380211
					else:
						return revjul_to_datetime(swisseph.revjul(day))
		else:
			if zodiac.index(this_degree[1]) < zodiac.index(data[1]) or \
				this_degree[1]=="Aries" and data[1]=="Pisces":
				day=day+1 #move along until we're there
			else:
				day=day-1 #same

def previous_full_moon(date):
	cycles=math.modf((datetime_to_julian(date)/29.53058868))[1]-0.2 #get a baseline
	day=cycles*29.53058868
	delta=day
	while math.fabs(day-delta) <= 2: #don't go too crazy
		# sun
		#/-----moon
		#sun-moon+ indicates that this is before
		#sun-moon- indicates that this is after
		degree1=swisseph.calc_ut(delta,swisseph.MOON)[0]
		degree2=swisseph.calc_ut(delta,swisseph.SUN)[0]
		swisseph.close()
		if round(degree2-degree1) > 180: #move forward
			delta=delta+0.020833334
		elif round(degree2-degree1) < 180: #move backward
			delta=delta-0.020833334
		else:
			return revjul_to_datetime(swisseph.revjul(delta))
	return revjul_to_datetime(swisseph.revjul(day))

def previous_new_moon(date):
	cycles=math.modf((datetime_to_julian(date)/29.53058868))[1]+0.3
	day=cycles*29.53058868
	delta=day
	while math.fabs(day-delta) <= 2: #don't go too crazy
		# sun
		#/-----moon
		#sun-moon+ indicates that this is before
		#sun-moon- indicates that this is after
		degree1=swisseph.calc_ut(delta,swisseph.MOON)[0]
		degree2=swisseph.calc_ut(delta,swisseph.SUN)[0]
		swisseph.close()
		diff=round(degree2-degree1)
		if diff > 180:
			diff=diff-360
		elif diff < -180:
			diff=diff+360
		if diff > 0: #move forward
			delta=delta+0.020833334/4
		elif diff < 0: #move backward
			delta=delta-0.020833334/4
		else:
			return revjul_to_datetime(swisseph.revjul(delta))
	return revjul_to_datetime(swisseph.revjul(day))

def prev_m_moon(date):
	cycles=math.modf((datetime_to_julian(date)/29.53058868))[1]+0.8
	day=cycles*29.53058868
	delta=day
	while math.fabs(day-delta) <= 2: #don't go too crazy
		# sun
		#/-----moon
		#sun-moon+ indicates that this is before
		#sun-moon- indicates that this is after
		degree1=swisseph.calc_ut(delta,swisseph.MOON)[0]
		degree2=swisseph.calc_ut(delta,swisseph.SUN)[0]
		swisseph.close()
		if round(degree2-degree1) > 180: #move forward
			delta=delta+0.020833334
		elif round(degree2-degree1) < 180: #move backward
			delta=delta-0.020833334
		else:
			return revjul_to_datetime(swisseph.revjul(delta))
	return revjul_to_datetime(swisseph.revjul(day))

def next_new_moon(date):
	cycles=math.modf((datetime_to_julian(date)/29.53058868))[1]+1.3
	day=cycles*29.53058868
	delta=day
	while math.fabs(day-delta) <= 2: #don't go too crazy
		# sun
		#/-----moon
		#sun-moon+ indicates that this is before
		#sun-moon- indicates that this is after
		degree1=swisseph.calc_ut(delta,swisseph.MOON)[0]
		degree2=swisseph.calc_ut(delta,swisseph.SUN)[0]
		swisseph.close()
		diff=round(degree2-degree1)
		if diff > 180:
			diff=diff-360
		elif diff < -180:
			diff=diff+360
		if diff > 0: #move forward
			delta=delta+0.020833334/4
		elif diff < 0: #move backward
			delta=delta-0.020833334/4
		else:
			return revjul_to_datetime(swisseph.revjul(delta))
	return revjul_to_datetime(swisseph.revjul(day))


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
	#note: houses move along!
	cusps,asmc=swisseph.houses(day, observer.lat, observer.long)
	#get REALLY precise house position
	hom=swisseph.house_pos(asmc[2], observer.lat, obliquity, objlon, objlat=oblt)
	swisseph.close()
	return hom,objlon,format_zodiacal_longitude(objlon)

def get_transit(planet, observer, date):
	day=datetime_to_julian(date)
	if observer.lat < 0:
		transit=revjul_to_datetime(swisseph.revjul(swisseph.rise_trans(day-1, \
				planet, observer.long, observer.lat, alt=observer.elevation, \
				rsmi=swisseph.CALC_MTRANSIT)[1][0]))
	else:
		transit=revjul_to_datetime(swisseph.revjul(swisseph.rise_trans(day-1, \
				planet, observer.long, observer.lat, alt=observer.elevation, \
				rsmi=swisseph.CALC_ITRANSIT)[1][0]))
	swisseph.close()
	return transit

#pisces, taurus
#notes: swisseph.TRUE_NODE
#south node = swisseph.TRUE_NODE's angle - 180
def get_signs(date, observer, nodes=False, axes=False):
	entries = []
	for i in xrange(10):
		house,truelon,info=get_house(i, observer, date)
		degrees,sign,minutes,seconds=info
		angle="%s*%s\"%s'" %(degrees, minutes, seconds)
		if i == swisseph.SUN or i == swisseph.MOON:
			retrograde='Not Applicable'
		else:
			retrograde=str(is_retrograde(i,date))
		entries.append([swisseph.get_planet_name(i), sign, angle, truelon, retrograde,str(int(house))])
	if nodes: #add node entries
		house,truelon,info=get_house(swisseph.TRUE_NODE, observer, date)
		degrees,sign,minutes,seconds=info
		angle="%s*%s\"%s'" %(degrees, minutes, seconds)
		retrograde="Always"
		entries.append(["North Node", sign, angle, truelon, retrograde,str(int(house))])

		#do some trickery to display the South Node
		reverse=swisseph.degnorm(truelon-180.0)
		reverse_house=(6+house)%12
		if reverse_house < 1:
			reverse_house=12+reverse_house
		rev_degrees,rev_sign,rev_minutes,rev_seconds=format_zodiacal_longitude(reverse)
		rev_angle="%s*%s\"%s'" %(rev_degrees, rev_minutes, rev_seconds)
		entries.append(["South Node", rev_sign, rev_angle, reverse, retrograde,str(int(reverse_house))])
	if axes:
		cusps,asmc=swisseph.houses(datetime_to_julian(date), observer.lat, observer.long)
		ascendant=asmc[0]
		descendant=cusps[6]
		mc=asmc[1]
		ic=cusps[3]
		retrograde='Not a Planet'

		a_degrees,a_sign,a_minutes,a_seconds=format_zodiacal_longitude(ascendant)
		d_degrees,d_sign,d_minutes,d_seconds=format_zodiacal_longitude(descendant)
		m_degrees,m_sign,m_minutes,m_seconds=format_zodiacal_longitude(mc)
		i_degrees,i_sign,i_minutes,i_seconds=format_zodiacal_longitude(ic)

		a_angle="%s*%s\"%s'" %(a_degrees, a_minutes, a_seconds)
		d_angle="%s*%s\"%s'" %(d_degrees, d_minutes, d_seconds)
		m_angle="%s*%s\"%s'" %(m_degrees, m_minutes, m_seconds)
		i_angle="%s*%s\"%s'" %(i_degrees, i_minutes, i_seconds)

		entries.append(["Ascendant", a_sign, a_angle, ascendant, retrograde,str(1)])
		entries.append(["MC", m_sign, m_angle, ascendant, retrograde,str(10)])
		entries.append(["Descendant", d_sign, d_angle, mc, retrograde,str(7)])
		entries.append(["IC", i_sign, i_angle, ic, retrograde,str(4)])

	#if stars:
		#print "Todo"
	swisseph.close()
	return entries

def grab_phase(date):
	day=datetime_to_julian(date)
	full_m=previous_new_moon(date)
	#next_new=next_new_moon(date)
	phase=swisseph.pheno_ut(day,swisseph.MOON)[1]*100

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
	if timedelta(days=0) > date - full_m:
		status = "Waxing"
	swisseph.close()
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
	swisseph.close()
	return state

def datetime_to_julian(date):
	utc=date.utctimetuple()
	total_hour=utc.tm_hour*1.0+utc.tm_min/60.0+utc.tm_sec/3600.0
	day=swisseph.julday(utc.tm_year, utc.tm_mon, utc.tm_mday, hour=total_hour)
	swisseph.close()
	return day

def timezone_to_utc(date):
	return date.astimezone(tz.gettz('UTC'))

#takes a UTC without UTC set
def utc_to_timezone(date):
	dateutc=date.replace(tzinfo=tz.gettz('UTC'))
	datenow=dateutc.astimezone(tz.gettz())
	return datenow

def get_moon_cycle(date):
	prev_new=previous_new_moon(date)
	new_m=next_new_moon(date)
	length = (new_m - prev_new) / 29
	moon_phase=[]

	for i in xrange (30):
		cycling=prev_new + length * i
		state_line=grab_phase(cycling)
		state=state_to_string(state_line, swisseph.MOON)
		moon_phase.append([cycling, state, state_line[2]])
	return moon_phase

def revjul_to_datetime(revjul):
	hours=int(math.modf(revjul[3])[1])
	minutedouble=math.modf(revjul[3])[0]*60
	minutes=int(minutedouble)
	seconds=int(math.modf(minutedouble)[0]*60)
	utc=datetime(int(revjul[0]), int(revjul[1]), int(revjul[2]), hour=hours,minute=minutes,second=seconds)
	return utc_to_timezone(utc)

def get_sunrise_and_sunset(date,observer):
	day=datetime_to_julian(date)

	sunrise=revjul_to_datetime(swisseph.revjul(swisseph.rise_trans(day-1, \
			swisseph.SUN, observer.long, observer.lat, alt=observer.elevation, \
			rsmi=swisseph.CALC_RISE)[1][0]))

	sunset=revjul_to_datetime(swisseph.revjul(swisseph.rise_trans(day-1, \
			swisseph.SUN, observer.long, observer.lat, observer.elevation, \
			rsmi=swisseph.CALC_SET)[1][0]))

	next_sunrise=revjul_to_datetime(swisseph.revjul(swisseph.rise_trans(day,
			swisseph.SUN, observer.long, observer.lat, observer.elevation, \
			rsmi=swisseph.CALC_RISE)[1][0]))
	swisseph.close()
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
	sign=get_house(swisseph.SUN, observer, date)[2][1]
	swisseph.close()
	return sign
