#!/usr/bin/env python

# icon.py
#http://www.saltycrane.com/blog/2007/12/pyqt-43-qtableview-qabstracttable-model/
#http://www.commandprompt.com/community/pyqt/book1
#http://doc.qt.nokia.com/latest/qstandarditemmodel.html
import os
import sys
import shlex
import ephem
import subprocess
from PyQt4 import QtGui,QtCore
import geolocationwidget ## from example, but modified a little
import datetimetz #from Zim source code

try:
	import pynotify
except ImportError:
	print "Warning, couldn't import pynotify! On Linux systems, the notifications might look ugly."


from astro import *
from astrowidgets import *
from eventplanner import *
from chronostext import *
import chronosconfig

class ChronosLNX(QtGui.QWidget):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)
		self.timer = QtCore.QTimer(self)
		self.now = datetimetz.now()
		self.make_settings_dialog()
		self.make_tray_icon()
		self.setFixedSize(840, 420)
		self.setWindowTitle('ChronosLNX')
		self.setWindowIcon(CLNXConfig.main_icons['logo'])
		self.mainLayout=QtGui.QHBoxLayout(self)
		self.leftLayout=QtGui.QVBoxLayout()
		self.rightLayout=QtGui.QVBoxLayout()
		self.add_widgets()
		self.mainLayout.addLayout(self.leftLayout)
		self.mainLayout.addLayout(self.rightLayout)
		QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.update)
		self.timer.start(1000)

	def add_widgets(self):
		##left pane
		self.calendar=AstroCalendar(self)
		self.calendar.setIcons(CLNXConfig.moon_icons)
		self.make_calendar_menu()
		self.leftLayout.addWidget(self.calendar)
		
		saveRangeButton=QtGui.QPushButton("Save data from dates",self)
		#saveRangeButton.clicked.connect(self.show_saveRange)
		saveRangeButton.setIcon(QtGui.QIcon.fromTheme("document-save-as"))
		self.leftLayout.addWidget(saveRangeButton)
		
		settingsButton=QtGui.QPushButton("Settings",self)
		settingsButton.clicked.connect(self.settings_dialog.open)
		settingsButton.setIcon(QtGui.QIcon.fromTheme("preferences-other"))
		self.leftLayout.addWidget(settingsButton)

		helpButton=QtGui.QPushButton("Help",self)
		helpButton.clicked.connect(self.show_about)
		helpButton.setIcon(QtGui.QIcon.fromTheme("help-contents"))
		self.leftLayout.addWidget(helpButton)

		aboutButton=QtGui.QPushButton("About",self)
		aboutButton.clicked.connect(self.show_about)
		aboutButton.setIcon(QtGui.QIcon.fromTheme("help-about"))
		self.leftLayout.addWidget(aboutButton)
		
		##right pane
		dayinfo=QtGui.QHBoxLayout()
		self.todayPicture=QtGui.QLabel()
		self.todayOther=QtGui.QLabel()
		dayinfo.addWidget(self.todayPicture)
		dayinfo.addWidget(self.todayOther)

		self.hoursToday=PlanetaryHoursList(self)
		self.hoursToday.setIcons(CLNXConfig.main_icons)

		self.moonToday=MoonCycleList(self)
		self.moonToday.setIcons(CLNXConfig.moon_icons)

		self.signsToday=SignsForDayList(self)
		self.signsToday.setIcons(CLNXConfig.main_icons)

		self.eventsToday=EventsList(self)

		dayData=QtGui.QTabWidget()
		self.prepare_hours_for_today()
		self.moonToday.get_moon_cycle(self.now)
		self.moonToday.highlight_cycle_phase(self.now)
		self.signsToday.get_constellations(self.now)

		CLNXConfig.todays_schedule.setDate(self.now.date())
		self.eventsToday.tree.setModel(CLNXConfig.todays_schedule)

		dayData.addTab(self.hoursToday,"Planetary Hours")
		dayData.addTab(self.moonToday,"Moon Cycles")
		dayData.addTab(self.signsToday,"Today's Signs")
		dayData.addTab(self.eventsToday,"Today's Events")

		self.rightLayout.addLayout(dayinfo)
		self.rightLayout.addWidget(dayData)
		self.update()

##time related

	def update_hours(self):
		self.hoursToday.clear()
		self.signsToday.clear()
		self.prepare_hours_for_today()
		self.eventsToday.tree.model().setDate(self.now.date())
		self.signsToday.get_constellations(self.now)

	def update_moon_cycle(self):
		if ephem.localtime(ephem.next_new_moon(self.now)).timetuple().tm_yday == self.now.timetuple().tm_yday:
			self.moonToday.clear()
			self.moonToday.get_moon_cycle(self.now)
		self.moonToday.highlight_cycle_phase(self.now)

	def prepare_hours_for_today(self):
		self.pday = get_planet_day(int(self.now.strftime('%w')))
		self.sunrise,self.sunset,self.next_sunrise=get_sunrise_and_sunset(self.now, 
										CLNXConfig.current_latitude, 
										CLNXConfig.current_longitude, 
										CLNXConfig.current_elevation)
		if self.now < self.sunrise:
			self.sunrise,self.sunset,self.next_sunrise=get_sunrise_and_sunset(self.now-timedelta(days=1), 
											CLNXConfig.current_latitude, 
											CLNXConfig.current_longitude, 
											CLNXConfig.current_elevation)
			self.hoursToday.prepareHours(self.now-timedelta(days=1), 
						CLNXConfig.current_latitude, 
						CLNXConfig.current_longitude, 
						CLNXConfig.current_elevation)
			self.pday = get_planet_day(int(self.now.strftime('%w'))-1)
		else:
			self.hoursToday.prepareHours(self.now, CLNXConfig.current_latitude, CLNXConfig.current_longitude, CLNXConfig.current_elevation)
			#http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/qtreewidgetitem.html#setIcon
			#http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/qtreewidget.html

	def event_trigger(self, event_type, text):
		if event_type == "Save to file":
			print_to_file(self, text, self.now)
		elif event_type == "Command":
			command=shlex.split(text)
			subprocess.call([command])
		else: #event_type == "Textual reminder"
			path=CLNXConfig.grab_icon_path(CLNXConfig.current_theme,"misc","chronoslnx")
			if pynotify.init("ChronosLNX"):
				n = pynotify.Notification("Textual reminder", text, path)
				n.set_timeout(10000)
				n.show()
			else:
				self.trayIcon.showMessage("Textual reminder", text, CLNXConfig.main_icons['logo'],msecs=10000)

	def check_alarm(self):
		for i in xrange(CLNXConfig.todays_schedule.rowCount()):
			hour_trigger=False
			real_row = CLNXConfig.todays_schedule.mapToSource(CLNXConfig.todays_schedule.index(i,0)).row()

			enabled_item=CLNXConfig.schedule.item(real_row,0)
			if enabled_item.checkState() == QtCore.Qt.Checked:
				hour_item=CLNXConfig.schedule.item(real_row,2).data(QtCore.Qt.UserRole).toPyObject()
				if isinstance(hour_item,QtCore.QTime):
					if self.now.hour == hour_item.hour() and \
						self.now.minute == hour_item.minute() and \
						self.now.second == 0:
						hour_trigger = True
				else:
					if self.phour == str(hour_item):
						for dt in self.hoursToday.grabHoursOfType(self.phour):
							if dt.hour == self.now.hour and \
							dt.minute == self.now.minute and \
							dt.second == self.now.second:
								hour_trigger=True
								break

				event_type_item=str(CLNXConfig.schedule.item(real_row,3).data(QtCore.Qt.EditRole).toPyObject())
				text_item=str(CLNXConfig.schedule.item(real_row,4).data(QtCore.Qt.EditRole).toPyObject())
				
				if hour_trigger:
					self.event_trigger(event_type_item,text_item)

##datepicking related
#http://eli.thegreenplace.net/2011/04/25/passing-extra-arguments-to-pyqt-slot/

	def get_info_for_date(self, date):
		info_dialog=QtGui.QDialog()
		info_dialog.setFixedSize(400,400)
		info_dialog.setWindowTitle("Info for %s" %(date.strftime("%m/%d/%Y")))
		hbox=QtGui.QHBoxLayout(info_dialog)

		hoursToday=PlanetaryHoursList(info_dialog)
		hoursToday.setIcons(CLNXConfig.main_icons)
		
		moonToday=MoonCycleList(info_dialog)
		moonToday.setIcons(CLNXConfig.moon_icons)

		signsToday=SignsForDayList(info_dialog)
		signsToday.setIcons(CLNXConfig.main_icons)

		eventsToday=EventsList(info_dialog)
		model=DayEventsModel()
		model.setSourceModel(CLNXConfig.schedule)
		model.setDate(date)
		eventsToday.tree.setModel(model)

		dayData=QtGui.QTabWidget(info_dialog)

		hoursToday.prepareHours(date,CLNXConfig.current_latitude,
					CLNXConfig.current_longitude,
					CLNXConfig.current_elevation)
		moonToday.get_moon_cycle(date)
		moonToday.highlight_cycle_phase(date)
		signsToday.get_constellations(date)

		dayData.addTab(hoursToday,"Planetary Hours")
		dayData.addTab(moonToday,"Moon Cycles")
		dayData.addTab(signsToday,"Signs For This Day")
		dayData.addTab(eventsToday,"Events for This Day")
		hbox.addWidget(dayData)
		info_dialog.exec_()

	def make_calendar_menu(self):
		self.calendar.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.connect(self.calendar,QtCore.SIGNAL('customContextMenuRequested(QPoint)'), self.get_cal_menu)
		#self.calendar.setContextMenu(self.menu)

	def copy_to_clipboard(self, option,date):
		if option == "All":
			text=prepare_all(date, CLNXConfig.current_latitude, 
					CLNXConfig.current_longitude, 
					CLNXConfig.current_elevation)
		elif option == "Moon":
			text=prepare_moon_cycle(date)
		elif option == "Signs":
			text=prepare_sign_info(date)
		elif option == "Hours":
			text=prepare_planetary_info(date, CLNXConfig.current_latitude, 
						CLNXConfig.current_longitude, 
						CLNXConfig.current_elevation)
		else: #option == "Events"
			text=prepare_events(date, CLNXConfig.schedule)
		app.clipboard().setText(text)

#KGlobal::locale::Warning your global KLocale is being recreated with a valid main component instead of a fake component, this usually means you tried to call i18n related functions before your main component was created. You should not do that since it most likely will not work
#X Error: RenderBadPicture (invalid Picture parameter) 174
#Extension:    153 (RENDER)
#Minor opcode: 8 (RenderComposite)
#Resource id:  0x3800836
#weird bug related to opening file dialog on linux through this, but it's harmless

	def print_to_file(self, option,date,filename=None):
		if option == "All":
			text=prepare_all(date, CLNXConfig.current_latitude, 
					CLNXConfig.current_longitude, 
					CLNXConfig.current_elevation)
		elif option == "Moon Cycle":
			text=prepare_moon_cycle(date)
		elif option == "Planetary Signs":
			text=prepare_sign_info(date)
		elif option == "Planetary Hours":
			text=prepare_planetary_info(date, CLNXConfig.current_latitude, 
						CLNXConfig.current_longitude, 
						CLNXConfig.current_elevation)
		else:  #option == "Events"
			text=prepare_events(date, CLNXConfig.schedule)
		if filename == None:
			filename=QtGui.QFileDialog.getSaveFileName(parent=self,
					caption="Saving %s for %s" %(option, date.strftime("%m/%d/%Y")),
					filter="*.txt")
		if filename is not None and filename != "":
			f=open(filename,"w")
			f.write(text)
			QtGui.QMessageBox.information(self,
						"Saved", 
						"%s has the %s you saved." %(filename, option))
			#replace this with systray notification

	def get_cal_menu(self, qpoint):
		table=self.calendar.findChild(QtGui.QTableView)
		idx=table.indexAt(qpoint)
		mdl=table.model()
		if idx.column() > 0 and idx.row() > 0:
			month=self.calendar.monthShown()
			year=self.calendar.yearShown()
			day=mdl.data(idx,0).toPyObject()
			if idx.row() is 1 and day > 7:
				date=datetime(year=year,month=month-1,day=day).replace(tzinfo=LocalTimezone())
			elif idx.row() is 6 and day < 24:
				date=datetime(year=year,month=month+1,day=day).replace(tzinfo=LocalTimezone())
			else:
				date=datetime(year=year,month=month,day=day).replace(tzinfo=LocalTimezone())
			#self.calendar.setGridVisible(True)
			menu=QtGui.QMenu()
			infoitem=menu.addAction("Info for %s" %(date.strftime("%m/%d/%Y")))
			infoitem.triggered.connect(lambda: self.get_info_for_date(date))
			infoitem.setIcon(QtGui.QIcon.fromTheme("dialog-information"))

			copymenu=menu.addMenu("Copy")
			copymenu.setIcon(QtGui.QIcon.fromTheme("edit-copy"))
			copyall=copymenu.addAction("All")
			copydate=copymenu.addAction("Date")
			copyplanetdata=copymenu.addAction("Planetary Hours")
			copymoonphasedata=copymenu.addAction("Moon Phases")
			copysignsdata=copymenu.addAction("Signs for this date")
			copyeventdata=copymenu.addAction("Events")

			copyall.triggered.connect(lambda: self.copy_to_clipboard("All",date))
			copydate.triggered.connect(lambda: app.clipboard().setText(date.strftime("%m/%d/%Y")))
			copyplanetdata.triggered.connect(lambda: self.copy_to_clipboard("Planetary Hours",date))
			copymoonphasedata.triggered.connect(lambda: self.copy_to_clipboard("Moon Cycle",date))
			copysignsdata.triggered.connect(lambda: self.copy_to_clipboard("Planetary Signs",date))
			copyeventdata.triggered.connect(lambda: self.copy_to_clipboard("Events", date))

			savemenu=menu.addMenu("Save to File")
			savemenu.setIcon(QtGui.QIcon.fromTheme("document-save-as"))
			saveall=savemenu.addAction("All")
			saveplanetdata=savemenu.addAction("Planetary Hours")
			savemoonphasedata=savemenu.addAction("Moon Phases")
			savesignsdata=savemenu.addAction("Signs for this date")
			saveeventdata=savemenu.addAction("Events")

			saveall.triggered.connect(lambda: self.print_to_file("All",date))
			saveplanetdata.triggered.connect(lambda: self.print_to_file("Planetary Hours",date))
			savemoonphasedata.triggered.connect(lambda: self.print_to_file("Moon Cycle",date))
			savesignsdata.triggered.connect(lambda: self.print_to_file("Planetary Signs",date))
			saveeventdata.triggered.connect(lambda: self.print_to_file("Events",date))

			menu.exec_(self.calendar.mapToGlobal(qpoint))
		#http://www.qtcentre.org/archive/index.php/t-42524.html?s=ef30fdd9697c337a1d588ce9d26f47d8

##config related

	def settings_reset(self):
		CLNXConfig.reset_settings()
		self.settings_dialog.location_widget.setLatitude(CLNXConfig.current_latitude)
		self.settings_dialog.location_widget.setLongitude(CLNXConfig.current_longitude)
		self.settings_dialog.location_widget.setElevation(CLNXConfig.current_elevation)
		self.settings_dialog.appearance_icons.setCurrentIndex(self.settings_dialog.appearance_icons.findText(CLNXConfig.current_theme))

	def settings_change(self):
		lat=float(self.settings_dialog.location_widget.latitude)
		lng=float(self.settings_dialog.location_widget.longitude)
		elv=float(self.settings_dialog.location_widget.elevation)
		thm=str(self.settings_dialog.appearance_icons.currentText())
		CLNXConfig.current_latitude=lat
		CLNXConfig.current_longitude=lng
		CLNXConfig.current_elevation=elv
		CLNXConfig.current_theme=thm
		CLNXConfig.prepare_icons()
		self.calendar.setIcons(CLNXConfig.moon_icons)
		self.hoursToday.setIcons(CLNXConfig.main_icons)
		self.moonToday.setIcons(CLNXConfig.moon_icons)
		self.signsToday.setIcons(CLNXConfig.main_icons)
		self.update_hours()
		self.moonToday.clear()
		self.moonToday.get_moon_cycle(self.now)
		#eventually load DB of events

	def settings_write(self):
		self.settings_change()
		CLNXConfig.save_settings()
		#CLNXConfig.save_schedule()
		self.settings_dialog.hide()

	def make_settings_dialog(self):
		self.settings_dialog=QtGui.QDialog(self)
		self.settings_dialog.setWindowTitle("Settings")
		tabs=QtGui.QTabWidget(self.settings_dialog)
		self.settings_dialog.setFixedSize(400,400)
		
		location_page=QtGui.QFrame()
		appearance_page=QtGui.QFrame()
		events_page=QtGui.QFrame()
		tabs.addTab(location_page,"Location")
		tabs.addTab(appearance_page,"Appearance")
		tabs.addTab(events_page,"Events")
		
		self.settings_dialog.location_widget = geolocationwidget.GeoLocationWidget(location_page)
		self.settings_dialog.location_widget.setLatitude(CLNXConfig.current_latitude)
		self.settings_dialog.location_widget.setLongitude(CLNXConfig.current_longitude)
		self.settings_dialog.location_widget.setElevation(CLNXConfig.current_elevation)
		
		layout=QtGui.QVBoxLayout(self.settings_dialog)
		layout.addWidget(tabs)
		
		grid=QtGui.QGridLayout(appearance_page)
		appearance_label=QtGui.QLabel("Icon theme")
		self.settings_dialog.appearance_icons=QtGui.QComboBox()
		self.settings_dialog.appearance_icons.addItem("None")
		for theme in CLNXConfig.get_available_themes():
			icon=QtGui.QIcon(CLNXConfig.grab_icon_path(theme,"misc","chronoslnx"))
			self.settings_dialog.appearance_icons.addItem(icon,theme)
		self.settings_dialog.appearance_icons.setCurrentIndex(self.settings_dialog.appearance_icons.findText(CLNXConfig.current_theme))
		grid.addWidget(appearance_label,0,0)
		grid.addWidget(self.settings_dialog.appearance_icons,0,1)
		
		buttonbox=QtGui.QDialogButtonBox(QtCore.Qt.Horizontal)
		resetbutton=buttonbox.addButton(QtGui.QDialogButtonBox.Reset)
		okbutton=buttonbox.addButton(QtGui.QDialogButtonBox.Ok)
		applybutton=buttonbox.addButton(QtGui.QDialogButtonBox.Apply)
		cancelbutton=buttonbox.addButton(QtGui.QDialogButtonBox.Cancel)
		
		resetbutton.clicked.connect(self.settings_reset)
		okbutton.clicked.connect(self.settings_write)
		applybutton.clicked.connect(self.settings_change)
		cancelbutton.clicked.connect(self.settings_dialog.hide)
		layout.addWidget(buttonbox)
		
		self.settings_dialog.eventplanner=EventsList(events_page)
		a_vbox=QtGui.QVBoxLayout(events_page)
		a_vbox.addWidget(self.settings_dialog.eventplanner)
		self.settings_dialog.eventplanner.tree.setModel(CLNXConfig.schedule)

## systray
#http://stackoverflow.com/questions/893984/pyqt-show-menu-in-a-system-tray-application
#http://www.itfingers.com/Question/758256/pyqt4-minimize-to-tray

	def make_tray_icon(self):
		  self.trayIcon = QtGui.QSystemTrayIcon(QtGui.QIcon(CLNXConfig.main_icons['logo']), app)
		  #self.trayIcon = QtGui.QSystemTrayIcon(app)
		  menu = QtGui.QMenu()
		  quitAction = QtGui.QAction(self.tr("&Quit"), self)
		  QtCore.QObject.connect(quitAction, QtCore.SIGNAL("triggered()"), QtGui.qApp, QtCore.SLOT("quit()"))
		  showaction=menu.addAction("&Show",self.show)
		  showaction.setIcon(QtGui.QIcon.fromTheme("show-menu"))
		  setaction=menu.addAction("&Settings",self.settings_dialog.open)
		  setaction.setIcon(QtGui.QIcon.fromTheme("preferences-other"))
		  menu.addAction(quitAction)
		  quitAction.setIcon(QtGui.QIcon.fromTheme("application-exit"))
		  self.trayIcon.setContextMenu(menu)
		  traySignal = "activated(QSystemTrayIcon::ActivationReason)"
		  QtCore.QObject.connect(self.trayIcon, QtCore.SIGNAL(traySignal), self.__icon_activated)
		  self.trayIcon.show()

	def _ChronosLNX__icon_activated(self,reason):
		if reason == QtGui.QSystemTrayIcon.DoubleClick:
			if(self.isHidden()):
				self.show()
			else:
				self.hide()

	def closeEvent(self, event):
		self.hide()
		event.ignore()

##misc
#http://www.saltycrane.com/blog/2008/01/python-variable-scope-notes/

	def show_about(self):
		QtGui.QMessageBox.about (self, "About ChronosLNX", "<center><big><b>ChronosLNX 0.2</b></big><br />\
A simple tool for checking planetary hours and moon phases.<br />\
(C) ShadowKyogre 2011<br /><a href=\"http://shadowkyogre.github.com/ChronosLNX/\">ChronosLNX Homepage</a></center>")

	def update(self):
		self.now = datetimetz.now()
		if self.now > self.next_sunrise:
			self.update_hours()
			self.update_moon_cycle()
		self.phour = self.hoursToday.grab_nearest_hour(self.now)
		planets_string = "This is the day of %s, the hour of %s" %(self.pday, self.phour)
		moon_phase=grab_moon_phase(self.now)
		sign_string="The sign of the month is %s" %(calculate_sign(self.now))
		if CLNXConfig.current_theme == "None":
			sysicon=QtGui.QIcon(CLNXConfig.grab_icon_path("DarkGlyphs","misc","chronoslnx"))
		else:
			sysicon=CLNXConfig.main_icons[str(self.phour)]
		self.trayIcon.setToolTip("%s - %s\n%s\n%s\n%s" %(self.now.strftime("%Y/%m/%d"), self.now.strftime("%H:%M:%S"), 
			sign_string, moon_phase, planets_string))
		self.trayIcon.setIcon(sysicon)
		self.todayPicture.setPixmap(CLNXConfig.main_icons[str(self.phour)].pixmap(64,64))
		self.todayOther.setText("%s\n%s\n%s\n%s" %(self.now.strftime("%H:%M:%S"), 
			sign_string, moon_phase, planets_string))
		self.check_alarm()

app = QtGui.QApplication(sys.argv)
CLNXConfig = chronosconfig.ChronosLNXConfig()
chronoslnx = ChronosLNX()
chronoslnx.show()
sys.exit(app.exec_())
