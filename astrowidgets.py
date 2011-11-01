#!/usr/bin/python
#http://www.kimgentes.com/worshiptech-web-tools-page/2008/10/14/regex-pattern-for-parsing-csv-files-with-embedded-commas-dou.html
#http://doc.qt.nokia.com/qq/qq26-pyqtdesigner.html#creatingacustomwidget
from PyQt4 import QtGui,QtCore
from astro_rewrite import *
import swisseph
import re
from dateutil import tz

#http://doc.qt.nokia.com/latest/qt.html#ItemDataRole-enum
##http://doc.qt.nokia.com/latest/widgets-analogclock.html

#class AstroClock(QtGui.QWidget):
	#def __init__(self, *args):
		#QtGui.QWidget.__init__(self, *args)

	#def setColors(self, aspectsColors):

	#def paintEvent(self, painter):

	#def setTimer(self, timer):
		#self.timer=timer

	#def setHourSource(self, hoursSource):

	#def setSignSource(self, hoursSource):

class AstroCalendar(QtGui.QCalendarWidget):

	def __init__(self, *args):

		QtGui.QCalendarWidget.__init__(self, *args)
		self.color = QtGui.QColor(self.palette().color(QtGui.QPalette.Midlight))
		#self.solar = QtGui.QColor("#C09600")
		#self.lunar = QtGui.QColor("#A8CDD1")
		self.color.setAlpha(64)
		#self.solar.setAlpha(64)
		#self.lunar.setAlpha(64)
		self.setDateRange(QtCore.QDate(1902,1,1),QtCore.QDate(2037,1,1))
		self.currentPageChanged.connect(self.checkInternals)
		self.selectionChanged.connect(self.updateCells)
		self.solarReturn=False
		self.lunarReturn=False
		self.showPhase=False
		self.birthtime=None

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
						  self.natal_sun)

	def updateMoon(self):
		self.lunarReturns=[]
		for m in xrange(1,13):
			self.lunarReturns.append(lunar_return(self.birthtime,\
				m,self.yearShown(),self.natal_moon))

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

	def paintCell(self, painter, rect, date):
		QtGui.QCalendarWidget.paintCell(self, painter, rect, date)

		if date == QtCore.QDate.currentDate():
			painter.fillRect(rect, self.color)

		if self.solarReturn:
			if self.solarReturnTime.date() == date.toPyDate():
				icon=self.icons['Solar Return']
				point=rect.bottomRight()
				icon.paint(painter,QtCore.QRect(rect.x(),point.y()-14, 14, 14))
				#painter.fillRect(rect, self.solar)

		if self.lunarReturn:
			idx=self.fetchLunarReturn(date.toPyDate())
			if idx >= 0:
				icon=self.icons['Lunar Return']
				point=rect.bottomRight()
				icon.paint(painter,QtCore.QRect(point.x()-14,point.y()-14, 14, 14))
				#painter.fillRect(rect, self.lunar)

		if self.showPhase:
			datetime=QtCore.QDateTime(date).toPyDateTime().replace(tzinfo=tz.gettz()).replace(hour=12)
			phase=state_to_string(grab_phase(datetime), swisseph.MOON)
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
		self.tree.setRootIsDecorated(True)
		color=self.palette().color(QtGui.QPalette.Midlight)
		color.setAlpha(64)
		self.color=QtGui.QBrush(color)
		self.base=QtGui.QBrush(self.palette().color(QtGui.QPalette.Base))

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
		self.tree.setRootIsDecorated(True)
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
		button=QtGui.QPushButton("Click me")
		button.clicked.connect(self.showAspects)
		grid.addWidget(button,2,0,1,2)

	def showAspects(self):
		#orbs = { 'conjunction': 10.0,
		#'semi-sextile':3.0,
		#'semi-square':3.0,
		#'sextile':6.0,
		#'quintile':1.0,
		#'square':10.0,
		#'trine':10.0,
		#'sesiquadrate':3.0,
		#'biquintile':1.0,
		#'inconjunct':3.0,
		#'opposition':10.0,
		#}
		orbs = { 'conjunction': 10.0,
		'semi-sextile':3.0,
		'semi-square':3.0,
		'sextile':6.0,
		'quintile':2.0,
		'square':8.0,
		'trine':8.0,
		'sesiquadrate':3.0,
		'biquintile':2.0,
		'inconjunct':3.0,
		'opposition':10.0,
		}
		at=create_aspect_table(get_signs(self.target_date,self.observer,\
		self.nodes,self.admi),orbs)
		info_dialog=QtGui.QDialog(self)
		info_dialog.setFixedSize(600,600)
		schedule=QtGui.QStandardItemModel()
		count=10
		a=["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto"]
		if self.nodes:
			count=count+2
			a.append("North Node")
			a.append("South Node")
		if self.admi:
			count=count+4
			a.append("Ascendant")
			a.append("MC")
			a.append("Descendant")
			a.append("IC")
		schedule.setColumnCount(count)
		schedule.setRowCount(count)
		schedule.setHorizontalHeaderLabels(a)
		schedule.setVerticalHeaderLabels(a)
		b=QtGui.QTableView(info_dialog)
		vbox=QtGui.QVBoxLayout(info_dialog)
		vbox.addWidget(b)
		b.setModel(schedule)
		b.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
		for i in at:
			if i[2] == None:
				#c=QtGui.QStandardItem("%.3f - %.3f = ~%.3f" %(i[3], i[4], i[5]))
				c=QtGui.QStandardItem("No aspect")
			else:
				c=QtGui.QStandardItem("%s" %(i[2].title()))
			c.setToolTip("Difference: %.3f" %(i[5]))
			schedule.setItem(a.index(i[1]),a.index(i[0]),c)
			print i
		info_dialog.show()

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

	def _grab(self):
		self.tree.clear()
		constellations=get_signs(self.target_date,self.observer,\
					self.nodes,self.admi)
		for i in constellations:
			item=QtGui.QTreeWidgetItem()
			if self.pluto_alternate and i[0] == "Pluto":
				item.setIcon(0,self.icons['Pluto 2'])
			elif (i[0] == "Ascendant" or i[0] == "Descendant" or \
			i[0] == "MC" or i[0] == "IC"):
				item.setIcon(0,self.sign_icons[i[0]])
			else:
				item.setIcon(0,self.icons[i[0]])
			item.setText(0,i[0])
			if i[1] == "Capricorn":
				item.setIcon(1,self.sign_icons[self.capricorn_alternate])
			else:
				item.setIcon(1,self.sign_icons[i[1]])
			item.setText(1,i[1])
			item.setText(2,i[2])
			item.setData(2,32,i[3])
			item.setToolTip(2,"The real longitude is %.3f degrees" %i[3])
			item.setText(3,i[4])
			item.setText(4,i[5])
			self.tree.addTopLevelItem(item)

	def get_constellations(self,date, observer):
		self.observer=observer
		self.target_date=date
		self.time.setTime(self.target_date.time())

class MoonCycleList(QtGui.QTreeWidget):
	def __init__(self, *args):

		QtGui.QTreeWidget.__init__(self, *args)
		self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
		self.setRootIsDecorated(True)
		header=QtCore.QStringList()
		header.append("Time")
		header.append("Phase")
		header.append("Illumination")
		self.setHeaderLabels(header)
		self.setColumnCount(3)
		self.color=self.palette().color(QtGui.QPalette.Midlight)
		self.color.setAlpha(64)
		self.last_index=0
		self.base=self.palette().color(QtGui.QPalette.Base)

	def setIcons(self, icon_list):
		self.icons=icon_list

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
			cycling=self.topLevelItem(i).data(0,32).toPyObject().toPyDateTime()
			if cycling.timetuple().tm_yday == date.timetuple().tm_yday:
				self._highlight_row(i)
				self.last_index=i
				break

	def get_moon_cycle(self,date):
		moon_cycle=get_moon_cycle(date)
		for i in xrange (29):
			newmooncycleitem = QtGui.QTreeWidgetItem()
			newmooncycleitem.setData(0,32,QtCore.QVariant(QtCore.QDateTime(moon_cycle[i][0])))
			newmooncycleitem.setIcon(0,self.icons[moon_cycle[i][1]])
			newmooncycleitem.setText(0,moon_cycle[i][0].strftime("%H:%M:%S - %m/%d/%Y"))
			newmooncycleitem.setText(1,moon_cycle[i][1])
			newmooncycleitem.setText(2,moon_cycle[i][2])
			self.addTopLevelItem(newmooncycleitem)
