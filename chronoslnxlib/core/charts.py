import math

from dateutil.relativedelta import relativedelta
import swisseph

from . import datetime_to_julian, revjul_to_datetime
from .aspects import DEFAULT_ORBS, Aspect, SpecialAspect
from .measurements import ZodiacalMeasurement, ActiveZodiacalMeasurement, \
                          HouseMeasurement, ZODIAC
from .planet import Planet

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


def get_transit(planet, observer, date):
	day = datetime_to_julian(date)
	if observer.lat < 0:
		transit = revjul_to_datetime(swisseph.revjul(swisseph.rise_trans(day-1, planet,
		                                                               observer.lng, 
		                                                               observer.lat, 
		                                                               alt=observer.elevation, 
		                                                               rsmi=swisseph.CALC_MTRANSIT)[1][0]
		                                          )
		                          )
	else:
		transit = revjul_to_datetime(swisseph.revjul(swisseph.rise_trans(day-1, planet, 
		                                                               observer.lng, 
		                                                               observer.lat, 
		                                                               alt=observer.elevation, 
		                                                               rsmi=swisseph.CALC_ITRANSIT)[1][0]
		                                          )
		                          )
	swisseph.close()
	return transit

def search_special_aspects(aspect_table):
	yods = set()
	gt = set()
	gc = set()
	stel = set()
	tsq = set()

	for i in range(10):
		pn = swisseph.get_planet_name(i)

		trine_entries = [y for y in aspect_table \
		                 if y.isForPlanet(pn) and y.aspect == 'trine']

		square_entries = [y for y in aspect_table 
		                  if y.isForPlanet(pn) and y.aspect  == 'square']

		sextile_entries = [y for y in aspect_table \
		                   if y.isForPlanet(pn) and y.aspect  == 'sextile']

		conjunction_entries = [y for y in aspect_table \
		                       if y.isForPlanet(pn) and y.aspect  == 'conjunction']

		inconjunct_entries = [y for y in aspect_table \
		                      if y.isForPlanet(pn) and y.aspect  == 'inconjunct']

		opposition_entries = [y for y in aspect_table \
		                      if y.isForPlanet(pn) and y.aspect  == 'opposition']

		intersection_entries = []
		intersection_entries2 = []
		intersection_entries3 = []
		intersection_entries4 = []
		intersection_entries5 = []

		if len(trine_entries) > 2:
			for i in range(len(trine_entries)-1):
				otherp = trine_entries[i].partnerPlanet(pn)
				otherp2 = trine_entries[i+1].partnerPlanet(pn)
				minitrines = [y for y in aspect_table \
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
			for i in range(len(square_entries)-1):
				otherp = square_entries[i].partnerPlanet(pn)
				otherp2 = square_entries[i+1].partnerPlanet(pn)
				miniopposition = [y for y in aspect_table \
				                  if y.isForPlanet(otherp) and y.isForPlanet(otherp2) \
				                  and y.aspect == 'opposition']
				minisquare = [y for y in aspect_table \
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
			for i in range(len(square_entries)-1):
				otherp = square_entries[i].partnerPlanet(pn)
				otherp2 = square_entries[i+1].partnerPlanet(pn)
				miniopposition = [y for y in aspect_table \
				                if y.isForPlanet(otherp) and y.isForPlanet(otherp2) \
				                and y.aspect == 'opposition']
				if len(miniopposition) > 0:
					intersection_entries3.append(square_entries[i])
					intersection_entries3.append(square_entries[i+1])
				for j in miniopposition:
					intersection_entries3.append(j)
				if len(intersection_entries3) > 2:
					tsq.add(SpecialAspect(intersection_entries3, 't-square'))
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
						stel.add(SpecialAspect(intersection_entries4, 'stellium'))
						break

		if len(inconjunct_entries) > 1:
			for i in range(len(inconjunct_entries)-1):
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
					yods.add(SpecialAspect(intersection_entries5, 'yod'))
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

	return yods, gt, gc, stel, tsq

def create_aspect_table(zodiac, orbs=DEFAULT_ORBS, compare=None):
	aspect_table = []
	comparison = []

	for idx, i in enumerate(zodiac):
		for j in zodiac[idx+1:]:
			pr = Aspect(i, j, orbs)
			aspect_table.append(pr)
		if zodiac is not compare and compare is not None:
			for j in compare:
				pr = Aspect(i, j, orbs)
				comparison.append(pr)
	if len(comparison) > 0:
		return aspect_table, comparison
	return aspect_table

def solar_return(date, year, data, refinements=2): #data contains the angule, date is for a reasonable baseline
	day = datetime_to_julian(date)+(SOLAR_YEAR_DAYS*(year-date.year))

	for i in range(refinements):
		angle = swisseph.calc_ut(day, swisseph.SUN)[0]
		sec = ((data-angle)/SOLAR_DEGREE_SECOND)/SECS_TO_DAYS
		day = day+sec
	for i in range(refinements):
		angle = swisseph.calc_ut(day, swisseph.SUN)[0]
		msec = ((data-angle)/SOLAR_DEGREE_MS)/(SECS_TO_DAYS*1000)

	return revjul_to_datetime(swisseph.revjul(day+msec))

def lunar_return(date, month, year, data, refinements=2): #data contains the angle, date is for a reasonable baseline
	day = datetime_to_julian(date)
	progress, cycles = math.modf((day/LUNAR_MONTH_DAYS))

	cycles = cycles+(year-date.year)*LMONTH_IN_SYEAR
	cycles = cycles+(month-date.month)*LMONTH_TO_MONTH

	day = (cycles)*LUNAR_MONTH_DAYS

	for i in range(refinements):
		angle = swisseph.calc_ut(day, swisseph.MOON)[0]
		day = day+(data-angle)/360*LUNAR_MONTH_DAYS

	for i in range(refinements):
		angle = swisseph.calc_ut(day, swisseph.MOON)[0]
		sec = ((data-angle)/LUNAR_DEGREE_SECOND)/SECS_TO_DAYS
		day = day+sec

	for i in range(refinements):
		angle = swisseph.calc_ut(day, swisseph.MOON)[0]
		msec = ((data-angle)/LUNAR_DEGREE_MS)/(SECS_TO_DAYS*1000)
		day = day+msec

	for i in range(refinements):
		angle = swisseph.calc_ut(day, swisseph.MOON)[0]
		nsec = ((data-angle)/LUNAR_DEGREE_NS)/(SECS_TO_DAYS*1000000)
		day = day+nsec

	return revjul_to_datetime(swisseph.revjul(day))

def fill_houses(date, observer, houses=None, data=None):
	day = datetime_to_julian(date)
	if not data:
		data = swisseph.houses(day, observer.lat, observer.lng)[0]
	if houses == None:
		houses = []
		for i in range(12):
			houses.append(HouseMeasurement(data[i], data[(i+1)%12], num=i+1))
		swisseph.close()
		return houses
	else:
		for i in range(12):
			houses[i].cusp.longitude = data[i]
			houses[i].end.longitude = data[(i+1)%12]
		swisseph.close()

def updatePandC(date, observer, houses, entries):
	day = datetime_to_julian(date)
	obliquity = swisseph.calc_ut(day, swisseph.ECL_NUT)[0]
	cusps, asmc = swisseph.houses(day, observer.lat, observer.lng)
	fill_houses(date, observer, houses=houses, data=cusps)
	for i in range(10):
		calcs = swisseph.calc_ut(day, i)
		hom = swisseph.house_pos(asmc[2], observer.lat, obliquity, calcs[0], objlat=calcs[1])
		if i == swisseph.SUN or i == swisseph.MOON:
			retrograde = 'Not Applicable'
		else:
			retrograde = str(calcs[3] < 0)
		entries[i].retrograde = retrograde
		entries[i].m.longitude = calcs[0]
		entries[i].m.latitude = calcs[1]
		entries[i].m.progress = hom % 1.0
		entries[i].m.house_info = houses[int(hom-1)]
	if len(entries) > 10: #add node entries
		calcs = swisseph.calc_ut(day, swisseph.TRUE_NODE)
		hom = swisseph.house_pos(asmc[2], observer.lat, obliquity, calcs[0], objlat=calcs[1])
		retrograde = "Always"

		entries[10].retrograde = retrograde
		entries[10].m.longitude = calcs[0]
		entries[10].m.latitude = calcs[1]
		entries[10].m.progress = hom%1.0
		entries[10].m.house_info = houses[int(hom-1)]

		#do some trickery to display the South Node
		reverse = swisseph.degnorm(calcs[0]-180.0)
		revhouse = (int(hom)+6)%12
		#revprogress = 1-hom%1.0
		revprogress = hom%1.0
		entries[11].retrograde = retrograde
		entries[11].m.longitude = reverse
		entries[11].m.latitude = calcs[1]
		entries[11].m.progress = revprogress
		entries[11].m.house_info = houses[int(revhouse-1)]
	if len(entries) > 12:
		ascendant = asmc[0]
		descendant = cusps[6]
		mc = asmc[1]
		ic = cusps[3]
		retrograde = 'Not a Planet'

		entries[12].m.longitude = ascendant
		entries[13].m.longitude = descendant
		entries[14].m.longitude = mc
		entries[15].m.longitude = ic

	swisseph.close()

#ascmc[0] =     Ascendant
#ascmc[1] =     MC
#ascmc[2] =     ARMC
#ascmc[3] =     Vertex
#ascmc[4] =     "equatorial ascendant"
#ascmc[5] =     "co-ascendant" (Walter Koch)
#ascmc[6] =     "co-ascendant" (Michael Munkasey)
#ascmc[7] =     "polar ascendant" (M. Munkasey)
def get_signs(date, observer, nodes, axes, prefix=None):
	entries = []
	houses = fill_houses(date, observer)
	day = datetime_to_julian(date)
	obliquity = swisseph.calc_ut(day, swisseph.ECL_NUT)[0]

	cusps, asmc = swisseph.houses(day, observer.lat, observer.lng)

	for i in range(10):
		calcs = swisseph.calc_ut(day, i)
		hom = swisseph.house_pos(asmc[2], observer.lat, obliquity, calcs[0], objlat=calcs[1])
		zm = ActiveZodiacalMeasurement(calcs[0], calcs[1], houses[int(hom-1)], progress=hom % 1.0)
		if i == swisseph.SUN or i == swisseph.MOON:
			retrograde = 'Not Applicable'
		else:
			retrograde = str(calcs[3] < 0)
		planet = Planet(swisseph.get_planet_name(i), prefix=prefix, m=zm, retrograde=retrograde)
		entries.append(planet)
	if nodes: #add node entries
		calcs = swisseph.calc_ut(day, swisseph.TRUE_NODE)
		hom = swisseph.house_pos(asmc[2], observer.lat, obliquity, calcs[0], objlat=calcs[1])
		zm = ActiveZodiacalMeasurement(calcs[0], calcs[1], houses[int(hom-1)], progress=hom % 1.0)
		retrograde = "Always"
		planet = Planet("North Node", prefix=prefix, m=zm, retrograde=retrograde)
		entries.append(planet)

		#do some trickery to display the South Node
		reverse = swisseph.degnorm(calcs[0]+180.0)
		revhouse = (int(hom)+6) % 12
		#revprogress = 1-hom%1.0
		revprogress = hom % 1.0
		zm = ActiveZodiacalMeasurement(reverse, calcs[1], houses[revhouse-1], progress=revprogress)
		planet = Planet("South Node", prefix=prefix ,m=zm, retrograde=retrograde)
		entries.append(planet)
	if axes:
		ascendant = asmc[0]
		descendant = cusps[6]
		mc = asmc[1]
		ic = cusps[3]
		retrograde = 'Not a Planet'

		zm = ActiveZodiacalMeasurement(ascendant, 0.0, houses[0], progress=0.0)
		planet = Planet("Ascendant", prefix=prefix, m=zm, retrograde=retrograde)
		entries.append(planet)

		zm = ActiveZodiacalMeasurement(descendant, 0.0, houses[6], progress=0.0)
		planet = Planet("Descendant", prefix=prefix, m=zm, retrograde=retrograde)
		entries.append(planet)

		zm = ActiveZodiacalMeasurement(mc, 0.0, houses[9], progress=0.0)
		planet = Planet("MC", prefix=prefix, m=zm, retrograde=retrograde)
		entries.append(planet)

		zm = ActiveZodiacalMeasurement(ic, 0.0, houses[3], progress=0.0)
		planet = Planet("IC", prefix=prefix, m=zm, retrograde=retrograde)
		entries.append(planet)

	#if stars:
		#print "Todo"
	swisseph.close()
	return houses, entries

def yearly_profection(date, birthdate, ascendant):
	years = relativedelta(date, birthdate).years
	yp = ZODIAC[(years+ascendant.signData['decanates'][0])%12]['name']
	return yp

def get_sun_sign(date, observer):
	sign = get_house(swisseph.SUN, observer, date)[2][1]
	swisseph.close()
	return sign
