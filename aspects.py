from measurements import format_zodiacal_difference

ASPECTS = { 'conjunction': 0.0,
'semi-sextile':30.0,
'semi-square':45.0,
'sextile':60.0,
'quintile':72.0,
'square':90.0,
'trine':120.0,
'sesiquadrate':135.0,
'biquintile':144.0,
'inconjunct':150.0,
'opposition':180.0,
}

DEFAULT_ORBS = { 'conjunction': 10.0,
'semi-sextile':3.0,
'semi-square':3.0,
'sextile':6.0,
'quintile':1.0,
'square':10.0,
'trine':10.0,
'sesiquadrate':3.0,
'biquintile':1.0,
'inconjunct':3.0,
'opposition':10.0,
}

class Aspect:
	def __init__(self, p1, p2, orbs=DEFAULT_ORBS):
		if not hasattr(p1, 'm') or \
		not hasattr(p2, 'm'):
			raise ValueError, "Cannot form a relationship without measurements"
		self.planet1=p1
		self.planet2=p2
		self.orbs=orbs

	@property
	def diff(self):
		return format_zodiacal_difference(self.planet1.m.longitude, \
		self.planet2.m.longitude)

	@property
	def aspect(self):
		for i in ASPECTS:
			degrees=ASPECTS[i]
			o=self.orbs[i]
			if degrees - o <= self.diff <= degrees + o:
				return i
		return "None"

	def isForPlanet(self, string):
		return self.planet1.realName == string or self.planet2.realName == string

	def partnerPlanet(self, string):
		if self.planet1.realName == string:
			return self.planet2.realName
		elif self.planet2.realName == string:
			return self.planet1.realName
		else:
			return None

	def __repr__(self):
		return ("Planet 1 - %s | %s"
		"\nPlanet 2 - %s | %s"
		"\nRelationship - %s") \
		%(self.planet1.realName, self.planet1.m.longitude, \
		self.planet2.realName, self.planet2.m.longitude, \
		self.aspect.title())

	def __eq__(self, pr):
		if not pr:
			return False
		return self.isForPlanet(pr.planet1.realName) and self.isForPlanet(pr.planet2.realName)

	def __ne__(self, pr):
		return not self.__eq__(pr)

class SpecialAspect:
	def __init__(self, descriptors, name):
		self.descriptors=descriptors
		self.name=name

	@property
	def uniquePlanets(self):
		planets=set()
		for d in self.descriptors:
			planets.add(d.planet1.realName)
			planets.add(d.planet2.realName)
		return planets

	@property
	def uniqueMeasurements(self):
		measurements=set()
		for d in self.descriptors:
			measurements.add(d.planet1.m.longitude)
			measurements.add(d.planet2.m.longitude)
		return measurements

	def contains(self, sa):
		otherplanets=sa.uniquePlanets
		return self.uniquePlanets.intersection(otherplanets) \
		== otherplanets and len(otherplanets) \
		< len(self.uniquePlanets)

	def __eq__(self, sa):
		return self.name == sa.name and \
		self.uniquePlanets == sa.uniquePlanets
		#because they are the same points

	def __ne__(self, sa):
		return not self.__eq__(pr)

	def __hash__(self):
		return hash(frozenset(self.uniquePlanets))

	def __repr__(self):
		return "%s\nUnique angles:%s\nUnique planets:%s" \
		%(self.name.title(), [ ("%.3f" %(i)) for i in list(self.uniqueMeasurements)], list(self.uniquePlanets))