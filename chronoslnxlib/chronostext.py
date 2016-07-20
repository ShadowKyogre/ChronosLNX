#!/usr/bin/python
from .core.charts import update_planets_and_cusps, get_signs
from .core.hours import AstrologicalDay
from .core.moon_phases import get_moon_cycle
from .eventplanner import DayEventsModel
from PyQt4 import QtGui ,QtCore
from datetime import timedelta
import swisseph

def prepare_planetary_info(date, observer):
    phinfo = AstrologicalDay(obvserver, date=date).hours_for_day()
    sphinfo = []
    header = "Planetary hours for {0}, {1}, {2} - {3}"\
             .format(observer.lat, observer.lng,
                     observer.elevation, date.strftime("%m/%d/%Y"))
    for hour in phinfo:
        data = hour[0].strftime("%m/%d/%Y - %H:%M:%S")
        if hour[2] is True:
            sphinfo.append(' - '.join([data, hour[1], "Day"]))
        else:
            sphinfo.append(' - '.join([data, hour[1], "Night"]))
    return "{0}\n{1}".format(header, "\n".join(sphinfo))

def prepare_sign_info(date, observer, nodes, admi):
    houses, signs = get_signs(date, observer, nodes, admi)
    sinfo = []
    header = "Sign info for {0}\n".format(date.strftime("%m/%d/%Y"))
    for hour in range(0, 24):
        sinfo.append("Info at {0}:00".format(hour))
        for i in signs:
            sinfo.append("{0} - {1} - {2} - {3} - {4}".format(i.name, i.m.signData['name'], 
                                                    i.m.only_degs(), i.retrograde, 
                                                    i.m.house_info.num)
                        )
        sinfo.append("\nHouses overview:")
        for i in houses:
            sinfo.append("{0} - {1} - {2} - {3} - {4} - {5}".format("House {0}".format(i.num),
                                                         i.natRulerData['name'],
                                                         i.cusp.signData['name'],
                                                         i.cusp.only_degs(),
                                                         i.end.signData['name'],
                                                         i.end.only_degs())
                        )
        date = date+timedelta(hours=1)
        update_planets_and_cusps(date, observer, houses, signs)
            #sinfo.append("\n")
    return "{0}{1}".format(header, "\n".join(sinfo))

def prepare_events(date, source):
    model = DayEventsModel()
    model.setSourceModel(source)
    model.setDate(date)
    rows = model.rowCount()
    sevents = []
    for j in range(rows):
        idx = model.index(j, 0, QtCore.QModelIndex())
        i = model.mapToSource(idx).row()
        if source.item(i, 0).checkState()==QtCore.Qt.Checked:
            first_column = "True"
        else:
            first_column = "False"
        second_column = source.item(i, 1).data(QtCore.Qt.UserRole) #need format like this: %m/%d/%Y

        if isinstance(second_column, QtCore.QDate):
            #print second_column
            second_column = second_column.toString("MM/dd/yyyy")
        else:
            second_column = source.item(i, 1).data(QtCore.Qt.EditRole)
        third_column = source.item(i, 2).data(QtCore.Qt.UserRole) #need format like this: %H:%M

        if isinstance(third_column, QtCore.QTime):
            third_column = third_column.toString("HH:mm")
        else:
            third_column = source.item(i, 2).data(QtCore.Qt.EditRole)
        fourth_column = source.item(i, 3).data(QtCore.Qt.EditRole)
        fifth_column = source.item(i, 4).data(QtCore.Qt.EditRole)
        sevents.append(','.join([first_column, second_column, third_column, 
                                 fourth_column, fifth_column])
                      )
    return "Events for {0}\n{1}".format(date.strftime("%m/%d/%Y"), "\n".join(sevents))

#http://love-python.blogspot.com/2008/02/read-csv-file-in-python.html

def prepare_moon_cycle(date):
    mooncycle = get_moon_cycle(date)
    smooncycle = []
    for phase in mooncycle:
        data = phase[0].strftime("%m/%d/%Y - %H:%M:%S")
        smooncycle.append(' - '.join([data, phase[1], phase[2]]))
    return "Moon phases for {0}\n{1}".format(date.strftime("%m/%d/%Y"), "\n".join(smooncycle))


def prepare_all(date, observer, source, nodes, admi):
    return "All data for {0}\n{1}\n\n{2}\n\n{3}\n\n{4}".format(date.strftime("%m/%d/%Y"),
                                                      prepare_planetary_info(date, observer),
                                                      prepare_moon_cycle(date),
                                                      prepare_sign_info(date, observer, nodes, admi),
                                                      prepare_events(date, source))
