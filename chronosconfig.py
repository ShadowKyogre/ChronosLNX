#!/usr/bin/python
from PyQt4 import QtGui,QtCore
import os, csv
from ast import literal_eval
from eventplanner import *
import datetime
from astro_rewrite import *
#import dateutil
from dateutil import tz
import zonetab
#from dateutil.parser import *

class Observer:
	def __init__(self):
		self.lat=0
		self.long=0
		self.elevation=0

class ChronosLNXConfig:

 	def __init__(self):
 		self.APPNAME="ChronosLNX"
		self.APPVERSION="0.7.0"
		self.AUTHOR="ShadowKyogre"
		self.DESCRIPTION="A simple tool for checking planetary hours and moon phases."
		self.YEAR="2011"
		self.PAGE="http://shadowkyogre.github.com/ChronosLNX/"

		self.settings=QtCore.QSettings(QtCore.QSettings.IniFormat,
						QtCore.QSettings.UserScope,
						self.AUTHOR,
						self.APPNAME)

		if os.uname()[0] != 'Linux':
			self.zt=os.sys.path[0]+"/zone.tab" #use the local copy if this isn't a Linux
		else:
			self.zt="/usr/share/zoneinfo/zone.tab"

		self.observer=Observer()
		self.baby=Observer()
		self.reset_settings()

		self.load_schedule()


	def grab_icon_path(self,theme,icon_type,looking):
		#icon type must be of following: planetss, moonphase, signs
		return "%s/%s/%s/%s.png" %(os.sys.path[0],theme,icon_type,looking)

	def prepare_icons(self):
		self.main_icons = {
			'Sun' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"planets","sun")),
			'Moon' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"planets","moon")),
			'Mercury' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"planets","mercury")),
			'Venus' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"planets","venus")),
			'Mars' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"planets","mars")),
			'Jupiter' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"planets","jupiter")),
			'Saturn' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"planets","saturn")),
			'Uranus' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"planets","uranus")),
			'Neptune' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"planets","neptune")),
			'Pluto' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"planets","pluto")),
			'Pluto 2' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"planets","pluto_2")),
			'North Node' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"planets","north_node")),
			'South Node' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"planets","south_node")),
			'logo' :  QtGui.QIcon(self.grab_icon_path(self.current_theme,"misc","chronoslnx")),
			'daylight' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"misc","day")),
			'nightlight' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"misc","night")),
		}
		#only needed to update lables
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
			'New Moon' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"moonphase","new_moon")),
			'Waxing Crescent Moon' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"moonphase","waxing_crescent_moon")),
			'First Quarter Moon' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"moonphase","first_quarter_moon")),
			'Waxing Gibbous Moon' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"moonphase","waxing_gibbous_moon")),
			'Full Moon' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"moonphase","full_moon")),
			'Waning Gibbous Moon' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"moonphase","waning_gibbous_moon")),
			'Last Quarter Moon' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"moonphase","last_quarter_moon")),
			'Waning Crescent Moon' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"moonphase","waning_crescent_moon")),
			'Solar Return' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"misc","solar_return")),
			'Lunar Return' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"misc","lunar_return")),
		}
		self.sign_icons = {
			'Aries': QtGui.QIcon(self.grab_icon_path(self.current_theme, "signs", 'aries')),
			'Taurus': QtGui.QIcon(self.grab_icon_path(self.current_theme, "signs", 'taurus')),
			'Gemini': QtGui.QIcon(self.grab_icon_path(self.current_theme, "signs", 'gemini')),
			'Cancer': QtGui.QIcon(self.grab_icon_path(self.current_theme, "signs", 'cancer')),
			'Leo': QtGui.QIcon(self.grab_icon_path(self.current_theme, "signs", 'leo')),
			'Virgo': QtGui.QIcon(self.grab_icon_path(self.current_theme, "signs", 'virgo')),
			'Libra': QtGui.QIcon(self.grab_icon_path(self.current_theme, "signs", 'libra')),
			'Scorpio': QtGui.QIcon(self.grab_icon_path(self.current_theme, "signs", 'scorpio')),
			'Sagittarius': QtGui.QIcon(self.grab_icon_path(self.current_theme, "signs", 'sagittarius')),
			'Capricorn': QtGui.QIcon(self.grab_icon_path(self.current_theme, "signs", 'capricorn')),
			'Capricorn 2': QtGui.QIcon(self.grab_icon_path(self.current_theme, "signs", 'capricorn_2')),
			'Capricorn 3': QtGui.QIcon(self.grab_icon_path(self.current_theme, "signs", 'capricorn_3')),
			'Aquarius': QtGui.QIcon(self.grab_icon_path(self.current_theme, "signs", 'aquarius')),
			'Pisces': QtGui.QIcon(self.grab_icon_path(self.current_theme, "signs", 'pisces')),
			'Ascendant' :  QtGui.QIcon(self.grab_icon_path(self.current_theme,"signs","ascendant")),
			'Descendant' :  QtGui.QIcon(self.grab_icon_path(self.current_theme,"signs","descendant")),
			'IC' :  QtGui.QIcon(self.grab_icon_path(self.current_theme,"signs","ic")),
			'MC' :  QtGui.QIcon(self.grab_icon_path(self.current_theme,"signs","mc")),
		}

	def generate_timezone(self, birth=False):
		timezone=zonetab.nearest_tz(self.baby.lat, \
					    self.baby.long, \
					    zonetab.timezones(zonetab=self.zt))[2]
		print "Detected natal timezone to be %s" % timezone
		return tz.gettz(timezone)

	#resets to what the values are on file if 'apply' was just clicked and user wants to undo
	def reset_settings(self):
		self.settings.beginGroup("Location")
		self.observer.lat=float(self.settings.value("latitude", 0.0).toPyObject())
		self.observer.long=float(self.settings.value("longitude", 0.0).toPyObject())
		self.observer.elevation=float(self.settings.value("elevation", 0.0).toPyObject())
		self.settings.endGroup()

		self.settings.beginGroup("Birth")
		self.birthzone=self.settings.value("birthZone",QtCore.QVariant())
		self.baby.lat=float(self.settings.value("latitude", 0.0).toPyObject())
		self.baby.long=float(self.settings.value("longitude", 0.0).toPyObject())
		self.baby.elevation=float(self.settings.value("elevation", 0.0).toPyObject())
		tzo=self.generate_timezone()
		self.birthtime=self.settings.value("birthTime", \
			QtCore.QVariant(datetime(2000,1,1,tzinfo=tzo))).toPyObject()
		#add bday
		self.settings.endGroup()

		self.settings.beginGroup("Appearance")
		self.current_theme=str(self.settings.value("iconTheme", QtCore.QString("DarkGlyphs")).toPyObject())
		self.pluto_alt=literal_eval(str(self.settings.value("alternatePluto",
					QtCore.QString("False")).toPyObject()))
		self.capricorn_alt=str(self.settings.value("alternateCapricorn", \
				str(QtCore.QString("Capricorn"))).toPyObject())
		self.settings.endGroup()

		self.settings.beginGroup("Tweaks")
		self.show_sign=literal_eval(str(self.settings.value("showSign",\
			QtCore.QString("True")).toPyObject()))
		self.show_moon=literal_eval(str(self.settings.value("showMoonPhase",\
			QtCore.QString("True")).toPyObject()))
		self.show_house_of_moment=literal_eval(str(self.settings.value("showHouseOfMoment",\
			QtCore.QString("True")).toPyObject()))
		self.show_nodes=literal_eval(str(self.settings.value("showNodes",
					QtCore.QString("True")).toPyObject()))
		self.show_admi=literal_eval(str(self.settings.value("showADMI",
					QtCore.QString("False")).toPyObject()))
		self.show_mcal=literal_eval(str(self.settings.value("showMoonOnCal",
					QtCore.QString("False")).toPyObject()))
		self.show_sr=literal_eval(str(self.settings.value("showSolarReturnOnCal",
					QtCore.QString("False")).toPyObject()))
		self.show_lr=literal_eval(str(self.settings.value("showLunarReturnOnCal",
					QtCore.QString("False")).toPyObject()))
		self.settings.endGroup()

		self.prepare_icons()
		self.load_natal_data()

	def load_natal_data(self):
		print "Loading natal data..."
		self.natal_data=get_signs(self.birthtime,self.baby,\
					  self.show_nodes,\
					  self.show_admi,prefix="Natal")
		#keep a copy of natal information for transits
		self.natal_sun=self.natal_data[1][0].m.longitude
		#keep a formatted copy for solar returns
		self.natal_moon=self.natal_data[1][1].m.longitude

	def load_schedule(self):
		self.schedule=QtGui.QStandardItemModel()
		self.schedule.setColumnCount(5)
		self.schedule.setHorizontalHeaderLabels(["Enabled","Date","Hour","Event Type","Text"])
		self.todays_schedule=DayEventsModel()
		self.todays_schedule.setSourceModel(self.schedule)
		path=''.join([str(QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.DataLocation)),
			self.APPNAME,'/schedule.csv']).replace('//', '/')

		if not os.path.exists(path):
			if not os.path.exists(path.replace("schedule.csv","")):
				print "Making directory to store schedule"
				os.mkdir(path.replace("schedule.csv",""))
			from shutil import copyfile
			copyfile("%s/schedule.csv" %(os.sys.path[0]), path)
		planner = csv.reader(open(path, "rb"))
		planner.next()

		for entry in planner:
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
		path=''.join([str(QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.DataLocation)),
			self.APPNAME,
			'/schedule.csv'])
		temppath=''.join([str(QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.DataLocation)),
			self.APPNAME,
			'/schedule_modified.csv'])
		planner = csv.writer(open(temppath, "wb"))
		planner.writerow(["Enabled","Date","Hour","Event Type","Text"])
		for i in xrange(rows):
			if self.schedule.item(i,0).checkState()==QtCore.Qt.Checked:
				first_column="True"
			else:
				first_column="False"
			second_column=self.schedule.item(i,1).data(QtCore.Qt.UserRole).toPyObject() #need format like this: %m/%d/%Y

			if isinstance(second_column,QtCore.QDate):
				#print second_column
				second_column=str(second_column.toString("MM/dd/yyyy"))
			else:
				second_column=str(self.schedule.item(i,1).data(QtCore.Qt.EditRole).toPyObject())
			third_column=self.schedule.item(i,2).data(QtCore.Qt.UserRole).toPyObject() #need format like this: %H:%M

			if isinstance(third_column,QtCore.QTime):
				third_column=str(third_column.toString("HH:mm"))
			else:
				third_column=str(self.schedule.item(i,2).data(QtCore.Qt.EditRole).toPyObject())
			fourth_column=str(self.schedule.item(i,3).data(QtCore.Qt.EditRole).toPyObject())
			fifth_column=str(self.schedule.item(i,4).data(QtCore.Qt.EditRole).toPyObject())
			planner.writerow([first_column,second_column,third_column,fourth_column,fifth_column])
		os.remove(path)
		os.renames(temppath, path)

	def get_available_themes(self):
		themes=[]
		for checking in os.listdir(os.sys.path[0]):
			path="%s/%s" %(os.sys.path[0], checking)
			if os.path.isdir(path) is True and \
				os.path.exists(path+"/signs") and \
				os.path.exists(path+"/planets") and \
				os.path.exists(path+"/moonphase") and \
				os.path.exists(path+"/misc"):
				themes.append(checking)
		return themes

	def save_settings(self):
		self.settings.beginGroup("Location")
		self.settings.setValue("latitude", self.observer.lat)
		self.settings.setValue("longitude", self.observer.long)
		self.settings.setValue("elevation", self.observer.elevation)
		self.settings.endGroup()

		self.settings.beginGroup("Birth")
		self.settings.setValue("birthTime", self.birthtime)
		self.settings.setValue("latitude", self.baby.lat)
		self.settings.setValue("longitude", self.baby.long)
		self.settings.setValue("elevation", self.baby.elevation)
		self.settings.endGroup()

		self.settings.beginGroup("Appearance")
		self.settings.setValue("iconTheme", self.current_theme)
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

		self.settings.sync()
