from . import angle_sub
from collections import OrderedDict as od

import swisseph

ASPECTS = od([('conjunction', 0.0),
              ('semi-sextile', 30.0),
              ('semi-square', 45.0),
              ('sextile', 60.0),
              ('quintile', 72.0),
              ('square', 90.0),
              ('trine', 120.0),
              ('sesiquadrate', 135.0),
              ('biquintile', 144.0),
              ('inconjunct', 150.0),
              ('opposition', 180.0)])

DEFAULT_ORBS = od([('conjunction', 10.0),
                   ('semi-sextile', 3.0),
                   ('semi-square', 3.0),
                   ('sextile', 6.0),
                   ('quintile', 1.0),
                   ('square', 10.0),
                   ('trine', 10.0),
                   ('sesiquadrate', 3.0),
                   ('biquintile', 1.0),
                   ('inconjunct', 3.0),
                   ('opposition', 10.0)])

def aspects_from_measurement(measurement, angle, orb):
    measurements = [
        swisseph.degnorm(measurement + angle + i * orb)
        for i in range(-1, 2, 2)
    ]
    return measurements

def tsquare_angles(angle, orb):
    behind_angles = aspects_from_measurement(angle, 90, orb)
    ahead_angles = aspects_from_measurement(angle, -90, orb)
    return behind_angles, ahead_angles

def grand_cross_angles(angle, orb):
    behind_angles = aspects_from_measurement(angle, 90, orb)
    across_angles = aspects_from_measurement(angle, 180, orb)
    ahead_angles = aspects_from_measurement(angle, -90, orb)
    return behind_angles, across_angles, ahead_angles

def yod_angles(angle, orb):
    behind_angles = aspects_from_measurement(angle, 150, orb)
    ahead_angles = aspects_from_measurement(angle, -150, orb)
    return behind_angles, ahead_angles

def grand_trine_angles(angle, orb):
    behind_angles = aspects_from_measurement(angle, 120, orb)
    ahead_angles = aspects_from_measurement(angle, -120, orb)
    return behind_angles, ahead_angles

class Aspect:
    def __init__(self, p1, p2, orbs=DEFAULT_ORBS):
        if not hasattr(p1, 'm') or not hasattr(p2, 'm'):
            raise ValueError("Cannot form a relationship without measurements")
        self.planet1=p1
        self.planet2=p2
        self.orbs=orbs

    @property
    def diff(self):
        return abs(angle_sub(self.planet1.m.projectedLon, self.planet2.m.projectedLon))

    @property
    def aspect(self):
        for i in ASPECTS:
            degrees = ASPECTS[i]
            o = self.orbs[i]
            if degrees - o <= self.diff <= degrees + o:
                return i
        return None

    def isForPlanet(self, planet):
        return self.planet1 == planet or self.planet2 == planet

    def partnerPlanet(self, planet):
        if self.planet1 == planet:
            return self.planet2.realName
        elif self.planet2 == planet:
            return self.planet1.realName
        else:
            return None

    def __str__(self):
        return (
            "Planet 1 - {0} | {1}"
            "\nPlanet 2 - {2} | {3}"
            "\nRelationship - {4}"
            ).format(
                self.planet1.realName, self.planet1.m.longitude,
                self.planet2.realName, self.planet2.m.longitude,
                self.aspect.title() if self.aspect is not None else "No aspect"
            )

    def __repr__(self):
        return "Aspect({0}, {1}, orbs={2})".format(repr(self.planet1),
                                                   repr(self.planet2),
                                                   repr(self.orbs))

    def __eq__(self, pr):
        if not pr:
            return False
        return self.isForPlanet(pr.planet1.realName) and self.isForPlanet(pr.planet2.realName)

    def __ne__(self, pr):
        return not self.__eq__(pr)

class SpecialAspect:
    def __init__(self, root_planets, descriptors, name):
        self.root_planets = root_planets
        self.descriptors = descriptors
        self.name = name

    @property
    def uniquePlanets(self):
        planets = set()
        for d in self.descriptors:
            planets.add(d.realName)
        return planets

    @property
    def uniqueMeasurements(self):
        measurements = set()
        for d in self.descriptors:
            measurements.add(d.m.longitude)
        return measurements

    def contains(self, sa):
        otherplanets = sa.uniquePlanets
        return otherplanets.issubset(self.uniquePlanets)

    def __eq__(self, sa):
        if sa is None:
            return False
        return self.name == sa.name and self.uniquePlanets == sa.uniquePlanets
        #because they are the same points

    def __ne__(self, sa):
        return not self.__eq__(sa)

    def __hash__(self):
        return hash(frozenset(self.uniquePlanets))

    def __repr__(self):
        "SpecialAspect({0}, {1}, {2})".format(
            repr(self.root_planets),
            repr(self.descriptors),
            repr(self.name)
        )

    def __str__(self):
        return (
            "{0}"
            "\nInitiating planets:{1}"
            "\nInitiating measurements:{2}"
            "\nUnique angles:{3}"
            "\nUnique planets:{4}"
        ).format(
            self.name.title(),
            [ p.realName for p in self.root_planets ],
            [ p.m.longitude for p in self.root_planets ],
            [ "{0:.3f}".format(i) for i in list(self.uniqueMeasurements)],
            list(self.uniquePlanets)
        )
