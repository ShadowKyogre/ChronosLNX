#!/usr/bin/python
import swisseph
from dateutil import tz
from datetime import datetime, timedelta
import math
from measurements import *
from planet import Planet
from aspects import *

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

#http://www.guidingstar.com/Articles/Rulerships.html ? Either this or just mod Uranus, Neptune, and Pluto to have just one sign

					  ##Formalhaut
#FIXED_STARS=["Aldebaran", "Regulus", "Antares", "Fomalhaut", \#major stars
#"Alpheratz" , "Baten Kaitos", \#Aries stars
				##Caput Algol
#"Mirach", "Hamal", "Almach", "Algol", "Alcyone", \#Taurus stars
##Hyades 	#Epsilon Tauri/Northern Bull's Eye		#Polaris
#"Prima Hyadum", "Ain", "Rigel", "Bellatrix", "Capella", "Alnilam", ",alUMi", "Betelgeuse", \#gemini stars
#"Sirius","Castor","Pollux","Procyon", \#cancer stars
#"Praesepe","Alphard", \#Leo stars
#"Zosma", "Denebola", \#Virgo stars
#"Vindemiatrix", "Algorab", "Spica", "Arcturus", \#Libra stars
			##Zuben Algenubi/North Scale	#Zuben Ashamali/South Scale
#"Princeps", "Alphecca", "Zuben Elgenubi", "Zuben Eshamali", "Unukalhai", \#Scorpio stars
	  ##Aculeus
#"Lesath", "Sargas", "Acumen", ""
#]

#http://stackoverflow.com/questions/946860/using-pythons-list-index-method-on-a-list-of-tuples-or-objects
#http://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order

def search_special_aspects(aspect_table):
	yods=set()
	gt=set()
	gc=set()
	stel=set()
	tsq=set()

	for i in xrange(10):
		pn=swisseph.get_planet_name(i)

		trine_entries=[y for y in aspect_table \
				if y.isForPlanet(pn) and y.aspect == 'trine']

		square_entries=[y for y in aspect_table \
				if y.isForPlanet(pn) and y.aspect  == 'square']

		sextile_entries=[y for y in aspect_table \
				if y.isForPlanet(pn) and y.aspect  == 'sextile']

		conjunction_entries=[y for y in aspect_table \
				if y.isForPlanet(pn) and y.aspect  == 'conjunction']

		inconjunct_entries=[y for y in aspect_table \
				if y.isForPlanet(pn) and y.aspect  == 'inconjunct']

		opposition_entries=[y for y in aspect_table \
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
				minitrines=[y for y in aspect_table \
					if y.isForPlanet(otherp) and y.isForPlanet(otherp2) \
					and y.aspect == 'trine']
				if len(minitrines) > 0:
					intersection_entries.append(trine_entries[i])
					intersection_entries.append(trine_entries[i+1])
				for j in minitrines:
					intersection_entries.append(j)
				if len(intersection_entries) > 2:
					gt.add(SpecialAspect(intersection_entries, 'grand trine'))
					break

		if len(opposition_entries) > 0:
			for i in xrange(len(square_entries)-1):
				otherp=square_entries[i].partnerPlanet(pn)
				otherp2=square_entries[i+1].partnerPlanet(pn)
				miniopposition=[y for y in aspect_table \
					if y.isForPlanet(otherp) and y.isForPlanet(otherp2) \
					and y.aspect == 'opposition']
				minisquare=[y for y in aspect_table \
					if (y.isForPlanet(otherp) or y.isForPlanet(otherp2)) \
					and y.aspect == "square" \
					and not y.isForPlanet(pn)]
				if len(miniopposition) > 0 and len(minisquare) > 0:
					intersection_entries2.append(square_entries[i])
					intersection_entries2.append(square_entries[i+1])
					intersection_entries2.append(miniopposition[0])
					intersection_entries2.append(minisquare[0])
					if len(intersection_entries2) > 3:
						gc.add(SpecialAspect(intersection_entries2, 'grand cross'))
						break

		if len(square_entries) > 2:
			for i in xrange(len(square_entries)-1):
				otherp=square_entries[i].partnerPlanet(pn)
				otherp2=square_entries[i+1].partnerPlanet(pn)
				miniopposition=[y for y in aspect_table \
					if y.isForPlanet(otherp) and y.isForPlanet(otherp2) \
					and y.aspect == 'opposition']
				if len(miniopposition) > 0:
					intersection_entries3.append(square_entries[i])
					intersection_entries3.append(square_entries[i+1])
				for j in miniopposition:
					intersection_entries3.append(j)
				if len(intersection_entries3) > 2:
					tsq.add(SpecialAspect(intersection_entries3,'t-square'))
					break

		if len(conjunction_entries) > 2:
			for n in conjunction_entries:
				#Check for other conjunctions that do not involve the root planet
				if n.planet1 != pn:
					b=[y for y in aspect_table \
					if y.isForPlanet(n.planet1) and not y.isForPlanet(pn) \
					and y.aspect == 'conjunction']
				else:
					b=[y for y in aspect_table \
					if y.isForPlanet(n.planet2) and not y.isForPlanet(pn) \
					and y.aspect == 'conjunction']
				if len(b) > 0:
					intersection_entries4.append(n)
					for j in b:
						intersection_entries4.append(j)
					if len(intersection_entries4) > 2:
						stel.add(SpecialAspect(intersection_entries4,'stellium'))
						break

		if len(inconjunct_entries) > 1:
			for i in xrange(len(inconjunct_entries)-1):
				otherp=inconjunct_entries[i].partnerPlanet(pn)
				otherp2=inconjunct_entries[i+1].partnerPlanet(pn)
				minisextiles=[y for y in aspect_table \
					if y.isForPlanet(otherp) and y.isForPlanet(otherp2) \
					and y.aspect == 'sextile']
				if len(minisextiles) > 0:
					intersection_entries5.append(inconjunct_entries[i])
					intersection_entries5.append(inconjunct_entries[i+1])
				for j in minisextiles:
					intersection_entries5.append(j)
				if len(intersection_entries5) > 2:
					yods.add(SpecialAspect(intersection_entries5,'yod'))
					break

	#remove stelliums contained in stelliums that
	#involve the same planets

	if len(stel) > 1:
		for i in stel.copy():
			for j in stel.copy():
				if j.contains(i):
					stel.remove(i)
					break

	#remove redundant entries in tsq that are described in gc
	if len(tsq) > 0:
		for i in tsq.copy():
			for j in gc:
				if j.contains(i):
					tsq.remove(i)
					break

	return yods,gt,gc,stel,tsq

def create_aspect_table(zodiac,orbs=DEFAULT_ORBS,compare=None):
	aspect_table=[]
	comparison=[]

	for idx, i in enumerate(zodiac):
		for j in zodiac[idx+1:]:
			pr=Aspect(i,j,DEFAULT_ORBS)
			aspect_table.append(pr)
		if zodiac is not compare and compare is not None:
			for j in compare:
				pr=Aspect(i,j,DEFAULT_ORBS)
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
#i, (i+1)%12 # counter clockwise
#(i+1)%12, i # clockwise
def fill_houses(date, observer, houses=None,data=None):
	day=datetime_to_julian(date)
	if not data:
		data=swisseph.houses(day, observer.lat, observer.long)[0]
	if houses == None:
		houses=[]
		for i in xrange(12):
			houses.append(HouseMeasurement(data[i],data[(i+1)%12],num=i+1))
		swisseph.close()
		return houses
	else:
		for i in xrange(12):
			houses[i].cusp.longitude=data[i]
			houses[i].end.longitude=data[(i+1)%12]
		swisseph.close()

def updatePandC(date, observer, houses, entries):
	day=datetime_to_julian(date)
	obliquity=swisseph.calc_ut(day,swisseph.ECL_NUT)[0]
	cusps,asmc=swisseph.houses(day, observer.lat, observer.long)
	fill_houses(date, observer, houses=houses, data=cusps)
	for i in xrange(10):
		calcs=swisseph.calc_ut(day,i)
		hom=swisseph.house_pos(asmc[2], observer.lat, obliquity, calcs[0], objlat=calcs[1])
		if i == swisseph.SUN or i == swisseph.MOON:
			retrograde='Not Applicable'
		else:
			retrograde=str(calcs[3] < 0)
		entries[i].retrograde=retrograde
		entries[i].m.longitude=calcs[0]
		entries[i].m.latitude=calcs[1]
		entries[i].m.progress=hom%1.0
		entries[i].m.house_info=houses[int(hom-1)]
	if len(entries) > 10: #add node entries
		calcs=swisseph.calc_ut(day,swisseph.TRUE_NODE)
		hom=swisseph.house_pos(asmc[2], observer.lat, obliquity, calcs[0], objlat=calcs[1])
		retrograde="Always"

		entries[10].retrograde=retrograde
		entries[10].m.longitude=calcs[0]
		entries[10].m.latitude=calcs[1]
		entries[10].m.progress=hom%1.0
		entries[10].m.house_info=houses[int(hom-1)]

		#do some trickery to display the South Node
		reverse=swisseph.degnorm(calcs[0]-180.0)
		revhouse=(int(hom)+6)%12
		revprogress=1-hom%1.0
		entries[11].retrograde=retrograde
		entries[11].m.longitude=reverse
		entries[11].m.latitude=calcs[1]
		entries[11].m.progress=revprogress
		entries[11].m.house_info=houses[int(revhouse-1)]
	if len(entries) > 12:
		ascendant=asmc[0]
		descendant=cusps[6]
		mc=asmc[1]
		ic=cusps[3]
		retrograde='Not a Planet'

		entries[12].m.longitude=ascendant
		entries[13].m.longitude=descendant
		entries[14].m.longitude=mc
		entries[15].m.longitude=ic

	swisseph.close()

#def update_planets(date, observer):
#notes: swisseph.TRUE_NODE
#south node = swisseph.TRUE_NODE's angle - 180
def get_signs(date, observer, nodes, axes, prefix=None):
	entries = []
	houses = fill_houses(date, observer)
	day=datetime_to_julian(date)
	obliquity=swisseph.calc_ut(day,swisseph.ECL_NUT)[0]

	cusps,asmc=swisseph.houses(day, observer.lat, observer.long)

	for i in xrange(10):
		calcs=swisseph.calc_ut(day,i)
		hom=swisseph.house_pos(asmc[2], observer.lat, obliquity, calcs[0], objlat=calcs[1])
		zm=ActiveZodiacalMeasurement(calcs[0], calcs[1], houses[int(hom-1)], progress=hom % 1.0)
		if i == swisseph.SUN or i == swisseph.MOON:
			retrograde='Not Applicable'
		else:
			retrograde=retrograde=str(calcs[3] < 0)
		planet=Planet(swisseph.get_planet_name(i),prefix=prefix,m=zm,retrograde=retrograde)
		entries.append(planet)
	if nodes: #add node entries
		calcs=swisseph.calc_ut(day,swisseph.TRUE_NODE)
		hom=swisseph.house_pos(asmc[2], observer.lat, obliquity, calcs[0], objlat=calcs[1])
		zm=ActiveZodiacalMeasurement(calcs[0], calcs[1], houses[int(hom-1)], progress=hom % 1.0)
		retrograde="Always"
		planet=Planet("North Node",prefix=prefix,m=zm,retrograde=retrograde)
		entries.append(planet)

		#do some trickery to display the South Node
		reverse=swisseph.degnorm(calcs[0]+180.0)
		revhouse=(int(hom)+6)%12
		revprogress=1-hom%1.0
		zm=ActiveZodiacalMeasurement(reverse, calcs[1], houses[revhouse-1], progress=revprogress)
		planet=Planet("South Node",prefix=prefix,m=zm,retrograde=retrograde)
		entries.append(planet)
	if axes:
		ascendant=asmc[0]
		descendant=cusps[6]
		mc=asmc[1]
		ic=cusps[3]
		retrograde='Not a Planet'

		zm=ActiveZodiacalMeasurement(ascendant, 0.0, houses[0], progress=0.0)
		planet=Planet("Ascendant",prefix=prefix,m=zm,retrograde=retrograde)
		entries.append(planet)

		zm=ActiveZodiacalMeasurement(descendant, 0.0, houses[6], progress=0.0)
		planet=Planet("Descendant",prefix=prefix,m=zm,retrograde=retrograde)
		entries.append(planet)

		zm=ActiveZodiacalMeasurement(mc, 0.0, houses[9], progress=0.0)
		planet=Planet("MC",prefix=prefix,m=zm,retrograde=retrograde)
		entries.append(planet)

		zm=ActiveZodiacalMeasurement(ic, 0.0, houses[3], progress=0.0)
		planet=Planet("IC",prefix=prefix,m=zm,retrograde=retrograde)
		entries.append(planet)

	#if stars:
		#print "Todo"
	swisseph.close()
	return houses,entries

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

	sunset=revjul_to_datetime(swisseph.revjul(swisseph.rise_trans(day, \
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

