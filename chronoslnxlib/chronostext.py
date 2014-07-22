#!/usr/bin/python
from .astro_rewrite import *
from .eventplanner import DayEventsModel
from PyQt4 import QtGui,QtCore
from datetime import timedelta
import swisseph

def prepare_planetary_info(date,observer):
	phinfo=hours_for_day(date,observer)
	sphinfo=[]
	header="Planetary hours for %s, %s, %s - %s" %(observer.lat,observer.lng,observer.elevation,date.strftime("%m/%d/%Y"))
	for hour in phinfo:
		data=hour[0].strftime("%m/%d/%Y - %H:%M:%S")
		if hour[2] is True:
			sphinfo.append(' - '.join([data, hour[1], "Day"]))
		else:
			sphinfo.append(' - '.join([data, hour[1], "Night"]))
	return "%s\n%s" %(header, "\n".join(sphinfo))

def prepare_sign_info(date,observer,nodes,admi):
	houses,signs=get_signs(date,observer,nodes,admi)
	sinfo=[]
	header="Sign info for %s\n" % date.strftime("%m/%d/%Y")
	for hour in range(0,24):
		sinfo.append("Info at %s:00" %(hour))
		for i in signs:
			sinfo.append("%s - %s - %s - %s - %s" %(
			i.name, i.m.signData['name'], i.m.only_degs(), \
			i.retrograde, i.m.house_info.num))
		sinfo.append("\nHouses overview:")
		for i in houses:
			sinfo.append("%s - %s - %s - %s - %s - %s" %(
				"House %s" %(i.num), i.natRulerData['name'], \
				i.cusp.signData['name'], i.cusp.only_degs(), \
				i.end.signData['name'], i.end.only_degs()))
		date=date+timedelta(hours=1)
		updatePandC(date, observer, houses, signs)
			#sinfo.append("\n")
	return header+"\n".join(sinfo)

def prepare_events(date, source):
	model=DayEventsModel()
	model.setSourceModel(source)
	model.setDate(date)
	rows = model.rowCount()
	sevents=[]
	for j in range(rows):
		idx=model.index(j,0,QtCore.QModelIndex())
		i=model.mapToSource(idx).row()
		if source.item(i,0).checkState()==QtCore.Qt.Checked:
			first_column="True"
		else:
			first_column="False"
		second_column=source.item(i,1).data(QtCore.Qt.UserRole) #need format like this: %m/%d/%Y

		if isinstance(second_column,QtCore.QDate):
			#print second_column
			second_column=second_column.toString("MM/dd/yyyy")
		else:
			second_column=source.item(i,1).data(QtCore.Qt.EditRole)
		third_column=source.item(i,2).data(QtCore.Qt.UserRole) #need format like this: %H:%M

		if isinstance(third_column,QtCore.QTime):
			third_column=third_column.toString("HH:mm")
		else:
			third_column=source.item(i,2).data(QtCore.Qt.EditRole)
		fourth_column=source.item(i,3).data(QtCore.Qt.EditRole)
		fifth_column=source.item(i,4).data(QtCore.Qt.EditRole)
		sevents.append(','.join([first_column,second_column,third_column,fourth_column,fifth_column]))
	return "Events for %s\n%s"%(date.strftime("%m/%d/%Y"),"\n".join(sevents))

#http://love-python.blogspot.com/2008/02/read-csv-file-in-python.html

def prepare_moon_cycle(date):
	mooncycle=get_moon_cycle(date)
	smooncycle=[]
	for phase in mooncycle:
	      data=phase[0].strftime("%m/%d/%Y - %H:%M:%S")
	      smooncycle.append(' - '.join([data, phase[1], phase[2]]))
	return "Moon phases for %s\n%s"%(date.strftime("%m/%d/%Y"),"\n".join(smooncycle))


def prepare_all(date,observer,source,nodes,admi):
	return "All data for %s\n%s\n\n%s\n\n%s\n\n%s" %(date.strftime("%m/%d/%Y"), \
	prepare_planetary_info(date,observer), \
	prepare_moon_cycle(date), \
	prepare_sign_info(date,observer,nodes,admi), \
	prepare_events(date, source))
