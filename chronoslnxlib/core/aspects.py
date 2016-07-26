from collections import OrderedDict as od

from itertools import chain

from . import angle_sub, closed_between, filtered_groups
from .planet import PlanetMovement

ASPECTS = od([
    ('conjunction', 0.0),
    ('semi-sextile', 30.0),
    ('semi-square', 45.0),
    ('sextile', 60.0),
    ('quintile', 72.0),
    ('square', 90.0),
    ('trine', 120.0),
    ('sesiquadrate', 135.0),
    ('biquintile', 144.0),
    ('inconjunct', 150.0),
    ('opposition', 180.0),
])

DEFAULT_ORBS = od([
    ('conjunction', 10.0),
    ('semi-sextile', 3.0),
    ('semi-square', 3.0),
    ('sextile', 6.0),
    ('quintile', 1.0),
    ('square', 10.0),
    ('trine', 10.0),
    ('sesiquadrate', 3.0),
    ('biquintile', 1.0),
    ('inconjunct', 3.0),
    ('opposition', 10.0),
])

def aspect_bounds(pos, angle, orb, must_be_empty=False):
    measurements = [
       (pos + angle + i * orb) % 360
        for i in range(-1, 2, 2)
    ]
    measurements.append(must_be_empty)
    return measurements

class AspectPattern:
    def __init__(self, bounds, orbs, label):
        self.bounds = bounds
        self.orbs = orbs
        self.label = label

    def verify(self, angles):
        filtered_angles = []
        bounds_met = []

        for start, end, empty_state in self.bounds:
            vertex_list = []
            met = empty_state
            for a in angles:
                if closed_between(start, end, a):
                    if empty_state:
                        met = False
                    else:
                        vertex_list.append(
                            a if not empty_state else None
                        )
                        met = True

            bounds_met.append(met)
            if empty_state and met:
                vertex_list.append(None)
            filtered_angles.append(vertex_list)

        return filtered_angles, bounds_met

    def create_data(self, root, parts, source):
        descriptors = [
            *chain(
                (p, source[p])
                for p in chain(*parts)
                if p is not None
            )
        ]
        desc_with_root = chain(
            ( (root, source[root]), ),
            descriptors
        )
        return SpecialAspect(od(desc_with_root), self.label)

class GrandCross(AspectPattern):
    def __init__(self, angle, orbs=None):
        if orbs is None:
            orbs = DEFAULT_ORBS
        orb = DEFAULT_ORBS['square']
        opp_orb = DEFAULT_ORBS['opposition']

        behind_angles = aspect_bounds(angle, 90, orb)
        across_angles = aspect_bounds(angle, 180, opp_orb)
        ahead_angles = aspect_bounds(angle, -90, orb)
        super().__init__(
            [behind_angles, across_angles, ahead_angles],
            orbs,
            'grand cross'
        )

class TSquare(AspectPattern):
    def __init__(self, angle, orbs=None):
        if orbs is None:
            orbs = DEFAULT_ORBS
        orb = DEFAULT_ORBS['square']
        opp_orb = DEFAULT_ORBS['opposition']

        behind_angles = aspect_bounds(angle, 90, orb)
        across_angles = aspect_bounds(angle, 180, opp_orb, must_be_empty=True)
        ahead_angles = aspect_bounds(angle, -90, orb)
        super().__init__(
            [behind_angles, across_angles, ahead_angles],
            orbs,
            't-square'
        )

class Yod(AspectPattern):
    def __init__(self, angle, orbs=None):
        if orbs is None:
            orbs = DEFAULT_ORBS
        orb = DEFAULT_ORBS['inconjunct']

        behind_angles = aspect_bounds(angle, 150, orb)
        ahead_angles = aspect_bounds(angle, -150, orb)
        super().__init__(
            [behind_angles, ahead_angles],
            orbs,
            'yod'
        )

class GrandTrine(AspectPattern):
    def __init__(self, angle, orbs=None):
        if orbs is None:
            orbs = DEFAULT_ORBS
        orb = DEFAULT_ORBS['trine']

        behind_angles = aspect_bounds(angle, 120, orb)
        ahead_angles = aspect_bounds(angle, -120, orb)
        super().__init__(
            [behind_angles, ahead_angles],
            orbs,
            'grand trine'
        )

class Stellium(AspectPattern):
    def __init__(self, angle, orbs=None):
        if orbs is None:
            orbs = DEFAULT_ORBS
        orb = DEFAULT_ORBS['conjunction']

        next_to_angles = aspect_bounds(angle, 0, orb)
        super().__init__(
            [next_to_angles],
            orbs,
            'stellium'
        )

    def verify(self, angles):
        orb = self.orbs['conjunction']

        filtered_angles = sorted(
            v
            for v in angles
            for start, end, _ in self.bounds
            if closed_between(start, end, v)
        )

        subfilter = filtered_angles
        if not subfilter:
            return [[]], [False]

        starts = []
        subfilter = filtered_angles
        sub_angle = subfilter[0]
        sub_angle_to_be = float('-inf')

        while subfilter and angle_sub(sub_angle, sub_angle_to_be) > 0:
            sub_angle = subfilter[0]
            start, end, _ = aspect_bounds(sub_angle, 0, orb)
            subfilter = sorted(
                v
                for v in angles
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
            start, end, _ = aspect_bounds(sub_angle, 0, orb)
            subfilter = sorted(
                v
                for v in angles
                if closed_between(start, end, v) and v != sub_angle
            )
            try:
                sub_angle_to_be = subfilter[-1]
            except IndexError:
                sub_angle_to_be = float('-inf')
            ends.extend(subfilter)

        result = set(starts + filtered_angles + ends)
        if len(result) > 2:
            return [sorted(result),], [True]
        else:
            return [[]], [False]

def _eligible_planet(planet):
    return planet.movement not in {
        PlanetMovement.AlwaysRetrograde,
        PlanetMovement.Fake
    }

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

    aspect_patterns = [
        GrandTrine,
        GrandCross,
        TSquare,
        Yod,
        Stellium,
    ]

    sorted_angles = sorted(measurements_by_angle)

    for angle in sorted_angles:
        for pattern_cls in aspect_patterns:
            pattern = pattern_cls(angle, orbs=orbs)
            parts, all_check = pattern.verify(sorted_angles)

            all_reqs_met = all(all_check) and bool(all_check)
            if all_reqs_met:
                value = pattern.create_data(angle, parts, measurements_by_angle)
                if pattern.label == 't-square':
                    tsq.add(value)
                elif pattern.label == 'grand cross':
                    gc.add(value)
                elif pattern.label == 'grand trine':
                    gt.add(value)
                elif pattern.label == 'yod':
                    yods.add(value)
                elif pattern.label == 'stellium':
                    stel.add(value)

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
