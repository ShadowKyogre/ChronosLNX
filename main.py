#!/usr/bin/env python

# icon.py
#http://www.saltycrane.com/blog/2007/12/pyqt-43-qtableview-qabstracttable-model/
#http://www.commandprompt.com/community/pyqt/book1
#http://doc.qt.nokia.com/latest/qstandarditemmodel.html
#http://www.interactivestars.com/lost_zodiac/lost_zodiac_sign.html <- interesting
#http://www.ips-planetarium.org/planetarian/articles/realconstellations_zodiac.html <- this too
import os
import sys
from shlex import split
from subprocess import call
from PyQt4 import QtGui,QtCore
import geolocationwidget ## from example, but modified a little
from re import findall,match
import datetime
from astro_rewrite import *
from astrowidgets import *
from eventplanner import *
from chronostext import *
import chronosconfig
pynf=True

class ReusableDialog(QtGui.QDialog):
	def __init__(self, *args):
		QtGui.QDialog.__init__(self, *args)

	def closeEvent(self, event):
		self.hide()
		event.ignore()

class ChronosLNX(QtGui.QWidget):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)
		self.timer = QtCore.QTimer(self)
		self.now = datetime.now().replace(tzinfo=tz.gettz())
		self.make_settings_dialog()
		self.make_save_for_date_range()
		self.make_tray_icon()
		self.setFixedSize(840, 420)
		self.setWindowTitle(CLNXConfig.APPNAME)
		self.setWindowIcon(CLNXConfig.main_icons['logo'])
		self.mainLayout=QtGui.QGridLayout(self)
		self.leftLayout=QtGui.QVBoxLayout()
		self.rightLayout=QtGui.QVBoxLayout()
		self.add_widgets()
		self.mainLayout.addLayout(self.leftLayout,0,0)
		self.mainLayout.addLayout(self.rightLayout,0,1)
		self.timer.timeout.connect(self.update)
		#self.setWindowFlags(QtGui.Qt.WA_Window)
		self.timer.start(1000)

	def add_widgets(self):
		##left pane
		self.calendar=AstroCalendar(self)
		self.calendar.setIcons(CLNXConfig.moon_icons)
		self.make_calendar_menu()
		self.leftLayout.addWidget(self.calendar)

		saveRangeButton=QtGui.QPushButton("Save data from dates",self)
		saveRangeButton.clicked.connect(self.save_for_range_dialog.open)
		saveRangeButton.setIcon(QtGui.QIcon.fromTheme("document-save-as"))
		self.leftLayout.addWidget(saveRangeButton)

		settingsButton=QtGui.QPushButton("Settings",self)
		settingsButton.clicked.connect(self.settings_dialog.open)
		settingsButton.setIcon(QtGui.QIcon.fromTheme("preferences-other"))
		self.leftLayout.addWidget(settingsButton)

		#helpButton=QtGui.QPushButton("Help",self)
		#helpButton.clicked.connect(self.show_about)
		#helpButton.setIcon(QtGui.QIcon.fromTheme("help-contents"))
		#self.leftLayout.addWidget(helpButton)

		aboutButton=QtGui.QPushButton("About",self)
		aboutButton.clicked.connect(self.show_about)
		aboutButton.setIcon(QtGui.QIcon.fromTheme("help-about"))
		self.leftLayout.addWidget(aboutButton)

		##right pane
		dayinfo=QtGui.QHBoxLayout()
		self.todayPicture=QtGui.QLabel()
		self.todayOther=QtGui.QLabel()
		self.todayOther.setTextFormat(QtCore.Qt.RichText)
		dayinfo.addWidget(self.todayPicture)
		dayinfo.addWidget(self.todayOther)

		self.hoursToday=PlanetaryHoursList(self)
		self.hoursToday.setIcons(CLNXConfig.main_icons)

		self.moonToday=MoonCycleList(self)
		self.moonToday.setIcons(CLNXConfig.moon_icons)

		self.signsToday=SignsForDayList(self)
		self.signsToday.setIcons(CLNXConfig.main_icons)
		self.signsToday.setSignIcons(CLNXConfig.sign_icons)
		self.signsToday.setNodes(CLNXConfig.show_nodes)
		self.signsToday.setPlutoAlternate(CLNXConfig.pluto_alt)
		self.signsToday.setCapricornAlternate(CLNXConfig.capricorn_alt)

		self.eventsToday=EventsList(self)

		dayData=QtGui.QTabWidget()
		self.prepare_hours_for_today()
		self.moonToday.get_moon_cycle(self.now)
		self.moonToday.highlight_cycle_phase(self.now)
		self.signsToday.get_constellations(self.now, CLNXConfig.observer)

		CLNXConfig.todays_schedule.setDate(self.now.date())
		self.eventsToday.tree.setModel(CLNXConfig.todays_schedule)

		dayData.addTab(self.hoursToday,"Planetary Hours")
		dayData.addTab(self.moonToday,"Moon Phases")
		dayData.addTab(self.signsToday,"Signs")
		dayData.addTab(self.eventsToday,"Events")

		self.rightLayout.addLayout(dayinfo)
		self.rightLayout.addWidget(dayData)
		self.update()

##time related

	def update_hours(self):
		self.hoursToday.clear()
		self.signsToday.tree.clear()
		self.prepare_hours_for_today()
		self.eventsToday.tree.model().setDate(self.now.date())
		self.signsToday.get_constellations(self.now, CLNXConfig.observer)

	def update_moon_cycle(self):
		if prev_new_moon(self.now).timetuple().tm_yday == self.now.timetuple().tm_yday:
			self.moonToday.clear()
			self.moonToday.get_moon_cycle(self.now)
		self.moonToday.highlight_cycle_phase(self.now)

	def prepare_hours_for_today(self):
		self.pday = get_planet_day(int(self.now.strftime('%w')))
		self.sunrise,self.sunset,self.next_sunrise=get_sunrise_and_sunset(self.now, CLNXConfig.observer)
		if self.now < self.sunrise:
			self.sunrise,self.sunset,self.next_sunrise=get_sunrise_and_sunset(self.now-timedelta(days=1), CLNXConfig.observer)
			self.hoursToday.prepareHours(self.now-timedelta(days=1), CLNXConfig.observer)
			self.pday = get_planet_day(int(self.now.strftime('%w'))-1)
		else:
			self.hoursToday.prepareHours(self.now, CLNXConfig.observer)
			#http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/qtreewidgetitem.html#setIcon
			#http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/qtreewidget.html

	def show_notification(self, title, text, ptrigger):
			if pynf:
				if ptrigger:
					path=CLNXConfig.grab_icon_path(CLNXConfig.current_theme,"planets",str(self.phour.toLower()))
				else:
					path=CLNXConfig.grab_icon_path(CLNXConfig.current_theme,"misc","chronoslnx")
				n = pynotify.Notification(title, text, path)
				n.set_timeout(10000)
				n.show()
			else:
				if self.trayIcon.supportsMessages():
					if ptrigger:
						self.trayIcon.showMessage(title, text, \
						      CLNXConfig.main_icons[self.phour],msecs=10000)
					else:
						self.trayIcon.showMessage(title, text, \
						      CLNXConfig.main_icons['logo'],msecs=10000)
				else:
					#last resort, as popup dialogs are annoying
					if ptrigger:
						pixmap=self.main_pixmaps[self.phour]
					else:
						pixmap=self.main_pixmaps['logo']
					dialog=QtGui.QMessageBox(self)
					dialog.setTitle(title)
					dialog.setTitle(text)
					dialog.setIconPixmap(pixmap)
					dialog.open()

##datepicking related
#http://eli.thegreenplace.net/2011/04/25/passing-extra-arguments-to-pyqt-slot/

	def get_info_for_date(self, date):
		info_dialog=QtGui.QDialog(self)
		info_dialog.setFixedSize(400,400)
		info_dialog.setWindowTitle("Info for %s" %(date.strftime("%m/%d/%Y")))
		date=date.replace(hour=12).replace(minute=0).replace(second=0) #use noon time for default
		info_dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
		#info_dialog.setFlags(QtCore.Qt.WA_DeleteOnClose)
		hbox=QtGui.QHBoxLayout(info_dialog)

		hoursToday=PlanetaryHoursList(info_dialog)
		hoursToday.setIcons(CLNXConfig.main_icons)
		hoursToday.setAttribute(QtCore.Qt.WA_DeleteOnClose)

		moonToday=MoonCycleList(info_dialog)
		moonToday.setIcons(CLNXConfig.moon_icons)
		moonToday.setAttribute(QtCore.Qt.WA_DeleteOnClose)

		signsToday=SignsForDayList(info_dialog)
		signsToday.setIcons(CLNXConfig.main_icons)
		signsToday.setSignIcons(CLNXConfig.sign_icons)
		signsToday.setPlutoAlternate(CLNXConfig.pluto_alt)
		signsToday.setNodes(CLNXConfig.show_nodes)
		signsToday.setCapricornAlternate(CLNXConfig.capricorn_alt)
		signsToday.setAttribute(QtCore.Qt.WA_DeleteOnClose)

		eventsToday=EventsList(info_dialog)
		model=DayEventsModel()
		model.setSourceModel(CLNXConfig.schedule)
		model.setDate(date)
		eventsToday.tree.setModel(model)
		eventsToday.setAttribute(QtCore.Qt.WA_DeleteOnClose)

		dayData=QtGui.QTabWidget(info_dialog)

		hoursToday.prepareHours(date,CLNXConfig.observer)
		moonToday.get_moon_cycle(date)
		moonToday.highlight_cycle_phase(date)
		signsToday.get_constellations(date, CLNXConfig.observer)

		dayData.addTab(hoursToday,"Planetary Hours")
		dayData.addTab(moonToday,"Moon Phases")
		dayData.addTab(signsToday,"Signs")
		dayData.addTab(eventsToday,"Events")
		hbox.addWidget(dayData)
		info_dialog.show()

	def make_save_for_date_range(self):
		#self.save_for_range_dialog=QtGui.QDialog(self)
		self.save_for_range_dialog=ReusableDialog(self)
		self.save_for_range_dialog.setFixedSize(380,280)
		self.save_for_range_dialog.setWindowTitle("Save Data for Dates")
		grid=QtGui.QGridLayout(self.save_for_range_dialog)

		self.save_for_range_dialog.date_start=QtGui.QDateEdit(self.save_for_range_dialog)
		self.save_for_range_dialog.date_start.setDisplayFormat("MM/dd/yyyy")
		self.save_for_range_dialog.date_end=QtGui.QDateEdit(self.save_for_range_dialog)
		self.save_for_range_dialog.date_end.setDisplayFormat("MM/dd/yyyy")

		grid.addWidget(QtGui.QLabel("Save from"),0,0)
		grid.addWidget(self.save_for_range_dialog.date_start,0,1)
		grid.addWidget(QtGui.QLabel("To"),1,0)
		grid.addWidget(self.save_for_range_dialog.date_end,1,1)
		grid.addWidget(QtGui.QLabel("Data to Save"),2,0)

		self.save_for_range_dialog.checkboxes=QtGui.QButtonGroup()
		self.save_for_range_dialog.checkboxes.setExclusive(False)
		checkboxes_frame=QtGui.QFrame(self.save_for_range_dialog)

		vbox=QtGui.QVBoxLayout(checkboxes_frame)

		all_check=QtGui.QCheckBox("All",checkboxes_frame)
		ph_check=QtGui.QCheckBox("Planetary Hours",checkboxes_frame)
		s_check=QtGui.QCheckBox("Planetary Signs",checkboxes_frame)
		m_check=QtGui.QCheckBox("Moon Phase",checkboxes_frame)
		e_check=QtGui.QCheckBox("Events",checkboxes_frame)

		self.save_for_range_dialog.checkboxes.addButton(all_check)
		self.save_for_range_dialog.checkboxes.addButton(ph_check)
		self.save_for_range_dialog.checkboxes.addButton(s_check)
		self.save_for_range_dialog.checkboxes.addButton(m_check)
		self.save_for_range_dialog.checkboxes.addButton(e_check)

		vbox.addWidget(all_check)
		vbox.addWidget(ph_check)
		vbox.addWidget(s_check)
		vbox.addWidget(m_check)
		vbox.addWidget(e_check)

		grid.addWidget(checkboxes_frame,2,1)

		grid.addWidget(QtGui.QLabel("Folder to save in"),3,0)
		hbox=QtGui.QHBoxLayout()
		self.save_for_range_dialog.filename=QtGui.QLineEdit(self.save_for_range_dialog)
		button=QtGui.QPushButton(self.save_for_range_dialog)
		button.setIcon(QtGui.QIcon.fromTheme("document-open"))
		button.clicked.connect(self.get_folder_name)
		hbox.addWidget(self.save_for_range_dialog.filename)
		hbox.addWidget(button)
		grid.addLayout(hbox,3,1)

		buttonbox=QtGui.QDialogButtonBox(QtCore.Qt.Horizontal)
		okbutton=buttonbox.addButton(QtGui.QDialogButtonBox.Ok)
		#okbutton.clicked.connect(self.print_to_file("All", date,filename="",suppress_notification=True))
		okbutton.clicked.connect(self.mass_print)
		cancelbutton=buttonbox.addButton(QtGui.QDialogButtonBox.Cancel)
		cancelbutton.clicked.connect(self.save_for_range_dialog.hide)
		grid.addWidget(buttonbox,4,0,1,2)

	def get_folder_name(self):
		text=QtGui.QFileDialog.getExistingDirectory(caption="Save in folder...")
		self.save_for_range_dialog.filename.setText(text)

	def mass_print(self):
		day_numbers=(self.save_for_range_dialog.date_end.date().toPyDate() - \
			self.save_for_range_dialog.date_start.date().toPyDate()).days
		if self.save_for_range_dialog.filename != "" or \
		self.save_for_range_dialog.filename != None:
			for j in self.save_for_range_dialog.checkboxes.buttons():
					if j.isChecked():
						os.mkdir("%s/%s" %(self.save_for_range_dialog.filename.text(), \
						str(j.text()).replace(" ", "_")))
			for i in xrange(day_numbers+1):
				date=self.save_for_range_dialog.date_start.date().toPyDate()+timedelta(days=i)
				for j in self.save_for_range_dialog.checkboxes.buttons():
					if j.isChecked():
						filename=str(self.save_for_range_dialog.filename.text() + "/%s/%s.txt" \
							%(str(j.text()).replace(" ", "_"),date.strftime("%m-%d-%Y")))
						self.print_to_file(j.text(), date,filename=filename,suppress_notification=False)
						if j.text() == "All":
							break

	def make_calendar_menu(self):
		self.calendar.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.connect(self.calendar,QtCore.SIGNAL('customContextMenuRequested(QPoint)'), self.get_cal_menu)
		#self.calendar.setContextMenu(self.menu)

	def copy_to_clipboard(self, option,date):
		if option == "All":
			text=prepare_all(date, CLNXConfig.observer, CLNXConfig.schedule)
		elif option == "Moon Phase":
			text=prepare_moon_cycle(date)
		elif option == "Planetary Signs":
			text=prepare_sign_info(date, CLNXConfig.observer)
		elif option == "Planetary Hours":
			text=prepare_planetary_info(date, CLNXConfig.observer)
		else: #option == "Events"
			text=prepare_events(date, CLNXConfig.schedule)
		app.clipboard().setText(text)

#KGlobal::locale::Warning your global KLocale is being recreated with a valid main component instead of a fake component, this usually means you tried to call i18n related functions before your main component was created. You should not do that since it most likely will not work
#X Error: RenderBadPicture (invalid Picture parameter) 174
#Extension:    153 (RENDER)
#Minor opcode: 8 (RenderComposite)
#Resource id:  0x3800836
#weird bug related to opening file dialog on linux through this, but it's harmless

	def print_to_file(self, option,date,filename=None,suppress_notification=False):
		if option == "All":
			text=prepare_all(date, CLNXConfig.observer, CLNXConfig.schedule)
		elif option == "Moon Phase":
			text=prepare_moon_cycle(date)
		elif option == "Planetary Signs":
			text=prepare_sign_info(date, CLNXConfig.observer)
		elif option == "Planetary Hours":
			text=prepare_planetary_info(date, CLNXConfig.observer)
		else:  #option == "Events"
			text=prepare_events(date, CLNXConfig.schedule)
		if filename == None:
			filename=QtGui.QFileDialog.getSaveFileName(self, caption="Saving %s for %s" \
					%(option, date.strftime("%m/%d/%Y")),
					filter="*.txt")
		if filename is not None and filename != "":
			f=open(filename,"w")
			f.write(text)
			if not suppress_notification:
				self.show_notification("Saved", "%s has the %s you saved." %(filename, option), False)

	def get_cal_menu(self, qpoint):
		table=self.calendar.findChild(QtGui.QTableView)
		idx=table.indexAt(qpoint)
		mdl=table.model()
		if idx.column() > 0 and idx.row() > 0:
			month=self.calendar.monthShown()
			year=self.calendar.yearShown()
			day=mdl.data(idx,0).toPyObject()
			if idx.row() is 1 and day > 7:
				replace_month=month-1
				if replace_month == 0:
					date=datetime(year=year-1,month=12,day=day).replace(tzinfo=tz.gettz())
				else:
					date=datetime(year=year,month=month-1,day=day).replace(tzinfo=tz.gettz())
			elif (idx.row() is 6 or idx.row() is 5) and day < 24:
				replace_month=(month+1)%12
				if replace_month == 1:
					 date=datetime(year=year+1,month=replace_month,day=day).replace(tzinfo=tz.gettz())
				else:
					date=datetime(year=year,month=replace_month,day=day).replace(tzinfo=tz.gettz())
			else:
				date=datetime(year=year,month=month,day=day).replace(tzinfo=tz.gettz())
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
			copymoonphasedata.triggered.connect(lambda: self.copy_to_clipboard("Moon Phase",date))
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
			savemoonphasedata.triggered.connect(lambda: self.print_to_file("Moon Phase",date))
			savesignsdata.triggered.connect(lambda: self.print_to_file("Planetary Signs",date))
			saveeventdata.triggered.connect(lambda: self.print_to_file("Events",date))

			menu.exec_(self.calendar.mapToGlobal(qpoint))
		#http://www.qtcentre.org/archive/index.php/t-42524.html?s=ef30fdd9697c337a1d588ce9d26f47d8

##config related

	def settings_reset(self):
		CLNXConfig.reset_settings()
		self.update_settings_widgets()

		self.calendar.setIcons(CLNXConfig.moon_icons)
		self.hoursToday.setIcons(CLNXConfig.main_icons)
		self.moonToday.setIcons(CLNXConfig.moon_icons)
		self.signsToday.setIcons(CLNXConfig.main_icons)
		self.signsToday.setSignIcons(CLNXConfig.sign_icons)
		self.signsToday.setPlutoAlternate(CLNXConfig.pluto_alt)
		self.signsToday.setNodes(CLNXConfig.show_nodes)
		self.update_hours()
		self.moonToday.clear()
		self.moonToday.get_moon_cycle(self.now)
		self.moonToday.highlight_cycle_phase(self.now)

	def update_settings_widgets(self):
		self.settings_dialog.location_widget.setLatitude(CLNXConfig.observer.lat)
		self.settings_dialog.location_widget.setLongitude(CLNXConfig.observer.long)
		self.settings_dialog.location_widget.setElevation(CLNXConfig.observer.elevation)

		idx=self.settings_dialog.appearance_icons.findText(CLNXConfig.current_theme)
		self.settings_dialog.appearance_icons.setCurrentIndex(idx)

		self.settings_dialog.s_check.setChecked(CLNXConfig.show_sign)
		self.settings_dialog.m_check.setChecked(CLNXConfig.show_moon)
		self.settings_dialog.h_check.setChecked(CLNXConfig.show_house_of_moment)

		self.settings_dialog.n_check.setChecked(CLNXConfig.show_nodes)
		self.settings_dialog.p_check.setChecked(CLNXConfig.pluto_alt)

		idx2=self.settings_dialog.c_check.findText(CLNXConfig.capricorn_alt)
		self.settings_dialog.c_check.setCurrentIndex(idx2)

	def settings_change(self):

		lat=float(self.settings_dialog.location_widget.latitude)
		lng=float(self.settings_dialog.location_widget.longitude)
		elv=float(self.settings_dialog.location_widget.elevation)
		thm=str(self.settings_dialog.appearance_icons.currentText())
		cp=str(self.settings_dialog.c_check.currentText())

		CLNXConfig.observer.lat=lat
		CLNXConfig.observer.long=lng
		CLNXConfig.observer.elevation=elv
		CLNXConfig.current_theme=thm
		CLNXConfig.show_sign=self.settings_dialog.s_check.isChecked()
		CLNXConfig.show_moon=self.settings_dialog.m_check.isChecked()
		CLNXConfig.show_house_of_moment=self.settings_dialog.h_check.isChecked()
		CLNXConfig.show_nodes=self.settings_dialog.n_check.isChecked()
		CLNXConfig.pluto_alt=self.settings_dialog.p_check.isChecked()
		CLNXConfig.capricorn_alt=cp

		CLNXConfig.prepare_icons()
		self.calendar.setIcons(CLNXConfig.moon_icons)
		self.hoursToday.setIcons(CLNXConfig.main_icons)
		self.moonToday.setIcons(CLNXConfig.moon_icons)
		self.signsToday.setIcons(CLNXConfig.main_icons)
		self.signsToday.setSignIcons(CLNXConfig.sign_icons)
		self.signsToday.setNodes(CLNXConfig.show_nodes)
		self.signsToday.setPlutoAlternate(CLNXConfig.pluto_alt)
		self.signsToday.setCapricornAlternate(CLNXConfig.capricorn_alt)
		self.update_hours()
		self.moonToday.clear()
		self.moonToday.get_moon_cycle(self.now)
		self.moonToday.highlight_cycle_phase(self.now)
		self.settings_dialog.c_check.setItemIcon(0, CLNXConfig.sign_icons['Capricorn'])
		self.settings_dialog.c_check.setItemIcon(1, CLNXConfig.sign_icons['Capricorn 2'])
		self.settings_dialog.c_check.setItemIcon(2, CLNXConfig.sign_icons['Capricorn 3'])
		#eventually load DB of events

	def settings_write(self):
		self.settings_change()
		CLNXConfig.save_settings()
		#CLNXConfig.save_schedule()
		self.settings_dialog.hide()

	def make_settings_dialog(self):
		self.settings_dialog=ReusableDialog(self)
		self.settings_dialog.setWindowTitle("Settings")
		tabs=QtGui.QTabWidget(self.settings_dialog)
		self.settings_dialog.setFixedSize(500,400)

		location_page=QtGui.QFrame()
		appearance_page=QtGui.QFrame()
		events_page=QtGui.QFrame()
		tweaks_page=QtGui.QFrame()

		tabs.addTab(location_page,"Location")
		tabs.addTab(appearance_page,"Appearance")
		tabs.addTab(events_page,"Events")
		tabs.addTab(tweaks_page,"Tweaks")

		self.settings_dialog.location_widget = geolocationwidget.GeoLocationWidget(location_page)

		layout=QtGui.QVBoxLayout(self.settings_dialog)
		layout.addWidget(tabs)

		grid=QtGui.QGridLayout(appearance_page)
		appearance_label=QtGui.QLabel("Icon theme")
		self.settings_dialog.appearance_icons=QtGui.QComboBox()
		self.settings_dialog.appearance_icons.addItem("None")
		for theme in CLNXConfig.get_available_themes():
			icon=QtGui.QIcon(CLNXConfig.grab_icon_path(theme,"misc","chronoslnx"))
			self.settings_dialog.appearance_icons.addItem(icon,theme)

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

		eventplanner=EventsList(events_page)
		a_vbox=QtGui.QVBoxLayout(events_page)
		a_vbox.addWidget(eventplanner)
		eventplanner.tree.setModel(CLNXConfig.schedule)

		tweak_grid=QtGui.QGridLayout(tweaks_page)
		self.settings_dialog.s_check=QtGui.QCheckBox("Sign of the month",tweaks_page)
		self.settings_dialog.m_check=QtGui.QCheckBox("Current moon phase",tweaks_page)
		self.settings_dialog.h_check=QtGui.QCheckBox("House of moment",tweaks_page)

		self.settings_dialog.n_check=QtGui.QCheckBox("Show Nodes",tweaks_page)
		self.settings_dialog.p_check=QtGui.QCheckBox("Use the P-looking Pluto icon",tweaks_page)
		self.settings_dialog.c_check=QtGui.QComboBox()
		self.settings_dialog.c_check.addItem(CLNXConfig.sign_icons["Capricorn"],"Capricorn")
		self.settings_dialog.c_check.addItem(CLNXConfig.sign_icons["Capricorn 2"],"Capricorn 2")
		self.settings_dialog.c_check.addItem(CLNXConfig.sign_icons["Capricorn 3"],"Capricorn 3")

		tweak_grid.addWidget(QtGui.QLabel("Show the following in the main window's textual information"),0,0,1,2)
		tweak_grid.addWidget(self.settings_dialog.s_check,1,1)
		tweak_grid.addWidget(self.settings_dialog.m_check,2,1)
		tweak_grid.addWidget(self.settings_dialog.h_check,3,1)
		tweak_grid.addWidget(QtGui.QLabel("Change the following in the main window's signs information"),4,0,1,2)
		tweak_grid.addWidget(self.settings_dialog.n_check,5,1)
		tweak_grid.addWidget(self.settings_dialog.p_check,6,1)
		tweak_grid.addWidget(self.settings_dialog.c_check,7,1)

		self.update_settings_widgets()

## systray
#http://stackoverflow.com/questions/893984/pyqt-show-menu-in-a-system-tray-application
#http://www.itfingers.com/Question/758256/pyqt4-minimize-to-tray

	def make_tray_icon(self):
		  self.trayIcon = QtGui.QSystemTrayIcon(QtGui.QIcon(CLNXConfig.main_icons['logo']), app)
		  menu = QtGui.QMenu()
		  quitAction = QtGui.QAction(self.tr("&Quit"), self)
		  quitAction.triggered.connect(QtGui.qApp.quit)
		  showaction=menu.addAction("&Show",self.show)
		  showaction.setIcon(QtGui.QIcon.fromTheme("show-menu"))
		  setaction=menu.addAction("&Settings",self.settings_dialog.open)
		  setaction.setIcon(QtGui.QIcon.fromTheme("preferences-other"))
		  menu.addAction(quitAction)
		  quitAction.setIcon(QtGui.QIcon.fromTheme("application-exit"))
		  self.trayIcon.setContextMenu(menu)
		  self.trayIcon.activated.connect(self.__icon_activated)
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
		QtGui.QMessageBox.about (self, "About %s" % CLNXConfig.APPNAME,
		"<center><big><b>%s %s</b></big><br />%s<br />(C) %s %s<br /><a href=\"%s\">%s Homepage</a></center>" \
		%(CLNXConfig.APPNAME, \
		CLNXConfig.APPVERSION, \
		CLNXConfig.DESCRIPTION, \
		CLNXConfig.AUTHOR, \
		CLNXConfig.YEAR, \
		CLNXConfig.PAGE, \
		CLNXConfig.APPNAME))

# house of moment == sun is in == #number of that hour in day or night
# so basically

	def update(self):
		self.now = datetime.now().replace(tzinfo=tz.gettz())
		if self.now > self.next_sunrise:
			self.update_hours()
			self.update_moon_cycle()
		self.phour = self.hoursToday.grab_nearest_hour(self.now)
		self.check_alarm()
		if CLNXConfig.show_house_of_moment:
			hom=int(get_house(0, CLNXConfig.observer, self.now)[0])
			if hom == 1:
				suffix="st"
			elif hom == 2:
				suffix="nd"
			elif hom == 3:
				suffix="rd"
			else:
				suffix="th"
			house_of_moment_string="<br />The sun is in the %s<sup>%s</sup> house" %(hom,suffix)
		else:
			house_of_moment_string=""
		if CLNXConfig.show_sign:
			sign_string="<br />The sign of the month is %s" %(get_sun_sign(self.now, CLNXConfig.observer))
		else:
			sign_string=""
		if CLNXConfig.show_moon:
			phase=grab_phase(self.now)
			moon_phase="<br />%s: %s illuminated" %(state_to_string(phase, swisseph.MOON), phase[2])
		else:
			moon_phase=""

		#probably get boolean of day/night out of model?
		planets_string = "Day of %s, the hour of %s" %(self.pday, self.phour)

		total_string="%s%s%s%s" %(planets_string, sign_string, moon_phase, house_of_moment_string)

		if CLNXConfig.current_theme == "None":
			sysicon=QtGui.QIcon(CLNXConfig.grab_icon_path("DarkGlyphs","misc","chronoslnx"))
		else:
			sysicon=CLNXConfig.main_icons[str(self.phour)]
		self.trayIcon.setToolTip("%s - %s\n%s" %(self.now.strftime("%Y/%m/%d"), self.now.strftime("%H:%M:%S"),
			total_string.replace("<br />","\n").replace("<sup>","").replace("</sup>","")))
		self.trayIcon.setIcon(sysicon)
		self.todayPicture.setPixmap(CLNXConfig.main_pixmaps[str(self.phour)])
		self.todayOther.setText("%s<br />%s" %(self.now.strftime("%H:%M:%S"), total_string))

	def event_trigger(self, event_type, text, planet_trigger):
		if event_type == "Save to file":
			print_to_file(self, text, self.now)
		elif event_type == "Command":
			callcall([split(text)])
		else: #event_type == "Textual reminder"
			self.show_notification("Reminder", text, planet_trigger)


	def parse_phour_args(string):
		alist=None
		args=len(findall("%\(prev\)s|%\(next\)s", string))
		if args == 2:
			if self.hoursToday.last_index > 0:
				idx=self.hoursToday.last_index - 1
			else:
				idx=self.hoursToday.last_index + 6
			prev_hour=self.hoursToday.get_planet(idx)
			alist={'prev': prev_hour, "next": self.phour}
		elif args == 1:
			if match("%\(prev\)s"):
				if self.hoursToday.last_index > 0:
					idx=self.hoursToday.last_index - 1
				else:
					idx=self.hoursToday.last_index + 6
				prev_hour=self.hoursToday.get_planet(idx)
				alist={"prev": prev_hour}
			else:
				alist={"next": self.phour}
		return alist,args

	def parse_hour_args(string):
		alist=None
		args=len(findall("%\(prev\)s|%\(next\)s", string))
		if args == 2:
			if self.now.hour == 0:
				prev_hour = 23
			else:
				prev_hour = self.now.hour - 1
			alist={'prev': prev_hour, "next": self.now.hour}
		elif args == 1:
			if match("%\(prev\)s"):
				if self.now.hour == 0:
					prev_hour = 23
				else:
					prev_hour = self.now.hour - 1
				alist={"prev": prev_hour}
			else:
				alist={"next": self.now.hour}
		return alist,args

	def check_alarm(self):
		for i in xrange(CLNXConfig.todays_schedule.rowCount()):
			hour_trigger=False
			pt=False
			real_row = CLNXConfig.todays_schedule.mapToSource(CLNXConfig.todays_schedule.index(i,0)).row()

			enabled_item=CLNXConfig.schedule.item(real_row,0)
			if enabled_item.checkState() == QtCore.Qt.Checked:
				hour_item=CLNXConfig.schedule.item(real_row,2).data(QtCore.Qt.UserRole).toPyObject()
				txt=str(CLNXConfig.schedule.item(real_row, 4).data(QtCore.Qt.EditRole).toPyObject())
				args=0
				if isinstance(hour_item,QtCore.QTime):
					hour_trigger = compare_to_the_second(self.now ,hour_item.hour(), \
								hour_item.minute(), 0)
				else:
					if hour_item == "Every planetary hour":
						dt = self.hoursToday.get_date(self.hoursToday.last_index)
						hour_trigger=compare_to_the_second(self.now, dt.hour, dt.minute, dt.second+1)
						if hour_trigger:
							pt=True
							alist,args=parse_phour_args(txt)
					elif self.phour == str(hour_item):
						dt = self.hoursToday.get_date(self.hoursToday.last_index)
						hour_trigger=compare_to_the_second(self.now, dt.hour, dt.minute, dt.second+1)
						pt=True
					elif hour_item == "When the sun rises":
						hour_trigger=compare_to_the_second(self.now, self.sunrise, \
								self.sunrise.minute, self.sunrise.second)
					elif hour_item == "When the sun sets":
						hour_trigger=compare_to_the_second(self.now, self.sunset.hour, \
								self.sunset.minute, self.minute.second)
					elif hour_item == "Every normal hour":
						hour_trigger=compare_to_the_second(self.now, self.now.hour,0,0)
						alist,args=parse_hour_args(txt)

				if hour_trigger:
					event_type_item=str(CLNXConfig.schedule.item(real_row, \
					3).data(QtCore.Qt.EditRole).toPyObject())
					if args > 0:
						self.event_trigger(event_type_item,txt % alist,pt)
					else:
						self.event_trigger(event_type_item,txt,pt)

app = QtGui.QApplication(sys.argv)
CLNXConfig = chronosconfig.ChronosLNXConfig()
try:
	import pynotify
	pynotify.init(CLNXConfig.APPNAME)
except ImportError:
	print "Warning, couldn't import pynotify! On Linux systems, the notifications might look ugly."
	pynf=False
chronoslnx = ChronosLNX()
chronoslnx.show()
sys.exit(app.exec_())
