from collections import OrderedDict as od
from itertools import chain

import swisseph

from . import angle_sub, closed_between, filtered_groups

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

def tsquare_angles(angle, orbs=None):
    if orbs is None:
        orbs = DEFAULT_ORBS
    orb = DEFAULT_ORBS['square']
    behind_angles = aspects_from_measurement(angle, 90, orb)
    ahead_angles = aspects_from_measurement(angle, -90, orb)
    return behind_angles, ahead_angles

def grand_cross_angles(angle, orbs=None):
    if orbs is None:
        orbs = DEFAULT_ORBS
    orb = DEFAULT_ORBS['square']
    opp_orb = DEFAULT_ORBS['opposition']

    behind_angles = aspects_from_measurement(angle, 90, orb)
    across_angles = aspects_from_measurement(angle, 180, opp_orb)
    ahead_angles = aspects_from_measurement(angle, -90, orb)
    return behind_angles, across_angles, ahead_angles

def yod_angles(angle, orbs=None):
    if orbs is None:
        orbs = DEFAULT_ORBS
    orb = DEFAULT_ORBS['inconjunct']

    behind_angles = aspects_from_measurement(angle, 150, orb)
    ahead_angles = aspects_from_measurement(angle, -150, orb)
    return behind_angles, ahead_angles

def grand_trine_angles(angle, orbs=None):
    if orbs is None:
        orbs = DEFAULT_ORBS
    orb = DEFAULT_ORBS['trine']

    behind_angles = aspects_from_measurement(angle, 120, orb)
    ahead_angles = aspects_from_measurement(angle, -120, orb)
    return behind_angles, ahead_angles

def stellarium_angles(angle, orbs=None):
    if orbs is None:
        orbs = DEFAULT_ORBS
    orb = DEFAULT_ORBS['conjunction']

    next_to_angles = aspects_from_measurement(angle, 0, orb)
    return next_to_angles,

def _eligible_planet(planet):
    return planet.retrograde not in {"Not a Planet", "Always"}

def expand_stellarium(bounds, angles, orbs=None):
    if orbs is None:
        orbs = DEFAULT_ORBS
    orb = DEFAULT_ORBS['conjunction']

    filtered_angles = sorted(
        v
        for v in angles
        for start, end in bounds
        if closed_between(start, end, v)
    )

    subfilter = filtered_angles
    if not subfilter:
        return []

    starts = []
    subfilter = filtered_angles
    sub_angle = subfilter[0]
    sub_angle_to_be = float('-inf')

    while subfilter and angle_sub(sub_angle, sub_angle_to_be) > 0:
        sub_angle = subfilter[0]
        sub_extent = stellarium_angles(sub_angle, orbs=orb)
        subfilter = sorted(
            v
            for v in angles
            for start, end in sub_extent
            if closed_between(start, end, v) and v != sub_angle
        )
        try:
            sub_angle_to_be = subfilter[0]
        except IndexError:
            sub_angle_to_be = float('inf')
        starts.extend(subfilter)

    ends = []
    subfilter = filtered_angles
    sub_angle = subfilter[-1]
    sub_angle_to_be = float('inf')

    while subfilter and angle_sub(sub_angle, sub_angle_to_be) < 0:
        sub_angle = subfilter[-1]
        sub_extent = stellarium_angles(sub_angle, orbs=orb)
        subfilter = sorted(
            v
            for v in angles
            for start, end in sub_extent
            if closed_between(start, end, v) and v != sub_angle
        )
        try:
            sub_angle_to_be = subfilter[-1]
        except IndexError:
            sub_angle_to_be = float('-inf')
        ends.extend(subfilter)

    result = set(starts + filtered_angles + ends)
    if len(result) > 2:
        return sorted(result),
    else:
        return []

def search_special_aspects(zodiac, orbs=None):
    if orbs is None:
        orbs = DEFAULT_ORBS

    yods = set()
    gt = set()
    gc = set()
    stel = set()
    tsq = set()

    measurements_by_angle = filtered_groups(
        filter(_eligible_planet, zodiac),
        lambda x: x.m.longitude
    )
    special_aspect_bound_funcs = [
        (
            grand_trine_angles,
            None,
            'grand trine',
            None,
        ),
        (
            grand_cross_angles,
            None,
            'grand cross',
            't-square',
        ),
        (
            yod_angles,
            None,
            'yod',
            None,
        ),
        (
            stellarium_angles,
            expand_stellarium,
            'stellium',
            None,
        ),
    ]
    sorted_angles = sorted(measurements_by_angle)

    for angle in sorted_angles:
        root_planets = measurements_by_angle[angle]
        for func, sanitize, label, alt_label in special_aspect_bound_funcs:
            angle_bounds = func(angle, orbs=orbs)
            if sanitize is not None:
                parts = [
                    filter(
                        lambda x: x != angle,
                        p
                    )
                    for p in sanitize(angle_bounds, sorted_angles, orbs=orbs)
                ]
            else:
                parts = [
                    [
                        v
                        for v in sorted_angles
                        if closed_between(start, end, v) and v != angle
                    ]
                    for start, end in angle_bounds
                ]
            descriptors = [
                *chain(
                    #*(
                        (p, measurements_by_angle[p])
                        for p in chain(*parts)
                    #)
                )
            ]
            all_check = [bool(p) for p in parts]
            desc_with_root = chain(
                ( (angle, root_planets), ),
                descriptors
            )
            all_reqs_met = all(all_check) and bool(all_check)
            if alt_label:
                tsq_check = (not all_check[0] and all_check[0] and all_check[2])
                if label == 'grand cross' and all_reqs_met:
                    gc.add(SpecialAspect(od(desc_with_root), label))
                elif alt_label == 't-square' and tsq_check:
                    tsq.add(SpecialAspect(od(desc_with_root), alt_label))
            elif all_reqs_met:
                if label == 'grand trine':
                    gt.add(SpecialAspect(od(desc_with_root), label))
                elif label == 'yod':
                    yods.add(SpecialAspect(od(desc_with_root), label))
                elif label == 'stellium':
                    stel.add(SpecialAspect(od(desc_with_root), label))

    return yods, gt, gc, stel, tsq

def create_aspect_table(zodiac, orbs=DEFAULT_ORBS, compare=None):
    aspect_table = []
    comparison = []

    for idx, i in enumerate(zodiac):
        for j in zodiac[idx+1:]:
            pr = Aspect(i, j, orbs)
            aspect_table.append(pr)
        if zodiac is not compare and compare is not None:
            for j in compare:
                pr = Aspect(i, j, orbs)
                comparison.append(pr)
    if comparison:
        return aspect_table, comparison
    return aspect_table

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
    def __init__(self, vertices, name):
        self.vertices = vertices
        self.name = name

    @property
    def uniquePoses(self):
        return frozenset(self.vertices.keys())

    def __eq__(self, sa):
        if sa is None:
            return False
        return self.name == sa.name and self.uniquePoses == sa.uniquePoses
        #because they are the same points

    def __ne__(self, sa):
        return not self.__eq__(sa)

    def __hash__(self):
        return hash(self.uniquePoses)

    def __repr__(self):
        return "SpecialAspect({0}, {1})".format(
            repr(self.vertices),
            repr(self.name)
        )

    def __str__(self):
        vertices_desc = ''.join(
            "{0:.3f}: {1}\n".format(
                k,
                ', '.join(p.realName for p in v)
            )
            for k, v in self.vertices.items()
        )

        return (
            "{0}"
            "\nVertices:\n{1}"
        ).format(
            self.name.title(),
            vertices_desc
        )
