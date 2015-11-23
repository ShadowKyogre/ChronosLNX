from .rulerships import RLIST,RTEMPLATE
from .measurements import ZODIAC

class Planet:
	def __init__(self, name, m=None, prefix=None, table='Uranian', 
	             notes=None, retrograde=False):
		self.table = table
		rules=RLIST[table]
		self.name=name
		definition=rules.get(name, RTEMPLATE)
		self.rules=definition['dignity']
		self.exalt=definition['exaltation']
		self.prefix=prefix
		self.m=m
		self.retrograde=retrograde

	def signAsString(self,idx):
		if idx==None:
			return None
		return ZODIAC[idx]['name']

	@property
	def detriments(self):
		if None in self.rules:
			return self.rules
		return [(self.rules[0]+6)%12,\
		(self.rules[1]+6)%12]

	@property
	def fall(self):
		if self.exalt == None:
			return None
		return (self.exalt+6)%12

	@property
	def realName(self):
		if self.prefix != None:
			return "%s %s" %(self.prefix, self.name)
		else:
			return self.name

	@property
	def status(self):
		if self.m == None:
			return None
		if self.m.sign == self.fall:
			return "Fallen"
		if self.m.sign == self.exalt:
			return "Exalted"
		elif self.m.sign in self.rules:
			return "Dignified"
		elif self.m.sign in self.detriments:
			return "Detrimented"
		else:
			return None

	def stats(self):
		return ("\nRules %s"
		"\nDetriment in %s"
		"\nExalted in %s"
		"\nFall in %s") \
		%([self.signAsString(self.rules[0]),\
		self.signAsString(self.rules[1])],\
		[self.signAsString(self.detriments[0]), \
		self.signAsString(self.detriments[1])], \
		self.signAsString(self.exalt), \
		self.signAsString(self.fall))

	def __repr__(self):
		return ("Planet(name={0}, m={1}, prefix={2}, "
		        "table={3}, retrograde={4})").format(repr(self.name), repr(self.m),
		            repr(self.prefix), repr(self.table), repr(self.retrograde))

	def __str__(self):
		return ("%s"
		"%s"
		"\nMeasurements - %s"
		"\nStatus - %s"
		"\nRetrograde - %s") \
		%(self.realName, self.stats(), self.m, self.status, self.retrograde)

	def __eq__(self, planet):
		if isinstance(planet, str):
			return self.realName == planet
		elif isinstance(planet, Planet):
			return self.realName == planet.realName
		else:
			return False

	def __ne__(self, planet):
		return not self.__eq__(planet)
