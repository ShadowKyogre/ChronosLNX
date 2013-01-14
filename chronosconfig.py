#!/usr/bin/python
from PyQt4 import QtGui,QtCore
import os, csv
from ast import literal_eval
from eventplanner import *
import datetime
from collections import OrderedDict as od

from astro_rewrite import *
from aspects import DEFAULT_ORBS
from dateutil import tz
import zonetab
#from dateutil.parser import *

class ChronosLNXConfig:

	APPNAME="ChronosLNX"
	APPVERSION="0.9.5"
	AUTHOR="ShadowKyogre"
	DESCRIPTION="A simple tool for checking planetary hours and moon phases."
	YEAR="2012"
	PAGE="http://shadowkyogre.github.com/ChronosLNX/"

	def __init__(self):
		self.settings=QtCore.QSettings(QtCore.QSettings.IniFormat,
						QtCore.QSettings.UserScope,
						ChronosLNXConfig.AUTHOR,
						ChronosLNXConfig.APPNAME)

		self.userconfdir=str(QtGui.QDesktopServices.storageLocation\
		(QtGui.QDesktopServices.DataLocation)).replace("//","/")
		#QtCore.QDir.currentPath()

		app_theme_path=os.path.join(os.sys.path[0],"themes")
		config_theme_path=os.path.join(self.userconfdir,"themes")

		QtCore.QDir.setSearchPaths("skins", [config_theme_path,app_theme_path])
		self.sys_icotheme=QtGui.QIcon.themeName()
		self.reset_settings()
		self.load_schedule()

	def grab_icon_path(self,icon_type,looking):
		#icon type must be of following: planets, moonphase, signs, misc
		return "skin:%s/%s.png" %(icon_type,looking)

	def load_theme(self):
		QtCore.QDir.setSearchPaths("skin", ["skins:%s" %(self.current_theme)])

		css=QtCore.QFile("skin:ui.css")
		if css.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text) and self.use_css == True:
			self.stylesheet=str(css.readAll(),
					encoding=os.sys.getdefaultencoding())
			make_icon=lambda g, n: QtGui.QIcon(self.grab_icon_path(g,n))
		else:
			self.stylesheet=""
			make_icon=lambda g, n: QtGui.QIcon.fromTheme("{}_clnx".format(n),
									QtGui.QIcon(self.grab_icon_path(g,n)))

		if self.current_icon_override > "":
			QtGui.QIcon.setThemeName(self.current_icon_override)
		else:
			QtGui.QIcon.setThemeName(self.sys_icotheme)

		self.main_icons = {
			'Sun' : make_icon("planets","sun"),
			'Moon' : make_icon("planets","moon"),
			'Mercury' : make_icon("planets","mercury"),
			'Venus' : make_icon("planets","venus"),
			'Mars' : make_icon("planets","mars"),
			'Jupiter' : make_icon("planets","jupiter"),
			'Saturn' : make_icon("planets","saturn"),
			'Uranus' : make_icon("planets","uranus"),
			'Neptune' : make_icon("planets","neptune"),
			'Pluto' : make_icon("planets","pluto"),
			'Pluto 2' : make_icon("planets","pluto_2"),
			'North Node' : make_icon("planets","north_node"),
			'South Node' : make_icon("planets","south_node"),
			'logo' :  make_icon("misc","chronoslnx"),
			'daylight' : make_icon("misc","day"),
			'nightlight' : make_icon("misc","night"),
		}
		#only needed to update labels
		self.main_pixmaps = {
			'Sun' : self.main_icons['Sun'].pixmap(64,64),
			'Moon' : self.main_icons['Moon'].pixmap(64,64),
			'Mercury' : self.main_icons['Mercury'].pixmap(64,64),
			'Venus' : self.main_icons['Venus'].pixmap(64,64),
			'Mars' : self.main_icons['Mars'].pixmap(64,64),
			'Jupiter' : self.main_icons['Jupiter'].pixmap(64,64),
			'Saturn' : self.main_icons['Saturn'].pixmap(64,64),
		}
		self.moon_icons = {
			'New Moon' : make_icon("moonphase","new_moon"),
			'Waxing Crescent Moon' : make_icon("moonphase","waxing_crescent_moon"),
			'First Quarter Moon' : make_icon("moonphase","first_quarter_moon"),
			'Waxing Gibbous Moon' : make_icon("moonphase","waxing_gibbous_moon"),
			'Full Moon' : make_icon("moonphase","full_moon"),
			'Waning Gibbous Moon' : make_icon("moonphase","waning_gibbous_moon"),
			'Last Quarter Moon' : make_icon("moonphase","last_quarter_moon"),
			'Waning Crescent Moon' : make_icon("moonphase","waning_crescent_moon"),
			'Solar Return' : make_icon("misc","solar_return"),
			'Lunar Return' : make_icon("misc","lunar_return"),
		}
		self.sign_icons = {
			'Aries': make_icon("signs", 'aries'),
			'Taurus': make_icon("signs", 'taurus'),
			'Gemini': make_icon("signs", 'gemini'),
			'Cancer': make_icon("signs", 'cancer'),
			'Leo': make_icon("signs", 'leo'),
			'Virgo': make_icon("signs", 'virgo'),
			'Libra': make_icon("signs", 'libra'),
			'Scorpio': make_icon("signs", 'scorpio'),
			'Sagittarius': make_icon("signs", 'sagittarius'),
			'Capricorn': make_icon("signs", 'capricorn'),
			'Capricorn 2': make_icon("signs", 'capricorn_2'),
			'Capricorn 3': make_icon("signs", 'capricorn_3'),
			'Aquarius': make_icon("signs", 'aquarius'),
			'Pisces': make_icon("signs", 'pisces'),
			'Ascendant' :  make_icon("signs","ascendant"),
			'Descendant' :  make_icon("signs","descendant"),
			'IC' :  make_icon("signs","ic"),
			'MC' :  make_icon("signs","mc"),
		}

	#resets to what the values are on file if 'apply' was just clicked and user wants to undo
	def reset_settings(self):
		self.settings.beginGroup("Location")
		lat = float(self.settings.value("latitude", 0.0))
		lng = float(self.settings.value("longitude", 0.0))
		elevation = float(self.settings.value("elevation", 0.0))
		self.observer = Observer(lat, lng, elevation)
		self.settings.endGroup()

		self.settings.beginGroup("Birth")
		blat = float(self.settings.value("latitude", 0.0))
		blng = float(self.settings.value("longitude", 0.0))
		belevation = float(self.settings.value("elevation", 0.0))
		self.baby = Observer(blat, blng, belevation)
		bdate = self.settings.value("birthTime", None)
		if bdate is not None:
			bdate = datetime.strptime(bdate,'%Y-%m-%d %H:%M:%S')
		else:
			bdate = datetime(2000,1,1)
		self.baby.obvdate = bdate
		#add bday
		self.settings.endGroup()

		self.settings.beginGroup("Appearance")
		self.current_theme = self.settings.value("iconTheme", "DarkGlyphs")
		self.current_icon_override = self.settings.value("stIconTheme", "")
		self.pluto_alt = literal_eval(self.settings.value("alternatePluto", "False"))
		self.use_css = literal_eval(self.settings.value("useCSS", "False"))
		self.capricorn_alt = self.settings.value("alternateCapricorn", "Capricorn")
		self.load_theme()
		self.settings.endGroup()

		self.settings.beginGroup("Tweaks")
		self.show_sign = literal_eval(self.settings.value("showSign","True"))
		self.show_moon = literal_eval(self.settings.value("showMoonPhase","True"))
		self.show_house_of_moment = literal_eval(self.settings.value("showHouseOfMoment","True"))
		self.show_nodes = literal_eval(self.settings.value("showNodes", "True"))
		self.show_admi = literal_eval(self.settings.value("showADMI", "False"))
		self.show_mcal = literal_eval(self.settings.value("showMoonOnCal", "False"))
		self.show_sr = literal_eval(self.settings.value("showSolarReturnOnCal", "False"))
		self.show_lr = literal_eval(self.settings.value("showLunarReturnOnCal", "False"))
		self.settings.endGroup()

		self.settings.beginGroup("Calculations")
		self.settings.beginGroup("refinements")
		self.refinements = {}
		self.refinements['Solar Return'] = int(self.settings.value("solar",2))
		self.refinements['Lunar Return'] = int(self.settings.value("lunar",2))
		self.refinements['Moon Phase'] = int(self.settings.value("phase",2))
		self.settings.endGroup()
		self.settings.beginGroup("orbs")
		self.orbs=od()
		for i in DEFAULT_ORBS:
			self.orbs[i]=float(self.settings.value(i, DEFAULT_ORBS[i]))
		self.settings.endGroup()
		self.settings.endGroup()
		self.load_theme()
		self.load_natal_data()

	def load_natal_data(self):
		print("Loading natal data...")
		self.natal_data=get_signs(self.baby.obvdate,self.baby,\
					  self.show_nodes,\
					  self.show_admi,prefix="Natal")
		#keep a copy of natal information for transits
		self.natal_sun=self.natal_data[1][0].m.longitude
		#keep a formatted copy for solar returns
		self.natal_moon=self.natal_data[1][1].m.longitude

	def load_schedule(self):
		self.schedule=QtGui.QStandardItemModel()
		self.schedule.setColumnCount(5)
		self.schedule.setHorizontalHeaderLabels(["Enabled","Date","Time","Event Type","Options"])
		self.todays_schedule=DayEventsModel()
		self.todays_schedule.setSourceModel(self.schedule)
		path=os.path.join(self.userconfdir, 'schedule.csv')

		if not os.path.exists(path):
			if not os.path.exists(path.replace("schedule.csv","")):
				print("Making directory to store schedule")
				os.makedirs(self.userconfdir)
			from shutil import copyfile
			sch=os.path.join(os.sys.path[0],"schedule.csv")
			copyfile(sch, path)
		planner = csv.reader(open(path, "r"))
		next(planner)

		for entry in planner:
			if len(entry) == 0:
				continue
			first_column=QtGui.QStandardItem()
			second_column=QtGui.QStandardItem()
			third_column=QtGui.QStandardItem()
			fourth_column=QtGui.QStandardItem()
			fifth_column=QtGui.QStandardItem()
			first_column.setCheckable(True)
			if literal_eval(entry[0]):
				first_column.setCheckState(QtCore.Qt.Checked)
			first_column.setEditable(False)
			if QtCore.QDate.fromString(entry[1], "MM/dd/yyyy").isValid():
				#second_column.setData(QtCore.Qt.UserRole,dateutil.parser.parse(entry[1]))
				second_column.setData(QtCore.QDate.fromString(entry[1], "MM/dd/yyyy"),QtCore.Qt.UserRole)
			else:
				second_column.setData(entry[1],QtCore.Qt.UserRole)
			second_column.setText(entry[1])
			if QtCore.QTime.fromString(entry[2],"HH:mm").isValid():
				third_column.setData(QtCore.QTime.fromString(entry[2],"HH:mm"),QtCore.Qt.UserRole)
			else:
				third_column.setData(entry[2],QtCore.Qt.UserRole)
			third_column.setText(entry[2])
			fourth_column.setText(entry[3])
			fifth_column.setText(entry[4])
			self.schedule.appendRow([first_column,second_column,third_column,fourth_column,fifth_column])
		self.schedule.rowsInserted.connect(self.add_delete_update)
		self.schedule.rowsRemoved.connect(self.add_delete_update)
		self.schedule.itemChanged.connect(self.changed_update)

	def changed_update(self, item):
		self.save_schedule()

	def add_delete_update(self, index, start, end):
		self.save_schedule()

	def save_schedule(self):
		rows=self.schedule.rowCount()
		path=os.path.join(self.userconfdir, 'schedule.csv')
		temppath=''.join(self.userconfdir, 'schedule_modified.csv')
		f=open(temppath, "w")
		planner = csv.writer(f)
		planner.writerow(["Enabled","Date","Hour","Event Type","Text"])
		for i in range(rows):
			if self.schedule.item(i,0).checkState()==QtCore.Qt.Checked:
				first_column="True"
			else:
				first_column="False"
			second_column=self.schedule.item(i,1).data(QtCore.Qt.UserRole) #need format like this: %m/%d/%Y
			if isinstance(second_column,QtCore.QDate):
				#print second_column
				second_column=str(second_column.toString("MM/dd/yyyy"))
			else:
				second_column=str(self.schedule.item(i,1).data(QtCore.Qt.EditRole))
			third_column=self.schedule.item(i,2).data(QtCore.Qt.UserRole) #need format like this: %H:%M

			if isinstance(third_column,QtCore.QTime):
				third_column=str(third_column.toString("HH:mm"))
			else:
				third_column=str(self.schedule.item(i,2).data(QtCore.Qt.EditRole))
			fourth_column=str(self.schedule.item(i,3).data(QtCore.Qt.EditRole))
			fifth_column=str(self.schedule.item(i,4).data(QtCore.Qt.EditRole))
			planner.writerow([first_column,second_column,third_column,fourth_column,fifth_column])
		f.close()
		os.remove(path)
		os.renames(temppath, path)

	def get_available_themes(self):
		themes=set()
		ath=QtCore.QDir("skins:")
		for at in ath.entryList():
			themes.add(str(at))
		themes.remove(".")
		themes.remove("..")
		return tuple(themes)

	def save_settings(self):
		self.settings.beginGroup("Location")
		self.settings.setValue("latitude", self.observer.lat)
		self.settings.setValue("longitude", self.observer.lng)
		self.settings.setValue("elevation", self.observer.elevation)
		self.settings.endGroup()

		self.settings.beginGroup("Birth")
		self.settings.setValue("birthTime", self.baby.obvdate.strftime('%Y-%m-%d %H:%M:%S'))
		self.settings.setValue("latitude", self.baby.lat)
		self.settings.setValue("longitude", self.baby.lng)
		self.settings.setValue("elevation", self.baby.elevation)
		self.settings.endGroup()

		self.settings.beginGroup("Appearance")
		self.settings.setValue("iconTheme", self.current_theme)
		self.settings.setValue("stIconTheme", self.current_icon_override)
		self.settings.setValue("useCSS", str(self.use_css))
		self.settings.setValue("alternatePluto",str(self.pluto_alt))
		self.settings.setValue("alternateCapricorn",str(self.capricorn_alt))
		self.settings.endGroup()

		self.settings.beginGroup("Tweaks")
		self.settings.setValue("showSign", str(self.show_sign))
		self.settings.setValue("showMoonPhase",str(self.show_moon))
		self.settings.setValue("showHouseOfMoment",str(self.show_house_of_moment))
		self.settings.setValue("showNodes",str(self.show_nodes))
		self.settings.setValue("showADMI",str(self.show_admi))
		self.settings.setValue("showMoonOnCal",str(self.show_mcal))
		self.settings.setValue("showSolarReturnOnCal",str(self.show_lr))
		self.settings.setValue("showLunarReturnOnCal",str(self.show_sr))
		self.settings.endGroup()

		self.settings.beginGroup("Calculations")
		self.settings.beginGroup("refinements")
		self.settings.setValue("solar", self.refinements['Solar Return'])
		self.settings.setValue("lunar", self.refinements['Lunar Return'])
		self.settings.setValue("phase", self.refinements['Moon Phase'])
		self.settings.endGroup()
		self.settings.beginGroup("orbs")
		for i in self.orbs:
			self.settings.setValue(i, self.orbs[i])
		self.settings.endGroup()
		self.settings.endGroup()

		self.settings.sync()
