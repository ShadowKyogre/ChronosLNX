#!/usr/bin/python
import swisseph

from . import datetime_to_julian, revjul_to_datetime
from datetime import timedelta

#http://www.astro.com/swisseph/swephprg.htm#_Toc283735418
#http://packages.python.org/pyswisseph/
#http://www.astrologyzine.com/what-is-a-house-cusp.shtml

DAY_SEQUENCE = (
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
)

HOUR_SEQUENCE = (
    "Sun",
    "Venus",
    "Mercury",
    "Moon",
    "Saturn",
    "Jupiter",
    "Mars"
)

# http://www.guidingstar.com/Articles/Rulerships.html
# Either this or just mod Uranus, Neptune, and Pluto to have just one sign

                      ##Formalhaut
#FIXED_STARS=["Aldebaran", "Regulus", "Antares", "Fomalhaut", \#major stars
#"Alpheratz" , "Baten Kaitos", \#Aries stars
                ##Caput Algol
#"Mirach", "Hamal", "Almach", "Algol", "Alcyone", \#Taurus stars
##Hyades    #Epsilon Tauri/Northern Bull's Eye      #Polaris
#"Prima Hyadum", "Ain", "Rigel", "Bellatrix", "Capella", "Alnilam", ",alUMi", "Betelgeuse", \#gemini stars
#"Sirius","Castor","Pollux","Procyon", \#cancer stars
#"Praesepe","Alphard", \#Leo stars
#"Zosma", "Denebola", \#Virgo stars
#"Vindemiatrix", "Algorab", "Spica", "Arcturus", \#Libra stars
            ##Zuben Algenubi/North Scale    #Zuben Ashamali/South Scale
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

class AstrologicalDay:
    def __init__(self, observer, date=None):
        if date is None:
            date = observer.obvdate

        day = datetime_to_julian(date.replace(hour=12))

        check = swisseph.rise_trans(
            day-1,
            swisseph.SUN,
            observer.lng,
            observer.lat,
            observer.elevation,
            rsmi=swisseph.CALC_RISE
        )

        if check[0][0] == -2:
            raise ValueError("Observer is circumpolar!")

        sunrise = revjul_to_datetime(
            swisseph.revjul(
                check[1][0]
            )
        ).astimezone(observer.timezone)

        if date < sunrise:
            day -= 1

        self.sunrise = revjul_to_datetime(
            swisseph.revjul(
                swisseph.rise_trans(
                    day-1,
                    swisseph.SUN,
                    observer.lng,
                    observer.lat,
                    alt=observer.elevation,
                    rsmi=swisseph.CALC_RISE
                )[1][0]
            )
        ).astimezone(observer.timezone)

        self.sunset = revjul_to_datetime(
            swisseph.revjul(
                swisseph.rise_trans(
                    day,
                    swisseph.SUN,
                    observer.lng,
                    observer.lat,
                    observer.elevation,
                    rsmi=swisseph.CALC_SET
                )[1][0]
            )
        ).astimezone(observer.timezone)

        self.next_sunrise = revjul_to_datetime(
            swisseph.revjul(
                swisseph.rise_trans(
                    day,
                    swisseph.SUN,
                    observer.lng,
                    observer.lat,
                    observer.elevation,
                    rsmi=swisseph.CALC_RISE
                )[1][0]
            )
        ).astimezone(observer.timezone)
        swisseph.close()

    def hours_for_day(self):
        day_type = int(self.sunrise.strftime('%w'))
        needed_planet = get_planet_day(day_type)
        day_length = self.sunset - self.sunrise
        night_length = self.next_sunrise - self.sunset
        dayhour_length = day_length/12
        nighthour_length = night_length/12
        hours = [
            [
                self.sunrise + i * dayhour_length,
                progression_check(needed_planet, i),
                True
            ] for i in range(12)
        ]
        hours.extend(
            [
                self.sunset + i * nighthour_length,
                progression_check(needed_planet, i+12),
                False
            ] for i in range(12)
        )
        return hours

def get_planet_day(day_type):
    return DAY_SEQUENCE[day_type]

def progression_check(needed_planet, hour):
    offset = HOUR_SEQUENCE.index(needed_planet)
    progress = ((hour % 7) + offset)%7
    return HOUR_SEQUENCE[progress]
