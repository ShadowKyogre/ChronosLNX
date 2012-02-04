#!/usr/bin/python
#http://www.kimgentes.com/worshiptech-web-tools-page/2008/10/14/regex-pattern-for-parsing-csv-files-with-embedded-commas-dou.html
#http://doc.qt.nokia.com/qq/qq26-pyqtdesigner.html#creatingacustomwidget
from PyQt4 import QtGui,QtCore
from astro_rewrite import *
from measurements import ZODIAC, format_zodiacal_difference
from csscalendar import CSSCalendar
import swisseph
import re
from dateutil import tz
from datetime import datetime

#http://doc.qt.nokia.com/latest/qt.html#ItemDataRole-enum
##http://doc.qt.nokia.com/latest/widgets-analogclock.html
#http://stackoverflow.com/questions/2526815/moon-lunar-phase-algorithm

LEVELS=(('Sun','Moon','Venus','Mercury'),\
('Mars','Jupiter','Saturn'),\
('Uranus','Neptune','Pluto'),\
('North Node','South Node'),\
('Ascendant','Descendant','MC','IC'))

class AstroClock(QtGui.QWidget):
	def __init__(self, *args):
		QtGui.QWidget.__init__(self, *args)
		self.size=500
		self.true_size=self.size+100
		self.inner_size=self.size-200
		self.setFixedSize(self.true_size,self.true_size)
		self.center=QtCore.QPointF(self.true_size/2,self.true_size/2)
		self.diff=(self.size-self.inner_size)/2+self.true_size/12
		self.centerRect=QtCore.QRectF(self.true_size*17/40,\
						self.true_size*17/40,90,90)
		self.outer_circle=QtCore.QRect(self.true_size/12,self.true_size/12,\
					self.size-2,self.size-2)
		self.inner_circle=QtCore.QRect(self.diff,self.diff,self.inner_size,self.inner_size)
		self.doodle_box=QtCore.QRectF(self.centerRect.x()+4,self.centerRect.y()+4,82,82)
		self.init_colors()
		self.timer=QtCore.QTimer(self)
		self.connect(self.timer, QtCore.SIGNAL("timeout()"), self, QtCore.SLOT("update()"))
		self.timer.start(1000)

	def init_colors(self):
		bg=QtGui.QColor(self.palette().color(QtGui.QPalette.Window))
		pbg=bg.lighter(250)
		prettybg=QtGui.QRadialGradient()
		prettybg.setCoordinateMode(QtGui.QGradient.ObjectBoundingMode)
		prettybg.setCenter(0.5,0.633333333)
		prettybg.setRadius(0.3333333333)
		prettybg.setFocalPoint(0.5,0.583333333)
		prettybg.setColorAt(0,pbg)
		prettybg.setColorAt(1,bg)

		ibg=QtGui.QColor(self.palette().color(QtGui.QPalette.Base))
		pibg=ibg.lighter(250)
		prettyibg=QtGui.QRadialGradient()
		prettyibg.setCoordinateMode(QtGui.QGradient.ObjectBoundingMode)
		prettyibg.setCenter(0.5,0.683333333)
		prettyibg.setRadius(0.5)
		prettyibg.setFocalPoint(0.5,0.583333333)
		prettyibg.setColorAt(0,pibg)
		prettyibg.setColorAt(1,ibg)

		self.__outerBG=QtGui.QBrush(prettybg)
		self.__outerF=QtGui.QBrush(QtGui.QColor(self.palette().color(QtGui.QPalette.WindowText)))

		self.__innerBG=QtGui.QBrush(prettyibg)
		self.__innerF=QtGui.QBrush(QtGui.QColor(self.palette().color(QtGui.QPalette.Text)))

		self.__innerH=QtGui.QBrush(QtGui.QColor(self.palette().color(QtGui.QPalette.WindowText)))
		self.__outerH=QtGui.QBrush(QtGui.QColor(self.palette().color(QtGui.QPalette.WindowText)))

		self.__aspectBrushes={
		'conjunction': QtGui.QColor(self.palette().color(QtGui.QPalette.BrightText)),
		'semi-sextile':QtGui.QColor(self.palette().color(QtGui.QPalette.BrightText)),
		'semi-square':QtGui.QColor(self.palette().color(QtGui.QPalette.BrightText)),
		'sextile':QtGui.QColor(self.palette().color(QtGui.QPalette.BrightText)),
		'quintile':QtGui.QColor(self.palette().color(QtGui.QPalette.BrightText)),
		'square':QtGui.QColor(self.palette().color(QtGui.QPalette.BrightText)),
		'trine':QtGui.QColor(self.palette().color(QtGui.QPalette.BrightText)),
		'sesiquadrate':QtGui.QColor(self.palette().color(QtGui.QPalette.BrightText)),
		'biquintile':QtGui.QColor(self.palette().color(QtGui.QPalette.BrightText)),
		'inconjunct':QtGui.QColor(self.palette().color(QtGui.QPalette.BrightText)),
		'opposition':QtGui.QColor(self.palette().color(QtGui.QPalette.BrightText)),}

	def __outerFill(self):
		return self.__outerBG

	def __setOuterFill(self, fill):
		self.__outerBG=fill

	def __outerFG(self):
		return self.__outerF

	def __setOuterFG(self, fill):
		print fill.color().name()
		self.__outerF=fill

	def __outerHouses(self):
		return self.__outerH

	def __setOuterHouses(self, fill):
		self.__outerH=fill

	def __innerFill(self):
		return self.__innerBG

	def __setInnerFill(self, fill):
		self.__innerBG=fill

	def __innerFG(self):
		return self.__innerF

	def __setInnerFG(self, fill):
		self.__innerF=fill

	def __innerHouses(self):
		return self.__innerH

	def __setInnerHouses(self, fill):
		self.__innerH=fill

	def __aspectBrush(self, aspect):
		return self.__aspectBrushes[aspect]

	def __setAspectBrush(self, fill, aspect):
		self.__aspectBrushes[aspect]=fill

	outerFill=QtCore.pyqtProperty("QBrush", __outerFill, __setOuterFill)
	outerFG=QtCore.pyqtProperty("QBrush", __outerFG, __setOuterFG)
	outerHouses=QtCore.pyqtProperty("QBrush", __outerHouses, __setOuterHouses)

	innerFill=QtCore.pyqtProperty("QBrush", __innerFill, __setInnerFill)
	innerFG=QtCore.pyqtProperty("QBrush", __innerFG, __setInnerFG)
	innerHouses=QtCore.pyqtProperty("QBrush", __innerHouses, __setInnerHouses)

	conjunction=QtCore.pyqtProperty("QColor", \
	lambda self: self.__aspectBrush("conjunction"), \
	lambda self,fill: self.__setAspectBrush(fill,"conjunction"))
	semiSextile=QtCore.pyqtProperty("QColor", \
	lambda self: self.__aspectBrush("semi-sextile"), \
	lambda self,fill: self.__setAspectBrush(fill,"semi-sextile"))
	semiSquare=QtCore.pyqtProperty("QColor", \
	lambda self: self.__aspectBrush("semi-square"), \
	lambda self,fill: self.__setAspectBrush(fill,"semi-square"))
	sextile=QtCore.pyqtProperty("QColor", \
	lambda self: self.__aspectBrush("sextile"), \
	lambda self,fill: self.__setAspectBrush(fill,"sextile"))
	quintile=QtCore.pyqtProperty("QColor", \
	lambda self: self.__aspectBrush("quintile"), \
	lambda self,fill: self.__setAspectBrush(fill,"quintile"))
	square=QtCore.pyqtProperty("QColor", \
	lambda self: self.__aspectBrush("square"), \
	lambda self,fill: self.__setAspectBrush(fill,"square"))
	trine=QtCore.pyqtProperty("QColor", \
	lambda self: self.__aspectBrush("trine"), \
	lambda self,fill: self.__setAspectBrush(fill,"trine"))
	sesiquadrate=QtCore.pyqtProperty("QColor", \
	lambda self: self.__aspectBrush("sesiquadrate"), \
	lambda self,fill: self.__setAspectBrush(fill,"sesiquadrate"))
	biquintile=QtCore.pyqtProperty("QColor", \
	lambda self: self.__aspectBrush("biquintile"), \
	lambda self,fill: self.__setAspectBrush(fill,"biquintile"))
	inconjunct=QtCore.pyqtProperty("QColor", \
	lambda self: self.__aspectBrush("inconjunct"), \
	lambda self,fill: self.__setAspectBrush(fill,"inconjunct"))
	opposition=QtCore.pyqtProperty("QColor", \
	lambda self: self.__aspectBrush("opposition"), \
	lambda self,fill: self.__setAspectBrush(fill,"opposition"))

	def setHourSource(self, hours):
		self.hours=hours

	def setNextSunrise(self, date):
		self.nexts=date

	def setBD(self, date):
		self.bd=date

	def setNatData(self, natData):
		self.natData=natData

	def setSignData(self, signData):
		self.signData=signData

	def setSignIcons(self, icons):
		self.sign_icons=icons

	def setIcons(self, icons):
		self.icons=icons

	def setOrbs(self, orbs):
		self.orbs=orbs

	def setCapricornAlternate(self, cap_alt):
		self.capricorn_alternate=cap_alt

	def setPlutoAlternate(self, plu_alt):
		self.pluto_alternate=plu_alt

	def createAspectDoodle(self, angles, bound_box):
		path=QtGui.QPainterPath()

		path.arcMoveTo(bound_box, angles[0])
		first_point=path.currentPosition()

		for i in angles:
			origin2=path.currentPosition()
			path.arcMoveTo (bound_box, i)
			last_point=path.currentPosition()
			path.lineTo(origin2)
			path.moveTo(last_point)

		path.lineTo(first_point)
		return path

	def getOffRect(self, circle, offset):
		tl=QtCore.QPointF(circle.top(),circle.left())
		tl.setX(tl.x()+offset)
		tl.setY(tl.y()+offset)
		br=QtCore.QPointF(circle.bottom(),circle.right())
		br.setX(br.x()-offset)
		br.setY(br.y()-offset)
		reccy=QtCore.QRectF(tl,br)
		return reccy

	def getPointAt(self, circle, angle, offset=0):
		arcs=QtGui.QPainterPath()
		if offset != 0:
			reccy=self.getOffRect(circle, offset)
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
				icon=self.sign_icons[i.name]
			else:
				if i.name=="Pluto" and self.pluto_alternate:
					icon=self.icons["Pluto 2"]
				else:
					icon=self.icons[i.name]
			for k,j in enumerate(LEVELS):
				if i.name in j:
					level=k
					break
			off=2+(4-level)*20
			placeHere=self.getPointAt(QtCore.QRectF(circle), i.m.projectedLon, offset=off)
			self.adjustPoint(placeHere, i.m.projectedLon)
			icon.paint(painter, QtCore.QRect(placeHere.x(),placeHere.y(), 20, 20))

	def drawZodiac(self, painter, circle):
		painter.save()
		for i in xrange(12):
			n=((12-i)+4)%12
			angle=n*30+15
			p=self.getPointAt(self.outer_circle,angle,offset=-20)
			self.adjustPoint(p,angle)
			if n==9:
				icon=self.sign_icons[self.capricorn_alternate]
			else:
				icon=self.sign_icons[ZODIAC[n]['name']]
			icon.paint(painter,QtCore.QRect(p.x(),p.y(),20,20))
			for j in xrange(1,30):
				tick=angle/30*30+j
				if tick % 5 == 0:
					off=10
				else:
					off=5
				p=self.getPointAt(self.outer_circle,tick,offset=off)
				p2=self.getPointAt(QtCore.QRectF(self.outer_circle),tick,offset=1)
				#self.adjustPoint(p,angle/30*30+j*6)
				#self.adjustPoint(p2,angle/30*30+j*6)
				painter.drawLine(p2,p)
		painter.restore()

	def drawHours(self, painter, circle):
		painter.save()
		trans=QtGui.QColor("#000000")
		trans.setAlpha(0)
		painter.setBrush(trans)
		off=datetime.now(tz.gettz())-self.hours.get_date(0)
		overall=self.nexts-self.hours.get_date(0)
		for i in xrange(24):
			top=self.hours.get_date(i)-self.hours.get_date(0)
			offp=off.total_seconds()/overall.total_seconds()
			percent=top.total_seconds()/overall.total_seconds()
			if i == 23:
				width=self.nexts-self.hours.get_date(i)
			else:
				width=self.hours.get_date(i+1)-self.hours.get_date(i)
			w=width.total_seconds()/overall.total_seconds()*360
			angle=(360*(percent-offp)+self.signData[1][0].m.projectedLon)%360.0
			put=(angle+w/2)%360
			painter.drawPie(circle, angle*16, w*16)
			p=self.getPointAt(circle,put)
			self.adjustPoint(p,put)
			icon=self.icons[str(self.hours.get_planet(i))]
			icon.paint(painter,QtCore.QRect(p.x(),p.y(),20,20))
		painter.restore()


	def prepPie(self, painter, circle, width=480, offset=0):
		painter.save()
		trans=QtGui.QColor("#000000")
		trans.setAlpha(0)
		painter.setBrush(trans)
		for i in xrange(5760/width):
			start=i*width
			painter.drawPie (circle, start+offset, width)
		painter.restore()

	def protate(self, painter, degrees):
		painter.translate(self.center)
		painter.rotate(degrees)
		painter.translate(-self.center.x(),-self.center.y())

	def drawHouses(self, painter, houses, circle):
		painter.save()
		trans=QtGui.QColor("#000000")
		trans.setAlpha(0)
		painter.setBrush(trans)

		for i in xrange(12):
			h=houses[i]
			start=h.cusp.longitude
			end=h.end.longitude
			painter.drawPie(circle, end*16, h.width*-16)
			angle=start+h.width*2/3
			placeHere=self.getPointAt(QtCore.QRectF(circle), angle, offset=circle.width()/8)
			self.adjustPoint(placeHere, angle)
			painter.drawText(QtCore.QRectF(placeHere.x(), placeHere.y(),20,20),str(i+1))
		painter.restore()

	def paintEvent(self, paintevent):
		painter = QtGui.QPainter(self)
		penifiedOFG=QtGui.QPen(self.outerFG, 0)
		penifiedOH=QtGui.QPen(self.outerHouses, 0)
		penifiedIFG=QtGui.QPen(self.innerFG, 0)
		penifiedIH=QtGui.QPen(self.innerHouses, 0)

		painter.setRenderHint(QtGui.QPainter.Antialiasing)
		painter.setPen(penifiedOFG)
		painter.setBrush(self.outerFill)

		hoursCircle=self.getOffRect(self.outer_circle, -40)
		signsCircle=self.getOffRect(self.outer_circle, -20)
		painter.drawEllipse(hoursCircle)
		self.drawHours(painter, hoursCircle)
		painter.drawEllipse(signsCircle)
		self.prepPie(painter,signsCircle)
		self.prepPie(painter,self.outer_circle)

		painter.setPen(penifiedOH)
		self.drawHouses(painter, self.signData[0], self.outer_circle)

		painter.setBrush(self.innerFill)
		painter.setPen(penifiedIFG)
		painter.drawEllipse(self.inner_circle)

		self.prepPie(painter,self.inner_circle)
		painter.setPen(penifiedIH)
		self.drawHouses(painter, self.natData[0], self.inner_circle)

		painter.setPen(penifiedOFG)
		self.drawZodiac(painter, self.outer_circle)
		painter.setPen(penifiedIFG)

		self.drawPlanets(painter, self.signData[1], self.outer_circle)
		self.drawPlanets(painter, self.natData[1], self.inner_circle)

		dt=self.hours.get_planet(0)
		ic=self.icons[str(dt)]
		ic.paint(painter,self.centerRect.toRect())

		c=create_aspect_table(self.natData[1])
		at,compare=create_aspect_table(self.signData[1],compare=self.natData[1],orbs=self.orbs)

		for aspect in c:
			if aspect.aspect == 'None':
				continue
			path=self.createAspectDoodle([aspect.planet1.m.projectedLon,\
			aspect.planet2.m.projectedLon], self.doodle_box)
			sparkles=self.__aspectBrushes[aspect.aspect]
			sparkles.setAlpha(50.0)
			painter.setPen(sparkles)
			painter.drawPath(path)

		years=int((datetime.now(tz.gettz())-self.bd).days/365.25)
		yearly_profection=ZODIAC[(years+self.natData[1][12].m.signData['decanates'][0])%12]['name']
		icon=self.sign_icons[yearly_profection]
		painter.setPen(penifiedOFG)
		#self.theme.outer['houses'].setBrush(self.inner['fill'])
		painter.drawText(0,12,"Yearly Profection")
		icon.paint(painter,QtCore.QRect(20,12,60,60))
		#painter.save()
		#minirect=QtCore.QRect(self.size/2+4+10,self.size/2+4+10,20,20)
		#self.protate(painter,self.signData[1][0].m.projectedLon)
		##painter.drawEllipse(minirect)
		#painter.drawConvexPolygon(QtCore.QPoint(10,self.center.y()-2),\
		#QtCore.QPoint(40,self.center.y()),\
		#QtCore.QPoint(10,self.center.y()+2),\
		#QtCore.QPoint(-5,self.center.y()))
		#painter.restore()

class AstroCalendar(CSSCalendar):

	def __init__(self, *args):

		CSSCalendar.__init__(self, *args)
		self.color = QtGui.QColor(self.palette().color(QtGui.QPalette.Midlight))
		self.color.setAlpha(64)
		self.setDateRange(QtCore.QDate(1902,1,1),QtCore.QDate(2037,1,1))
		self.currentPageChanged.connect(self.checkInternals)
		self.selectionChanged.connect(self.updateCells)
		self.solarReturn=False
		self.lunarReturn=False
		self.showPhase=False
		self.birthtime=None
		children=self.findChildren (QtGui.QToolButton)
		children[0].setArrowType(QtCore.Qt.LeftArrow)
		children[1].setArrowType(QtCore.Qt.RightArrow)
		self.solarF=QtGui.QTextCharFormat()
		self.lunarF=QtGui.QTextCharFormat()

	def setIcons(self, icon_list):
		self.icons=icon_list

	def setShowPhase(self, value):
		self.showPhase=value

	def setSolarReturn(self, value):
		self.solarReturn=value

	def setLunarReturn(self, value):
		self.lunarReturn=value

	def setBirthTime(self, time):
		self.birthtime=time
		#self.updateSun()
		#self.updateMoon()

	def setRefinements(self, ref):
		self.refinements=ref

	def setNatalMoon(self, zodiacal_data):
		if not self.birthtime:
			raise RuntimeError, "Cannot update natal moon without a birthtime!"
		self.natal_moon=zodiacal_data
		if self.lunarReturn:
			self.updateMoon()

	def setNatalSun(self, zodiacal_data):
		if not self.birthtime:
			raise RuntimeError, "Cannot update natal sun without a birthtime!"
		self.natal_sun=zodiacal_data
		if self.solarReturn:
			self.updateSun()

	def checkInternals(self, year, month):
		if self.solarReturn:
			if not self.isSolarReturnValid():
				print "Updating solar return..."
				self.updateSun()
		if self.lunarReturn:
			if not self.isLunarReturnsValid():
				print "Updating lunar returns..."
				self.updateMoon()
		#self.listidx=self.isLunarReturnsValid()

	def updateSun(self):
		self.solarReturnTime=solar_return(self.birthtime, \
						  self.yearShown(), \
						  self.natal_sun,refinements=self.refinements['Solar Return'])

	def updateMoon(self):
		self.lunarReturns=[]
		for m in xrange(1,13):
			self.lunarReturns.append(lunar_return(self.birthtime,\
				m,self.yearShown(),self.natal_moon,refinements=self.refinements['Lunar Return']))

	def isSolarReturnValid(self):
		return self.solarReturnTime.year == self.yearShown()

	def isLunarReturnsValid(self):
		stillInYear=False
		for i in xrange(len(self.lunarReturns)):
			t=self.lunarReturns[i]
			if t.year == self.yearShown() and \
				t.month == self.monthShown():
				return i
			elif t.year == self.yearShown():
				stillInYear=True
		return stillInYear

	def fetchLunarReturn(self,date):
		for i in xrange(len(self.lunarReturns)):
			t=self.lunarReturns[i]
			if t.year == date.year and \
				t.month == date.month and \
				t.day == date.day:
				return i
		return -1

	def selectedDateTime(self):
		return QtCore.QDateTime(self.selectedDate())

	def lunarFG(self):
		return self.lunarF.foreground()

	def setLunarFG(self, fill):
		self.lunarF.setForeground(fill)

	def lunarFill(self):
		return self.lunarF.background()

	def setLunarFill(self, fill):
		self.lunarF.setBackground(fill)

	def solarFG(self):
		return self.solarF.foreground()

	def setSolarFG(self, fill):
		self.solarF.setForeground(fill)

	def solarFill(self):
		return self.solarF.background()

	def setSolarFill(self, fill):
		self.solarF.setBackground(fill)

	lunarReturnFG = QtCore.pyqtProperty("QBrush", lunarFG, setLunarFG)
	lunarReturnFill = QtCore.pyqtProperty("QBrush", lunarFill, setLunarFill)
	solarReturnFG = QtCore.pyqtProperty("QBrush", solarFG, setSolarFG)
	solarReturnFill = QtCore.pyqtProperty("QBrush", solarFill, setSolarFill)

	def paintCell(self, painter, rect, date):
		QtGui.QCalendarWidget.paintCell(self, painter, rect, date)
		if date == QtCore.QDate.currentDate():
			painter.fillRect(rect, self.color)

		if self.lunarReturn:
			idx=self.fetchLunarReturn(date.toPyDate())
			if idx >= 0:
				icon=self.icons['Lunar Return']
				point=rect.bottomRight()
				icon.paint(painter,QtCore.QRect(point.x()-14,point.y()-14, 14, 14))
				if self.useCSS:
					self.setDateTextFormat(date, self.lunarF)
				else:
					self.setDateTextFormat(date, QtGui.QTextCharFormat())

		if self.solarReturn:
			if self.solarReturnTime.date() == date.toPyDate():
				icon=self.icons['Solar Return']
				point=rect.bottomRight()
				icon.paint(painter,QtCore.QRect(rect.x(),point.y()-14, 14, 14))
				if self.useCSS:
					self.setDateTextFormat(date, self.solarF)
				else:
					self.setDateTextFormat(date, QtGui.QTextCharFormat())

		if self.showPhase:
			datetime=QtCore.QDateTime(date).toPyDateTime().replace(tzinfo=tz.gettz()).replace(hour=12)
			phase=state_to_string(grab_phase(datetime, refinements=self.refinements['Moon Phase']), swisseph.MOON)
			icon=self.icons[phase]
			icon.paint(painter,QtCore.QRect(rect.x(),rect.y(),14,14))

#http://doc.qt.nokia.com/stable/qhelpcontentwidget.html
#http://www.riverbankcomputing.com/static/Docs/PyQt4/html/qthelp.html
#http://ubuntuforums.org/showthread.php?t=1110989
#http://www.commandprompt.com/community/pyqt/x6082

class PlanetaryHoursList(QtGui.QWidget):
	def __init__(self, parent = None):

		QtGui.QWidget.__init__(self, parent)
		hbox=QtGui.QVBoxLayout(self)
		self.tree=QtGui.QTreeView(self)
		self.tree.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
		self.tree.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		self.tree.setRootIsDecorated(False)
		color=self.palette().color(QtGui.QPalette.Midlight)
		color.setAlpha(64)
		self.color=QtGui.QBrush(color)
		c2=self.palette().color(QtGui.QPalette.Base)
		c2.setAlpha(0)
		self.base=QtGui.QBrush(c2)

		inputstuff=QtGui.QGridLayout()
		inputstuff.addWidget(QtGui.QLabel("Hour type to filter"),0,0)
		self.filter_hour=QtGui.QComboBox(self)
		self.filter_hour.addItem("All")
		self.filter_hour.addItem("Sun")
		self.filter_hour.addItem("Moon")
		self.filter_hour.addItem("Mars")
		self.filter_hour.addItem("Mercury")
		self.filter_hour.addItem("Jupiter")
		self.filter_hour.addItem("Venus")
		self.filter_hour.addItem("Saturn")
		self.filter_hour.setCurrentIndex(0)
		inputstuff.addWidget(self.filter_hour,0,1)
		hbox.addLayout(inputstuff)
		hbox.addWidget(self.tree)
		model=QtGui.QStandardItemModel()
		model.setColumnCount(2)
		model.setHorizontalHeaderLabels(["Time","Planet"])
		filter_model=QtGui.QSortFilterProxyModel()
		filter_model.setSourceModel(model)
		filter_model.setFilterKeyColumn(1)
		self.tree.setModel(filter_model)
		self.filter_hour.activated.connect(self.filter_hours)
		self.filter_hour.setToolTip("Select the hour type you want to show.")
		self.last_index=0

	def clear(self):
		model=self.tree.model().sourceModel()
		model.removeRows(0,24)
		self.last_index=0

	def get_planet(self,idx):
		return self.tree.model().sourceModel().item(idx, 1).data(0).toPyObject()

	def get_date(self,idx):
		return self.tree.model().sourceModel().item(idx, 0).data(32).toPyObject()

	def setIcons(self, icon_list):
		self.icons=icon_list

	def prepareHours(self,date,observer):
		planetary_hours = hours_for_day(date,observer)
		model=self.tree.model().sourceModel()
		for i in xrange(0,24):
			icon=self.icons[planetary_hours[i][1]]

			if planetary_hours[i][2] is True:
				status_icon=self.icons['daylight']
			else:
				status_icon=self.icons['nightlight']
			newhouritem=QtGui.QStandardItem(status_icon,planetary_hours[i][0].strftime("%H:%M:%S - %m/%d/%Y"))
			newhouritem.setData(QtCore.QVariant(planetary_hours[i][0]),32)
			newplanetitem=QtGui.QStandardItem(icon,planetary_hours[i][1])
			model.insertRow(i,[newhouritem,newplanetitem])

	def _highlight_row(self, idx):
		self.tree.model().sourceModel().item(idx, 0).setBackground(self.color)
		self.tree.model().sourceModel().item(idx, 1).setBackground(self.color)

	def _unhighlight_row(self, idx):
		self.tree.model().sourceModel().item(idx, 0).setBackground(self.base)
		self.tree.model().sourceModel().item(idx, 1).setBackground(self.base)

	def filter_hours(self,idx):
		if 0 == idx:
			self.tree.model().setFilterFixedString("")
		else:
			self.tree.model().setFilterFixedString(self.filter_hour.itemText(idx)) #set filter based on planet name

	def grab_nearest_hour(self,date):
		for i in xrange(self.last_index,24):
			if i+1 > 23:
				looking_behind = self.get_date(i)
				if looking_behind <= date:
					self._highlight_row(i)
					self._unhighlight_row(i-1)
					self.last_index=i
					return self.get_planet(i)
			else:
				looking_behind = self.get_date(i)
				looking_ahead = self.get_date(i+1)
				if looking_behind <= date and looking_ahead > date:
					self._highlight_row(i)
					if i != 0:
						self._unhighlight_row(i-1)
					self.last_index=i
					return self.get_planet(i)
		return "-Error-"

class AspectTableDisplay(QtGui.QWidget):
	def __init__(self, *args):
		QtGui.QWidget.__init__(self, *args)
		vbox=QtGui.QVBoxLayout(self)
#orbs = { 'conjunction': 10.0,
		#'semi-sextile':3.0,
		#'semi-square':3.0,
		#'sextile':6.0,
		#'quintile':2.0,
		#'square':8.0,
		#'trine':8.0,
		#'sesiquadrate':3.0,
		#'biquintile':2.0,
		#'inconjunct':3.0,
		#'opposition':10.0,
		#}
		self.tableAspects=QtGui.QStandardItemModel()
		self.tableSpecial=QtGui.QStandardItemModel()
		self.headers=[]

		sa=["Yod","Grand Trine", "Grand Cross", "T-Square", "Stellium"]

		self.guiAspects=QtGui.QTableView(self)
		self.guiSpecial=QtGui.QTableView(self)
		vbox.addWidget(QtGui.QLabel("General Aspects:\nThe row indicates the planet being aspected."))
		vbox.addWidget(self.guiAspects)
		vbox.addWidget(QtGui.QLabel("Special Aspects"))
		vbox.addWidget(self.guiSpecial)

		self.guiAspects.setModel(self.tableAspects)
		self.guiAspects.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

		self.guiSpecial.setModel(self.tableSpecial)
		self.guiSpecial.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

		self.tableSpecial.setColumnCount(5)
		self.tableSpecial.setHorizontalHeaderLabels(sa)

	def refresh(self,zodiac,orbs):
		at=create_aspect_table(zodiac,orbs=orbs)
		sad=search_special_aspects(at)
		self.buildTable(at,sad)

	def buildTable(self,at,sad,comparative=False):
		self.comparative=comparative
		self.updateHeaders()
		max_length,longest_element = max([(len(x),x) for x in sad])
		self.tableSpecial.setRowCount(max_length)
		self.tableSpecial.removeRows(0, self.tableSpecial.rowCount())
		for i in at:
			if i.aspect == None:
				c=QtGui.QStandardItem("No aspect")
			else:
				c=QtGui.QStandardItem("%s" %(i.aspect.title()))
			c.setToolTip("%s" %(i))
			c.setData(i,32)
			self.tableAspects.setItem(self.headers.index(i.planet2.name),\
			self.headers.index(i.planet1.name),c)
		i=0
		for yod in sad[0]:
			c=QtGui.QStandardItem(str(yod))
			self.tableSpecial.setItem(i,0,c)
			i=i+1
		i=0
		for gt in sad[1]:
			d=QtGui.QStandardItem(str(gt))
			self.tableSpecial.setItem(i,1,d)
			i=i+1
		i=0
		for gc in sad[2]:
			e=QtGui.QStandardItem(str(gc))
			self.tableSpecial.setItem(i,2,e)
			i=i+1
		i=0
		for tsq in sad[3]:
			f=QtGui.QStandardItem(str(tsq))
			self.tableSpecial.setItem(i,4,f)
			i=i+1
		i=0
		for stellium in sad[4]:
			g=QtGui.QStandardItem(str(stellium))
			self.tableSpecial.setItem(i,3,g)
			i=i+1
		self.guiAspects.resizeRowsToContents()
		self.guiAspects.resizeColumnsToContents()
		self.guiSpecial.resizeRowsToContents()
		self.guiSpecial.resizeColumnsToContents()

	def updateHeaders(self):
		self.headers=["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto"]
		if self.nodes:
			self.headers.append("North Node")
			self.headers.append("South Node")
		if self.admi:
			self.headers.append("Ascendant")
			self.headers.append("Descendant")
			self.headers.append("MC")
			self.headers.append("IC")
		length=len(self.headers)
		self.tableAspects.setColumnCount(length)
		self.tableAspects.setRowCount(length)
		for v,i in enumerate(self.headers):
			item=QtGui.QStandardItem(i)
			if self.pluto_alternate and i == "Pluto":
				item.setIcon(0,self.icons['Pluto 2'])
			elif (i == "Ascendant" or i == "Descendant" or \
			i == "MC" or i == "IC"):
				item.setIcon(self.sign_icons[i])
			else:
				item.setIcon(self.icons[i])
			item2=QtGui.QStandardItem(item)
			if self.comparative:
				item2.setText("Natal %s" %i)
			self.tableAspects.setHorizontalHeaderItem(v,item)
			self.tableAspects.setVerticalHeaderItem(v,item2)

	def setADMI(self, value):
		self.admi=value

	def setIcons(self, icon_list):
		self.icons=icon_list

	def setSignIcons(self, icon_list):
		self.sign_icons=icon_list

	def setPlutoAlternate(self, value):
		self.pluto_alternate=value #should be boolean

	def setNodes(self, value):
		self.nodes=value

def aspectsDialog(widget, zodiac, other_table, icons, \
	sign_icons, pluto_alternate, admi, nodes, orbs):
	info_dialog=QtGui.QDialog(widget)
	tabs=QtGui.QTabWidget(info_dialog)
	aspects=AspectTableDisplay(info_dialog)
	aspects.setIcons(icons)
	aspects.setSignIcons(sign_icons)
	aspects.setPlutoAlternate(pluto_alternate)
	aspects.setADMI(admi)
	aspects.setNodes(nodes)
	vbox=QtGui.QVBoxLayout(info_dialog)
	tabs.addTab(aspects,"Aspects for this table")
	vbox.addWidget(tabs)
	if other_table:
		caspects=AspectTableDisplay(info_dialog)
		caspects.setIcons(icons)
		caspects.setSignIcons(sign_icons)
		caspects.setPlutoAlternate(pluto_alternate)
		caspects.setADMI(admi)
		caspects.setNodes(nodes)
		at,compare=create_aspect_table(zodiac,compare=other_table,orbs=orbs)
		sado=search_special_aspects(at)
		sad=search_special_aspects(at+compare)
		caspects.buildTable(compare,sad,comparative=True)
		aspects.buildTable(at,sado)
		tabs.addTab(caspects,"Aspects to Natal Chart")
	else:
		aspects.refresh(zodiac,orbs)
	info_dialog.show()

def housesDialog(widget, houses, capricorn_alternate, sign_icons):
	info_dialog=QtGui.QDialog(widget)
	tree=QtGui.QTreeWidget(info_dialog)
	tree.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
	tree.setRootIsDecorated(False)
	tree.setHeaderLabels(["Number","Natural Ruler","Cusp Sign","Degrees","End Sign","Degrees"])
	tree.setColumnCount(6)
	vbox=QtGui.QVBoxLayout(info_dialog)
	vbox.addWidget(tree)
	for i in houses:
		item=QtGui.QTreeWidgetItem()
		item.setText(0,"House %s" %(i.num))
		item.setToolTip(0,str(i))
		if i.natRulerData['name'] == "Capricorn":
			item.setIcon(1,sign_icons[capricorn_alternate])
		else:
			item.setIcon(1,sign_icons[i.natRulerData['name']])
		item.setText(1,i.natRulerData['name'])
		item.setToolTip(1,i.natRulerStr())
		if i.cusp.signData['name'] == "Capricorn":
			item.setIcon(2,sign_icons[capricorn_alternate])
		else:
			item.setIcon(2,sign_icons[i.cusp.signData['name']])
		item.setText(2,i.cusp.signData['name'])
		item.setToolTip(2,i.cusp.dataAsText())
		item.setText(3,i.cusp.only_degs())
		item.setToolTip(3,"The real longitude is %.3f degrees" %(i.cusp.longitude))
		if i.end.signData['name'] == "Capricorn":
			item.setIcon(4,sign_icons[capricorn_alternate])
		else:
			item.setIcon(4,sign_icons[i.end.signData['name']])
		item.setText(4,i.end.signData['name'])
		item.setToolTip(4,i.end.dataAsText())
		item.setText(5,i.end.only_degs())
		item.setToolTip(5,"The real longitude is %.3f degrees" %(i.end.longitude))
		tree.addTopLevelItem(item)
	info_dialog.show()

class SignsForDayList(QtGui.QWidget):
	def __init__(self, *args):

		QtGui.QWidget.__init__(self, *args)
		vbox=QtGui.QVBoxLayout(self)
		grid=QtGui.QGridLayout()
		vbox.addLayout(grid)
		grid.addWidget(QtGui.QLabel("Pick a time to view for"),0,0)
		self.time=QtGui.QTimeEdit()
		grid.addWidget(self.time,0,1)
		self.tree=QtGui.QTreeWidget(self)
		self.tree.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
		self.tree.setRootIsDecorated(False)
		header=QtCore.QStringList()
		header.append("Planet")
		header.append("Constellation")
		header.append("Angle")
		header.append("Retrograde?")
		header.append("House")
		self.tree.setHeaderLabels(header)
		self.tree.setColumnCount(5)
		vbox.addWidget(self.tree)
		self.time.setDisplayFormat("HH:mm:ss")
		self.time.timeChanged.connect(self.update_degrees)
		button=QtGui.QPushButton("&Aspects")
		button.clicked.connect(self.showAspects)
		button2=QtGui.QPushButton("&Houses Overview")
		button2.clicked.connect(self.showHouses)
		grid.addWidget(button,2,0)
		grid.addWidget(button2,2,1)
		self.z=[]
		self.h=[]
		self.table=[]

	def setCompareTable(self,table):
		self.table=table

	def showAspects(self):
		aspectsDialog(self, self.z, self.table, self.icons, \
		self.sign_icons, self.pluto_alternate, self.admi, self.nodes,\
		self.orbs)

	def showHouses(self):
		housesDialog(self, self.h, self.capricorn_alternate, self.sign_icons)

	def setOrbs(self, orbs):
		self.orbs=orbs

	def update_degrees(self, qtime):
		self.tree.clear()
		self.target_date=self.target_date.replace(hour=qtime.hour())\
		.replace(minute=qtime.minute())\
		.replace(second=qtime.second())
		self._grab()

	def setADMI(self, value):
		self.admi=value

	def setIcons(self, icon_list):
		self.icons=icon_list

	def setSignIcons(self, icon_list):
		self.sign_icons=icon_list

	def setPlutoAlternate(self, value):
		self.pluto_alternate=value #should be boolean

	def setCapricornAlternate(self, value):
		self.capricorn_alternate=value #should be string

	def setNodes(self, value):
		self.nodes=value

	def assembleFromZodiac(self, zodiac):
		self.tree.clear()
		if len(self.z) == 0:
			self.z=zodiac
		for i in zodiac:
			item=QtGui.QTreeWidgetItem()
			if self.pluto_alternate and i.name == "Pluto":
				item.setIcon(0,self.icons['Pluto 2'])
			elif (i.name == "Ascendant" or i.name == "Descendant" or \
			i.name == "MC" or i.name == "IC"):
				item.setIcon(0,self.sign_icons[i.name])
			else:
				item.setIcon(0,self.icons[i.name])
			item.setText(0,i.name)
			item.setToolTip(0,str(i))
			if i.m.signData['name'] == "Capricorn":
				item.setIcon(1,self.sign_icons[self.capricorn_alternate])
			else:
				item.setIcon(1,self.sign_icons[i.m.signData['name']])
			item.setText(1,i.m.signData['name'])
			item.setToolTip(1,i.m.dataAsText())
			item.setText(2,i.m.only_degs())
			item.setToolTip(2,("The real longitude is %.3f degrees"
			"\nOr %.3f, if ecliptic latitude is considered.")\
			%(i.m.longitude, i.m.projectedLon))
			item.setText(3,i.retrograde)
			item.setText(4,str(i.m.house_info.num))
			item.setToolTip(4,i.m.status())
			self.tree.addTopLevelItem(item)

	def _grab(self):
		if len(self.z) == 0:
			self.h,self.z=get_signs(self.target_date,self.observer,\
						self.nodes,self.admi)
		else:
			updatePandC(self.target_date, self.observer, self.h, self.z)
		self.assembleFromZodiac(self.z)

	def get_constellations(self,date, observer):
		self.observer=observer
		self.target_date=date
		self.time.setTime(self.target_date.time())

class MoonCycleList(QtGui.QTreeWidget):
	def __init__(self, *args):

		QtGui.QTreeWidget.__init__(self, *args)
		self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
		self.setRootIsDecorated(False)
		header=QtCore.QStringList()
		header.append("Time")
		header.append("Phase")
		header.append("Illumination")
		self.setHeaderLabels(header)
		self.setColumnCount(3)
		self.color=self.palette().color(QtGui.QPalette.Midlight)
		self.color.setAlpha(64)
		self.last_index=0
		c2=self.palette().color(QtGui.QPalette.Base)
		c2.setAlpha(0)
		self.base=QtGui.QBrush(c2)

	def setIcons(self, icon_list):
		self.icons=icon_list

	def setRefinement(self, ref):
		self.refinement=ref

	def _highlight_row(self, idx):
		self.topLevelItem(idx).setBackground(0,self.color)
		self.topLevelItem(idx).setBackground(1,self.color)
		self.topLevelItem(idx).setBackground(2,self.color)

	def _unhighlight_row(self, idx):
		self.topLevelItem(idx).setBackground(0,self.base)
		self.topLevelItem(idx).setBackground(1,self.base)
		self.topLevelItem(idx).setBackground(2,self.base)

	def highlight_cycle_phase(self,date):
		for i in xrange(self.last_index,29):
			self._unhighlight_row(i)
			if i <= 27:
				cycling=self.topLevelItem(i).data(0,32).toPyObject().toPyDateTime()
				cycling2=self.topLevelItem(i+1).data(0,32).toPyObject().toPyDateTime()
				if cycling.timetuple().tm_yday <= \
				date.timetuple().tm_yday \
				< cycling2.timetuple().tm_yday:
					self._highlight_row(i)
					self.last_index=i
					break
			else:
				cycling=self.topLevelItem(i).data(0,32).toPyObject().toPyDateTime()
				if cycling.timetuple().tm_yday == date.timetuple().tm_yday:
					self._highlight_row(i)
					self.last_index=i
					break
	def get_moon_cycle(self,date):
		moon_cycle=get_moon_cycle(date,refinements=self.refinement)
		for i in xrange (29):
			newmooncycleitem = QtGui.QTreeWidgetItem()
			newmooncycleitem.setData(0,32,QtCore.QVariant(QtCore.QDateTime(moon_cycle[i][0])))
			newmooncycleitem.setIcon(0,self.icons[moon_cycle[i][1]])
			newmooncycleitem.setText(0,moon_cycle[i][0].strftime("%H:%M:%S - %m/%d/%Y"))
			newmooncycleitem.setText(1,moon_cycle[i][1])
			newmooncycleitem.setText(2,moon_cycle[i][2])
			self.addTopLevelItem(newmooncycleitem)

