#http://www.kimgentes.com/worshiptech-web-tools-page/2008/10/14/regex-pattern-for-parsing-csv-files-with-embedded-commas-dou.html
#http://doc.qt.nokia.com/qq/qq26-pyqtdesigner.html#creatingacustomwidget
from PyQt5 import QtGui, QtWidgets, QtCore
#import re
from dateutil import tz
from datetime import datetime

from .core.charts import get_signs, update_planets_and_cusps
from .core.aspects import create_aspect_table, search_special_aspects
from .core.hours import AstrologicalDay
from .core.moon_phases import get_moon_cycle

from .core.aspects import DEFAULT_ORBS

# aspect pattern class types
from .core.aspects import GrandCross, GrandTrine, TSquare, Stellium, Yod

#http://doc.qt.nokia.com/latest/qt.html#ItemDataRole-enum
##http://doc.qt.nokia.com/latest/widgets-analogclock.html
#http://stackoverflow.com/questions/2526815/moon-lunar-phase-algorithm

# Special Models for planetary and moon phase stuff

#http://doc.qt.nokia.com/stable/qhelpcontentwidget.html
#http://www.riverbankcomputing.com/static/Docs/PyQt4/html/qthelp.html
#http://ubuntuforums.org/showthread.php?t=1110989
#http://www.commandprompt.com/community/pyqt/x6082
class BookMarkedModel(QtGui.QStandardItemModel):
    def __init__(self, rows=0, columns=0, parent=None):
        super().__init__(rows, columns, parent)
        color = QtGui.QPalette().color(QtGui.QPalette.Midlight)
        color.setAlpha(64)
        self.color = QtGui.QBrush(color)
        c2 = QtGui.QPalette().color(QtGui.QPalette.Base)
        c2.setAlpha(0)
        self.base = QtGui.QBrush(c2)
        self.last_index = 0

    def clear(self):
        self.removeRows(0, self.rowCount())
        self.last_index = 0

    def _highlight_row(self, idx):
        for i in range(self.columnCount()):
            self.item(idx, i).setBackground(self.color)

    def _unhighlight_row(self, idx):
        for i in range(self.columnCount()):
            self.item(idx, i).setBackground(self.base)

class PHModel(BookMarkedModel):
    def __init__(self, parent=None):
        super().__init__(parent=parent, columns=2)
        self.setHorizontalHeaderLabels(["Time", "Planet"])

    def grab_nearest_hour(self, date):
        for i in range(self.last_index, 24):
            if i+1 > 23:
                looking_behind = self.get_date(i)
                if looking_behind <= date:
                    self._highlight_row(i)
                    self._unhighlight_row(i-1)
                    self.last_index = i
                    return self.get_planet(i)
            else:
                looking_behind = self.get_date(i)
                looking_ahead = self.get_date(i+1)
                if looking_behind <= date < looking_ahead:
                    self._highlight_row(i)
                    if i != 0:
                        self._unhighlight_row(i-1)
                    self.last_index = i
                    return self.get_planet(i)
        return "-Error-"

    def get_planet(self, idx):
        return self.item(idx, 1).data(0)

    def get_date(self, idx):
        return self.item(idx, 0).data(32)

    @classmethod
    def prepareHours(cls, icon_source, date=None, observer=None, astro_day=None):
        if astro_day is None:
            if observer is None:
                raise ValueError("If no astro day specified, observer must not be None!")
            astro_day = AstrologicalDay.day_for_ref_point(observer, dt=date)
        planetary_hours = astro_day.planetary_hours()
        model = cls()
        for ph in planetary_hours:
            icon = icon_source[ph[1]]
            if ph[2] is True:
                status_icon = icon_source['daylight']
            else:
                status_icon = icon_source['nightlight']
            newhouritem = QtGui.QStandardItem(status_icon, ph[0].strftime("%H:%M:%S - %m/%d/%Y"))
            newhouritem.setData(ph[0], 32)
            newplanetitem = QtGui.QStandardItem(icon, ph[1])
            model.appendRow([newhouritem, newplanetitem])
        return model

class MPModel(BookMarkedModel):
    def __init__(self, parent=None):
        super().__init__(columns=3, parent=parent)
        self.setHorizontalHeaderLabels(["Time", "Phase", "Illumination"])

    def highlight_cycle_phase(self, date):
        rowCount = self.rowCount()
        for i in range(self.last_index, rowCount):
            self._unhighlight_row(i)
            if i <= rowCount-2:
                cycling = self.get_date(i)
                cycling2 = self.get_date(i+1)
                if cycling.timetuple().tm_yday <= date.timetuple().tm_yday < cycling2.timetuple().tm_yday:
                    self._highlight_row(i)
                    self.last_index = i
                    break
            else:
                cycling = self.get_date(i)
                if cycling.timetuple().tm_yday == date.timetuple().tm_yday:
                    self._highlight_row(i)
                    self.last_index = i
                    break

    def get_date(self, idx):
        return self.item(idx, 0).data(32)

    @classmethod
    def getMoonCycle(cls, date, icon_source, observer):
        moon_cycle = get_moon_cycle(date)
        model = cls()
        for mc in moon_cycle:
            dt = mc[0].astimezone(observer.timezone)
            mptitem = QtGui.QStandardItem(icon_source[mc[1]], dt.strftime("%H:%M:%S - %m/%d/%Y"))
            mppitem = QtGui.QStandardItem(mc[1])
            mplitem = QtGui.QStandardItem(mc[2])

            mptitem.setData(dt, 32)
            mppitem.setText(mc[1])
            mplitem.setText(mc[2])
            model.appendRow([mptitem, mppitem, mplitem])
        return model

### Planetary Hours and Moon Phase Widgets
'''
self.moonToday.icons=clnxcfg.moon_icons
self.moonToday.refinement=clnxcfg.refinements['Moon Phase']
    def update_moon_cycle(self):
        if previous_new_moon(self.now).timetuple().tm_yday == self.now.timetuple().tm_yday:
            self.moonToday.clear()
            self.moonToday.get_moon_cycle(self.now)
        self.moonToday.highlight_cycle_phase(self.now)
#updatey
    if self.now >= self.next_sunrise:
        self.update_moon_cycle()
'''
class MoonCycleList(QtWidgets.QTreeView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setRootIsDecorated(False)
        self.setModel(MPModel())

    def clear(self):
        self.model().clear()

    def highlight_cycle_phase(self, date):
        self.model().highlight_cycle_phase(date)

    def get_moon_cycle(self, date, observer):
        self.setModel(MPModel.getMoonCycle(date, self.icons, observer))

class PlanetaryHoursList(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        hbox = QtWidgets.QVBoxLayout(self)
        self.tree = QtWidgets.QTreeView(self)
        self.tree.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tree.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tree.setRootIsDecorated(False)

        inputstuff = QtWidgets.QGridLayout()
        inputstuff.addWidget(QtWidgets.QLabel("Hour type to filter"), 0, 0)
        self.filter_hour = QtWidgets.QComboBox(self)
        self.filter_hour.addItem("All")
        self.filter_hour.addItem("Sun")
        self.filter_hour.addItem("Moon")
        self.filter_hour.addItem("Mars")
        self.filter_hour.addItem("Mercury")
        self.filter_hour.addItem("Jupiter")
        self.filter_hour.addItem("Venus")
        self.filter_hour.addItem("Saturn")
        self.filter_hour.setCurrentIndex(0)
        inputstuff.addWidget(self.filter_hour, 0, 1)
        hbox.addLayout(inputstuff)
        hbox.addWidget(self.tree)
        model = PHModel()
        filter_model = QtCore.QSortFilterProxyModel()
        filter_model.setSourceModel(model)
        filter_model.setFilterKeyColumn(1)
        self.tree.setModel(filter_model)
        self.filter_hour.activated.connect(self.filter_hours)
        self.filter_hour.setToolTip("Select the hour type you want to show.")

    def clear(self):
        self.tree.model().sourceModel().clear()

    def prepareHours(self, date=None, observer=None, astro_day=None):
        if astro_day is None:
            if observer is None:
                raise ValueError("If no astro day specified, observer must not be None!")
            astro_day = AstrologicalDay.day_for_ref_point(observer, dt=date)

        planetary_hours = astro_day.planetary_hours()
        ph_model = PHModel.prepareHours(self.icons, astro_day=astro_day)
        self.tree.model().setSourceModel(ph_model)

    def filter_hours(self, idx):
        if 0 == idx:
            self.tree.model().setFilterFixedString("")
        else:
            planet_name = self.filter_hour.itemText(idx)
            #set filter based on planet name
            self.tree.model().setFilterFixedString(planet_name)

    def grab_nearest_hour(self, date):
        return self.tree.model().sourceModel().grab_nearest_hour(date)

### Sign stuff

class AspectTableDisplay(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        vbox = QtWidgets.QVBoxLayout(self)
        self.tableAspects = QtGui.QStandardItemModel()
        self.tableSpecial = QtGui.QStandardItemModel()
        self.headers = []

        sa = ["Yod", "Grand Trine", "Grand Cross", "T-Square", "Stellium"]

        self.guiAspects = QtWidgets.QTableView(self)
        self.guiSpecial = QtWidgets.QTableView(self)
        vbox.addWidget(
            QtWidgets.QLabel(
                (
                    "General Aspects:"
                    "\nThe row indicates the planet being aspected."
                )
            )
        )
        vbox.addWidget(self.guiAspects)
        vbox.addWidget(QtWidgets.QLabel("Special Aspects"))
        vbox.addWidget(self.guiSpecial)

        self.guiAspects.setModel(self.tableAspects)
        self.guiAspects.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.guiSpecial.setModel(self.tableSpecial)
        self.guiSpecial.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.tableSpecial.setColumnCount(5)
        self.tableSpecial.setHorizontalHeaderLabels(sa)

    def refresh(self, zodiac, orbs):
        at = create_aspect_table(zodiac, orbs=orbs)
        sad = search_special_aspects(zodiac, orbs=orbs)
        self.buildTable(at, sad)

    def buildTable(self, at, sad, comparative=False):
        self.comparative = comparative
        self.updateHeaders()
        max_length, longest_element = max([(len(x), x) for x in sad.values()])
        self.tableSpecial.setRowCount(max_length)
        self.tableSpecial.removeRows(0, self.tableSpecial.rowCount())
        for i in at:
            if i.aspect == None:
                c = QtGui.QStandardItem("No aspect")
            else:
                c = QtGui.QStandardItem(i.aspect.title())
            c.setToolTip(str(i))
            c.setData(i, 32)
            self.tableAspects.setItem(self.headers.index(i.planet2.name), 
                                      self.headers.index(i.planet1.name), c)
        i = 0
        for yod in sad.get(Yod, []):
            c = QtGui.QStandardItem(str(yod))
            self.tableSpecial.setItem(i, 0, c)
            i += 1
        i = 0
        for gt in sad.get(GrandTrine, []):
            d = QtGui.QStandardItem(str(gt))
            self.tableSpecial.setItem(i, 1, d)
            i += 1
        i = 0
        for gc in sad.get(GrandCross, []):
            e = QtGui.QStandardItem(str(gc))
            self.tableSpecial.setItem(i, 2, e)
            i += 1
        i = 0
        for tsq in sad.get(TSquare, []):
            f = QtGui.QStandardItem(str(tsq))
            self.tableSpecial.setItem(i, 4, f)
            i += 1
        i = 0
        for stellium in sad.get(Stellium, []):
            g = QtGui.QStandardItem(str(stellium))
            self.tableSpecial.setItem(i, 3, g)
            i += 1
        self.guiAspects.resizeRowsToContents()
        self.guiAspects.resizeColumnsToContents()
        self.guiSpecial.resizeRowsToContents()
        self.guiSpecial.resizeColumnsToContents()

    def updateHeaders(self):
        self.headers = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter",
                        "Saturn", "Uranus", "Neptune", "Pluto"]
        if self.nodes:
            self.headers.append("North Node")
            self.headers.append("South Node")
        if self.admi:
            self.headers.append("Ascendant")
            self.headers.append("Descendant")
            self.headers.append("MC")
            self.headers.append("IC")
        length = len(self.headers)
        self.tableAspects.setColumnCount(length)
        self.tableAspects.setRowCount(length)
        for v, i in enumerate(self.headers):
            item = QtGui.QStandardItem(i)
            if self.pluto_alternate and i == "Pluto":
                item.setIcon(0, self.icons['Pluto 2'])
            elif i in {"Ascendant", "Descendant", "MC", "IC"}:
                item.setIcon(self.sign_icons[i])
            else:
                item.setIcon(self.icons[i])
            item2 = QtGui.QStandardItem(item)
            if self.comparative:
                item2.setText("Natal {0}".format(i))
            self.tableAspects.setHorizontalHeaderItem(v, item)
            self.tableAspects.setVerticalHeaderItem(v, item2)

def aspectsDialog(widget, zodiac, other_table,
        icons, sign_icons, pluto_alternate,
        admi, nodes, orbs):
    info_dialog = QtWidgets.QDialog(widget)
    info_dialog.setWindowTitle("Aspectarian")
    tabs = QtWidgets.QTabWidget(info_dialog)
    aspects = AspectTableDisplay(info_dialog)
    aspects.icons = icons
    aspects.sign_icons = sign_icons
    aspects.pluto_alternate = pluto_alternate
    aspects.admi = admi
    aspects.nodes = nodes
    vbox = QtWidgets.QVBoxLayout(info_dialog)
    tabs.addTab(aspects, "Aspects for this table")
    vbox.addWidget(tabs)
    if other_table:
        caspects = AspectTableDisplay(info_dialog)
        caspects.icons = icons
        caspects.sign_icons = sign_icons
        caspects.pluto_alternate = pluto_alternate
        caspects.admi = admi
        caspects.nodes = nodes
        at, compare = create_aspect_table(zodiac, compare=other_table, orbs=orbs)
        sado = search_special_aspects(zodiac)
        sad = search_special_aspects(zodiac+other_table)
        caspects.buildTable(compare, sad, comparative=True)
        aspects.buildTable(at, sado)
        tabs.addTab(caspects, "Aspects to Natal Chart")
    else:
        aspects.refresh(zodiac, orbs)
    info_dialog.show()

def housesDialog(widget, houses, capricorn_alternate, sign_icons):
    info_dialog = QtWidgets.QDialog(widget)
    info_dialog.setWindowTitle("Houses Overview")
    tree = QtWidgets.QTreeWidget(info_dialog)
    tree.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
    tree.setRootIsDecorated(False)
    tree.setHeaderLabels(["Number", "Natural Ruler", "Cusp Sign", "Degrees", "End Sign", "Degrees"])
    tree.setColumnCount(6)
    vbox = QtWidgets.QVBoxLayout(info_dialog)
    vbox.addWidget(tree)
    for i in houses:
        item = QtWidgets.QTreeWidgetItem()
        item.setText(0, str(i.num))
        item.setToolTip(0, str(i))
        if i.natRulerData.name == "Capricorn":
            item.setIcon(1, sign_icons[capricorn_alternate])
        else:
            item.setIcon(1, sign_icons[i.natRulerData.name])
        item.setText(1, i.natRulerData.name)
        item.setToolTip(1, i.natRulerStr())
        if i.cusp.signData.name == "Capricorn":
            item.setIcon(2, sign_icons[capricorn_alternate])
        else:
            item.setIcon(2, sign_icons[i.cusp.signData.name])
        item.setText(2, i.cusp.signData.name)
        item.setToolTip(2, str(i.cusp.signData))
        item.setText(3, i.cusp.only_degs())
        item.setToolTip(3, "The real longitude is %.3f degrees" %(i.cusp.longitude))
        if i.end.signData.name == "Capricorn":
            item.setIcon(4, sign_icons[capricorn_alternate])
        else:
            item.setIcon(4, sign_icons[i.end.signData.name])
        item.setText(4, i.end.signData.name)
        item.setToolTip(4, str(i.end.signData))
        item.setText(5, i.end.only_degs())
        item.setToolTip(5, "The real longitude is %.3f degrees" %(i.end.longitude))
        tree.addTopLevelItem(item)
    info_dialog.show()

class SignsForDayList(QtWidgets.QWidget):
    def __init__(self, icons, sign_icons, admi, nodes, pluto_alt, cprc_alt, 
                 table=None, orbs=DEFAULT_ORBS, parent=None):
        super().__init__(parent=parent)
        vbox = QtWidgets.QVBoxLayout(self)
        grid = QtWidgets.QGridLayout()
        vbox.addLayout(grid)
        grid.addWidget(QtWidgets.QLabel("Pick a time to view for"), 0, 0)
        self.time = QtWidgets.QTimeEdit()
        grid.addWidget(self.time, 0, 1)
        self.tree = QtWidgets.QTreeWidget(self)
        self.tree.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tree.setRootIsDecorated(False)
        self.tree.setHeaderLabels(["Planet", "Constellation", "Angle", "Movement", "House"])
        self.tree.setColumnCount(5)
        vbox.addWidget(self.tree)
        self.time.setDisplayFormat("HH:mm:ss")
        self.time.timeChanged.connect(self.update_degrees)
        button = QtWidgets.QPushButton("&Aspects")
        button.clicked.connect(self.showAspects)
        button2 = QtWidgets.QPushButton("&Houses Overview")
        button2.clicked.connect(self.showHouses)
        grid.addWidget(button, 2, 0)
        grid.addWidget(button2, 2, 1)

        self.z = []
        self.h = []
        self.icons = icons
        self.sign_icons = sign_icons
        self.admi = admi
        self.nodes = nodes
        self.pluto_alternate = pluto_alt
        self.capricorn_alternate = cprc_alt
        self.table = table or []
        self.orbs = orbs

    def showAspects(self):
        aspectsDialog(self, self.z, self.table, self.icons, 
        self.sign_icons, self.pluto_alternate, self.admi, 
        self.nodes, self.orbs)

    def showHouses(self):
        housesDialog(self, self.h, self.capricorn_alternate, self.sign_icons)

    def update_degrees(self, time):
        self.tree.clear()
        self.target_date = self.target_date.replace(
            hour=time.hour(),
            minute=time.minute(),
            second=time.second()
        )
        self._grab()

    def assembleFromZodiac(self, zodiac):
        self.tree.clear()
        if not self.z:
            self.z = zodiac
        for i in zodiac:
            item = QtWidgets.QTreeWidgetItem()
            if self.pluto_alternate and i.name == "Pluto":
                item.setIcon(0, self.icons['Pluto 2'])
            elif i.name in {"Ascendant", "Descendant", "MC", "IC"}:
                item.setIcon(0, self.sign_icons[i.name])
            else:
                item.setIcon(0, self.icons[i.name])
            item.setText(0, i.name)
            item.setToolTip(0, str(i))
            if i.m.signData.name == "Capricorn":
                item.setIcon(1, self.sign_icons[self.capricorn_alternate])
            else:
                item.setIcon(1, self.sign_icons[i.m.signData.name])
            item.setText(1, i.m.signData.name)
            item.setToolTip(1, str(i.m.signData))
            item.setText(2, i.m.only_degs())
            coord_tooltip = (
                "The real longitude is {0:.3f} degrees"
                "\nOr {1:.3f}, if ecliptic latitude is considered."
            ).format(i.m.longitude, i.m.projectedLon)
            item.setToolTip(2, coord_tooltip)
            item.setText(3, i.movement.label)
            item.setText(4, str(i.m.house_info.num))
            item.setToolTip(4, i.m.status())
            self.tree.addTopLevelItem(item)

    def _grab(self):
        if not self.z:
            self.h, self.z = get_signs(
                self.target_date,
                self.observer,
                self.nodes,
                self.admi
            )
        else:
            update_planets_and_cusps(self.target_date, self.observer, self.h, self.z)
        self.assembleFromZodiac(self.z)

    def get_constellations(self, date, observer):
        self.observer = observer
        self.target_date = date
        self.time.setTime(self.target_date.time())


