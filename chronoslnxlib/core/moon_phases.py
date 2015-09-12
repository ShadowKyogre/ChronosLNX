import swisseph

from . import datetime_to_julian, revjul_to_datetime, angle_sub
from . import date_to_moon_cycles, moon_cycles_to_jul
from . import LUNAR_MONTH_DAYS, LAST_NM

### UTILITY FUNCTIONS FOR predict_phase ###

def get_moon_sun_diff(day):
	degree1 = swisseph.calc_ut(day, swisseph.MOON)[0]
	degree2 = swisseph.calc_ut(day, swisseph.SUN)[0]
	swisseph.close()
	#print(degree1, degree2)
	diff = angle_sub(degree2, degree1)
	#diff=(degree2-degree1)
	#print(degree1, degree2, revjul_to_datetime(swisseph.revjul(day)))
	return diff

### /UTILITY FUNCTIONS FOR predict_phase ###

#-90 == last quarter of last cycle
#	0 == new moon
# 90 == first quarter of current cycle
# 180 == full moon of current cycle

# use this for proofreading: http://aa.usno.navy.mil/data/docs/MoonPhase.php
def predict_phase(date, offset=0, target_angle=0):
	#print(repr(date), offset, target_angle)
	if target_angle < -90 or target_angle > 180:
		raise ValueError("No, you'll get something inaccurate...")
	cycles_with_stuff = date_to_moon_cycles(date)
	cycles = int(cycles_with_stuff)+offset
	diff = float('inf')
	while abs(diff) >= 1E-3:
		 angle_diff = get_moon_sun_diff(moon_cycles_to_jul(cycles))
		 angle_diff = angle_sub(angle_diff, target_angle)
		 #print(revjul_to_datetime(swisseph.revjul(mooncycles_to_jul(cycles))), get_moon_sun_diff(mooncycles_to_jul(cycles)), angle_diff)
		 cycles += angle_diff / 360
		 diff = angle_diff
	return revjul_to_datetime(swisseph.revjul(moon_cycles_to_jul(cycles)))

def grab_phase(date, full_m=None):
	day = datetime_to_julian(date)
	if full_m is None:
		full_m = predict_phase(date, target_angle=180)
	phase = swisseph.pheno_ut(day, swisseph.MOON)[1]*100

	if 97.0 <= phase <= 100.0:
		illumination = "Full"
	elif 0 <= phase <= 2.0:
		illumination = "New"
	elif 2.0 <= phase <= 47.0:
		illumination = "Crescent"
	elif 47.0 <= phase <= 52.0:
		illumination = "Quarter"
	else:
		illumination = "Gibbous"
	status = "Waxing"
	if date > full_m:
		status = "Waning"
	swisseph.close()
	return status, illumination, "%.3f%%" %(phase)

	#attr[0] = phase angle (earth-planet-sun)
	#attr[1] = phase (illumined fraction of disc)
	#attr[2] = elongation of planet
	#attr[3] = apparent diameter of disc
	#attr[4] = apparent magnitude

def state_to_string(state_line, planet):
	name = swisseph.get_planet_name(planet)
	if state_line[1] == "New" or state_line[1] == "Full":
		state = "%s %s" %(state_line[1], name)
	elif state_line[1] == "Quarter":
		if state_line[0] == "Waning":
			state = "Last %s %s" %(state_line[1], name)
		else:
			state = "First %s %s" %(state_line[1], name)
	else:
		state = "%s %s %s" %(state_line[0], state_line[1], name)
	swisseph.close()
	return state

def get_moon_cycle(date):
	new_m_start = predict_phase(date, target_angle=0)
	first_quarter = predict_phase(date, target_angle=-90)
	full_m = predict_phase(date, target_angle=180)
	last_quarter = predict_phase(date, offset=1, target_angle=90)
	new_m_end = predict_phase(date, offset=1, target_angle=0)

	moon_phase = []
	items = [new_m_start, first_quarter, full_m, last_quarter, new_m_end]

	for i in items:
		state_line = grab_phase(i, full_m=full_m)
		state = state_to_string(state_line, swisseph.MOON)
		moon_phase.append([i, state, state_line[2]])
	return moon_phase
