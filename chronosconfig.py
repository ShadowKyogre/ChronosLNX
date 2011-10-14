#!/usr/bin/python
from PyQt4 import QtGui,QtCore
import os, csv, ast
from eventplanner import *
from datetimetz import *
import datetime
#import dateutil
#from dateutil.tz import *
#from dateutil.parser import *

class ChronosLNXConfig:

 	def __init__(self):
 		self.APPNAME="ChronosLNX"
		self.APPVERSION="0.2.0"
		self.AUTHOR="ShadowKyogre"
		self.settings=QtCore.QSettings(QtCore.QSettings.IniFormat,
						QtCore.QSettings.UserScope,
						self.AUTHOR,
						self.APPNAME)
		#self.settings=QtCore.QSettings(self.AUTHOR,self.APPNAME)
		
		self.settings.beginGroup("Location")
		self.current_latitude=float(self.settings.value("latitude", 0.0).toPyObject())
		self.current_longitude=float(self.settings.value("longitude", 0.0).toPyObject())
		self.current_elevation=float(self.settings.value("elevation", 0.0).toPyObject())
		self.settings.endGroup()
		
		self.settings.beginGroup("Appearance")
		self.current_theme=str(self.settings.value("icontheme", 
					QtCore.QString("DarkGlyphs")).toPyObject())
		self.settings.endGroup()
		
		self.prepare_icons()
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
			'logo' :  QtGui.QIcon(self.grab_icon_path(self.current_theme,"misc","chronoslnx")),
			'daylight' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"misc","day")),
			'nightlight' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"misc","night")),
		}
		#only needed to update lables
		self.main_pixmaps = {
			'Sun' : self.main_icons['Sun'].pixmap(64,64),
			'Moon' : self.main_icons['Moon'].pixmap(64,64),
			'Mercury' : self.main_icons['Sun'].pixmap(64,64),
			'Venus' : self.main_icons['Venus'].pixmap(64,64),
			'Mars' : self.main_icons['Mars'].pixmap(64,64),
			'Jupiter' : self.main_icons['Jupiter'].pixmap(64,64),
			'Saturn' : self.main_icons['Saturn'].pixmap(64,64),
		}
		self.moon_icons = {
			'New moon' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"moonphase","new_moon")),
			'Waxing crescent moon' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"moonphase","waxing_crescent_moon")),
			'First quarter moon' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"moonphase","first_quarter_moon")),
			'Waxing gibbous moon' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"moonphase","waxing_gibbous_moon")),
			'Full moon' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"moonphase","full_moon")),
			'Waning gibbous moon' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"moonphase","waning_gibbous_moon")),
			'Last quarter moon' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"moonphase","last_quarter_moon")),
			'Waning crescent moon' : QtGui.QIcon(self.grab_icon_path(self.current_theme,"moonphase","waning_crescent_moon")),
		}
		#self.sign_icons = {}

	#resets to what the values are on file if 'apply' was just clicked and user wants to undo
	def reset_settings(self):
		self.settings.beginGroup("Location")
		self.current_latitude=float(self.settings.value("latitude", 0.0).toPyObject())
		self.current_longitude=float(self.settings.value("longitude", 0.0).toPyObject())
		self.current_elevation=float(self.settings.value("elevation", 0.0).toPyObject())
		self.settings.endGroup()
		self.settings.beginGroup("Appearance")
		self.current_theme=str(self.settings.value("icontheme", QtCore.QString("DarkGlyphs")).toPyObject())
		self.settings.endGroup()

	def load_schedule(self):
		self.schedule=QtGui.QStandardItemModel()
		self.schedule.setColumnCount(5)
		self.schedule.setHorizontalHeaderLabels(["Enabled","Date","Hour","Event Type","Text"])
		self.todays_schedule=DayEventsModel()
		self.todays_schedule.setSourceModel(self.schedule)
		path=''.join([str(QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.DataLocation)),
			self.APPNAME,
			'/schedule.csv'])
		firsttime=False
		#need more elegant first time
		try:
			planner = csv.reader(open(path, "rb"))
		except IOError:
			f=open(path,"w")
			f.write("")
			f.close()
			firsttime=True
			planner = csv.reader(open(path, "rb"))
		if not firsttime:
			planner.next()
			for entry in planner:
				first_column=QtGui.QStandardItem()
				second_column=QtGui.QStandardItem()
				third_column=QtGui.QStandardItem()
				fourth_column=QtGui.QStandardItem()
				fifth_column=QtGui.QStandardItem()
				first_column.setCheckable(True)
				if ast.literal_eval(entry[0]):
					first_column.setCheckState(QtCore.Qt.Checked)
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
			if os.path.isdir(path) is True:
				themes.append(checking)
		return themes

	def save_settings(self):
		self.settings.beginGroup("Location")
		self.settings.setValue("latitude", self.current_latitude)
		self.settings.setValue("longitude", self.current_longitude)
		self.settings.setValue("elevation", self.current_elevation)
		self.settings.endGroup()

		self.settings.beginGroup("Appearance")
		self.settings.setValue("icontheme", self.current_theme)
		self.settings.endGroup()
		self.settings.sync()
