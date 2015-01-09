from PyQt4 import QtGui, QtCore
from datetime import datetime
from dateutil.relativedelta import relativedelta

from .measurements import ZODIAC
from .astro_rewrite import create_aspect_table, yearly_profection

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

class AstroClock(QtGui.QWidget):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.size = 500
		self.true_size = self.size+100
		self.inner_size = self.size-200
		self.setFixedSize(self.true_size, self.true_size)
		self.center = QtCore.QPointF(self.true_size/2, self.true_size/2)
		self.diff = (self.size-self.inner_size)/2+self.true_size/12
		self.centerRect = QtCore.QRectF(self.true_size*17/40,
		                                self.true_size*17/40, 90, 90)
		self.outer_circle = QtCore.QRect(self.true_size/12, self.true_size/12,
		                                 self.size-2, self.size-2)
		self.inner_circle = QtCore.QRect(self.diff, self.diff, self.inner_size, self.inner_size)
		self.doodle_box = QtCore.QRectF(self.centerRect.x()+4, self.centerRect.y()+4, 82, 82)
		self.init_colors()
		self.timer = QtCore.QTimer(self)
		self.connect(self.timer, QtCore.SIGNAL("timeout()"), self, QtCore.SLOT("update()"))
		self.timer.start(1000)

	def init_colors(self):
		bg = QtGui.QColor(self.palette().color(QtGui.QPalette.Window))
		pbg = bg.lighter(250)
		prettybg = QtGui.QRadialGradient()
		prettybg.setCoordinateMode(QtGui.QGradient.ObjectBoundingMode)
		prettybg.setCenter(0.5, 0.633333333)
		prettybg.setRadius(0.3333333333)
		prettybg.setFocalPoint(0.5, 0.583333333)
		prettybg.setColorAt(0, pbg)
		prettybg.setColorAt(1, bg)

		ibg = QtGui.QColor(self.palette().color(QtGui.QPalette.Base))
		pibg = ibg.lighter(250)
		prettyibg = QtGui.QRadialGradient()
		prettyibg.setCoordinateMode(QtGui.QGradient.ObjectBoundingMode)
		prettyibg.setCenter(0.5, 0.683333333)
		prettyibg.setRadius(0.5)
		prettyibg.setFocalPoint(0.5, 0.583333333)
		prettyibg.setColorAt(0, pibg)
		prettyibg.setColorAt(1, ibg)

		self.__outerBG = QtGui.QBrush(prettybg)
		self.__outerF = QtGui.QBrush(QtGui.QColor(self.palette().color(QtGui.QPalette.WindowText)))

		self.__innerBG = QtGui.QBrush(prettyibg)
		self.__innerF = QtGui.QBrush(QtGui.QColor(self.palette().color(QtGui.QPalette.Text)))

		self.__innerH = QtGui.QBrush(QtGui.QColor(self.palette().color(QtGui.QPalette.WindowText)))
		self.__outerH = QtGui.QBrush(QtGui.QColor(self.palette().color(QtGui.QPalette.WindowText)))

		self.__aspectBrushes = {'conjunction': QtGui.QColor(self.palette().color(QtGui.QPalette.BrightText)),
		                        'semi-sextile': QtGui.QColor(self.palette().color(QtGui.QPalette.BrightText)),
		                        'semi-square': QtGui.QColor(self.palette().color(QtGui.QPalette.BrightText)),
		                        'sextile': QtGui.QColor(self.palette().color(QtGui.QPalette.BrightText)),
		                        'quintile': QtGui.QColor(self.palette().color(QtGui.QPalette.BrightText)),
		                        'square': QtGui.QColor(self.palette().color(QtGui.QPalette.BrightText)),
		                        'trine': QtGui.QColor(self.palette().color(QtGui.QPalette.BrightText)),
		                        'sesiquadrate': QtGui.QColor(self.palette().color(QtGui.QPalette.BrightText)),
		                        'biquintile': QtGui.QColor(self.palette().color(QtGui.QPalette.BrightText)),
		                        'inconjunct': QtGui.QColor(self.palette().color(QtGui.QPalette.BrightText)),
		                        'opposition': QtGui.QColor(self.palette().color(QtGui.QPalette.BrightText)),}

	def __outerFill(self):
		return self.__outerBG

	def __setOuterFill(self, fill):
		self.__outerBG = fill

	def __outerFG(self):
		return self.__outerF

	def __setOuterFG(self, fill):
		self.__outerF = fill

	def __outerHouses(self):
		return self.__outerH

	def __setOuterHouses(self, fill):
		self.__outerH = fill

	def __innerFill(self):
		return self.__innerBG

	def __setInnerFill(self, fill):
		self.__innerBG = fill

	def __innerFG(self):
		return self.__innerF

	def __setInnerFG(self, fill):
		self.__innerF = fill

	def __innerHouses(self):
		return self.__innerH

	def __setInnerHouses(self, fill):
		self.__innerH = fill

	def __aspectBrush(self, aspect):
		return self.__aspectBrushes[aspect]

	def __setAspectBrush(self, fill, aspect):
		self.__aspectBrushes[aspect] = fill

	outerFill = QtCore.pyqtProperty("QBrush", __outerFill, __setOuterFill)
	outerFG = QtCore.pyqtProperty("QBrush", __outerFG, __setOuterFG)
	outerHouses = QtCore.pyqtProperty("QBrush", __outerHouses, __setOuterHouses)

	innerFill = QtCore.pyqtProperty("QBrush", __innerFill, __setInnerFill)
	innerFG = QtCore.pyqtProperty("QBrush", __innerFG, __setInnerFG)
	innerHouses = QtCore.pyqtProperty("QBrush", __innerHouses, __setInnerHouses)

	conjunction = QtCore.pyqtProperty("QColor", lambda self: self.__aspectBrush("conjunction"), 
	                                  lambda self, fill: self.__setAspectBrush(fill, "conjunction"))
	semiSextile = QtCore.pyqtProperty("QColor", lambda self: self.__aspectBrush("semi-sextile"), 
	                                  lambda self, fill: self.__setAspectBrush(fill, "semi-sextile"))
	semiSquare = QtCore.pyqtProperty("QColor", lambda self: self.__aspectBrush("semi-square"), 
	                                 lambda self, fill: self.__setAspectBrush(fill, "semi-square"))
	sextile = QtCore.pyqtProperty("QColor", lambda self: self.__aspectBrush("sextile"), 
	                              lambda self, fill: self.__setAspectBrush(fill, "sextile"))
	quintile = QtCore.pyqtProperty("QColor", lambda self: self.__aspectBrush("quintile"), 
	                               lambda self, fill: self.__setAspectBrush(fill, "quintile"))
	square = QtCore.pyqtProperty("QColor", lambda self: self.__aspectBrush("square"), 
	                             lambda self, fill: self.__setAspectBrush(fill, "square"))
	trine = QtCore.pyqtProperty("QColor", lambda self: self.__aspectBrush("trine"), 
	                            lambda self, fill: self.__setAspectBrush(fill, "trine"))
	sesiquadrate = QtCore.pyqtProperty("QColor", lambda self: self.__aspectBrush("sesiquadrate"), 
	                                   lambda self, fill: self.__setAspectBrush(fill, "sesiquadrate"))
	biquintile = QtCore.pyqtProperty("QColor", lambda self: self.__aspectBrush("biquintile"), 
	                                 lambda self, fill: self.__setAspectBrush(fill, "biquintile"))
	inconjunct = QtCore.pyqtProperty("QColor", lambda self: self.__aspectBrush("inconjunct"), 
	                                 lambda self, fill: self.__setAspectBrush(fill, "inconjunct"))
	opposition = QtCore.pyqtProperty("QColor", lambda self: self.__aspectBrush("opposition"), 
	                                 lambda self, fill: self.__setAspectBrush(fill, "opposition"))

	def setHourSource(self, hours):
		self.hours = hours

	def setNextSunrise(self, date):
		self.nexts = date

	def setBD(self, date):
		self.bd = date

	def setNatData(self, natData):
		self.natData = natData

	def setSignData(self, signData):
		self.signData = signData

	def setSignIcons(self, icons):
		self.sign_icons = icons

	def setIcons(self, icons):
		self.icons = icons

	def setOrbs(self, orbs):
		self.orbs = orbs

	def setCapricornAlternate(self, cap_alt):
		self.capricorn_alternate = cap_alt

	def setPlutoAlternate(self, plu_alt):
		self.pluto_alternate = plu_alt

	def createAspectDoodle(self, angles, bound_box):
		path = QtGui.QPainterPath()

		path.arcMoveTo(bound_box, angles[0])
		first_point = path.currentPosition()

		for i in angles:
			origin2 = path.currentPosition()
			path.arcMoveTo (bound_box, i)
			last_point = path.currentPosition()
			path.lineTo(origin2)
			path.moveTo(last_point)

		path.lineTo(first_point)
		return path

	def getOffRect(self, circle, offset):
		tl = QtCore.QPointF(circle.top(), circle.left())
		tl.setX(tl.x()+offset)
		tl.setY(tl.y()+offset)
		br = QtCore.QPointF(circle.bottom(), circle.right())
		br.setX(br.x()-offset)
		br.setY(br.y()-offset)
		reccy = QtCore.QRectF(tl, br)
		return reccy

	def getPointAt(self, circle, angle, offset=0):
		arcs = QtGui.QPainterPath()
		if offset != 0:
			reccy = self.getOffRect(circle, offset)
			arcs.arcMoveTo(reccy, angle)
		else:
			arcs.arcMoveTo(circle, angle)
		return arcs.currentPosition()

	def adjustPoint(self, point, angle):
		if angle < 90:
			point.setX(point.x()-18)
		elif angle == 180:
			point.setX(point.x()+20)
		elif angle == 270:
			point.setY(point.y()-18)
		elif 270 > angle > 180:
			point.setX(point.x()+0)
			point.setY(point.y()-18)
		elif 360 >= angle > 270 or angle <= 5:
			point.setX(point.x()-18)
			point.setY(point.y()-18)

	def drawPlanets(self, painter, planets, circle):
		for i in planets:
			if i.name in self.sign_icons:
				icon = self.sign_icons[i.name]
			else:
				if i.name == "Pluto" and self.pluto_alternate:
					icon = self.icons["Pluto 2"]
				else:
					icon = self.icons[i.name]
			for k, j in enumerate(LEVELS):
				if i.name in j:
					level = k
					break
			off = 2+(4-level)*20
			placeHere = self.getPointAt(QtCore.QRectF(circle), i.m.projectedLon, offset=off)
			self.adjustPoint(placeHere, i.m.projectedLon)
			icon.paint(painter, QtCore.QRect(placeHere.x(), placeHere.y(), 20, 20))

	def drawZodiac(self, painter, circle):
		painter.save()
		for i in range(12):
			n = ((12-i)+4)%12
			angle = n*30+15
			p = self.getPointAt(self.outer_circle, angle, offset=-20)
			self.adjustPoint(p, angle)
			if n==9:
				icon = self.sign_icons[self.capricorn_alternate]
			else:
				icon = self.sign_icons[ZODIAC[n]['name']]
			icon.paint(painter, QtCore.QRect(p.x(), p.y(), 20, 20))
			for j in range(1, 30):
				tick = angle/30*30+j
				if tick % 5 == 0:
					off = 10
				else:
					off = 5
				p = self.getPointAt(self.outer_circle, tick, offset=off)
				p2 = self.getPointAt(QtCore.QRectF(self.outer_circle), tick, offset=1)
				#self.adjustPoint(p,angle/30*30+j*6)
				#self.adjustPoint(p2,angle/30*30+j*6)
				painter.drawLine(p2, p)
		painter.restore()

	def drawHours(self, painter, circle):
		painter.save()
		trans = QtGui.QColor("#000000")
		trans.setAlpha(0)
		painter.setBrush(trans)
		phm = self.hours.tree.model().sourceModel()
		off = datetime.now(self.observer.timezone)-phm.get_date(0)
		overall = self.nexts-phm.get_date(0)
		for i in range(24):
			top = phm.get_date(i)-phm.get_date(0)
			offp = off.total_seconds()/overall.total_seconds()
			percent = top.total_seconds()/overall.total_seconds()
			if i == 23:
				width = self.nexts-phm.get_date(i)
			else:
				width = phm.get_date(i+1)-phm.get_date(i)
			w = width.total_seconds()/overall.total_seconds()*360
			angle = (360*(percent-offp)+self.signData[1][0].m.projectedLon)%360.0
			put = (angle+w/2)%360
			painter.drawPie(circle, angle*16, w*16)
			p = self.getPointAt(circle, put)
			self.adjustPoint(p, put)
			icon = self.icons[phm.get_planet(i)]
			icon.paint(painter, QtCore.QRect(p.x(), p.y(), 20, 20))
		painter.restore()

	def prepPie(self, painter, circle, width=480, offset=0):
		painter.save()
		trans = QtGui.QColor("#000000")
		trans.setAlpha(0)
		painter.setBrush(trans)
		for i in range(int(5760/width)):
			start = i*width
			painter.drawPie (circle, start+offset, width)
		painter.restore()

	def protate(self, painter, degrees):
		painter.translate(self.center)
		painter.rotate(degrees)
		painter.translate(-self.center.x(), -self.center.y())

	def drawHouses(self, painter, houses, circle):
		painter.save()
		trans = QtGui.QColor("#000000")
		trans.setAlpha(0)
		painter.setBrush(trans)

		for i in range(12):
			h = houses[i]
			start = h.cusp.longitude
			end = h.end.longitude
			painter.drawPie(circle, end*16, h.width*-16)
			angle = start+h.width*2/3
			placeHere = self.getPointAt(QtCore.QRectF(circle), angle, offset=circle.width()/8)
			self.adjustPoint(placeHere, angle)
			painter.drawText(QtCore.QRectF(placeHere.x(), placeHere.y(), 20, 20), str(i+1))
		painter.restore()

	def paintEvent(self, paintevent):
		painter = QtGui.QPainter(self)
		penifiedOFG = QtGui.QPen(self.outerFG, 0)
		penifiedOH = QtGui.QPen(self.outerHouses, 0)
		penifiedIFG = QtGui.QPen(self.innerFG, 0)
		penifiedIH = QtGui.QPen(self.innerHouses, 0)

		painter.setRenderHint(QtGui.QPainter.Antialiasing)
		painter.setPen(penifiedOFG)
		painter.setBrush(self.outerFill)

		hoursCircle = self.getOffRect(self.outer_circle, -40)
		signsCircle = self.getOffRect(self.outer_circle, -20)
		painter.drawEllipse(hoursCircle)
		self.drawHours(painter, hoursCircle)
		painter.drawEllipse(signsCircle)
		self.prepPie(painter, signsCircle)
		self.prepPie(painter, self.outer_circle)

		painter.setPen(penifiedOH)
		self.drawHouses(painter, self.signData[0], self.outer_circle)

		painter.setBrush(self.innerFill)
		painter.setPen(penifiedIFG)
		painter.drawEllipse(self.inner_circle)

		self.prepPie(painter, self.inner_circle)
		painter.setPen(penifiedIH)
		self.drawHouses(painter, self.natData[0], self.inner_circle)

		painter.setPen(penifiedOFG)
		self.drawZodiac(painter, self.outer_circle)
		painter.setPen(penifiedIFG)

		self.drawPlanets(painter, self.signData[1], self.outer_circle)
		self.drawPlanets(painter, self.natData[1], self.inner_circle)

		dt = self.hours.tree.model().sourceModel().get_planet(0)
		ic = self.icons[dt]
		ic.paint(painter, self.centerRect.toRect())

		c = create_aspect_table(self.natData[1])
		at, compare = create_aspect_table(self.signData[1], compare=self.natData[1], orbs=self.orbs)

		for aspect in c:
			if aspect.aspect == 'None':
				continue
			path = self.createAspectDoodle([aspect.planet1.m.projectedLon,
			                                aspect.planet2.m.projectedLon], 
			                               self.doodle_box)
			sparkles = self.__aspectBrushes[aspect.aspect]
			sparkles.setAlpha(50.0)
			painter.setPen(sparkles)
			painter.drawPath(path)

		years = relativedelta(self.observer.dt_now(), self.bd).years
		need_idx = 0
		if len(self.natData[1]) == 14:
			need_idx = 10
		elif len(self.natData[1]) == 16:
			need_idx = 12
		if need_idx > 0:
			yp = yearly_profection(self.observer.dt_now(), self.bd, self.natData[1][need_idx].m)
			icon = self.sign_icons[yp]
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
