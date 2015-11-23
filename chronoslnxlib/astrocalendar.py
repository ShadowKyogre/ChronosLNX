from PyQt4 import QtGui, QtCore
from .core.charts import lunar_return, solar_return
from .core.moon_phases import state_to_string, grab_phase
from .csscalendar import CSSCalendar, TodayDelegate
from datetime import datetime

import swisseph

### CSS Themable Custom Widgets
'''
self.calendar.setRefinements(clnxcfg.refinements)
self.calendar.setIcons(clnxcfg.moon_icons)
self.calendar.setShowPhase(clnxcfg.show_mcal)
self.calendar.setSolarReturn(clnxcfg.show_sr)
self.calendar.setLunarReturn(clnxcfg.show_lr)
self.calendar.setBirthTime(clnxcfg.baby.obvdate)
self.calendar.setNatalMoon(clnxcfg.natal_moon)
self.calendar.setNatalSun(clnxcfg.natal_sun)
self.calendar.useCSS=clnxcfg.use_css
self.calendar.observer=clnxcfg.observer
'''

class AstroCalendarDelegate(TodayDelegate):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.observer = None
		self.icons = None
	def paint(self, painter, option, index):
		super().paint(painter, option, index)
		if self.icons is None:
			return
		rect = option.rect
		#model = index.model()
		islunarreturn = index.data(QtCore.Qt.UserRole+2)
		issolarreturn = index.data(QtCore.Qt.UserRole+3)
		phase = index.data(QtCore.Qt.UserRole+4)
		if islunarreturn:
			icon = self.icons['Lunar Return']
			point = rect.bottomRight()
			icon.paint(painter, QtCore.QRect(point.x()-14, point.y()-14, 14, 14))
		if issolarreturn:
			icon = self.icons['Solar Return']
			point = rect.bottomRight()
			icon.paint(painter, QtCore.QRect(rect.x(), point.y()-14, 14, 14))
		if phase is not None:
			icon = self.icons[phase]
			icon.paint(painter, QtCore.QRect(rect.x() ,rect.y(), 14, 14))

class AstroCalendar(CSSCalendar):
	def __init__(self, *args):
		super().__init__(*args)
		#self.color = QtGui.QColor(self.palette().color(QtGui.QPalette.Midlight))
		#self.color.setAlpha(64)
		#self.setDateRange(QtCore.QDate(1902,1,1),QtCore.QDate(2037,1,1))
		self.currentPageChanged.connect(self.checkInternals)
		#self.selectionChanged.connect(self.updateCells)
		self.solarReturn = False
		self.lunarReturn = False
		self.showPhase = False
		self.birthtime = None
		self._observer = None
		#children = self.findChildren (QtGui.QToolButton)
		#children[0].setArrowType(QtCore.Qt.LeftArrow)
		#children[1].setArrowType(QtCore.Qt.RightArrow)
		self.solarF = QtGui.QTextCharFormat()
		self.lunarF = QtGui.QTextCharFormat()
		#self._refillCells()

	def observer(self):
		return self._observer

	def setObserver(self, newo):
		self._observer = newo
		self._delegate = AstroCalendarDelegate()
		self._delegate.observer = self._observer
		self._delegate.icons = self.icons
		self._table.setItemDelegate(self._delegate)
		self.checkInternals(self.yearShown(), self.monthShown())
		self._refillCells()

	observer = property(observer, setObserver)

	def setIcons(self, icon_list):
		self.icons = icon_list

	def setShowPhase(self, value):
		self.showPhase = value

	def setSolarReturn(self, value):
		self.solarReturn = value

	def setLunarReturn(self, value):
		self.lunarReturn = value

	def setBirthTime(self, time):
		self.birthtime = time
		#self.updateSun()
		#self.updateMoon()

	def setNatalMoon(self, zodiacal_data):
		if not self.birthtime:
			raise RuntimeError("Cannot update natal moon without a birthtime!")
		self.natal_moon = zodiacal_data
		if self.lunarReturn:
			self.updateMoon(self.yearShown())

	def setNatalSun(self, zodiacal_data):
		if not self.birthtime:
			raise RuntimeError("Cannot update natal sun without a birthtime!")
		self.natal_sun = zodiacal_data
		if self.solarReturn:
			self.updateSun(self.yearShown())

	def checkInternals(self, year, month):
		if self.solarReturn:
			if not self.isSolarReturnValid():
				print("Updating solar return...")
				self.updateSun(year)
		if self.lunarReturn:
			if not self.isLunarReturnsValid(year, month):
				print("Updating lunar returns...")
				self.updateMoon(year)
			caldates = set(self._calendar.itermonthdates(year, month))
			self.here = caldates&self.lunarReturnss
			#print(self.lunarReturnss)
			#print(self.here)
		#self.listidx=self.isLunarReturnsValid()

	def updateSun(self, year):
		self.solarReturnTime = solar_return(self.birthtime.replace(year=year), self.birthtime, self.natal_sun)
		#print(self.solarReturnTime)

	def updateMoon(self, year):
		self.lunarReturns=[]
		guesstimate_point = datetime(year-1, 12, 14, 12)
		self.lunarReturns.append(lunar_return(guesstimate_point, self.birthtime,
			                                      self.natal_moon))
		for m in range(1, 13):
			guesstimate_point = datetime(year, m, 14, 12)
			self.lunarReturns.append(lunar_return(guesstimate_point, self.birthtime,
			                                      self.natal_moon))
		guesstimate_point = datetime(year+1, 1, 14, 12)
		self.lunarReturns.append(lunar_return(guesstimate_point, self.birthtime,
			                                      self.natal_moon))
		self.lunarReturnss = {d.date() for d in self.lunarReturns}
		#print(self.lunarReturns)

	def isSolarReturnValid(self):
		return self.solarReturnTime.year == self.yearShown()

	def isLunarReturnsValid(self, year, month):
		stillInYear=False
		for i in range(len(self.lunarReturns)):
			t = self.lunarReturns[i]
			if t.year == year and t.month == month:
				return True
			elif t.year == year:
				stillInYear = True
		return stillInYear

	def fetchLunarReturn(self, date):
		return self._fetchLunarReturn(date, 0, 11)

	def _fetchLunarReturn(self, date, l, r):
		if r < l:
			return int((r-l)/2)-1
		mid = int((l+r)/2)
		other_date = self.lunarReturns[mid].date()
		if date > other_date:
			return self._fetchLunarReturn(date, mid+1, r)
		elif date < other_date:
			return self._fetchLunarReturn(date, l, mid-1)
		else:
			return mid

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

	def _isToday(self, date):
		return hasattr(self, 'observer') and self.observer.obvdate.date() == date

	def _modifyDayItem(self, item):
		date = item.data(QtCore.Qt.UserRole)
		super()._modifyDayItem(item)
		if not hasattr(self, 'observer'):
			return
		tooltiptxt = ''
		here = self.lunarReturn and date in self.here
		item.setData(QtCore.Qt.UserRole+2, here)
		here2 = self.solarReturn and self.solarReturnTime.date() == date
		item.setData(QtCore.Qt.UserRole+3, here2)
		if self.showPhase:
			datetime = QtCore.QDateTime(date).toPyDateTime()\
			                                 .replace(tzinfo=self.observer.timezone)\
			                                 .replace(hour=12)
			phase = state_to_string(grab_phase(datetime), swisseph.MOON)
			item.setData(QtCore.Qt.UserRole+4, phase)
		else:
			item.setData(QtCore.Qt.UserRole+4, None)
		item.setData(QtCore.Qt.ToolTipRole, tooltiptxt)
