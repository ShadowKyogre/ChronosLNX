from collections import OrderedDict as od
from copy import deepcopy

RTEMPLATE={'dignity':[None,None],
	'exaltation':None,}

URANIAN_RULERSHIPS = od(
	[('Sun' , {'dignity':[4,4],
		'exaltation':0,}),
	('Moon', {'dignity':[3,3],
		'exaltation':1,}),
	('Mercury', {'dignity':[5,2],
		'exaltation':10,}),
	('Venus', {'dignity':[6,1],
		'exaltation':11,}),
	('Mars', {'dignity':[7,0],
		'exaltation':9,}),
	('Jupiter', {'dignity':[8,11],
		'exaltation':3,}),
	('Saturn', {'dignity':[9,10],
		'exaltation':6,}),
	('Uranus', {'dignity':[10,10],
		'exaltation':7}),
	('Neptune', {'dignity':[11,11],
		'exaltation':3,}),
	('Pluto', {'dignity':[7,7],
		'exaltation':4,})])

SL_URANIAN_RULERSHIPS=deepcopy(URANIAN_RULERSHIPS)
SL_URANIAN_RULERSHIPS['Neptune']['dignity']=[11,8]
SL_URANIAN_RULERSHIPS['Pluto']['dignity']=[0,7]

ARCHAIC=deepcopy(URANIAN_RULERSHIPS)
ARCHAIC.pop('Uranus')
ARCHAIC.pop('Neptune')
ARCHAIC.pop('Pluto')

RLIST = {
  'Solar/Lunar Uranian':SL_URANIAN_RULERSHIPS,
  'Uranian':URANIAN_RULERSHIPS,
  'Classic':ARCHAIC,
  }