#!/usr/bin/python
import swisseph

from . import datetime_to_julian, revjul_to_datetime
from datetime import timedelta

#http://www.astro.com/swisseph/swephprg.htm#_Toc283735418
#http://packages.python.org/pyswisseph/
#http://www.astrologyzine.com/what-is-a-house-cusp.shtml

DAY_SEQUENCE = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
HOUR_SEQUENCE = ("Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars")

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

#i, (i+1)%12 # counter clockwise
#(i+1)%12, i # clockwise

#def update_planets(date, observer):
#notes: swisseph.TRUE_NODE
#south node = swisseph.TRUE_NODE's angle - 180

def get_sunrise_and_sunset(date, observer):
	day = datetime_to_julian(date.replace(hour=12))

	sunrise = revjul_to_datetime(swisseph.revjul(swisseph.rise_trans(day-1, swisseph.SUN, 
	                                                                 observer.lng, 
	                                                                 observer.lat, 
	                                                                 alt=observer.elevation, 
	                                                                 rsmi=swisseph.CALC_RISE)[1][0]
	                                            )
	                            ).astimezone(observer.timezone)

	sunset = revjul_to_datetime(swisseph.revjul(swisseph.rise_trans(day, swisseph.SUN, 
	                                                                observer.lng, observer.lat, 
	                                                                observer.elevation, 
	                                                                rsmi=swisseph.CALC_SET)[1][0]
	                                           )
	                           ).astimezone(observer.timezone)

	next_sunrise = revjul_to_datetime(swisseph.revjul(swisseph.rise_trans(day, swisseph.SUN, 
	                                                                      observer.lng, observer.lat, 
	                                                                      observer.elevation, 
	                                                                      rsmi=swisseph.CALC_RISE)[1][0]
	                                                 )
	                                 ).astimezone(observer.timezone)
	swisseph.close()
	return sunrise, sunset, next_sunrise

def hours_for_day(date, observer):
	sunrise, sunset, next_sunrise = get_sunrise_and_sunset(date, observer)
	if date < sunrise:
		sunrise, sunset, next_sunrise = get_sunrise_and_sunset(date.replace(hour=12)-timedelta(days=1), observer)
	day_type = int(sunrise.strftime('%w'))
	needed_planet = get_planet_day(day_type)
	day_length = sunset - sunrise
	night_length = next_sunrise - sunset
	dayhour_length = day_length/12
	nighthour_length = night_length/12
	hours = []
	for i in range(0, 12):
		hours.append([(sunrise+ i * dayhour_length), 
		              progression_check(needed_planet, i), True])
	for j in range(0, 12):
		hours.append([(sunset + j * nighthour_length), 
		              progression_check(needed_planet, j+12), False])
	return hours

def get_planet_day(day_type):
	return DAY_SEQUENCE[day_type]

def progression_check(needed_planet, hour):
	offset = HOUR_SEQUENCE.index(needed_planet)
	progress = ((hour % 7) + offset)%7
	return HOUR_SEQUENCE[progress]
