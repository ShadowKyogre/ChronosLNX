from datetime import datetime

from PyQt5 import QtGui, QtCore, QtWidgets

from .core.measurements import Zodiac
from .core.charts import yearly_profection
from .core.aspects import create_aspect_table

LEVELS=(('Sun', 'Moon', 'Venus', 'Mercury'),
        ('Mars', 'Jupiter', 'Saturn'),
        ('Uranus', 'Neptune', 'Pluto'),
        ('North Node', 'South Node'),
        ('Ascendant', 'Descendant', 'MC', 'IC'))

### CSS Themable Custom Widgets
'''
self.astroClock.icons=clnxcfg.main_icons
self.astroClock.sign_icons=clnxcfg.sign_icons
self.astroClock.natData=clnxcfg.natal_data
self.astroClock.bd=clnxcfg.baby.obvdate
self.astroClock.signData=[self.houses,self.zodiac]
self.astroClock.hours=self.hoursToday
self.astroClock.pluto_alternate=clnxcfg.pluto_alt
self.astroClock.capricorn_alternate=clnxcfg.capricorn_alt
self.astroClock.orbs=clnxcfg.orbs
self.astroClock.observer=clnxcfg.observer
if not clnxcfg.use_css:
    self.astroClock.init_colors()

updatePandC(self.now, clnxcfg.observer, self.houses, self.zodiac)
self.astroClock.signData=[self.houses,self.zodiac]
'''

def painterRotate(painter, degrees, point):
    painter.translate(point)
    painter.rotate(degrees)
    painter.translate(-point.x(), -point.y())

def offsetRect(bound_box, offset):
    '''
    Return a modified version of a bounding box with all sides
    adjusted by an offset

    Parameters
    ----------
    bound_box : QtCore.QRectF
        The bounding box for the arc calculation
    offset : float
        The number of pixels to adjust the bound_box's perimeters by.
    '''

    tl = QtCore.QPointF(bound_box.top(), bound_box.left())
    tl.setX(tl.x() + offset)
    tl.setY(tl.y() + offset)
    br = QtCore.QPointF(bound_box.bottom(), bound_box.right())
    br.setX(br.x() - offset)
    br.setY(br.y() - offset)
    reccy = QtCore.QRectF(tl, br)
    return reccy

def arcPointAt(bound_box, angle):
    '''
    Get the point where an angle lies on an ellipse

    Parameters
    ----------
    bound_box : QtCore.QRectF
        The bounding box for the arc calculation
    angle : float
        The angle in degrees on along the bound_box, counterclockwise

    Returns
    -------
    QtCore.QPointF
        The coordinates of the angle along the ellipse defined by bound_box
    '''
    arcs = QtGui.QPainterPath()
    arcs.arcMoveTo(bound_box, angle)
    return arcs.currentPosition()

def adjustPoint(point, angle):
    if angle < 90:
        point.setX(point.x() - 18)
    elif angle == 180:
        point.setX(point.x() + 20)
    elif angle == 270:
        point.setY(point.y() - 18)
    elif 270 > angle > 180:
        point.setX(point.x() + 0)
        point.setY(point.y() - 18)
    elif 360 >= angle > 270 or angle <= 5:
        point.setX(point.x() - 18)
        point.setY(point.y() - 18)

def createAspectDoodle(angles, bound_box):
    path = QtGui.QPainterPath()

    path.arcMoveTo(bound_box, angles[0])
    first_point = path.currentPosition()

    for i in angles:
        origin2 = path.currentPosition()
        path.arcMoveTo(bound_box, i)
        last_point = path.currentPosition()
        path.lineTo(origin2)
        path.moveTo(last_point)

    path.lineTo(first_point)
    return path

def drawSlicedEllipse(painter, circle, width=480, offset=0):
    painter.save()
    trans = QtGui.QColor("#000000")
    trans.setAlpha(0)
    painter.setBrush(trans)
    for i in range(int(5760 / width)):
        start = i * width
        painter.drawPie(circle, start + offset, width)
    painter.restore()

def drawHouses(painter, houses, circle):
    painter.save()
    trans = QtGui.QColor("#000000")
    trans.setAlpha(0)
    painter.setBrush(trans)

    offset = circle.width() / 8
    adjustedRect = offsetRect(QtCore.QRectF(circle), offset)
    for i in range(12):
        h = houses[i]
        start = h.cusp.longitude
        end = h.end.longitude
        painter.drawPie(circle, end * 16, h.width * -16)
        angle = start + h.width * 2 / 3
        placeHere = arcPointAt(
            adjustedRect,
            angle
        )
        adjustPoint(placeHere, angle)
        painter.drawText(
            QtCore.QRectF(placeHere.x(), placeHere.y(), 20, 20),
            str(i + 1)
        )
    painter.restore()

def drawZodiac(painter, circle, sign_icons=None, capricorn_alt="Capricorn"):
    if sign_icons is None:
        sign_icons = {}
    painter.save()
    adjustedRect = offsetRect(circle, -20)
    smallTickCircle = offsetRect(circle, 5)
    bigTickCircle = offsetRect(circle, 10)
    offCircle = offsetRect(circle, 1)

    for i in range(12):
        n = ( ( 12 - i ) + 4) % 12
        angle = n * 30 + 15
        p = arcPointAt(adjustedRect, angle)
        adjustPoint(p, angle)
        if n == 9:
            icon = sign_icons.get(capricorn_alt, None)
        else:
            icon = sign_icons.get(Zodiac(n).name, None)
        if icon is not None:
            icon.paint(painter, QtCore.QRect(p.x(), p.y(), 20, 20))
        for j in range(1, 30):
            tick = float(angle + j)
            if tick % 5 == 0:
                tickCircle = bigTickCircle
            else:
                tickCircle = smallTickCircle
            #print(tick, j % 15, off)
            p = arcPointAt(
                tickCircle,
                tick
            )
            p2 = arcPointAt(
                offCircle,
                tick
            )
            #self.adjustPoint(p,angle/30*30+j*6)
            #self.adjustPoint(p2,angle/30*30+j*6)
            painter.drawLine(p2, p)
    painter.restore()


def drawPlanets(painter, planets, circle, icons=None, sign_icons=None, pluto_alt=False):
    if sign_icons is None:
        sign_icons = {}

    if icons is None:
        icons = {}

    circleF = QtCore.QRectF(circle)

    for i in planets:
        if i.name in sign_icons:
            icon = sign_icons[i.name]
        else:
            if i.name == "Pluto" and pluto_alt:
                icon = icons["Pluto 2"]
            else:
                icon = icons[i.name]
        for k, j in enumerate(LEVELS):
            if i.name in j:
                level = k
                break
        off = 2 + (4 - level) * 20
        adjustedRect = offsetRect(circleF, off)
        placeHere = arcPointAt(
            adjustedRect,
            i.m.projectedLon,
        )
        adjustPoint(placeHere, i.m.projectedLon)
        icon.paint(
            painter,
            QtCore.QRect(placeHere.x(), placeHere.y(), 20, 20)
        )

def drawHours(painter, circle, phm, cur_time, next_sunrise, sun_pos, icons=None):
    if icons is None:
        icons = {}

    painter.save()
    trans = QtGui.QColor("#000000")
    trans.setAlpha(0)
    painter.setBrush(trans)
    off = cur_time - phm.get_date(0)
    overall = next_sunrise - phm.get_date(0)
    for i in range(24):
        top = phm.get_date(i) - phm.get_date(0)
        offp = off.total_seconds() / overall.total_seconds()
        percent = top.total_seconds() / overall.total_seconds()
        if i == 23:
            width = next_sunrise - phm.get_date(i)
        else:
            width = phm.get_date(i + 1) - phm.get_date(i)
        w = width.total_seconds() / overall.total_seconds() * 360
        angle = (
            360
            * (percent - offp)
            + sun_pos
        ) % 360.0
        put = (angle + w / 2) % 360
        painter.drawPie(circle, angle * 16, w * 16)
        p = arcPointAt(circle, put)
        adjustPoint(p, put)
        icon = icons.get(phm.get_planet(i))
        if icon:
            icon.paint(painter, QtCore.QRect(p.x(), p.y(), 20, 20))
    painter.restore()

class AstroClock(QtWidgets.QWidget):
    def __init__(self, *args, size=500, **kwargs):
        super().__init__(*args, **kwargs)

        self._trueSize = size + 100
        self._innerSize = size - 200
        self.setFixedSize(self._trueSize, self._trueSize)

        self.icons = None
        self.signIcons = None
        self.hourModel = None
        self.birthday = None
        self.natData = None
        self.signData = None
        self.nextSunrise = None
        self.orbs = None
        self.capricornAlternate = None
        self.plutoAlternate = None

        self._center = QtCore.QPointF(
            self._trueSize / 2,
            self._trueSize / 2
        )
        diff_pt = (
            ( size - self._innerSize) / 2
            + self._trueSize / 12
        )
        self._centerRect = QtCore.QRectF(
            self._trueSize * 17 / 40,
            self._trueSize * 17 / 40,
            90, 90
        )
        self._outerCircle = QtCore.QRect(
            self._trueSize / 12,
            self._trueSize / 12,
            size-2, size-2
        )
        self._innerCircle = QtCore.QRect(
            diff_pt, diff_pt,
            self._innerSize, self._innerSize
        )
        self._doodleBox = QtCore.QRectF(
            self._centerRect.x() + 4,
            self._centerRect.y() + 4,
            82, 82
        )
        self.init_colors()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)

    def init_colors(self):
        palette = self.palette()
        bg = QtGui.QColor(palette.color(QtGui.QPalette.Window))
        pbg = bg.lighter(250)
        prettybg = QtGui.QRadialGradient()
        prettybg.setCoordinateMode(QtGui.QGradient.ObjectBoundingMode)
        prettybg.setCenter(0.5, 0.633333333)
        prettybg.setRadius(0.3333333333)
        prettybg.setFocalPoint(0.5, 0.583333333)
        prettybg.setColorAt(0, pbg)
        prettybg.setColorAt(1, bg)

        ibg = QtGui.QColor(palette.color(QtGui.QPalette.Base))
        pibg = ibg.lighter(250)
        prettyibg = QtGui.QRadialGradient()
        prettyibg.setCoordinateMode(QtGui.QGradient.ObjectBoundingMode)
        prettyibg.setCenter(0.5, 0.683333333)
        prettyibg.setRadius(0.5)
        prettyibg.setFocalPoint(0.5, 0.583333333)
        prettyibg.setColorAt(0, pibg)
        prettyibg.setColorAt(1, ibg)

        self._outerBG = QtGui.QBrush(prettybg)
        self._outerF = QtGui.QBrush(
            palette.color(QtGui.QPalette.WindowText)
        )

        self._innerBG = QtGui.QBrush(prettyibg)
        self._innerF = QtGui.QBrush(
            palette.color(QtGui.QPalette.Text)
        )

        self._innerH = QtGui.QBrush(
            palette.color(QtGui.QPalette.WindowText)
        )
        self._outerH = QtGui.QBrush(
            palette.color(QtGui.QPalette.WindowText)
        )

        self._aspectBrushes = {
            'conjunction': QtGui.QColor(palette.color(QtGui.QPalette.BrightText)),
            'semi-sextile': QtGui.QColor(palette.color(QtGui.QPalette.BrightText)),
            'semi-square': QtGui.QColor(palette.color(QtGui.QPalette.BrightText)),
            'sextile': QtGui.QColor(palette.color(QtGui.QPalette.BrightText)),
            'quintile': QtGui.QColor(palette.color(QtGui.QPalette.BrightText)),
            'square': QtGui.QColor(palette.color(QtGui.QPalette.BrightText)),
            'trine': QtGui.QColor(palette.color(QtGui.QPalette.BrightText)),
            'sesiquadrate': QtGui.QColor(palette.color(QtGui.QPalette.BrightText)),
            'biquintile': QtGui.QColor(palette.color(QtGui.QPalette.BrightText)),
            'inconjunct': QtGui.QColor(palette.color(QtGui.QPalette.BrightText)),
            'opposition': QtGui.QColor(palette.color(QtGui.QPalette.BrightText)),
        }

    def outerFill(self):
        return self._outerBG

    def setOuterFill(self, fill):
        self._outerBG = fill

    def outerFG(self):
        return self._outerF

    def setOuterFG(self, fill):
        self._outerF = fill

    def outerHouses(self):
        return self._outerH

    def setOuterHouses(self, fill):
        self._outerH = fill

    def innerFill(self):
        return self._innerBG

    def setInnerFill(self, fill):
        self._innerBG = fill

    def innerFG(self):
        return self._innerF

    def setInnerFG(self, fill):
        self._innerF = fill

    def innerHouses(self):
        return self._innerH

    def setInnerHouses(self, fill):
        self._innerH = fill

    def aspectBrush(self, aspect):
        return self._aspectBrushes[aspect]

    def setAspectBrush(self, fill, aspect):
        self._aspectBrushes[aspect] = fill

    outerFill = QtCore.pyqtProperty(
        "QBrush", outerFill, setOuterFill
    )
    outerFG = QtCore.pyqtProperty(
        "QBrush", outerFG, setOuterFG
    )
    outerHouses = QtCore.pyqtProperty(
        "QBrush", outerHouses, setOuterHouses
    )

    innerFill = QtCore.pyqtProperty(
        "QBrush", innerFill, setInnerFill
    )
    innerFG = QtCore.pyqtProperty(
        "QBrush", innerFG, setInnerFG
    )
    innerHouses = QtCore.pyqtProperty(
        "QBrush", innerHouses, setInnerHouses
    )

    conjunction = QtCore.pyqtProperty(
        "QColor",
        lambda self: self.aspectBrush("conjunction"),
        lambda self, fill: self.setAspectBrush(fill, "conjunction")
    )
    semiSextile = QtCore.pyqtProperty(
        "QColor",
        lambda self: self.aspectBrush("semi-sextile"),
        lambda self, fill: self.setAspectBrush(fill, "semi-sextile")
    )
    semiSquare = QtCore.pyqtProperty(
        "QColor",
        lambda self: self.aspectBrush("semi-square"),
        lambda self, fill: self.setAspectBrush(fill, "semi-square")
    )
    sextile = QtCore.pyqtProperty(
        "QColor",
        lambda self: self.aspectBrush("sextile"),
        lambda self, fill: self.setAspectBrush(fill, "sextile")
    )
    quintile = QtCore.pyqtProperty(
        "QColor",
        lambda self: self.aspectBrush("quintile"),
        lambda self, fill: self.setAspectBrush(fill, "quintile")
    )
    square = QtCore.pyqtProperty(
        "QColor",
        lambda self: self.aspectBrush("square"),
        lambda self, fill: self.setAspectBrush(fill, "square")
    )
    trine = QtCore.pyqtProperty(
        "QColor",
        lambda self: self.aspectBrush("trine"),
        lambda self, fill: self.setAspectBrush(fill, "trine")
    )
    sesiquadrate = QtCore.pyqtProperty(
        "QColor",
        lambda self: self.aspectBrush("sesiquadrate"),
        lambda self, fill: self.setAspectBrush(fill, "sesiquadrate")
    )
    biquintile = QtCore.pyqtProperty(
        "QColor",
        lambda self: self.aspectBrush("biquintile"),
        lambda self, fill: self.setAspectBrush(fill, "biquintile")
    )
    inconjunct = QtCore.pyqtProperty(
        "QColor",
        lambda self: self.aspectBrush("inconjunct"),
        lambda self, fill: self.setAspectBrush(fill, "inconjunct")
    )
    opposition = QtCore.pyqtProperty(
        "QColor",
        lambda self: self.aspectBrush("opposition"),
        lambda self, fill: self.setAspectBrush(fill, "opposition")
    )


    def paintEvent(self, paintevent):
        painter = QtGui.QPainter(self)
        penifiedOFG = QtGui.QPen(self.outerFG, 0)
        penifiedOH = QtGui.QPen(self.outerHouses, 0)
        penifiedIFG = QtGui.QPen(self.innerFG, 0)
        penifiedIH = QtGui.QPen(self.innerHouses, 0)

        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(penifiedOFG)
        painter.setBrush(self.outerFill)

        hoursCircle = offsetRect(self._outerCircle, -40)
        signsCircle = offsetRect(self._outerCircle, -20)
        painter.drawEllipse(hoursCircle)
        if self.hourModel is not None and self.hourModel.rowCount() > 0:
            drawHours(
                painter,
                hoursCircle,
                self.hourModel,
                datetime.now(self.observer.timezone),
                self.nextSunrise,
                self.signData[1][0].m.projectedLon,
                icons=self.icons
            )
        painter.drawEllipse(signsCircle)
        drawSlicedEllipse(painter, signsCircle)
        drawSlicedEllipse(painter, self._outerCircle)

        painter.setPen(penifiedOH)
        drawHouses(painter, self.signData[0], self._outerCircle)

        painter.setBrush(self.innerFill)
        painter.setPen(penifiedIFG)
        painter.drawEllipse(self._innerCircle)

        drawSlicedEllipse(painter, self._innerCircle)
        painter.setPen(penifiedIH)
        drawHouses(painter, self.natData[0], self._innerCircle)

        painter.setPen(penifiedOFG)
        drawZodiac(
            painter,
            self._outerCircle,
            sign_icons=self.signIcons,
            capricorn_alt=self.capricornAlternate
        )
        painter.setPen(penifiedIFG)

        drawPlanets(
            painter,
            self.signData[1],
            self._outerCircle,
            icons=self.icons,
            sign_icons=self.signIcons,
            pluto_alt=self.plutoAlternate
        )
        drawPlanets(
            painter,
            self.natData[1],
            self._innerCircle,
            icons=self.icons,
            sign_icons=self.signIcons,
            pluto_alt=self.plutoAlternate
        )

        if self.hourModel is not None and self.hourModel.rowCount() > 0:
            dt = self.hourModel.get_planet(0)
            ic = self.icons[dt]
            ic.paint(painter, self._centerRect.toRect())

        c = create_aspect_table(self.natData[1])
        #at, compare = create_aspect_table(self.signData[1], compare=self.natData[1], orbs=self.orbs)

        for aspect in c:
            if aspect.aspect is None:
                continue
            path = createAspectDoodle(
                [
                    aspect.planet1.m.projectedLon,
                    aspect.planet2.m.projectedLon,
                ], 
               self._doodleBox
            )
            sparkles = self._aspectBrushes[aspect.aspect]
            sparkles.setAlpha(50.0)
            painter.setPen(sparkles)
            painter.drawPath(path)

        need_idx = 0
        if len(self.natData[1]) == 14:
            need_idx = 10
        elif len(self.natData[1]) == 16:
            need_idx = 12
        if need_idx > 0:
            yp = yearly_profection(
                self.observer.dt_now(),
                self.birthday,
                self.natData[1][need_idx].m
            )
            icon = self.signIcons[yp]
            painter.setPen(penifiedOFG)
            #self.theme.outer['houses'].setBrush(self.inner['fill'])
            painter.drawText(0, 12, "Yearly Profection")
            icon.paint(painter, QtCore.QRect(20, 12, 60, 60))
            #painter.save()
            #minirect=QtCore.QRect(self.size/2+4+10,self.size/2+4+10,20,20)
            #self.protate(painter,self.signData[1][0].m.projectedLon)
            ##painter.drawEllipse(minirect)
            #painter.drawConvexPolygon(QtCore.QPoint(10,self.center.y()-2),\
            #QtCore.QPoint(40,self.center.y()),\
            #QtCore.QPoint(10,self.center.y()+2),\
            #QtCore.QPoint(-5,self.center.y()))
            #painter.restore()
