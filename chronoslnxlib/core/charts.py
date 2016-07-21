from dateutil.relativedelta import relativedelta
import swisseph

import functools
import math

from . import datetime_to_julian, revjul_to_datetime
from . import date_to_moon_cycles, moon_cycles_to_jul
from . import date_to_solar_cycles, solar_cycles_to_jul
from . import angle_sub
from . import zipped_func, angle_average, filtered_groups
from .aspects import DEFAULT_ORBS, Aspect, SpecialAspect
from .measurements import (
    ActiveZodiacalMeasurement,
    HouseMeasurement,
    Zodiac
)
from .planet import Planet

def get_transit(planet, observer, date):
    day = datetime_to_julian(date)
    if observer.lat < 0:
        transit = revjul_to_datetime(
            swisseph.revjul(
                swisseph.rise_trans(
                    day-1,
                    planet,
                    observer.lng,
                    observer.lat,
                    alt=observer.elevation,
                    rsmi=swisseph.CALC_MTRANSIT
                )[1][0]
            )
        )
    else:
        transit = revjul_to_datetime(
            swisseph.revjul(
                swisseph.rise_trans(
                day-1,
                planet,
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

    wanted_aspects = filtered_groups(
        aspect_table,
        lambda x: x.aspect
    )

    trines = wanted_aspects['trine']
    squares = wanted_aspects['square']
    sextiles = wanted_aspects['sextile']
    conjunctions = wanted_aspects['conjunction']
    inconjuncts = wanted_aspects['inconjunct']
    oppositions = wanted_aspects['opposition']

    for i in range(10):
        pn = swisseph.get_planet_name(i)

        intersection_entries = []
        intersection_entries2 = []
        intersection_entries3 = []
        intersection_entries4 = []
        intersection_entries5 = []

        if len(trines) > 2:
            for i in range(len(trines)-1):
                otherp = trines[i].partnerPlanet(pn)
                otherp2 = trines[i+1].partnerPlanet(pn)
                minitrines = [
                    y for y in trines
                    if y.isForPlanet(otherp) and y.isForPlanet(otherp2)
                ]
                if not minitrines:
                    intersection_entries.append(trines[i])
                    intersection_entries.append(trines[i+1])
                for j in minitrines:
                    intersection_entries.append(j)
                if len(intersection_entries) > 2:
                    gt.add(SpecialAspect(intersection_entries, 'grand trine'))
                    break

        if len(oppositions) > 0:
            for i in range(len(squares)-1):
                otherp = squares[i].partnerPlanet(pn)
                otherp2 = squares[i+1].partnerPlanet(pn)
                miniopposition = [
                    y for y in oppositions
                    if y.isForPlanet(otherp) and y.isForPlanet(otherp2)
                ]
                minisquare = [
                    y for y in squares
                    if (y.isForPlanet(otherp) or y.isForPlanet(otherp2))
                    and not y.isForPlanet(pn)
                ]
                if miniopposition and minisquare:
                    intersection_entries2.append(squares[i])
                    intersection_entries2.append(squares[i+1])
                    intersection_entries2.append(miniopposition[0])
                    intersection_entries2.append(minisquare[0])
                    if len(intersection_entries2) > 3:
                        gc.add(SpecialAspect(intersection_entries2, 'grand cross'))
                        break

        if len(squares) > 2:
            for i in range(len(squares)-1):
                otherp = squares[i].partnerPlanet(pn)
                otherp2 = squares[i+1].partnerPlanet(pn)
                miniopposition = [
                    y for y in oppositions
                    if y.isForPlanet(otherp) and y.isForPlanet(otherp2)
                ]
                if miniopposition:
                    intersection_entries3.append(squares[i])
                    intersection_entries3.append(squares[i+1])
                for j in miniopposition:
                    intersection_entries3.append(j)
                if len(intersection_entries3) > 2:
                    tsq.add(SpecialAspect(intersection_entries3, 't-square'))
                    break

        if len(conjunctions) > 2:
            for n in conjunctions:
                #Check for other conjunctions that do not involve the root planet
                if n.planet1 != pn:
                    b=[
                       y for y in conjunctions
                       if y.isForPlanet(n.planet1) and not y.isForPlanet(pn)
                    ]
                else:
                    b=[
                       y for y in conjunctions
                       if y.isForPlanet(n.planet2) and not y.isForPlanet(pn)
                    ]
                if b:
                    intersection_entries4.append(n)
                    for j in b:
                        intersection_entries4.append(j)
                    if len(intersection_entries4) > 2:
                        stel.add(SpecialAspect(intersection_entries4, 'stellium'))
                        break

        if len(inconjuncts) > 1:
            for i in range(len(inconjuncts)-1):
                otherp=inconjuncts[i].partnerPlanet(pn)
                otherp2=inconjuncts[i+1].partnerPlanet(pn)
                minisextiles=[
                    y for y in sextiles
                    if y.isForPlanet(otherp) and y.isForPlanet(otherp2)
                ]
                if minisextiles:
                    intersection_entries5.append(inconjuncts[i])
                    intersection_entries5.append(inconjuncts[i+1])
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
    if tsq:
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
    if comparison:
        return aspect_table, comparison
    return aspect_table

def lunar_return(date, birth_date, target_angle):
    #print(repr(date), offset, target_angle)
    bdate = datetime_to_julian(birth_date)
    cycles_with_stuff = date_to_moon_cycles(date, orig_date=bdate)
    cycles = round(cycles_with_stuff)
    diff = float('inf')
    #print("---", cycles_with_stuff)
    while abs(diff) >= 1E-5:
        rejulified = moon_cycles_to_jul(cycles, orig_date=bdate)
        cur_angle = swisseph.calc_ut(rejulified, swisseph.MOON)[0]
        angle_diff = angle_sub(target_angle, cur_angle)
        #print(revjul_to_datetime(swisseph.revjul(rejulified)), cur_angle, angle_diff)
        cycles += angle_diff / 360
        diff = angle_diff
    return revjul_to_datetime(swisseph.revjul(moon_cycles_to_jul(cycles, orig_date=bdate)))

def solar_return(date, birth_date, target_angle):
    #print(repr(date), offset, target_angle)
    bdate = datetime_to_julian(birth_date)
    cycles_with_stuff = date_to_solar_cycles(date, bdate)
    cycles = round(cycles_with_stuff)
    diff = float('inf')
    #print("---", cycles_with_stuff)
    while abs(diff) >= 1E-5:
        rejulified = solar_cycles_to_jul(cycles, bdate)
        cur_angle = swisseph.calc_ut(rejulified, swisseph.SUN)[0]
        angle_diff = angle_sub(target_angle, cur_angle)
        #print(revjul_to_datetime(swisseph.revjul(rejulified)), cur_angle, angle_diff)
        cycles += angle_diff / 360
        diff = angle_diff
    return revjul_to_datetime(swisseph.revjul(solar_cycles_to_jul(cycles, bdate)))

def fill_houses(date, observer, houses=None, data=None):
    day = datetime_to_julian(date)
    if not data:
        data = swisseph.houses(day, observer.lat, observer.lng)[0]
    if houses is None:
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

def update_planets_and_cusps(date, observer, houses, entries):
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

def average_house(comp_asc, asc1, asc2, x, y):
    # we don't want to wrap for diff calc
    diff_cusp_x = x.cusp.longitude - asc1
    if diff_cusp_x < 0:
        diff_cusp_x += 360.0
    diff_cusp_y = y.cusp.longitude - asc2
    if diff_cusp_y < 0:
        diff_cusp_y += 360.0

    diff_end_x = x.end.longitude - asc1
    if diff_end_x < 0:
        diff_end_x += 360.0
    diff_end_y = y.end.longitude - asc2
    if diff_end_y < 0:
        diff_end_y += 360.0

    new_cusp_diff = (diff_cusp_x+diff_cusp_y)/2
    new_end_diff = (diff_end_x+diff_end_y)/2
    cusp_avg = comp_asc+new_cusp_diff
    #print(x.cusp.longitude, y.cusp.longitude, cusp_avg, ':', diff_cusp_x, diff_cusp_y)
    end_avg = comp_asc+new_end_diff
    h = HouseMeasurement(cusp_avg, end_avg, num=x.num)
    #print(str(h))
    #print('***')
    return h

def average_planet(houses, house_keys, x, y):
    if x.retrograde == 'Not a Planet':
        if x.name == 'Ascendant':
            newhouse = 0
        elif x.name == 'Descendant':
            newhouse = 6
        elif x.name == 'MC':
            newhouse = 9
        elif x.name == 'IC':
            newhouse = 3
        zm = ActiveZodiacalMeasurement(
            houses[newhouse].cusp.longitude,
            0,
            houses[newhouse]
        )
        zm.progress = 0
        return Planet(
            x.name,
            prefix='Composite {0} {1}'.format(x.prefix, y.prefix),
            m=zm,
            retrograde='Not a Planet'
        )
    else:
        avglong  = angle_average(x.m.longitude, y.m.longitude)
        avglat   = angle_average(x.m.latitude, y.m.latitude)
        max_neg_dist = float('-inf')
        newhouse = None
        for i in range(12):
            cur_dist = angle_sub(house_keys[i], avglong)
            if cur_dist < 0 and cur_dist > max_neg_dist:
                newhouse = i
                max_neg_dist = cur_dist
        zm = ActiveZodiacalMeasurement(avglong, avglat, houses[newhouse])
        zm.progress = houses[newhouse].getProgress(zm)
        return Planet(
            x.name,
            prefix='Composite {0} {1}'.format(x.prefix, y.prefix),
            m=zm,
            retrograde='Not Applicable'
        )

def average_signs(houses1, entries1, houses2, entries2):
    asc1 = houses1[0].cusp.longitude
    asc2 = houses2[0].cusp.longitude
    comp_asc = angle_average(asc1, asc2)
    #print(comp_asc)

    avg_house_fnc = functools.partial(average_house, comp_asc, asc1, asc2)
    houses = zipped_func(houses1, houses2, func=avg_house_fnc)

    house_keys = [house.cusp.longitude for house in houses]
    avg_planet_fnc = functools.partial(average_planet, houses, house_keys)
    
    entries = zipped_func(entries1, entries2, func=avg_planet_fnc)

    return houses, entries

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
        planet = Planet("South Node", prefix=prefix, m=zm, retrograde=retrograde)
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
    yp = Zodiac((years+ascendant.signData.decanates[0])%12).name
    return yp

def get_sun_sign(date, observer):
    sign = get_house(swisseph.SUN, observer, date)[2][1]
    swisseph.close()
    return sign
