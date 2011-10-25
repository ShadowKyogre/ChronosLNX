#!/usr/bin/python
from astro import *
from eventplanner import DayEventsModel
from PyQt4 import QtGui,QtCore

def prepare_planetary_info(date,observer):
	phinfo=hours_for_day(date,observer)
	sphinfo=[]
	header="Planetary hours for %s, %s, %s - %s" %(observer.lat,observer.long,observer.elevation,date.strftime("%m/%d/%Y"))
	for hour in phinfo:
		data=hour[0].strftime("%m/%d/%Y - %H:%M:%S")
		if hour[2] is True:
			sphinfo.append(' - '.join([data, hour[1], "Day"]))
		else:
			sphinfo.append(' - '.join([data, hour[1], "Night"]))
	return header +"\n"+"\n".join(sphinfo)

def prepare_sign_info(date):
	info=get_ruling_constellations_for_date(date)
	sinfo=[]
	for phase in info:
	      sinfo.append(' - '.join([info[phase][1], phase]))
	return "Sign info for "+date.strftime("%m/%d/%Y")+"\n"+"\n".join(sinfo)

def prepare_events(date, source):
	model=DayEventsModel()
	model.setSourceModel(source)
	model.setDate(date)
	rows = model.rowCount()
	sevents=[]
	for j in xrange(rows):
		idx=model.index(j,0,QtCore.QModelIndex())
		i=model.mapToSource(idx).row()
		if source.item(i,0).checkState()==QtCore.Qt.Checked:
			first_column="True"
		else:
			first_column="False"
		second_column=source.item(i,1).data(QtCore.Qt.UserRole).toPyObject() #need format like this: %m/%d/%Y

		if isinstance(second_column,QtCore.QDate):
			#print second_column
			second_column=str(second_column.toString("MM/dd/yyyy"))
		else:
			second_column=str(source.item(i,1).data(QtCore.Qt.EditRole).toPyObject())
		third_column=source.item(i,2).data(QtCore.Qt.UserRole).toPyObject() #need format like this: %H:%M

		if isinstance(third_column,QtCore.QTime):
			third_column=str(third_column.toString("HH:mm"))
		else:
			third_column=str(source.item(i,2).data(QtCore.Qt.EditRole).toPyObject())
		fourth_column=str(source.item(i,3).data(QtCore.Qt.EditRole).toPyObject())
		fifth_column=str(source.item(i,4).data(QtCore.Qt.EditRole).toPyObject())
		sevents.append(','.join([first_column,second_column,third_column,fourth_column,fifth_column]))
	return "Events for "+date.strftime("%m/%d/%Y")+"\n"+"\n".join(sevents)

#http://love-python.blogspot.com/2008/02/read-csv-file-in-python.html

def prepare_moon_cycle(date):
	mooncycle=get_moon_cycle(date)
	smooncycle=[]
	for phase in mooncycle:
	      data=phase[0].strftime("%m/%d/%Y - %H:%M:%S")
	      smooncycle.append(' - '.join([data, phase[1], phase[2]]))
	return "Moon phases for "+date.strftime("%m/%d/%Y")+"\n"+"\n".join(smooncycle)


def prepare_all(date,observer):
	return "All data for %s\n" %(date.strftime("%m/%d/%Y"))+prepare_planetary_info(date,observer)+"\n"+prepare_moon_cycle(date)+"\n"+prepare_sign_info(date)