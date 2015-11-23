from chronoslnxlib import core as astrocore
from chronoslnxlib.core import charts
from chronoslnxlib.core.measurements import ZodiacalMeasurement

try:
	ignore_fixstars_opt = False
	from chronoslnxlib.core import fixstars
except ImportError as e:
	ignore_fixstars_opt = True

from dateutil.parser import parse as dparse
from dateutil.relativedelta import relativedelta as rdelta
from dateutil import tz

import swisseph

from argparse import ArgumentParser, Action, RawTextHelpFormatter
from collections import OrderedDict as od
import csv
from datetime import datetime
from os import path
import re
import subprocess
import sqlite3
import sys

OBSERVER_PARSE=re.compile(r'''
(?:([^:]+):) # LABEL
( # --- datetime of calculation ---
	(?:
		(?: # --- date ---
			[0-9]{4}-             # YEAR 
			(?:0[0-9]|1[0-2])-    # MONTH
			(?:[1-2][0-9]|3[0-2]) # DAY
		)
	/
		(?: # --- time ---
			(?:[2][0-3]|[01][0-9]) # HOUR
			:
			(?:[0-5][0-9])         # MINUTE
			:
			(?:[0-5][0-9])         # SECOND
		)
	)
	|
	NOW # shortcut for current DT at call
)
@
( # --- location of chart calculation ---
	-?(?:90|[0-8]?[0-9])(?:.[0-9]+)?              # LATITUDE
	,
	-?(?:180|1[0-7][0-9]|[0-9]?[0-9])(?:.[0-9]+)? # LONGITUDE
	(?:,
	-?(?:[0-9]*.[0-9]+))?                         # ELEVATION
)''', re.X)

def string_to_observer(obvstr):
	items = OBSERVER_PARSE.findall(obvstr)
	if items:
		label, dt, loc = items[0]
		loccy = loc.split(',')
		if len(loccy) == 2:
			lat, lng, elv=float(loccy[0]), float(loccy[1]), 0
		else:
			lat, lng, elv=float(loccy[0]), float(loccy[1]), float(loccy[2])
		o = astrocore.Observer(lat=lat, lng=lng, elevation=elv)
		if dt != 'NOW':
			tztmp = {o.obvdate.tzname(): o.obvdate.tzinfo}
			o.obvdate = dparse('{} {}'.format(dt, o.obvdate.tzname()), tzinfos=tztmp)

		if dt == 'NOW':
			return 'NOW_{}'.format(label), o
		else:
			return label, o
	else:
		return None, None

def nowified_label(o, o_dt):
	if o.startswith('NOW_'):
		olabel = '{}_{}'.format(o_dt.strftime('%Y-%m-%d_%H%M%S'), o[4:])
	else:
		olabel = o
	return olabel

def output_single_chart(olabel, o_dt, o_obj, output=sys.stdout,
                        planet_poses=None, houses=None, precalced_stars=None,
                        aspect_table='table', print_houses=False, fixed_stars=False):
	PHEADERS = ['Planet', 'Sign', 'Degree', 'Status', 'Retrograde?']
	HHEADERS = ['House #', 'Sign', 'Degree']
	if None in (houses, planet_poses):
		houses, planet_poses = charts.get_signs(o_dt, o_obj, True, True, prefix=olabel)
	if fixed_stars and not ignore_fixstars_opt:
		if precacled_stars is None:
			keys, outs_and_keys = fixstars.list_fixed_stars(o_dt)
		else:
			keys, outs_and_keys = precalced_stars[0], precalced_stars[1]
		print('~~~~ Planets ~~~~', file=output)
		if print_houses:
			print('\t'.join(PHEADERS+['House #', 'Fixed Stars?']), file=output)
			for planet_pos in planet_poses:
				nfixstar = fixstars.nearest_fixed_star([planet_pos.m.longitude],
				                                        keys, outs_and_keys)
				nfixstar = nfixstar.get(planet_pos.m.longitude, [])
				print('{0}\t{1}\t{2}\t{3}\t{4}\tHouse {5}\t{6}'.format(planet_pos.name,
					   planet_pos.m.signData['name'], planet_pos.m.only_degs(),
					   planet_pos.status, planet_pos.retrograde,
					   planet_pos.m.house_info.num,
					   ', '.join([fs[0] for fs in nfixstar])), file=output)
		else:
			print('\t'.join(PHEADERS+['Fixed Stars?']), file=output)
			for planet_pos in planet_poses:
				nfixstar = fixstars.nearest_fixed_star([planet_pos.m.longitude],
				                                        keys, outs_and_keys)
				nfixstar = nfixstar.get(planet_pos.m.longitude, [])
				print('{0}\t{1}\t{2}\t{3}\t{4}\t{5}'.format(planet_pos.name,
					   planet_pos.m.signData['name'], planet_pos.m.only_degs(),
					   planet_pos.status, planet_pos.retrograde,
					   ', '.join([fs[0] for fs in nfixstar])), file=output)
		if print_houses:
			print('\n~~~~ Houses ~~~~', file=output)
			print('\t'.join(HHEADERS+['Fixed Stars?']), file=output)
			for house_pos in houses:
				nfixstar = fixstars.nearest_fixed_star([house_pos.cusp.longitude],
				                                        keys, outs_and_keys)
				nfixstar = nfixstar.get(planet_pos.m.longitude, [])
				print('House {0}\t{1}\t{2}\t{3}'.format(house_pos.num,
					   house_pos.cusp.signData['name'], house_pos.cusp.only_degs(),
					   ', '.join([fs[0] for fs in nfixstar])), file=output)
		print('\n~~~~ Fixed stars ~~~~', file=output)
		print('\t'.join(['Fixed Star', 'Sign', 'Degree']), file=output)
		for output, key in outs_and_keys:
			zm = ZodiacalMeasurement(key, 0)
			print('{0}\t{1}\t{2}'.format(output, zm.signData['name'], zm.only_degs()), file=output)
	else:
		print('~~~~ Planets ~~~~', file=output)
		if print_houses:
			print('\t'.join(PHEADERS+['House #']), file=output)
			for planet_pos in planet_poses:
				print('{0}\t{1}\t{2}\t{3}\t{4}\tHouse {5}'.format(planet_pos.name,
					   planet_pos.m.signData['name'], planet_pos.m.only_degs(),
					   planet_pos.status, planet_pos.retrograde,
					   planet_pos.m.house_info.num), file=output)
		else:
			print('\t'.join(PHEADERS), file=output)
			for planet_pos in planet_poses:
				print('{0}\t{1}\t{2}\t{3}\t{4}'.format(planet_pos.name,
					   planet_pos.m.signData['name'], planet_pos.m.only_degs(),
					   planet_pos.status, planet_pos.retrograde), file=output)
		if print_houses:
			print('\n~~~~ Houses ~~~~', file=output)
			print('\t'.join(HHEADERS))
			for house_pos in houses:
				print('House {0}\t{1}\t{2}'.format(house_pos.num,
					   house_pos.cusp.signData['name'], house_pos.cusp.only_degs()), file=output)

	if aspect_table == 'table':
		print('\n~~~~ Aspect Table ~~~~', file=output)
		aspect_table = charts.create_aspect_table(planet_poses)
		headers = [planet_pos.name for planet_pos in planet_poses]
		print('\t'.join(['Aspected Planet']+headers), file=output)
		
		aspect_table_rows = od([])
		for item in aspect_table:
			if item.planet2.name not in aspect_table_rows:
				aspect_table_rows[item.planet2.name] = []

			if item.aspect is None:
				aspect_table_rows[item.planet2.name].append('No aspect')
			else:
				aspect_table_rows[item.planet2.name].append(item.aspect.title())

		for arow in aspect_table_rows:
			idx = headers.index(arow)+1
			print('{0}\t{1}'.format(arow, '\t'.join(aspect_table_rows[arow][:idx])), file=output)

	elif aspect_table == 'list':
		print('\n~~~~ Aspect List ~~~~', file=output)
		aspect_table = charts.create_aspect_table(planet_poses)
		combos = set()
		for arow in aspect_table:
			aspect_id = frozenset((arow.planet1.name, arow.planet2.name))
			if aspect_id in combos:
				continue
			if arow.aspect is not None:
				print(' '.join((arow.planet1.name, arow.aspect.title(), arow.planet2.name)), file=output)
			combos.add(aspect_id)

def output_paired_chart(pair_label,
                        houses1, planet_poses1, fixstars1,
                        houses2, planet_poses2, fixstars2,
                        output=sys.stdout,
                        aspect_table='table',
                        print_houses=False,
                        fixed_stars=False):
	prefix1 = planet_poses1[0].prefix
	prefix2 = planet_poses2[0].prefix
	if print_houses:
		print('~~~~ Cross House - {0} in {1}\'s houses ~~~~'.format(prefix1, prefix2), file=output)
		for planet_pos in planet_poses1:
			newhouse = None
			max_neg_dist = float('-inf')
			for i in range(12):
				cur_dist = astrocore.angle_sub(houses2[i].cusp.longitude, planet_pos.m.longitude)
				if cur_dist < 0 and cur_dist > max_neg_dist:
					newhouse = i
					max_neg_dist = cur_dist
			print('{0}\t{1}\'s House {2}'.format(planet_pos.realName, prefix2, newhouse+1), file=output)
		print('\n~~~~ Cross House - {1} in {0}\'s houses ~~~~'.format(prefix1, prefix2), file=output)
		for planet_pos in planet_poses2:
			newhouse = None
			max_neg_dist = float('-inf')
			for i in range(12):
				cur_dist = astrocore.angle_sub(houses1[i].cusp.longitude, planet_pos.m.longitude)
				if cur_dist < 0 and cur_dist > max_neg_dist:
					newhouse = i
					max_neg_dist = cur_dist
			print('{0}\t{1}\'s House {2}'.format(planet_pos.realName, prefix1, newhouse+1))
	
	if fixed_stars:
		print('~~~~ Cross fixed stars - {0} in {1}\'s chart ~~~~'.format(prefix1, prefix2), file=output)
		print('\n~~~~ Cross fixed stars - {1} in {0}\'s chart ~~~~'.format(prefix1, prefix2), file=output)

	if aspect_table == 'table':
		print('\n~~~~ Aspect Table ~~~~', file=output)
		_, aspect_table = charts.create_aspect_table(planet_poses1, compare=planet_poses2)
		headers = [planet_pos.realName for planet_pos in planet_poses2]
		print('\t'.join(['Aspected Planet']+headers), file=output)
		
		aspect_table_rows = od([])
		for item in aspect_table:
			#print(item.planet1.realName, item.planet2.realName, sep='::')
			if item.planet1.realName not in aspect_table_rows:
				aspect_table_rows[item.planet1.realName] = [item.planet1.realName,]
			
			if item.aspect is None:
				aspect_table_rows[item.planet1.realName].append('No aspect')
			else:
				aspect_table_rows[item.planet1.realName].append(item.aspect.title())

		for arow in aspect_table_rows:
			print('{0}'.format('\t'.join(aspect_table_rows[arow])), file=output)

	elif aspect_table == 'list':
		print('\n~~~~ Aspect List ~~~~', file=output)
		_, aspect_table = charts.create_aspect_table(planet_poses1, compare=planet_poses2)
		combos = set()
		for arow in aspect_table:
			aspect_id = frozenset((arow.planet1.realName, arow.planet2.realName))
			if aspect_id in combos:
				continue
			if arow.aspect is not None:
				print(' '.join((arow.planet1.realName, arow.aspect.title(), arow.planet2.realName)), file=output)
			combos.add(aspect_id)

# COMMAND CALLBACKS

def debug_callback(observers, args):
	if args.repr:
		for o in observers:
			o_obj = observers[o]
			print(repr(o_obj))
	else:
		for o in observers:
			o_obj = observers[o]
			print(o, o_obj.lat, o_obj.lng, o_obj.elevation, '@', o_obj.obvdate)

def radix_callback(observers, args):
	for o in observers:
		o_obj = observers[o]
		o_dt = o_obj.obvdate
		olabel = nowified_label(o, o_dt)
		out_fname = args.name_format.format(mode='radix', label=olabel)
		with open(path.join(args.output_dir, out_fname), 'w', encoding='utf-8') as ofile:
			output_single_chart(olabel, o_dt, o_obj,
			                    output=ofile,
			                    aspect_table=args.aspect_table,
			                    houses=args.houses,
			                    fixed_stars=args.fixed_stars)

def paired_callback(observers, args):
	pairings = []

	if args.pairing_file is not None:
		for pfile in args.pairing_file:
			with open(pfile, 'r', encoding='utf-8') as pf:
				csvr = csv.reader(pf, delimiter='\t')
				for row in csvr:
					pairings.append(row[:2])
	
	for pair in args.pairing_entry:
		pairings.append(pair.split(':'))

	chart_cache = od([])

	if args.pairing_mode == 'composite':
		for pair in pairings:
			o1, o2 = pair
			obv1, obv2 = observers[o1], observers[o2]
			olabel1 = nowified_label(o1, obv1.obvdate)
			olabel2 = nowified_label(o2, obv2.obvdate)

			if o1 not in chart_cache:
				o1houses, o1entries = charts.get_signs(obv1.obvdate, obv1, True, True, prefix=olabel1)
				if args.fixed_stars:
					o1stars = fixstars.list_fixed_stars(obv1.obvdate)
				else:
					o1stars = None
				chart_cache[o1] = (o1houses, o1entries, o1stars)
			else:
				o1houses, o1entries, o1stars = chart_cache[o1]

			if o2 not in chart_cache:
				o2houses, o2entries = charts.get_signs(obv2.obvdate, obv2, True, True, prefix=olabel2)
				if args.fixed_stars:
					o2stars = fixstars.list_fixed_stars(obv2.obvdate)
				else:
					o2stars = None
				chart_cache[o2] = (o2houses, o2entries, o1stars)
			else:
				o2houses, o2entries, o2stars = chart_cache[o2]

			olabel = args.pairing_label.format(first=olabel1, second=olabel2)
			houses, entries = charts.average_signs(o1houses, o1entries, o2houses, o2entries)

			if args.fixed_stars:
				pcstars = fixstars.average_fixed_stars(o1stars, o2stars)
			else:
				pcstars = None

			out_fname = args.name_format.format(mode='composite', label=pairing_label)
			with open(path.join(args.output_dir, out_fname), 'w', encoding='utf-8') as ofile:
				output_single_chart(olabel, None, None,
				                    output=ofile,
				                    houses=houses,
				                    planet_poses=entries,
				                    precalced_stars=pcstars,
				                    aspect_table=args.aspect_table,
				                    print_houses=args.houses,
				                    fixed_stars=args.fixed_stars)

	elif args.pairing_mode == 'combine':
		for pair in pairings:
			o1, o2 = pair
			obv1, obv2 = observers[o1], observers[o2]
			o_obj = obv1.average(obv2)
			olabel1 = nowified_label(o1, obv1.obvdate)
			olabel2 = nowified_label(o2, obv2.obvdate)

			olabel = args.pairing_label.format(first=olabel1, second=olabel2)

			o_dt = o_obj.obvdate
			out_fname = args.name_format.format(mode='combine', label=olabel)
			with open(path.join(args.output_dir, out_fname), 'w', encoding='utf-8') as ofile:
				output_single_chart(olabel, o_dt, o_obj,
				                    output=ofile,
				                    aspect_table=args.aspect_table,
				                    print_houses=args.houses,
				                    fixed_stars=args.fixed_stars)

	elif args.pairing_mode == 'compare':
		for pair in pairings:
			o1, o2 = pair
			obv1, obv2 = observers[o1], observers[o2]
			olabel1 = nowified_label(o1, obv1.obvdate)
			olabel2 = nowified_label(o2, obv2.obvdate)

			if o1 not in chart_cache:
				o1houses, o1entries = charts.get_signs(obv1.obvdate, obv1, True, True, prefix=olabel1)
				if args.fixed_stars:
					o1stars = fixstars.list_fixed_stars(obv1.obvdate)
				else:
					o1stars = None
				chart_cache[o1] = (o1houses, o1entries, o1stars)
			else:
				o1houses, o1entries, o1stars = chart_cache[o1]

			if o2 not in chart_cache:
				o2houses, o2entries = charts.get_signs(obv2.obvdate, obv2, True, True, prefix=olabel2)
				if args.fixed_stars:
					o2stars = fixstars.list_fixed_stars(obv2.obvdate)
				else:
					o2stars = None
				chart_cache[o2] = (o2houses, o2entries, o1stars)
			else:
				o2houses, o2entries, o2stars = chart_cache[o2]

			olabel = args.pairing_label.format(first=olabel1, second=olabel2)

			out_fname = args.name_format.format(mode='compare', label=olabel)
			with open(path.join(args.output_dir, out_fname), 'w', encoding='utf-8') as ofile:
				output_paired_chart(olabel,
				    o1houses, o1entries, o1stars,
				    o2houses, o2entries, o2stars,
				    output=ofile,
				    aspect_table=args.aspect_table,
				    print_houses=args.houses,
				    fixed_stars=args.fixed_stars)

def returns_callback(observers, args):
	bump_to_date = dparse(args.date, default=datetime.now(tz=tz.gettz()), fuzzy=True)
	ret_cache = od([])
	ret_res_cache = od([])
	if args.bump:
		for o in observers:
			o_obj = observers[o]
			if args.cbody == 'moon':
				dt_jul = astrocore.datetime_to_julian(o_obj.obvdate)
				if o not in ret_cache:
					ret_cache[o] = swisseph.calc_ut(dt_jul, swisseph.MOON)[0]
				orig_pos = ret_cache[o]
				if o not in ret_res_cache:
					ret_res_cache[o] = charts.lunar_return(bump_to_date, o_obj.obvdate, orig_pos)
				bumped_date = ret_res_cache[o]
			elif args.cbody == 'sun':
				dt_jul = astrocore.datetime_to_julian(o_obj.obvdate)
				if o not in ret_cache:
					ret_cache[o] = swisseph.calc_ut(dt_jul, swisseph.SUN)[0]
				orig_pos = ret_cache[o]
				if o not in ret_res_cache:
					ret_res_cache[o] = charts.solar_return(bump_to_date, o_obj.obvdate, orig_pos)
				bumped_date = ret_res_cache[o]
			o_obj.obvdate = bumped_date
			o_dt = o_obj.obvdate
			olabel = nowified_label(o, o_dt)
			print('{0}:{1}:{2},{3},{4}'.format(olabel,
			       o_obj.obvdate.strftime('%Y-%m-%d/%H:%M:%S'),
			       o_obj.lat, o_obj.lng, o_obj.elevation))
	else:
		for o in observers:
			o_obj = observers[o]
			if args.cbody == 'moon':
				dt_jul = astrocore.datetime_to_julian(o_obj.obvdate)
				if o not in ret_cache:
					ret_cache[o] = swisseph.calc_ut(dt_jul, swisseph.MOON)[0]
				orig_pos = ret_cache[o]
				if o not in ret_res_cache:
					ret_res_cache[o] = charts.lunar_return(bump_to_date, o_obj.obvdate, orig_pos)
				bumped_date = ret_res_cache[o]
			elif args.cbody == 'sun':
				dt_jul = astrocore.datetime_to_julian(o_obj.obvdate)
				if o not in ret_cache:
					ret_cache[o] = swisseph.calc_ut(dt_jul, swisseph.SUN)[0]
				orig_pos = ret_cache[o]
				if o not in ret_res_cache:
					ret_res_cache[o] = charts.solar_return(bump_to_date, o_obj.obvdate, orig_pos)
				bumped_date = ret_res_cache[o]
			o_obj.obvdate = bumped_date
			o_dt = o_obj.obvdate
			olabel = nowified_label(o, o_dt)
			out_fname = args.name_format.format(mode='return_{0}_{1}'.format(args.cbody, o_dt.strftime('%Y-%m-%d_%H%M%S')), label=olabel)
			with open(path.join(args.output_dir, out_fname), 'w', encoding='utf-8') as ofile:
				output_single_chart(olabel, o_dt, o_obj,
				                    output=ofile,
				                    aspect_table=args.aspect_table,
				                    print_houses=args.houses,
				                    fixed_stars=args.fixed_stars)

def progression_callback(observers, args):
	bump_to_date = dparse(args.date, default=datetime.now(tz=tz.gettz()), fuzzy=True)
	if args.bump:
		for o in observers:
			o_obj = observers[o]
			rd = rdelta(bump_to_date, o_obj.obvdate)
			o_obj.obvdate = o_obj.obvdate+rdelta(days=rd.years)
			o_dt = o_obj.obvdate
			olabel = nowified_label(o, o_dt)
			print('{0}:{1}:{2},{3},{4}'.format(olabel,
			       o_obj.obvdate.strftime('%Y-%m-%d/%H:%M:%S'),
			       o_obj.lat, o_obj.lng, o_obj.elevation))
	else:
		for o in observers:
			o_obj = observers[o]
			rd = rdelta(bump_to_date, o_obj.obvdate)
			o_obj.obvdate = o_obj.obvdate+rdelta(days=rd.years)
			o_dt = o_obj.obvdate
			olabel = nowified_label(o, o_dt)
			out_fname = args.name_format.format(mode='progression_{}'.format(o_dt.strftime('%Y-%m-%d_%H%M%S')), label=olabel)
			with open(path.join(args.output_dir, out_fname), 'w', encoding='utf-8') as ofile:
				output_single_chart(olabel, o_dt, o_obj,
				                    output=ofile,
				                    aspect_table=args.aspect_table,
				                    print_houses=args.houses,
				                    fixed_stars=args.fixed_stars)

aparser = ArgumentParser()

obs_parser = ArgumentParser(add_help=False)
obs_parser.add_argument('--observers-file', '-obvf', action='append',
                     help='Import observers from a file')
obs_parser.add_argument('--orbs-file', '-orbf',
                     help='Use orb settings from a file')
obs_parser.add_argument('observers', nargs='*',
                        help=('Additional observers to load.\n'
                              'Format is LABEL:YYYY-MM-DD/'
                              'HH:MM:SS@LAT,LNG[,ELV]\n'
                              'All times are written in '
                              'local time for that location.'))

calcs_parser = ArgumentParser(add_help=False)
calcs_parser.add_argument('--houses',         '-u', action='store_true',
                     help='Consider houses')
calcs_parser.add_argument('--fixed-stars',    '-fs', action='store_true',
                     help='Mark any found fixed stars')
calcs_parser.add_argument('--aspect-table',    '-at', default='table',
                     choices=['none', 'list', 'table'],
                     help='Mark any found fixed stars')
calcs_parser.add_argument('--name-format',    '-nf', 
                     help='Use this name format for writing files',
                     default='{mode}_-_{label}.txt')
calcs_parser.add_argument('--output-dir', '-odir', default='.',
                     help='Write files to this directory')

bumpable_parser = ArgumentParser(add_help=False)
bumpable_parser.add_argument('-d', '--date', required=True,
                             help='The date to progress the observers to')
bumpable_parser.add_argument('-b', '--bump', action='store_true',
                             help=('Bump the observers using the mandatory '
                                   'date and don\'t generate charts'))

asubparser = aparser.add_subparsers(dest='mode')

debug_parser = asubparser.add_parser('debug', parents=[obs_parser],
                                     help='Print all imported observers',
                                     formatter_class=RawTextHelpFormatter)
debug_parser.add_argument('--repr', '-r', action='store_true',
                          help='Output for pasting into a python shell')
debug_parser.set_defaults(func=debug_callback)

radix_parser = asubparser.add_parser('radix', parents=[obs_parser, calcs_parser],
                                      help='Generate charts that use one observer',
                                      formatter_class=RawTextHelpFormatter)
radix_parser.set_defaults(func=radix_callback)

paired_parser = asubparser.add_parser('paired', parents=[obs_parser, calcs_parser],
                                      help='Generate charts that use two observers',
                                      formatter_class=RawTextHelpFormatter)
paired_parser.add_argument('--pairing-entry',   '-pe',
                          help='Specify a pairing from the command line',
                          action='append')
paired_parser.add_argument('--pairing-file',   '-pf',
                          help='Import pairings from a file')
paired_parser.add_argument('--pairing-mode',   '-pm', required=True,
                          choices=['composite','combine','compare'],
                          help=('Set the pairing mode for the charts to be generated:\n'
                                'composite: Take an average of the two observers\' planet positions.\n'
                                '           This is also known as a composite chart using\n'
                                '           the midpoint-method.\n'
                                'combine:   Take an average of the two observers\' dates. \n'
                                '           This is also known as a composite chart using\n'
                                '           the reference place method.\n'
                                'compare:   Check if any planets on either observer are aspecting each other.\n'
                                '           You likely want this for synastry or transits.')
                          )
paired_parser.add_argument('--pairing-label',  '-pl',
                           help='Use this format for paired labels',
                            default='{first}_w_{second}')
paired_parser.set_defaults(func=paired_callback)

returns_parser = asubparser.add_parser('returns', 
                                       parents=[obs_parser, calcs_parser,
                                                bumpable_parser],
                                       help=('Generate charts that predict when '
                                       'a planet will be in the same position'),
                                       formatter_class=RawTextHelpFormatter)
returns_parser.add_argument('-c', '--cbody', required=True,
                            help='The celestial body to predict the return of',
                            choices=['moon', 'sun'])
returns_parser.set_defaults(func=returns_callback)

progression_parser = asubparser.add_parser('progression',
                                           parents=[obs_parser, calcs_parser,
                                                bumpable_parser],
                                           help=('Generate charts that advance observers '
                                                 'by a day per year difference'),
                                           formatter_class=RawTextHelpFormatter)
progression_parser.set_defaults(func=progression_callback)

args = aparser.parse_args()

read_observers = od([])
for observer in args.observers:
	label, o = string_to_observer(observer)
	if label is not None and label not in read_observers:
		read_observers[label]=o

if args.observers_file is not None:
	for observer_file in args.observers_file:
		mimetype = subprocess.check_output(['file', '-L', '-b', '--mime-type',
		                                    observer_file]).decode('utf-8').strip()
		if mimetype == 'text/plain':
			with open(observers_file) as fobj:
				for line in fobj:
					label, o = string_to_observer(line)
					if label is not None and label not in observers:
						read_observers[label]=o

		elif mimetype == 'application/octet-stream':
			#TODO: detect openastro sqlite specifically
			with sqlite3.connect(observer_file) as db:
				db.row_factory = sqlite3.Row
				c = db.cursor()
				for row in c.execute(('SELECT name,year,month,day,hour,'
									  'geolon,geolat from event_natal')):
					if row['name'] not in read_observers:
						o = astrocore.Observer(lat=float(row['geolat']),
							                   lng=float(row['geolon']),
							                   elevation=0)
						float_hour = float(row['hour'])
						hour = int(float_hour)
						minute = int((float_hour % 1.) * 60)
						second = int((((float_hour % 1.) * 60) % 1.) * 60)
						wip_date = datetime(year=int(row['year']), month=int(row['month']),
							                day=int(row['day']), hour=hour,
							                minute=minute, second=second,
							                tzinfo=tz.gettz('UTC'))
						o.obvdate = wip_date
						read_observers[row['name']] = o
		else:
			pass

args.func(read_observers, args)
