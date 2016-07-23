from . import angle_sub

from enum import Enum, unique

@unique
class ZodiacalMode(Enum):
    Cardinal = 0
    Fixed = 1
    Mutable = 2

    def __repr__(self):
        return("ZodiacalMode.{0}".format(self.name))

@unique
class ZodiacalElement(Enum):
    Fire = 0
    Earth = 1
    Air = 2
    Water = 3

    def __repr__(self):
        return("ZodiacalElement.{0}".format(self.name))

@unique
class Zodiac(Enum):
    Aries = 0
    Taurus = 1
    Gemini = 2
    Cancer = 3
    Leo = 4
    Virgo = 5
    Libra = 6
    Scorpio = 7
    Sagittarius = 8
    Capricorn = 9
    Aquarius = 10
    Pisces = 11

    def __init__(self, value):
        self.element = ZodiacalElement(value % 4)
        self.mode = ZodiacalMode(value % 3)
        self.decanates = [ (value + i) % 12 for i in range(0, 12, 4) ]

    def __repr__(self):
        return("Zodiac.{0}".format(self.name))

    def __str__(self):
        return (
            "{0}"
            "\nElement: {1}"
            "\nMode: {2}"
            "\nDecanates: {3}"
        ).format(
           self.name,
           self.element.name.title(),
           self.mode.name.title(),
           ', '.join(
               Zodiac(d).name for d in self.decanates
           )
       )

def format_degrees(angle):
    sign = angle // 30
    degrees = angle % 30
    decanate = degrees // 10
    minutes = degrees % 1.0 * 60
    seconds = minutes % 1.0 * 60

    dec_suffix = {
        0: 'st',
        1: 'nd',
        2: 'rd'
    }.get(decanate, 'th')

    dec_sign = Zodiac((sign + decanate * 4) % 12)
    dec_string = "{0}{1} decanate, {2}".format(
        int(decanate + 1),
        dec_suffix,
        dec_sign.name
    )

    return '{0} {1}*{2}\"{3} ({4})'.format(
        Zodiac(sign).name,
        int(degrees),
        int(minutes),
        int(seconds),
        dec_string
    )

class HousePos:
    def __init__(self, cusp, end, num=-1):
        self.cusp = ActiveZodiacalPos(cusp, 0.0, self, progress=0.0)
        self.end = ActiveZodiacalPos(end, 0.0, self, progress=1.0)
        self.num =num

    def encompassedSigns(self):
        signs=[
            Zodiac((self.cusp.sign + i) % 12)
            for i in range(self.width // 30)
        ]
        return signs

    @property
    def natRulerData(self):
        return Zodiac(self.num-1)

    def natRulerStr(self):
        return str(self.natRulerData)

    def getCuspDist(self, zd):
        return abs(angle_sub(self.cusp.longitude, zd.longitude))

    def getProgress(self,zd):
        return self.getCuspDist(zd)/self.width*100.0

    @property
    def width(self):
        return abs(angle_sub(self.cusp.longitude, self.end.longitude))

    def __str__(self):
        return ("House {0}"
        "\nStarts at {1}"
        "\nEnds at {2}").format(self.num, self.cusp, self.end)

    def __repr__(self):
        return "HousePos({0}, {1}, num={2})".format(
            repr(self.cusp.longitude),
            repr(self.end.longitude),
            repr(self.num)
        )

class ZodiacalPos:
    __slots__ = ('latitude','longitude')
    def __init__(self, lng, lat):
        self.longitude = lng % 360.0
        self.latitude = lat

    @property
    def sign(self):
        return self.longitude // 30

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
        return self.degrees // 10

    @property
    def decanate(self):
        return self.signData.decanates[self.dn]

    @property
    def signData(self):
        return Zodiac(self.sign)

    def dataAsText(self):
        return str(self.signData)

    @property
    def decstring(self):
        suffix="rd"
        if int(self.dn)==0:
            suffix="st"
        elif int(self.dn)==1:
            suffix="nd"
        return "{0}{1} decanate, {2}".format(
            int(self.dn) + 1,
            suffix,
            Zodiac(self.decanate).name
        )

    def only_degs(self):
        return '{0}*{1}\"{2} ({3})'.format(
            self.degrees,
            self.minutes,
            self.seconds,
            self.decstring
        )

    def __str__(self):
        return '{0} {1}'.format(
            Zodiac(self.sign).name,
            self.only_degs()
        )

    def __repr__(self):
        return "ZodiacalPos({0}, {1})".format(
            repr(self.longitude),
            repr(self.latitude)
        )

    def __eq__(self, zm):
        if not zm:
            return False
        return self.longitude==zm.longitude

class ActiveZodiacalPos(ZodiacalPos):
    __slots__ = ('house_info', 'progress')
    def __init__(self, lng, lat, house_info, progress=None):
        super().__init__(lng, lat)
        self.house_info = house_info
        self.progress = progress

    def __repr__(self):
        return "ActiveZodiacalPos({0}, {1}, {2}, {3})".format(
           repr(self.longitude),
           repr(self.latitude),
           repr(self.house_info),
           repr(self.progress)
        )

    @property
    def projectedLon(self):
        if self.progress is None:
            return None
        return (
            (self.progress * self.house_info.width)
            + self.house_info.cusp.longitude
        )

    def status(self):
        return (
            "Natural house number: {0}"
            "\nCurrent house number: {1}"
            "\nCurrent house ruler: {2}"
            "\nProgress away from current house cusp: {3:.3f}%"
            "\nProjected longitude estimate: {4}"
        ).format(
            self.nhouse,
            self.house_info.num,
            self.house_info.cusp.signData.name,
            self.progress*100.0,
            self.projectedLon
        )
