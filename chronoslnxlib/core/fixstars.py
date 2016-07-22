import swisseph

from bisect import bisect_left, bisect_right

from . import datetime_to_julian, angle_average, zipped_func, angle_sub

# Default list of fixed stars
WANTED_STARS = [
    'Alpheratz',
    'Baten Kaitos',
    'Mirach',
    'Hamal',
    'Almach',
    'Algol',          # Caput Algol
    'Alcyone',
    'Prima Hyadum',   # Hyades (star cluster)
    'Secunda Hyadum', # Hyades (star cluster)
    'Ain',            # Epsilon Tauri
    'Aldebaran',
    'Rigel',
    'Bellatrix',
    'Capella',
    'Alnilam',
    'Polaris',
    'Betelgeuse',
    'Sirius',
    'Castor',
    'Pollux',
    'Procyon',
    'Praesepe',
    'Alphard',
    'Regulus',
    'Zosma',
    'Denebola',
    'Vindemiatrix',
    'Algorab',
    'Spica',
    'Arcturus',
    'Princeps',
    'Alphecca',
    'Zuben Elgenubi', # South scale
    'Zuben Eshamali', # North scale
    'Unukalhai',
    'Antares',
    'Lesath',
    'Aculeus',
    'Acumen',
    'Vega',
    'Deneb el Okab Australis',
    'Terebellium',
    'Altair',
    'Giedi',
    'Armus',
    'Deneb Algedi',
    'Fomalhaut',
    'Deneb Adige',
    'Achernar',
    'Markab',
    'Scheat',
]

def average_verify_fixed_star(fs1, fs2):
    if fs1[0] != fs2[0]:
        raise ValueError(("Can't average positions for different fixed stars: "
                          "{0} != {1}".format(fs1[0], fs2[0])))
    else:
        return fs1[0], angle_average(fs1[1], fs2[1])

def average_fixed_stars(fixed_stars_1, fixed_stars_2):
    fixed_stars_copy1 = fixed_stars_1[:]
    fixed_stars_copy2 = fixed_stars_2[:]

    fixed_stars_copy1.sort(key=lambda x: x[0])
    fixed_stars_copy2.sort(key=lambda x: x[0])
    # line the copies up by star name

    output = zipped_func(fixed_stars_copy1, fixed_stars_copy2, 
                         func=average_verify_fixed_star)

    output.sort(key=lambda x: x[1])
    output_keys = [x[1] for x in output]
    return output_keys, output

def list_fixed_stars(date, wanted_stars=None):
    output = []
    if wanted_stars is None:
        wanted_stars = WANTED_STARS

    dtjul = datetime_to_julian(date)
    for star in wanted_stars:
        starpos = swisseph.fixstar_ut(star, dtjul)[0]
        output.append((star, starpos))

    output.sort(key=lambda x: x[1])
    output_keys = [x[1] for x in output]

    return output_keys, output

def nearest_fixed_star(positions, wanted_star_keys, wanted_stars, orb=3):
    output = {}
    lenkeys = len(wanted_star_keys)

    for pos in positions:
        closest_staridx_1 = bisect_left(wanted_star_keys, pos)
        closest_staridx_2 = bisect_right(wanted_star_keys, pos)

        closest_starpos_1 = wanted_star_keys[closest_staridx_1]
        if closest_staridx_2 >= lenkeys:
            closest_starpos_2 = float('inf')
        else:
            closest_starpos_2 = wanted_star_keys[closest_staridx_2]

        dist1 = abs(angle_sub(pos, closest_starpos_1))
        dist2 = abs(angle_sub(pos, closest_starpos_2))

        in_orb1 = dist1 <= orb
        in_orb2 = dist2 <= orb

        if any((in_orb1, in_orb2)) and pos not in output:
            output[pos]=[]

        if all((in_orb1, in_orb2)):
            smallest = min(closest_starpos_1, closest_starpos_2)
            if smallest == closest_starpos_1:
                star = wanted_stars[closest_staridx_1]
            else:
                star = wanted_stars[closest_staridx_2]
        elif in_orb1:
            star = wanted_stars[closest_staridx_1]
        elif in_orb2:
            star = wanted_stars[closest_staridx_2]
        else:
            continue

        output[pos].append(star)

    return output
