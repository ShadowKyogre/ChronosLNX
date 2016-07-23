from collections import OrderedDict as od, ChainMap
from copy import deepcopy

from .measurements import Zodiac

RTEMPLATE = {
    'dignity': [None, None],
    'exaltation': None,
}

URANIAN_RULERSHIPS = od([
    ('Sun' , {
        'dignity': [Zodiac.Leo],
        'exaltation': Zodiac.Aries,
    }),
    ('Moon', {
        'dignity': [Zodiac.Cancer],
        'exaltation': Zodiac.Taurus,
    }),
    ('Mercury', {
        'dignity': [Zodiac.Virgo, Zodiac.Gemini],
        'exaltation': Zodiac.Aquarius,
    }),
    ('Venus', {
        'dignity': [Zodiac.Libra, Zodiac.Taurus],
        'exaltation': Zodiac.Pisces,
    }),
    ('Mars', {
        'dignity': [Zodiac.Scorpio, Zodiac.Aries],
        'exaltation': Zodiac.Capricorn,
    }),
    ('Jupiter', {
        'dignity': [Zodiac.Sagittarius, Zodiac.Pisces],
        'exaltation': Zodiac.Cancer,
    }),
    ('Saturn', {
        'dignity': [Zodiac.Capricorn, Zodiac.Aquarius],
        'exaltation': Zodiac.Libra,
    }),
    ('Uranus', {
        'dignity': [Zodiac.Aquarius],
        'exaltation': Zodiac.Scorpio
    }),
    ('Neptune', {
        'dignity': [Zodiac.Pisces],
        'exaltation': Zodiac.Cancer,
    }),
    ('Pluto', {
        'dignity': [Zodiac.Scorpio],
        'exaltation': Zodiac.Leo,
    })
])

SL_URANIAN_RULERSHIPS = ChainMap({}, URANIAN_RULERSHIPS)
SL_URANIAN_RULERSHIPS['Neptune'] = deepcopy(SL_URANIAN_RULERSHIPS['Neptune'])
SL_URANIAN_RULERSHIPS['Pluto'] = deepcopy(SL_URANIAN_RULERSHIPS['Pluto'])
SL_URANIAN_RULERSHIPS['Neptune']['dignity'] = [
    Zodiac.Pisces,
    Zodiac.Sagittarius,
]
SL_URANIAN_RULERSHIPS['Pluto']['dignity'] = [
    Zodiac.Aries,
    Zodiac.Scorpio,
]

ARCHAIC = ChainMap({}, URANIAN_RULERSHIPS)
ARCHAIC['Uranus'] = RTEMPLATE
ARCHAIC['Neptune'] = RTEMPLATE
ARCHAIC['Pluto'] = RTEMPLATE

RLIST = {
  'Solar/Lunar Uranian': SL_URANIAN_RULERSHIPS,
  'Uranian': URANIAN_RULERSHIPS,
  'Classic': ARCHAIC,
}
