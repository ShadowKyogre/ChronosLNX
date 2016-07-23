from enum import Enum, unique
import re

from .rulerships import RLIST,RTEMPLATE
from .measurements import Zodiac

camel_spacify = re.compile('([A-Z])([A-Z])([a-z])|([a-z])([A-Z])')

@unique
class PlanetMovement(Enum):
    Fake = -2
    AlwaysForward = -1
    Normal = 0
    Retrograde = 1
    AlwaysRetrograde = 2

    def __init__(self, value):
        self._label = None

    @property
    def label(self):
        '''
        A user friendly version of an enum's name

        Source: http://stackoverflow.com/a/15370765
        '''
        if self._label is None:
            self._label = camel_spacify.sub(r"\1\4 \2\3\5", self.name)
        return self._label

    def __repr__(self):
        return "PlanetState.{0}".format(self.name)

@unique
class PlanetState(Enum):
    Fallen = -2
    Detrimented = -1
    Normal = 0
    Dignified = 1
    Exalted = 2

class Planet:
    def __init__(self, name, m=None, prefix=None, table='Uranian', 
                 notes=None, movement=PlanetMovement.Normal):
        self.table = table
        rules=RLIST[table]
        self.name=name
        definition=rules.get(name, RTEMPLATE)
        self.rules=definition['dignity']
        self.exalt=definition['exaltation']
        self.prefix=prefix
        self.m=m
        self.movement=movement

    @property
    def detriments(self):
        if None in self.rules:
            return self.rules
        return [ (r + 6) % 12 for r in self.rules ]

    @property
    def fall(self):
        if self.exalt is None:
            return None
        return (self.exalt + 6) % 12

    @property
    def realName(self):
        if self.prefix is not None:
            return "{0} {1}".format(self.prefix, self.name)
        else:
            return self.name

    @property
    def status(self):
        if self.m is None:
            return None
        if self.m.sign == self.fall:
            return PlanetState.Fallen
        if self.m.sign == self.exalt:
            return PlanetState.Exalted
        elif self.m.sign in self.rules:
            return PlanetState.Dignified
        elif self.m.sign in self.detriments:
            return PlanetState.Detrimented
        else:
            return PlanetState.Normal

    def stats(self):
        return (
            "\nRules {0}"
            "\nDetriment in {1}"
            "\nExalted in {2}"
            "\nFall in {3}"
        ).format(
            [
                Zodiac(r) for r in self.rules if r is not None
            ],
            [
                Zodiac(d) for d in self.detriments if d is not None
            ],
            Zodiac(self.exalt) if self.exalt is not None else None,
            Zodiac(self.fall) if self.fall is not None else None
        )

    def __repr__(self):
        return (
            "Planet(name={0}, m={1}, prefix={2}, "
            "table={3}, movement={4})"
        ).format(
            repr(self.name),
            repr(self.m),
            repr(self.prefix),
            repr(self.table),
            repr(self.movement)
        )

    def __str__(self):
        return (
            "{0}"
            "{1}"
            "\nMeasurements - {2}"
            "\nStatus - {3}"
            "\nMovement - {4}"
        ).format(
            self.realName,
            self.stats(),
            self.m,
            self.status.name if self.status is not None else None,
            self.movement.label
        )

    def __eq__(self, planet):
        if isinstance(planet, str):
            return self.realName == planet
        elif isinstance(planet, Planet):
            return self.realName == planet.realName
        else:
            return False

    def __ne__(self, planet):
        return not self.__eq__(planet)
