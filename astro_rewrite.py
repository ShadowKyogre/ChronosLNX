#!/usr/bin/python
import swisseph
from dateutil import tz
from datetime import datetime, timedelta
import math
from operator import itemgetter

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

SOLAR_YEAR_SECONDS=31556925.51 #source openastro.org
SOLAR_DEGREE_SECOND=1.1407955438685572e-05
SOLAR_DEGREE_MS=1.1407955438685574e-08
SOLAR_YEAR_DAYS=365.2421934027778

LUNAR_MONTH_SECONDS=2551442.8619520003
LUNAR_DEGREE_SECOND=0.00014109663413139473
LUNAR_DEGREE_MS=1.4109663413139472e-07
LUNAR_DEGREE_NS=1.410966341313947e-10
LUNAR_MONTH_DAYS=29.53058868
LMONTH_IN_SYEAR=12.368266591655964
LMONTH_TO_MONTH=0.9702248824500268

SECS_TO_DAYS=86400.0

ZODIAC =['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
ZODIAC_ELEMENT = ['fire','earth','air','water','fire','earth','air','water','fire','earth','air','water']
ZODIAC_MODE = ['cardinal', 'fixed', 'mutable','cardinal', 'fixed', 'mutable','cardinal', 'fixed', 'mutable']
aspects = { 'conjunction': 0.0,
	    'semi-sextile':30.0,
	    'semi-square':45.0,
	    'sextile':60.0,
	    'quintile':72.0,
	    'square':90.0,
	    'trine':120.0,
	    'sesiquadrate':135.0,
	    'biquintile':144.0,
	    'inconjunct':150.0,
	    'opposition':180.0,
	  }

DEFAULT_ORBS = { 'conjunction': 10.0,
'semi-sextile':3.0,
'semi-square':3.0,
'sextile':6.0,
'quintile':1.0,
'square':10.0,
'trine':10.0,
'sesiquadrate':3.0,
'biquintile':1.0,
'inconjunct':3.0,
'opposition':10.0,
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
	sign = ZODIAC[int(split[1] / 30)]
	minutes = int(split[0] * 60)
	second = int(math.modf(split[0] * 60)[0] * 60)
	return degrees, sign, minutes, second

def get_zodiacal_mode(sign):
	return ZODIAC_MODE[ZODIAC.index(sign)]

def get_zodiacal_element(sign):
	return ZODIAC_ELEMENT[ZODIAC.index(sign)]


def parse_zodiacal_longitude(sign, degree, minute, second):
	degrees=ZODIAC.index(sign)*30.0
	return degrees+degree+minute/60.0+second/3600

def format_zodiacal_difference(zodiacal1,zodiacal2):
	difference=math.fabs(zodiacal1-zodiacal2)
	if difference > 180.0:
		difference=360.0-difference
	return difference

def check_distance(orb, diff):
	for i in aspects:
		degrees=aspects[i]
		o=orb[i]
		if degrees - o <= diff <= degrees + o:
			return i
#http://stackoverflow.com/questions/946860/using-pythons-list-index-method-on-a-list-of-tuples-or-objects
#http://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order

class SpecialAspect:
	def __init__(self, descriptors, name):
		self.descriptors=descriptors
		self.name=name

	def uniquePlanets(self):
		planets=set()
		for d in self.descriptors:
			planets.add(d.planet1)
			planets.add(d.planet2)
		return planets

	def uniqueMeasuerments(self):
		measurements=set()
		for d in self.descriptors:
			measurements.add(d.measurements[0])
			measurements.add(d.measurements[1])
		return measurements

	def __eq__(self, sa):
		return self.name == sa.name and \
		self.uniquePlanets() == sa.uniquePlanets()
		#because they are the same points

	def __ne__(self, sa):
		return not self.__eq__(pr)

	def __repr__(self):
		return "%s\nUnique angles:%s\nUnique planets:%s" \
		%(self.name.title(), [ ("%.3f" %(i)) for i in list(self.uniqueMeasuerments())], list(self.uniquePlanets()))

class PlanetRelationship:
	def __init__(self, p1, p2, aspect, measurements):
		self.planet1=p1
		self.planet2=p2
		self.aspect=aspect
		self.measurements=measurements

	def isForPlanet(self, string):
		return self.planet1==string or self.planet2==string

	def partnerPlanet(self, string):
		if self.planet1 == string:
			return self.planet2
		elif self.planet2 == string:
			return self.planet1
		else:
			return None

	def __repr__(self):
		return "Planet 1 - %s\nPlanet 2 - %s\nRelationship - %s\nMeasurements - %s" \
		%(self.planet1, self.planet2, self.aspect, [ ("%.3f" %(i)) for i in self.measurements])

	def __eq__(self, pr):
		return self.isForPlanet(pr.planet1) and self.isForPlanet(pr.planet2)

	def __ne__(self, pr):
		return not self.__eq__(pr)

def search_special_aspects(aspect_table):
	yods=[]
	gt=[]
	gc=[]
	stel=[]
	tsq=[]
	#if prefix != None:
		#checking_planets=20
	#else:
		#checking_planets=10
	#for i in xrange(checking_planets):
		#if i > 9:
			#pn="%s %s" %(prefix, swisseph.get_planet_name(i%10))
		#else:
			#pn=swisseph.get_planet_name(i)

	for i in xrange(10):
		pn=swisseph.get_planet_name(i)

		trine_entries=[y for x, y in enumerate(aspect_table) \
				if y.isForPlanet(pn) and y.aspect == 'trine']

		square_entries=[y for x, y in enumerate(aspect_table) \
				if y.isForPlanet(pn) and y.aspect  == 'square']

		sextile_entries=[y for x, y in enumerate(aspect_table) \
				if y.isForPlanet(pn) and y.aspect  == 'sextile']

		conjunction_entries=[y for x, y in enumerate(aspect_table) \
				if y.isForPlanet(pn) and y.aspect  == 'conjunction']

		inconjunct_entries=[y for x, y in enumerate(aspect_table) \
				if y.isForPlanet(pn) and y.aspect  == 'inconjunct']

		opposition_entries=[y for x, y in enumerate(aspect_table) \
				if y.isForPlanet(pn) and y.aspect  == 'opposition']

		intersection_entries=[]
		intersection_entries2=[]
		intersection_entries3=[]
		intersection_entries4=[]
		intersection_entries5=[]

		if len(trine_entries) > 2:
			for i in xrange(len(trine_entries)-1):
				otherp=trine_entries[i].partnerPlanet(pn)
				otherp2=trine_entries[i+1].partnerPlanet(pn)
				minitrines=[y for x, y in enumerate(aspect_table) \
					if y.isForPlanet(otherp) and y.isForPlanet(otherp2) \
					and y.aspect == 'trine']
				if len(minitrines) > 0:
					intersection_entries.append(trine_entries[i])
					intersection_entries.append(trine_entries[i+1])
				for j in minitrines:
					intersection_entries.append(j)
				if len(intersection_entries) > 2:
					gt.append(SpecialAspect(intersection_entries, 'grand trine'))
					break

		if len(opposition_entries) > 0:
			for i in xrange(len(square_entries)-1):
				otherp=square_entries[i].partnerPlanet(pn)
				otherp2=square_entries[i+1].partnerPlanet(pn)
				miniopposition=[y for x, y in enumerate(aspect_table) \
					if y.isForPlanet(otherp) and y.isForPlanet(otherp2) \
					and y.aspect == 'opposition']
				minisquare=[y for x, y in enumerate(aspect_table) \
					if (y.isForPlanet(otherp) or y.isForPlanet(otherp2)) \
					and y.aspect == "square" \
					and not y.isForPlanet(pn)]
				if len(miniopposition) > 0 and len(minisquare) > 0:
					intersection_entries2.append(square_entries[i])
					intersection_entries2.append(square_entries[i+1])
					intersection_entries2.append(miniopposition[0])
					intersection_entries2.append(minisquare[0])
					if len(intersection_entries2) > 3:
						gc.append(SpecialAspect(intersection_entries2, 'grand cross'))

		if len(square_entries) > 2:
			for i in xrange(len(square_entries)-1):
				otherp=square_entries[i].partnerPlanet(pn)
				otherp2=square_entries[i+1].partnerPlanet(pn)
				miniopposition=[y for x, y in enumerate(aspect_table) \
					if y.isForPlanet(otherp) and y.isForPlanet(otherp2) \
					and y.aspect == 'opposition']
				if len(miniopposition) > 0:
					intersection_entries3.append(square_entries[i])
					intersection_entries3.append(square_entries[i+1])
				for j in miniopposition:
					intersection_entries3.append(j)
				if len(intersection_entries3) > 2:
					tsq.append(SpecialAspect(intersection_entries3,'t-square'))
					break

		if len(conjunction_entries) > 2:
			for n in conjunction_entries:
				#Check for other conjunctions that do not involve the root planet
				if n.planet1 != pn:
					b=[y for x, y in enumerate(aspect_table) \
					if y.isForPlanet(n.planet1) and not y.isForPlanet(pn) \
					and y.aspect == 'conjunction']
				else:
					b=[y for x, y in enumerate(aspect_table) \
					if y.isForPlanet(n.planet2) and not y.isForPlanet(pn) \
					and y.aspect == 'conjunction']
				if len(b) > 0:
					intersection_entries4.append(n)
					for j in b:
						intersection_entries4.append(j)
				if len(intersection_entries4) > 2:
					stel.append(SpecialAspect(intersection_entries4,'stellium'))
					break

		if len(inconjunct_entries) > 1:
			for i in xrange(len(inconjunct_entries)-1):
				otherp=inconjunct_entries[i].partnerPlanet(pn)
				otherp2=inconjunct_entries[i+1].partnerPlanet(pn)
				minisextiles=[y for x, y in enumerate(aspect_table) \
					if y.isForPlanet(otherp) and y.isForPlanet(otherp2) \
					and y.aspect == 'sextile']
				if len(minisextiles) > 0:
					intersection_entries5.append(inconjunct_entries[i])
					intersection_entries5.append(inconjunct_entries[i+1])
				for j in minisextiles:
					intersection_entries5.append(j)
				if len(intersection_entries5) > 2:
					yods.append(SpecialAspect(intersection_entries5,'yod'))
					break

	#clean up the entries of special configs by removing entries describing the same relationship
	gt=[x for i,x in enumerate(gt) if x not in gt[i+1:]]
	yods=[x for i,x in enumerate(yods) if x not in yods[i+1:]]
	gc=[x for i,x in enumerate(gc) if x not in gc[i+1:]]
	stel=[x for i,x in enumerate(stel) if x not in stel[i+1:]]
	tsq=[x for i,x in enumerate(tsq) if x not in tsq[i+1:]]

	#remove redundant entries in tsq that are described in gc
	if len(tsq) > 0:
		for i in tsq[:]:
			for j in gc:
				planets=i.uniquePlanets()
				if planets.intersection(j.uniquePlanets()) == planets:
					tsq.remove(i)
					break
				else:
					"Failed to remove. %s|%s|%s|%s" %(planets,j.uniquePlanets(),planets.intersection(j.uniquePlanets()),planets.intersection(j.uniquePlanets()) == planets)

	return yods,gt,gc,stel,tsq

def create_aspect_table(zodiac,orbs=DEFAULT_ORBS,compare=None, prefix="Natal"):
	aspect_table=[]
	comparison=[]

	for i in zodiac:
		for j in zodiac:
			if i[0] == j[0]:
				continue
			if len(aspect_table) > 0:
				if len([x for x, y in enumerate(aspect_table) \
				if y.isForPlanet(j[0]) and y.isForPlanet(i[0])]) > 0:
					continue
			diff=format_zodiacal_difference(i[3],j[3])
			pr=PlanetRelationship(i[0],j[0],\
			check_distance(orbs,diff),\
			[i[3],j[3],diff])
			aspect_table.append(pr)
		if zodiac is not compare and compare is not None:
			for j in compare:
				diff=format_zodiacal_difference(i[3],j[3])
				pr=PlanetRelationship(i[0], "%s %s" %(prefix,j[0]),\
				check_distance(orbs,diff),\
				[i[3],j[3],diff])
				comparison.append(pr)
	if len(comparison) > 0:
		return aspect_table,comparison

	return aspect_table

def solar_return(date,year,data): #data contains the angule, date is for a reasonable baseline
	day=datetime_to_julian(date)+(SOLAR_YEAR_DAYS*(year-date.year))

	angle=swisseph.calc_ut(day,swisseph.SUN)[0]
	sec=((data-angle)/SOLAR_DEGREE_SECOND)/SECS_TO_DAYS
	day=day+sec

	angle=swisseph.calc_ut(day,swisseph.SUN)[0]
	msec=((data-angle)/SOLAR_DEGREE_MS)/(SECS_TO_DAYS*1000)

	return revjul_to_datetime(swisseph.revjul(day+msec))

def lunar_return(date,month,year,data): #data contains the angle, date is for a reasonable baseline
	day=datetime_to_julian(date)
	progress,cycles=math.modf((day/LUNAR_MONTH_DAYS))

	cycles=cycles+(year-date.year)*LMONTH_IN_SYEAR
	cycles=cycles+(month-date.month)*LMONTH_TO_MONTH

	day=(cycles)*LUNAR_MONTH_DAYS

	angle=swisseph.calc_ut(day,swisseph.MOON)[0]
	day=day+(data-angle)/360*LUNAR_MONTH_DAYS

	angle=swisseph.calc_ut(day,swisseph.MOON)[0]
	day=day+(data-angle)/360*LUNAR_MONTH_DAYS

	angle=swisseph.calc_ut(day,swisseph.MOON)[0]
	sec=((data-angle)/LUNAR_DEGREE_SECOND)/SECS_TO_DAYS
	day=day+sec

	angle=swisseph.calc_ut(day,swisseph.MOON)[0]
	sec=((data-angle)/LUNAR_DEGREE_SECOND)/SECS_TO_DAYS
	day=day+sec

	angle=swisseph.calc_ut(day,swisseph.MOON)[0]
	msec=((data-angle)/LUNAR_DEGREE_MS)/(SECS_TO_DAYS*1000)
	day=day+msec

	angle=swisseph.calc_ut(day,swisseph.MOON)[0]
	msec=((data-angle)/LUNAR_DEGREE_MS)/(SECS_TO_DAYS*1000)
	day=day+msec

	angle=swisseph.calc_ut(day,swisseph.MOON)[0]
	nsec=((data-angle)/LUNAR_DEGREE_NS)/(SECS_TO_DAYS*1000000)
	day=day+nsec

	angle=swisseph.calc_ut(day,swisseph.MOON)[0]
	nsec=((data-angle)/LUNAR_DEGREE_NS)/(SECS_TO_DAYS*1000000)
	day=day+nsec

	return revjul_to_datetime(swisseph.revjul(day))

def previous_full_moon(date):
	cycles=math.modf((datetime_to_julian(date)/LUNAR_MONTH_DAYS))[1]-0.2 #get a baseline
	day=cycles*LUNAR_MONTH_DAYS
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
	cycles=math.modf((datetime_to_julian(date)/LUNAR_MONTH_DAYS))[1]+0.3
	day=cycles*LUNAR_MONTH_DAYS
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

def prev_full_moon(date):
	cycles=math.modf((datetime_to_julian(date)/LUNAR_MONTH_DAYS))[1]+0.8
	day=cycles*LUNAR_MONTH_DAYS
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
	cycles=math.modf((datetime_to_julian(date)/LUNAR_MONTH_DAYS))[1]+1.3
	day=cycles*LUNAR_MONTH_DAYS
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
	#hom=swisseph.house_pos(asmc[2], observer.lat, obliquity, objlon)
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
def get_signs(date, observer, nodes, axes):
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
		entries.append(["MC", m_sign, m_angle, mc, retrograde,str(10)])
		entries.append(["Descendant", d_sign, d_angle, descendant, retrograde,str(7)])
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

