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
		self.color.setAlpha(64)
		self.setDateRange(QtCore.QDate(1902,1,1),QtCore.QDate(2037,1,1))
		self.selectionChanged.connect(self.updateCells)

	def setIcons(self, icon_list):
		self.icons=icon_list

	def selectedDateTime(self):
		return QtCore.QDateTime(self.selectedDate())

	def paintCell(self, painter, rect, date):
		QtGui.QCalendarWidget.paintCell(self, painter, rect, date)

		#first_day = self.firstDayOfWeek()
		#last_day = first_day + 6
		##current_date = self.selectedDate()
		#current_day = current_date.dayOfWeek()
		##print first_day,last_day
		#if first_day <= current_day:
			#first_date = current_date.addDays(first_day - current_day)
		#else:
			#first_date = current_date.addDays(first_day - 7 - current_day)
		#last_date = first_date.addDays(6)
		#print grab_moon_phase(datetime(date.toPyDate()))
		if date == QtCore.QDate.currentDate():
		#if first_date <= date <= last_date:
			painter.fillRect(rect, self.color)
		datetime=QtCore.QDateTime(date).toPyDateTime().replace(tzinfo=tz.gettz())
		phase=state_to_string(grab_phase(datetime), swisseph.MOON)
		icon=self.icons[phase]
		icon.paint(painter,QtCore.QRect(rect.x(),rect.y(),14,14))

#http://doc.qt.nokia.com/stable/qhelpcontentwidget.html
#http://www.riverbankcomputing.com/static/Docs/PyQt4/html/qthelp.html
#http://ubuntuforums.org/showthread.php?t=1110989
#figure out how to get these to load icons
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

	# def currentHour(self):
		# return self.current_hour
#
	# def isUpdating(self):
		# return self.updating
#
	# @pyqtSignature("setUpdating(bool)")
	# def setUpdating(self,update_status):
		# if self.updating != update_status:
			# self.updating=updating
			# self.emit(SIGNAL("updatingChanged(bool)"))
	# updating = pyqtProperty("datetime", dateTime, setDateTime)
#
	# def dateTime(self):
		# return self.datetime
#
	# @pyqtSignature("setDateTime(datetime)")
	# def setDateTime(self, date):
		# if self.datetime != date:
			# self.date=date
			# self.emit(SIGNAL("dateTimeChanged(datetime)"), date)
	#
	# datetime = pyqtProperty("datetime", dateTime, setDateTime)

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
		self.time.setDisplayFormat("HH:mm")
		self.time.timeChanged.connect(self.update_degrees)

	def update_degrees(self, qtime):
		self.tree.clear()
		self.target_date=self.target_date.replace(hour=qtime.hour())\
		.replace(minute=qtime.minute())\
		.replace(second=qtime.second())
		self._grab()

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
		constellations=get_signs(self.target_date,self.observer,nodes=self.nodes)
		for i in constellations:
			item=QtGui.QTreeWidgetItem()
			if self.pluto_alternate and i[0] == "Pluto":
				item.setIcon(0,self.icons['Pluto 2'])
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
