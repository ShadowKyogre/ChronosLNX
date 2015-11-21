import swisseph

from bisect import bisect_left, bisect_right

from . import datetime_to_julian, angle_sub

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

def list_fixed_stars(date, wanted_stars=WANTED_STARS):
	output = []

	dtjul = datetime_to_julian(date)
	for star in wanted_stars:
		starpos = swisseph.fixstar_ut(star, dtjul)[0]
		output.append((star, starpos))

	output.sort(key=lambda x: x[1])
	output_keys = [x[1] for x in output]

	return output_keys, output

def nearest_fixed_star(positions, wanted_star_keys, wanted_stars,  orb=3):
	output = {}

	for pos in positions:
		closest_staridx_1 = bisect_left(wanted_star_keys, pos)
		closest_staridx_2 = bisect_right(wanted_star_keys, pos)

		closest_starpos_1 = wanted_star_keys[closest_staridx_1]
		closest_starpos_2 = wanted_star_keys[closest_staridx_2]

		dist1 = abs(angle_sub(pos, closest_starpos_2))
		dist2 = abs(angle_sub(pos, closest_starpos_1))

		in_orb1 = dist1 <= orb
		in_orb2 = dist2 <= orb

		if any((in_orb1, in_orb2)):
			if pos not in output:
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
