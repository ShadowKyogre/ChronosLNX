from . import angle_sub

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

class HouseMeasurement:
	def __init__(self, lon1, lon2, num=-1):
		self.cusp=ActiveZodiacalMeasurement(lon1, 0.0, self, progress=0.0)
		self.end=ActiveZodiacalMeasurement(lon2, 0.0, self, progress=1.0)
		self.num=num

	def encompassedSigns(self):
		signs=[]
		for i in range(int(self.width/30.0)):
			signs.append(ZODIAC[(self.cusp.sign+i)%12])
		return signs

	@property
	def natRulerData(self):
		return ZODIAC[self.num-1]

	def natRulerStr(self):
		return ("Name %s"
		"\nElement: %s"
		"\nMode: %s"
		"\nDecanates: %s") %(self.natRulerData['name'],\
		self.natRulerData['element'].title(),\
		self.natRulerData['mode'].title(),\
		[ZODIAC[self.natRulerData['decanates'][0]]['name'],\
		ZODIAC[self.natRulerData['decanates'][1]]['name'],\
		ZODIAC[self.natRulerData['decanates'][2]]['name']])

	def getCuspDist(self, zd):
		return abs(angle_sub(self.cusp.longitude, zd.longitude))

	def getProgress(self,zd):
		return self.getCuspDist(zd)/self.width*100.0

	@property
	def width(self):
		return abs(angle_sub(self.cusp.longitude, self.end.longitude))

	def __str__(self):
		return ("House %s"
		"\nStarts at %s"
		"\nEnds at %s") %(self.num, self.cusp, self.end)

	def __repr__(self):
		return "HouseMeasurement({0}, {1}, num={2})".format(repr(self.cusp.longitude),
		                                             repr(self.end.longitude),
		                                             repr(self.num))

class ZodiacalMeasurement (object):
	__slots__ = ('latitude','longitude')
	def __init__(self, l, a):
		self.longitude=l%360.0
		self.latitude=a

	@property
	def sign(self):
		return int(self.longitude / 30)

	@property
	def degrees(self):
		return int(self.longitude % 30)

	@property
	def minutes(self):
		return int((self.longitude % 1.0 % 30) * 60)

	@property
	def seconds(self):
		return int(((self.longitude % 1.0 % 30) * 60) % 1.0 * 60)

	@property
	def nhouse(self):
		return self.sign+1

	@property
	def dn(self):
		return self.degrees/10

	@property
	def decanate(self):
		return self.signData['decanates'][int(self.dn)]

	@property
	def signData(self):
		return ZODIAC[self.sign]

	def dataAsText(self):
		return ("Name %s"
		"\nElement: %s"
		"\nMode: %s"
		"\nDecanates: %s") %(self.signData['name'],\
		self.signData['element'].title(),\
		self.signData['mode'].title(),\
		[ZODIAC[self.signData['decanates'][0]]['name'],\
		ZODIAC[self.signData['decanates'][1]]['name'],\
		ZODIAC[self.signData['decanates'][2]]['name']])

	@property
	def decanateData(self):
		return ZODIAC[self.decanate]

	@property
	def decstring(self):
		suffix="rd"
		if int(self.dn)==0:
			suffix="st"
		elif int(self.dn)==1:
			suffix="nd"
		return "%s%s decanate, %s" %(int(self.dn)+1,suffix,ZODIAC[self.decanate]['name'])

	def only_degs(self):
		return '%s*%s\"%s (%s)' %(self.degrees, self.minutes, self.seconds, self.decstring)

	def __str__(self):
		return '%s %s' %(ZODIAC[self.sign]['name'], self.only_degs())

	def __repr__(self):
		return "ZodiacalMeasurement({0}, {0})".format(repr(self.longitude), repr(self.latitude))

	def __eq__(self, zm):
		if not zm:
			return False
		return self.longitude==zm.longitude

class ActiveZodiacalMeasurement(ZodiacalMeasurement):
	__slots__ = ('house_info','progress')
	def __init__(self, l, a, house_info, progress=None):
		super().__init__(l,a)
		self.house_info=house_info
		self.progress=progress

	def __repr__(self):
		return "ActiveZodiacalMeasurement({0}, {1}, {2}, {3})".format(
		           repr(self.longitude),
		           repr(self.latitude),
		           repr(self.house_info),
		           repr(self.progress)
		)

	@property
	def projectedLon(self):
		if self.progress is None:
			return None
		return (self.progress * self.house_info.width) + self.house_info.cusp.longitude

	def status(self):
		return ("Natural house number: %s"
		"\nCurrent house number: %s"
		"\nCurrent house ruler: %s"
		"\nProgress away from current house cusp: %.3f%%"
		"\nProjected longitude estimate: %s") \
		%(self.nhouse,\
		self.house_info.num, \
		self.house_info.cusp.signData['name'],\
		self.progress*100.0,\
		self.projectedLon)
