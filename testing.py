import astro_rewrite
import astro_old
from dateutil import tz;from datetime import datetime,timedelta
from chronosconfig import Observer
from collections import namedtuple

ZodiacEntry=namedtuple('ZodiacEntry','name element mode decanates')

class ZE:
	def __init__(self,name,element,mode,decanates):
		self.name=name
		self.element=element
		self.mode=mode
		self.decanates=decanates

def normal_zodiac():
	ZODIAC =({'name':'Aries',
	'element':'fire',
	'mode':'cardinal',
	'decanates':[0,4,8],},

	{'name':'Taurus',
	'element':'earth',
	'mode':'fixed',
	'decanates':[1,5,9],},

	{'name':'Gemini',
	'element':'air',
	'mode':'mutable',
	'decanates':[2,6,10],},

	{'name':'Cancer',
	'element':'water',
	'mode':'cardinal',
	'decanates':[3,7,11],},

	{'name':'Leo',
	'element':'fire',
	'mode':'fixed',
	'decanates':[4,8,0],},

	{'name':'Virgo',
	'element':'earth',
	'mode':'mutable',
	'decanates':[5,9,1],},

	{'name':'Libra',
	'element':'air',
	'mode':'cardinal',
	'decanates':[6,10,2],},

	{'name':'Scorpio',
	'element':'water',
	'mode':'fixed',
	'decanates':[7,11,3],},

	{'name':'Sagittarius',
	'element':'fire',
	'mode':'mutable',
	'decanates':[8,0,4],},

	{'name':'Capricorn',
	'element':'earth',
	'mode':'cardinal',
	'decanates':[9,1,5],},

	{'name':'Aquarius',
	'element':'air',
	'mode':'fixed',
	'decanates':[10,2,6],},

	{'name':'Pisces',
	'element':'water',
	'mode':'mutable',
	'decanates':[11,3,7],})

def zodiac_as_tuples():
	ZODIAC=(ZodiacEntry('Aries', 'fire','cardinal', [0,4,8]),
	ZodiacEntry('Taurus','earth','fixed',[1,5,9]),
	ZodiacEntry('Gemini','air','mutable',[2,6,10]),
	ZodiacEntry('Cancer','water','cardinal',[3,7,11]),
	ZodiacEntry('Leo','fire','fixed',[4,8,0]),
	ZodiacEntry('Virgo','earth','mutable',[5,9,1]),
	ZodiacEntry('Libra','air','cardinal',[6,10,2]),
	ZodiacEntry('Scorpio','water','fixed',[7,11,3]),
	ZodiacEntry('Sagittarius','fire','mutable',[8,0,4]),
	ZodiacEntry('Capricorn','earth','cardinal',[9,1,5]),
	ZodiacEntry('Aquarius','air','fixed',[10,2,6]),
	ZodiacEntry('Pisces','water','mutable',[11,3,7]),)

def zodiac_as_classes():
	ZODIAC=(ZE('Aries', 'fire','cardinal', [0,4,8]),
	ZE('Taurus','earth','fixed',[1,5,9]),
	ZE('Gemini','air','mutable',[2,6,10]),
	ZE('Cancer','water','cardinal',[3,7,11]),
	ZE('Leo','fire','fixed',[4,8,0]),
	ZE('Virgo','earth','mutable',[5,9,1]),
	ZE('Libra','air','cardinal',[6,10,2]),
	ZE('Scorpio','water','fixed',[7,11,3]),
	ZE('Sagittarius','fire','mutable',[8,0,4]),
	ZE('Capricorn','earth','cardinal',[9,1,5]),
	ZE('Aquarius','air','fixed',[10,2,6]),
	ZE('Pisces','water','mutable',[11,3,7]),)

def old_update():
	observer=Observer();observer.lat=47;observer.long=-122;observer.elevation=115.824
	date=datetime.now(tz.gettz())
	date3=datetime(1992,12,25,hour=4,minute=6, tzinfo=tz.gettz())
	signs=astro_old.get_signs(date,observer,True,True)
	signs2=astro_old.get_signs(date3,observer,True,True)
	for i in xrange(100):
		date=date+timedelta(days=1)
		signs=astro_old.get_signs(date,observer,True,True)
		aspects,c=astro_old.create_aspect_table(signs,compare=signs2)
		astro_old.search_special_aspects(c)

def new_update():
	observer=Observer();observer.lat=47;observer.long=-122;observer.elevation=115.824
	date2=datetime.now(tz.gettz())
	date3=datetime(1992,12,25,hour=4,minute=6, tzinfo=tz.gettz())
	houses,signs=astro_rewrite.get_signs(date2,observer,True,True)
	houses2,signs2=astro_rewrite.get_signs(date3,observer,True,True,prefix="Natal")
	for i in xrange(100):
		date2=date2+timedelta(days=1)
		astro_rewrite.updatePandC(date2, observer, houses, signs)
		aspects,c=astro_rewrite.create_aspect_table(signs,compare=signs2)
		astro_rewrite.search_special_aspects(c)


if __name__ == '__main__':
	from timeit import Timer
	t = Timer("old_update()", "from __main__ import old_update")
	t2 = Timer("new_update()", "from __main__ import new_update")
	print ("Old time: %s"
	"\nNew time: %s") %(t.timeit(number=1),t2.timeit(number=1))