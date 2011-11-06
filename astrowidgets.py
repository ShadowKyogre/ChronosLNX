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
		self.tree.setRootIsDecorated(False)
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

	def refresh(self,zodiac):
		at=create_aspect_table(zodiac)
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
	sign_icons, pluto_alternate, admi, nodes):
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
	if other_table is not None and len(other_table) > 0:
		caspects=AspectTableDisplay(info_dialog)
		caspects.setIcons(icons)
		caspects.setSignIcons(sign_icons)
		caspects.setPlutoAlternate(pluto_alternate)
		caspects.setADMI(admi)
		caspects.setNodes(nodes)
		at,compare=create_aspect_table(zodiac,compare=other_table)
		sado=search_special_aspects(at)
		sad=search_special_aspects(compare)
		caspects.buildTable(compare,sad,comparative=True)
		aspects.buildTable(at,sado)
		tabs.addTab(caspects,"Aspects to Natal Chart")
	else:
		aspects.refresh(zodiac)
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
		self.sign_icons, self.pluto_alternate, self.admi, self.nodes)

	def showHouses(self):
		housesDialog(self, self.h, self.capricorn_alternate, self.sign_icons)

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

