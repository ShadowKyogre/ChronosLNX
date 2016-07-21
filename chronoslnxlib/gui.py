#!/usr/bin/env python

# icon.py
#http://www.saltycrane.com/blog/2007/12/pyqt-43-qtableview-qabstracttable-model/
#http://www.commandprompt.com/community/pyqt/book1
#http://doc.qt.nokia.com/latest/qstandarditemmodel.html
#http://www.interactivestars.com/lost_zodiac/lost_zodiac_sign.html <- interesting
#http://www.ips-planetarium.org/planetarian/articles/realconstellations_zodiac.html <- this too
import os
import sys
import datetime
from datetime import timedelta
import argparse
from shlex import split
from subprocess import call
from re import findall, match, sub

from PyQt4 import QtGui, QtCore
import swisseph

from . import geolocationwidget ## from example, but modified a little
from .core import compare_to_the_second
from .core.charts import update_planets_and_cusps, get_signs
from .core.hours import AstrologicalDay, get_planet_day
#previous_new_moon -> predict_phase
from .core.moon_phases import predict_phase, grab_phase, state_to_string

from .astroclock import AstroClock
from .astrocalendar import AstroCalendar
from .astrowidgets import PlanetaryHoursList, MoonCycleList, SignsForDayList, housesDialog
from .eventplanner import EventsList, DayEventsModel
from .chronostext import (
    prepare_planetary_info,
    prepare_moon_cycle,
    prepare_sign_info,
    prepare_events,
    prepare_all
)
from .guiconfig import ChronosLNXConfig, grab_icon_path, get_available_themes
from . import APPNAME, APPVERSION, DESCRIPTION, EMAIL, AUTHOR, YEAR, PAGE
pynf = True

#http://pastebin.com/BvNx9wdk

class ReusableDialog(QtGui.QDialog):
    # because some dialogs are better if they're made and
    # just re-used instead of completely reconstructed
    def __init__(self, *args):
        super().__init__(*args)

    def closeEvent(self, event):
        if hasattr(self.parent(), "trayIcon") and self.parent().trayIcon.isVisible():
            self.hide()
            event.ignore()

class ChronosLNX(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.prevtime = None
        self.timer = QtCore.QTimer(self)
        self.draw_timer = QtCore.QTimer(self)
        self.now = clnxcfg.observer.obvdate
        self.make_settings_dialog()
        self.make_save_for_date_range()
        self.make_tray_icon()
        self.setWindowTitle(APPNAME)

        self.houses, self.zodiac = get_signs(clnxcfg.baby.obvdate, clnxcfg.baby,
                                            clnxcfg.show_nodes, clnxcfg.show_admi)
        #self.setDocumentMode (True)
        self.add_widgets()
        self.timer.timeout.connect(self.update)
        self.draw_timer.timeout.connect(self.update_astro_clock)
        self.setDockNestingEnabled(True)
        self.timer.start(1000)
        if self.astroClock is not None:
            self.draw_timer.start(60000)

    def add_widgets(self):
        ##left pane
        if clnxcfg.show_aclk:
            self.astroClock = AstroClock(self)
            self.setCentralWidget(self.astroClock)
        else:
            self.astroClock = None
        #self.astroClock.hide()

        self.todayOther = QtGui.QLabel()

        self.todayOther.setTextFormat(QtCore.Qt.RichText)

        docktlabel = QtGui.QDockWidget(self)
        docktlabel.setWidget(self.todayOther)
        docktlabel.setWindowTitle("Info for Today")
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, docktlabel)

        dockcalendar = QtGui.QDockWidget(self)
        self.calendar = AstroCalendar(dockcalendar)
        dockcalendar.setWidget(self.calendar)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dockcalendar)
        dockcalendar.setWindowTitle("Calendar")
        self.make_calendar_menu()

        aspectsAction = QtGui.QAction(
            QtGui.QIcon.fromTheme("view-calendar-list"),
            'Aspects for Now',
            self
        )
        aspectsAction.triggered.connect(
            lambda: aspectsDialog(
                self,
                self.zodiac,
                clnxcfg.natal_data[1],
                clnxcfg.main_icons,
                clnxcfg.sign_icons,
                clnxcfg.pluto_alt,
                clnxcfg.show_admi,
                clnxcfg.show_nodes,
                clnxcfg.orbs
            )
        )

        housesAction = QtGui.QAction(
            QtGui.QIcon.fromTheme("measure"),
            'Houses for Now',
            self
        )
        housesAction.triggered.connect(
            lambda: housesDialog(
                self,
                self.houses,
                clnxcfg.capricorn_alt,
                clnxcfg.sign_icons
            )
        )

        natalAction = QtGui.QAction(
            QtGui.QIcon.fromTheme("view-calendar-birthday"),
            '&View Natal Data',
            self
        )
        natalAction.triggered.connect(
            lambda: self.get_info_for_date(
                clnxcfg.baby.obvdate,
                birth=True
            )
        )

        saveRangeAction = QtGui.QAction(
            QtGui.QIcon.fromTheme("document-save-as"),
            'Save data from dates',
            self
        )
        saveRangeAction.triggered.connect(self.save_for_range_dialog.open)

        settingsAction = QtGui.QAction(
            QtGui.QIcon.fromTheme('preferences-other'),
            'Settings',
            self
        )
        settingsAction.triggered.connect(self.settings_dialog.open)

        helpAction = QtGui.QAction(
            QtGui.QIcon.fromTheme('help-contents'),
            'Help',
            self
        )
        helpAction.triggered.connect(self.show_help)

        aboutAction = QtGui.QAction(
            QtGui.QIcon.fromTheme('help-about'),
            'About',
            self
        )
        aboutAction.triggered.connect(self.show_about)

        toolbar = self.addToolBar('Main')
        toolbar.addAction(aspectsAction)
        toolbar.addAction(housesAction)
        toolbar.addAction(natalAction)
        toolbar.addAction(saveRangeAction)
        toolbar.addAction(settingsAction)
        toolbar.addAction(helpAction)
        toolbar.addAction(aboutAction)

        ##right pane
        #dayinfo = QtGui.QHBoxLayout()
        #self.todayPicture = QtGui.QLabel()

        #dayinfo.addWidget(self.todayPicture)
        #dayinfo.addWidget(self.todayOther)

        dockhours = QtGui.QDockWidget(self)
        self.hoursToday = PlanetaryHoursList(self)
        dockhours.setWindowTitle("Planetary Hours")
        dockhours.setWidget(self.hoursToday)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dockhours)

        dockmoon = QtGui.QDockWidget(self)
        self.moonToday = MoonCycleList(self)
        dockmoon.setWindowTitle("Moon Phases")
        dockmoon.setWidget(self.moonToday)
        self.tabifyDockWidget(dockhours, dockmoon)

        docksigns = QtGui.QDockWidget(self)
        self.signsToday = SignsForDayList(
            clnxcfg.main_icons,
            clnxcfg.sign_icons,
            clnxcfg.show_admi,
            clnxcfg.show_nodes,
            clnxcfg.pluto_alt,
            clnxcfg.capricorn_alt,
            table=clnxcfg.natal_data[1],
            orbs=clnxcfg.orbs,
            parent=self
        )
        docksigns.setWindowTitle("Signs")
        docksigns.setWidget(self.signsToday)
        self.tabifyDockWidget(dockmoon, docksigns)

        dockevents = QtGui.QDockWidget(self)
        self.eventsToday = EventsList(self)
        dockevents.setWindowTitle("Events")
        dockevents.setWidget(self.eventsToday)
        self.tabifyDockWidget(docksigns, dockevents)

        #comment this out later
        self.update_widgets_config()

        self.prepare_hours_for_today()
        self.moonToday.get_moon_cycle(self.now, clnxcfg.observer)
        self.moonToday.highlight_cycle_phase(self.now)
        self.signsToday.get_constellations(self.now, clnxcfg.observer)

        clnxcfg.todays_schedule.setDate(self.now.date())
        self.eventsToday.tree.setModel(clnxcfg.todays_schedule)

        self.update()

    def update_astro_clock(self):
        if self.astroClock is not None:
            self.astroClock.signData = [self.houses, self.zodiac]

    def update_widgets_config(self):
        app.setStyleSheet(clnxcfg.stylesheet)

        if not clnxcfg.show_aclk:
            if self.astroClock is not None:
                self.setCentralWidget(None)
                self.astroClock = None
                self.draw_timer.stop()
        else:
            self.astroClock = AstroClock(self)
            self.setCentralWidget(self.astroClock)

            self.astroClock.icons = clnxcfg.main_icons
            self.astroClock.sign_icons = clnxcfg.sign_icons
            self.astroClock.natData = clnxcfg.natal_data
            self.astroClock.bd = clnxcfg.baby.obvdate
            self.astroClock.signData = [self.houses, self.zodiac]
            self.astroClock.hours = self.hoursToday
            self.astroClock.pluto_alternate = clnxcfg.pluto_alt
            self.astroClock.capricorn_alternate = clnxcfg.capricorn_alt
            self.astroClock.orbs = clnxcfg.orbs
            self.astroClock.observer = clnxcfg.observer
            if not clnxcfg.use_css:
                self.astroClock.init_colors()
            self.draw_timer.start(60000)

        self.calendar.setIcons(clnxcfg.moon_icons)
        self.calendar.setShowPhase(clnxcfg.show_mcal)
        self.calendar.setSolarReturn(clnxcfg.show_sr)
        self.calendar.setLunarReturn(clnxcfg.show_lr)
        self.calendar.setBirthTime(clnxcfg.baby.obvdate)
        self.calendar.setNatalMoon(clnxcfg.natal_moon)
        self.calendar.setNatalSun(clnxcfg.natal_sun)
        self.calendar.useCSS = clnxcfg.use_css
        self.calendar.observer = clnxcfg.observer

        self.hoursToday.icons = clnxcfg.main_icons
        self.moonToday.icons = clnxcfg.moon_icons

        self.signsToday.table = clnxcfg.natal_data[1]
        self.signsToday.icons = clnxcfg.main_icons
        self.signsToday.sign_icons = clnxcfg.sign_icons
        self.signsToday.admi = clnxcfg.show_admi
        self.signsToday.nodes = clnxcfg.show_nodes
        self.signsToday.pluto_alternate = clnxcfg.pluto_alt
        self.signsToday.capricorn_alternate = clnxcfg.capricorn_alt
        self.signsToday.orbs = clnxcfg.orbs
##time related

    def update_hours(self):
        self.hoursToday.clear()
        self.signsToday.tree.clear()
        self.now = clnxcfg.observer.obvdate
        self.prepare_hours_for_today()
        self.eventsToday.tree.model().setDate(self.now.date())
        self.signsToday.get_constellations(self.now, clnxcfg.observer)

    def update_moon_cycle(self):
        if predict_phase(self.now).timetuple().tm_yday == self.now.timetuple().tm_yday:
            self.moonToday.clear()
            self.moonToday.get_moon_cycle(self.now, clnxcfg.observer)
        self.moonToday.highlight_cycle_phase(self.now)

    def prepare_hours_for_today(self):
        self.astro_day = AstrologicalDay(clnxcfg.observer, date=self.now)
        dayn = self.astro_day.sunrise.isoweekday() % 7
        self.pday = get_planet_day(dayn)
        print(
            self.astro_day.sunrise,
            self.astro_day.sunset,
            self.astro_day.next_sunrise
        )
        if self.astroClock is not None:
            self.astroClock.nexts = self.astro_day.next_sunrise
        self.hoursToday.prepareHours(astro_day=self.astro_day)
        #http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/qtreewidgetitem.html#setIcon
        #http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/qtreewidget.html

    def show_notification(self, title, text, ptrigger):
            if pynf:
                fldr = QtCore.QDir("skin:/")
                if ptrigger:
                    path = grab_icon_path("planets", self.phour.lower())
                else:
                    path = grab_icon_path("misc", "chronoslnx")
                path = fldr.absoluteFilePath(path.replace("skin:", ""))
                call(['notify-send', '-t', '10000', '-a', APPNAME,
                      '-i', path, title, text])
            else:
                if self.trayIcon.supportsMessages():
                    if ptrigger:
                        self.trayIcon.showMessage(title, text, msecs=10000)
                              #clnxcfg.main_icons[self.phour],msecs = 10000)
                    else:
                        self.trayIcon.showMessage(title, text, msecs=10000)
                              #clnxcfg.main_icons['logo'],msecs = 10000)
                else:
                    #last resort, as popup dialogs are annoying
                    if ptrigger:
                        pixmap = self.main_pixmaps[self.phour]
                    else:
                        pixmap = self.main_pixmaps['logo']
                    dialog = QtGui.QMessageBox(self)
                    dialog.setTitle(title)
                    dialog.setTitle(text)
                    dialog.setIconPixmap(pixmap)
                    dialog.open()

##datepicking related
#http://eli.thegreenplace.net/2011/04/25/passing-extra-arguments-to-pyqt-slot/

    def get_info_for_date(self, date, birth=False):
        info_dialog = QtGui.QDialog(self)
        dateinfo = "Info for {0}".format(date.strftime("%m/%d/%Y"))
        if birth:
            ob = clnxcfg.baby
            text = (
                "\nNote: This is for the birth timezone {0} and this time."
                "\nIf you want adjust your birth time, go to Settings."
            ).format(clnxcfg.baby.obvdate.tzname())
        else:
            ob = clnxcfg.observer
            text = ""
        infotext = "{dateinfo}{text}".format(**locals())
        info_dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        vbox = QtGui.QVBoxLayout(info_dialog)
        vbox.addWidget(QtGui.QLabel(text))

        hoursToday = PlanetaryHoursList(info_dialog)
        hoursToday.icons = clnxcfg.main_icons

        moonToday = MoonCycleList(info_dialog)
        moonToday.icons = clnxcfg.moon_icons

        signsToday = SignsForDayList(
            clnxcfg.main_icons,
            clnxcfg.sign_icons,
            clnxcfg.show_admi,
            clnxcfg.show_nodes,
            clnxcfg.pluto_alt,
            clnxcfg.capricorn_alt,
            orbs=clnxcfg.orbs,
            parent=info_dialog
        )
        if not birth:
            signsToday.table = clnxcfg.natal_data[1]

        eventsToday = EventsList(info_dialog)
        model = DayEventsModel()
        model.setSourceModel(clnxcfg.schedule)
        model.setDate(date)
        eventsToday.tree.setModel(model)
        eventsToday.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        dayData = QtGui.QTabWidget(info_dialog)

        hoursToday.prepareHours(date, ob)
        moonToday.get_moon_cycle(date, clnxcfg.observer)
        moonToday.highlight_cycle_phase(date)
        if birth:
            print("Using already available birth data instead of recalculating it")
            signsToday.time.timeChanged.disconnect()
            signsToday.time.setReadOnly(True)
            signsToday.time.setTime(clnxcfg.baby.obvdate.time())
            signsToday.assembleFromZodiac(clnxcfg.natal_data[1])
            signsToday.h = clnxcfg.natal_data[0]
        else:
            signsToday.get_constellations(date, ob)

        dayData.addTab(hoursToday, "Planetary Hours")
        dayData.addTab(moonToday, "Moon Phases")
        dayData.addTab(signsToday, "Signs")
        dayData.addTab(eventsToday, "Events")
        vbox.addWidget(dayData)
        info_dialog.show()

    def make_save_for_date_range(self):
        #self.save_for_range_dialog = QtGui.QDialog(self)
        self.save_for_range_dialog = ReusableDialog(self)
        self.save_for_range_dialog.setFixedSize(380, 280)
        self.save_for_range_dialog.setWindowTitle("Save Data for Dates")
        grid = QtGui.QGridLayout(self.save_for_range_dialog)

        self.save_for_range_dialog.date_start = QtGui.QDateTimeEdit(self.save_for_range_dialog)
        self.save_for_range_dialog.date_start.setDisplayFormat("MM/dd/yyyy")
        self.save_for_range_dialog.date_end = QtGui.QDateTimeEdit(self.save_for_range_dialog)
        self.save_for_range_dialog.date_end.setDisplayFormat("MM/dd/yyyy")

        grid.addWidget(QtGui.QLabel("Save from"), 0, 0)
        grid.addWidget(self.save_for_range_dialog.date_start, 0, 1)
        grid.addWidget(QtGui.QLabel("To"), 1, 0)
        grid.addWidget(self.save_for_range_dialog.date_end, 1, 1)
        grid.addWidget(QtGui.QLabel("Data to Save"), 2, 0)

        self.save_for_range_dialog.checkboxes = QtGui.QButtonGroup()
        self.save_for_range_dialog.checkboxes.setExclusive(False)
        checkboxes_frame = QtGui.QFrame(self.save_for_range_dialog)

        vbox = QtGui.QVBoxLayout(checkboxes_frame)

        all_check = QtGui.QCheckBox("All", checkboxes_frame)
        ph_check = QtGui.QCheckBox("Planetary Hours", checkboxes_frame)
        s_check = QtGui.QCheckBox("Planetary Signs", checkboxes_frame)
        m_check = QtGui.QCheckBox("Moon Phase", checkboxes_frame)
        e_check = QtGui.QCheckBox("Events", checkboxes_frame)

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

        grid.addWidget(checkboxes_frame, 2, 1)

        grid.addWidget(QtGui.QLabel("Folder to save in"), 3, 0)
        hbox = QtGui.QHBoxLayout()
        self.save_for_range_dialog.filename = QtGui.QLineEdit(self.save_for_range_dialog)
        button = QtGui.QPushButton(self.save_for_range_dialog)
        button.setIcon(QtGui.QIcon.fromTheme("document-open"))
        button.clicked.connect(self.get_folder_name)
        hbox.addWidget(self.save_for_range_dialog.filename)
        hbox.addWidget(button)
        grid.addLayout(hbox, 3, 1)

        buttonbox = QtGui.QDialogButtonBox(QtCore.Qt.Horizontal)
        okbutton = buttonbox.addButton(QtGui.QDialogButtonBox.Ok)
        okbutton.clicked.connect(self.mass_print)
        cancelbutton = buttonbox.addButton(QtGui.QDialogButtonBox.Cancel)
        cancelbutton.clicked.connect(self.save_for_range_dialog.hide)
        grid.addWidget(buttonbox, 4, 0, 1, 2)

    def get_folder_name(self):
        text = QtGui.QFileDialog.getExistingDirectory(
            caption="Save in folder...",
            options=QtGui.QFileDialog.ShowDirsOnly
        )
        self.save_for_range_dialog.filename.setText(text)

    def mass_print(self):
        start_pydate = self.save_for_range_dialog.date_end.date().toPyDate()
        end_pydate = self.save_for_range_dialog.date_start.date().toPyDate()
        day_numbers = (start_pydate - end_pydate).days
        if self.save_for_range_dialog.filename.text() > "":
            for j in self.save_for_range_dialog.checkboxes.buttons():
                if j.isChecked():
                    store_here = os.path.join(
                        self.save_for_range_dialog.filename.text(),
                        j.text().replace(" ", "_")
                    )
                    if not os.path.exists(store_here):
                        os.mkdir(store_here)
            for i in range(day_numbers+1):
                py_dt = self.save_for_range_dialog.date_start.dateTime().toPyDateTime()
                date = py_dt.replace(tzinfo=clnxcfg.observer.timezone) + timedelta(days=i)
                for j in self.save_for_range_dialog.checkboxes.buttons():
                    if j.isChecked():
                        filename = os.path.join(
                            self.save_for_range_dialog.filename.text(),
                            j.text().replace(" ", "_"),
                            date.strftime("%m-%d-%Y.txt")
                        )
                        self.print_to_file(
                            j.text(),
                            date,
                            filename=filename,
                            suppress_notification=True
                        )
    #'''
    def make_calendar_menu(self):
        self.calendar._table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.calendar._table.customContextMenuRequested.connect(self.get_cal_menu)
        #self.calendar.setContextMenu(self.menu)
    #'''
    def copy_to_clipboard(self, option, date):
        if option == "All":
            text = prepare_all(
                date,
                clnxcfg.observer,
                clnxcfg.schedule,
                clnxcfg.show_nodes,
                clnxcfg.show_admi
            )
        elif option == "Moon Phase":
            text = prepare_moon_cycle(date)
        elif option == "Planetary Signs":
            text = prepare_sign_info(
                date,
                clnxcfg.observer,
                clnxcfg.show_nodes,
                clnxcfg.show_admi
            )
        elif option == "Planetary Hours":
            text = prepare_planetary_info(date, clnxcfg.observer)
        else: #option == "Events"
            text = prepare_events(date, clnxcfg.schedule)
        app.clipboard().setText(text)

# KGlobal::locale::Warning your global KLocale is being recreated
# with a valid main component instead of a fake component,
# this usually means you tried to call i18n related functions before
# your main component was created.
# You should not do that since it most likely will not work

# X Error: RenderBadPicture (invalid Picture parameter) 174
# Extension:    153 (RENDER)
# Minor opcode: 8 (RenderComposite)
# Resource id:  0x3800836

 #weird bug related to opening file dialog on linux through this, but it's harmless

    def print_to_file(self, option, date, filename=None,
        suppress_notification=False):
        if option == "All":
            text = prepare_all(
                date,
                clnxcfg.observer,
                clnxcfg.schedule,
                clnxcfg.show_nodes,
                clnxcfg.show_admi
            )
        elif option == "Moon Phase":
            text = prepare_moon_cycle(date)
        elif option == "Planetary Signs":
            text = prepare_sign_info(
                date,
                clnxcfg.observer,
                clnxcfg.show_nodes,
                clnxcfg.show_admi
            )
        elif option == "Planetary Hours":
            text = prepare_planetary_info(date, clnxcfg.observer)
        else:  #option == "Events"
            text = prepare_events(date, clnxcfg.schedule)
        if filename is None:
            filename = QtGui.QFileDialog.getSaveFileName(
                self,
                caption="Saving {0} for {1}".format(option, date.strftime("%m/%d/%Y")),
                filter="*.txt"
            )
        if filename is not None and filename != "":
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(text)
                if not suppress_notification:
                    self.show_notification(
                        "Saved",
                        "{0} has the {1} you saved.".format(
                            filename,
                            option
                        ),
                        False
                    )

    def get_cal_menu(self, qpoint):
        table = self.calendar._table
        item = table.itemAt(qpoint)

        day = item.data(QtCore.Qt.UserRole)
        date2 = None
        date3 = None
        tzone = clnxcfg.observer.timezone
        date = datetime.datetime.fromordinal(day.toordinal())
        date = date.replace(hour=12, minute=0, second=0, tzinfo=tzone)

        if self.calendar.lunarReturn:
            idx = self.calendar.fetchLunarReturn(day)
            if idx >= 0:
                date2 = self.calendar.lunarReturns[idx]
        if self.calendar.solarReturn and day == self.calendar.solarReturnTime.date():
            date3 = self.calendar.solarReturnTime

        #self.calendar.setGridVisible(True)
        menu = QtGui.QMenu(self.calendar)
        if date2:
            lritem_label = "Lunar Return for {0}".format(date.strftime("%m/%d/%Y"))
            lritem = menu.addAction(lritem_label)
            lritem.triggered.connect(lambda: self.get_info_for_date(date2))
            lritem.setIcon(QtGui.QIcon.fromTheme("dialog-information"))
        if date3:
            sritem_label = "Solar Return for {0}".format(date.strftime("%m/%d/%Y"))
            sritem = menu.addAction(sritem_label)
            sritem.triggered.connect(lambda: self.get_info_for_date(date3))
            sritem.setIcon(QtGui.QIcon.fromTheme("dialog-information"))

        infoitem = menu.addAction("Info for {0}".format(date.strftime("%m/%d/%Y")))
        infoitem.triggered.connect(lambda: self.get_info_for_date(date))
        infoitem.setIcon(QtGui.QIcon.fromTheme("dialog-information"))

        copymenu = menu.addMenu("Copy")
        copymenu.setIcon(QtGui.QIcon.fromTheme("edit-copy"))
        copyall = copymenu.addAction("All")
        copydate = copymenu.addAction("Date")
        copyplanetdata = copymenu.addAction("Planetary Hours")
        copymoonphasedata = copymenu.addAction("Moon Phases")
        copysignsdata = copymenu.addAction("Signs for this date")
        copyeventdata = copymenu.addAction("Events")

        copyall_cb = lambda: self.copy_to_clipboard("All", date)
        copydate_cb = lambda: app.clipboard().setText(date.strftime("%m/%d/%Y"))
        copyplanetdata_cb = lambda: self.copy_to_clipboard("Planetary Hours", date)
        copymoonphasedata_cb = lambda: self.copy_to_clipboard("Moon Phase", date)
        copysignsdata_cb = lambda: self.copy_to_clipboard("Planetary Signs", date)
        copyeventdata_cb = lambda: self.copy_to_clipboard("Events", date)

        copyall.triggered.connect(copyall_cb)
        copydate.triggered.connect(copydate_cb)
        copyplanetdata.triggered.connect(copyplanetdata_cb)
        copymoonphasedata.triggered.connect(copymoonphasedata_cb)
        copysignsdata.triggered.connect(copysignsdata_cb)
        copyeventdata.triggered.connect(copyeventdata_cb)

        savemenu = menu.addMenu("Save to File")
        savemenu.setIcon(QtGui.QIcon.fromTheme("document-save-as"))
        saveall = savemenu.addAction("All")
        saveplanetdata = savemenu.addAction("Planetary Hours")
        savemoonphasedata = savemenu.addAction("Moon Phases")
        savesignsdata = savemenu.addAction("Signs for this date")
        saveeventdata = savemenu.addAction("Events")

        saveall_cb = lambda: self.print_to_file("All", date)
        saveplanetdata_cb = lambda: self.print_to_file("Planetary Hours", date)
        savemoonphasedata_cb = lambda: self.print_to_file("Moon Phase", date)
        savesignsdata_cb = lambda: self.print_to_file("Planetary Signs", date)
        saveeventdata_cb = lambda: self.print_to_file("Events", date)

        saveall.triggered.connect(saveall_cb)
        saveplanetdata.triggered.connect(saveplanetdata_cb)
        savemoonphasedata.triggered.connect(savemoonphasedata_cb)
        savesignsdata.triggered.connect(savesignsdata_cb)
        saveeventdata.triggered.connect(saveeventdata_cb)

        menu.exec_(self.calendar.mapToGlobal(qpoint))
        #http://www.qtcentre.org/archive/index.php/t-42524.html?s = ef30fdd9697c337a1d588ce9d26f47d8

##config related

    def settings_reset(self):
        clnxcfg.reset_settings()
        self.update_settings_widgets()
        self.update_widgets_config()

        self.update_hours()
        self.moonToday.clear()
        self.moonToday.get_moon_cycle(self.now, clnxcfg.observer)
        self.moonToday.highlight_cycle_phase(self.now)

    def update_settings_widgets(self):
        self.settings_dialog.location_widget.setLatitude(clnxcfg.observer.lat)
        self.settings_dialog.location_widget.setLongitude(clnxcfg.observer.lng)
        self.settings_dialog.location_widget.setElevation(clnxcfg.observer.elevation)
        self.settings_dialog.css_check.setChecked(clnxcfg.use_css)
        self.settings_dialog.override_ui_icon.setText(clnxcfg.current_icon_override)

        self.settings_dialog.date.setDateTime(clnxcfg.baby.obvdate)
        self.settings_dialog.birth_widget.setLatitude(clnxcfg.baby.lat)
        self.settings_dialog.birth_widget.setLongitude(clnxcfg.baby.lng)
        self.settings_dialog.birth_widget.setElevation(clnxcfg.baby.elevation)

        idx = self.settings_dialog.appearance_icons.findText(clnxcfg.current_theme)
        self.settings_dialog.appearance_icons.setCurrentIndex(idx)

        self.settings_dialog.s_check.setChecked(clnxcfg.show_sign)
        self.settings_dialog.m_check.setChecked(clnxcfg.show_moon)
        self.settings_dialog.h_check.setChecked(clnxcfg.show_house_of_moment)

        self.settings_dialog.mp_check.setChecked(clnxcfg.show_mcal)
        self.settings_dialog.sr_check.setChecked(clnxcfg.show_sr)
        self.settings_dialog.lr_check.setChecked(clnxcfg.show_lr)
        self.settings_dialog.a_check.setChecked(clnxcfg.show_admi)
        self.settings_dialog.n_check.setChecked(clnxcfg.show_nodes)
        self.settings_dialog.p_check.setChecked(clnxcfg.pluto_alt)
        self.settings_dialog.ac_check.setChecked(clnxcfg.show_aclk)

        idx2 = self.settings_dialog.c_check.findText(clnxcfg.capricorn_alt)
        self.settings_dialog.c_check.setCurrentIndex(idx2)

        for i in self.settings_dialog.orbs:
            self.settings_dialog.orbs[i].setValue(clnxcfg.orbs[i])

    def settings_change(self):
        lat = float(self.settings_dialog.location_widget.latitude)
        lng = float(self.settings_dialog.location_widget.longitude)
        elv = float(self.settings_dialog.location_widget.elevation)

        blat = float(self.settings_dialog.birth_widget.latitude)
        blng = float(self.settings_dialog.birth_widget.longitude)
        belv = float(self.settings_dialog.birth_widget.elevation)

        thm = self.settings_dialog.appearance_icons.currentText()
        cp = self.settings_dialog.c_check.currentText()
        iothm = self.settings_dialog.override_ui_icon.text()

        clnxcfg.observer.lat = lat
        clnxcfg.observer.lng = lng
        clnxcfg.observer.elevation = elv

        clnxcfg.baby.lat = blat
        clnxcfg.baby.lng = blng
        clnxcfg.baby.elevation = belv
        #how to migrate?
        clnxcfg.baby.obvdate = self.settings_dialog.date.dateTime().toPyDateTime()

        clnxcfg.current_theme = thm
        clnxcfg.current_icon_override = iothm
        clnxcfg.show_sign = self.settings_dialog.s_check.isChecked()
        clnxcfg.show_moon = self.settings_dialog.m_check.isChecked()
        clnxcfg.show_house_of_moment = self.settings_dialog.h_check.isChecked()
        clnxcfg.show_nodes = self.settings_dialog.n_check.isChecked()
        clnxcfg.show_admi = self.settings_dialog.a_check.isChecked()
        clnxcfg.show_mcal = self.settings_dialog.mp_check.isChecked()
        clnxcfg.show_sr = self.settings_dialog.sr_check.isChecked()
        clnxcfg.show_lr = self.settings_dialog.lr_check.isChecked()
        clnxcfg.pluto_alt = self.settings_dialog.p_check.isChecked()
        clnxcfg.capricorn_alt = cp
        clnxcfg.use_css = self.settings_dialog.css_check.isChecked()
        clnxcfg.show_aclk = self.settings_dialog.ac_check.isChecked()

        for i in self.settings_dialog.orbs:
            clnxcfg.orbs[i] = self.settings_dialog.orbs[i].value()

        clnxcfg.load_theme()
        clnxcfg.load_natal_data()

        self.update_widgets_config()

        self.update_hours()
        self.moonToday.clear()
        self.moonToday.get_moon_cycle(self.now, clnxcfg.observer)
        self.moonToday.highlight_cycle_phase(self.now)

        for idx, ico in enumerate(['Capricorn', 'Capricorn 2', 'Capricorn 3']):
            self.settings_dialog.c_check.setItemIcon(idx, clnxcfg.sign_icons[ico])
        #eventually load DB of events

    def settings_write(self):
        self.settings_change()
        clnxcfg.save_settings()
        #clnxcfg.save_schedule()
        self.settings_dialog.hide()

    def make_settings_dialog(self):
        self.settings_dialog = ReusableDialog(self)
        self.settings_dialog.setWindowTitle("Settings")
        tabs = QtGui.QTabWidget(self.settings_dialog)

        location_page = QtGui.QFrame()
        appearance_page = QtGui.QFrame()
        events_page = QtGui.QFrame()
        tweaks_page = QtGui.QFrame()
        calculations_page = QtGui.QFrame()

        tabs.addTab(location_page, "Your Info")
        tabs.addTab(appearance_page, "Appearance")
        tabs.addTab(events_page, "Events")
        tabs.addTab(tweaks_page, "Tweaks")
        tabs.addTab(calculations_page, "Calculations")

        groupbox = QtGui.QGroupBox("Current Location", location_page)
        groupbox2 = QtGui.QGroupBox("Birth Information", location_page)
        self.settings_dialog.location_widget = geolocationwidget.GeoLocationWidget(groupbox)
        vbox = QtGui.QVBoxLayout(location_page)
        gvbox = QtGui.QVBoxLayout(groupbox)
        gvbox.addWidget(self.settings_dialog.location_widget)

        vbox.addWidget(groupbox)
        vbox.addWidget(groupbox2)

        self.settings_dialog.birth_widget = geolocationwidget.GeoLocationWidget(groupbox2)
        self.settings_dialog.date = QtGui.QDateTimeEdit(groupbox2)
        self.settings_dialog.date.setDateRange(
            QtCore.QDate(1902, 1, 1),
            QtCore.QDate(2037, 1, 1)
        )
        self.settings_dialog.date.setDisplayFormat("MM/dd/yyyy - HH:mm:ss")

        tgrid = QtGui.QGridLayout(groupbox2)
        tgrid.addWidget(self.settings_dialog.birth_widget, 0, 0, 3, 2)
        tgrid.addWidget(QtGui.QLabel("Birth time"), 3, 0)
        tgrid.addWidget(self.settings_dialog.date, 3, 1)

        layout = QtGui.QVBoxLayout(self.settings_dialog)
        layout.addWidget(tabs)

        grid = QtGui.QGridLayout(appearance_page)
        appearance_label = QtGui.QLabel("Icon theme")
        self.settings_dialog.appearance_icons = QtGui.QComboBox()
        self.settings_dialog.appearance_icons.addItem("None")
        self.settings_dialog.css_check = QtGui.QCheckBox(
            "Use the custom UI styling in the theme",
            appearance_page
        )
        for theme in get_available_themes():
            #is it all right to format path here?
            path = "skins:{0}/misc/chronoslnx.png".format(theme)
            icon = QtGui.QIcon(path)
            self.settings_dialog.appearance_icons.addItem(icon, theme)

        grid.addWidget(appearance_label, 0, 0)
        grid.addWidget(self.settings_dialog.appearance_icons, 0, 1)
        self.settings_dialog.override_ui_icon = QtGui.QLineEdit(appearance_page)
        self.settings_dialog.override_ui_icon.setToolTip(
            (
                "You should only set this if"
                "standard icons, like Quit, "
                "are not showing.\n"
                "This will take effect after "
                "a restart of ChronosLNX.\n"
                "Currently detected icon theme by system: {0}"
            ).format(clnxcfg.sys_icotheme)
        )
        grid.addWidget(QtGui.QLabel("UI Icon theme: "), 1, 0)
        grid.addWidget(self.settings_dialog.override_ui_icon, 1, 1)
        grid.addWidget(self.settings_dialog.css_check, 2, 0, 1, 2)
        grid.addWidget(
            QtGui.QLabel("Change the following for signs information"),
            3, 0, 1, 2
        )
        self.settings_dialog.c_check = QtGui.QComboBox(appearance_page)
        for ico in ['Capricorn', 'Capricorn 2', 'Capricorn 3']:
            self.settings_dialog.c_check.addItem(clnxcfg.sign_icons[ico], ico)
        self.settings_dialog.p_check = QtGui.QCheckBox(
            "Use the P-looking Pluto icon", appearance_page
        )
        grid.addWidget(self.settings_dialog.p_check, 4, 1)
        grid.addWidget(QtGui.QLabel("Use this Capricorn glyph"), 5, 0)
        grid.addWidget(self.settings_dialog.c_check, 5, 1)


        buttonbox = QtGui.QDialogButtonBox(QtCore.Qt.Horizontal)
        resetbutton = buttonbox.addButton(QtGui.QDialogButtonBox.Reset)
        okbutton = buttonbox.addButton(QtGui.QDialogButtonBox.Ok)
        applybutton = buttonbox.addButton(QtGui.QDialogButtonBox.Apply)
        cancelbutton = buttonbox.addButton(QtGui.QDialogButtonBox.Cancel)

        resetbutton.clicked.connect(self.settings_reset)
        okbutton.clicked.connect(self.settings_write)
        applybutton.clicked.connect(self.settings_change)
        cancelbutton.clicked.connect(self.settings_dialog.hide)
        layout.addWidget(buttonbox)

        eventplanner = EventsList(events_page)
        a_vbox = QtGui.QVBoxLayout(events_page)
        a_vbox.addWidget(eventplanner)
        eventplanner.tree.setModel(clnxcfg.schedule)

        tweak_grid = QtGui.QGridLayout(tweaks_page)
        self.settings_dialog.s_check = QtGui.QCheckBox(
            "Sign of the month",
            tweaks_page
        )
        self.settings_dialog.m_check = QtGui.QCheckBox(
            "Current moon phase",
            tweaks_page
        )
        self.settings_dialog.h_check = QtGui.QCheckBox(
            "House of moment",
            tweaks_page
        )
        self.settings_dialog.n_check = QtGui.QCheckBox(
            "Show Nodes",
            tweaks_page
        )
        self.settings_dialog.a_check = QtGui.QCheckBox(
            "Show the ADMI axis",
            tweaks_page
        )
        a_check_tooltip = "This will show the Ascendant, Descendant, MC, and IC"
        self.settings_dialog.a_check.setToolTip(a_check_tooltip)
        self.settings_dialog.mp_check = QtGui.QCheckBox(
            "Show moon phases",
            tweaks_page
        )
        self.settings_dialog.sr_check = QtGui.QCheckBox(
            "Show solar returns",
            tweaks_page
        )
        self.settings_dialog.lr_check = QtGui.QCheckBox(
            "Show lunar returns",
            tweaks_page
        )
        self.settings_dialog.ac_check = QtGui.QCheckBox(
            "Show rendered astrological clock?",
            tweaks_page
        )
        tweak_grid.addWidget(
            QtGui.QLabel("Show these main window's textual information"),
            0, 0, 1, 2
        )
        tweak_grid.addWidget(self.settings_dialog.s_check, 1, 1)
        tweak_grid.addWidget(self.settings_dialog.m_check, 2, 1)
        tweak_grid.addWidget(self.settings_dialog.h_check, 3, 1)
        tweak_grid.addWidget(
            QtGui.QLabel("Change the following for signs information"),
            4, 0, 1, 2
        )
        tweak_grid.addWidget(self.settings_dialog.n_check, 5, 1)
        tweak_grid.addWidget(self.settings_dialog.a_check, 6, 1)
        tweak_grid.addWidget(
            QtGui.QLabel("Change the following for the calendar"),
            7, 0, 1, 2
        )
        tweak_grid.addWidget(self.settings_dialog.mp_check, 8, 1)
        tweak_grid.addWidget(self.settings_dialog.sr_check, 9, 1)
        tweak_grid.addWidget(self.settings_dialog.lr_check, 10, 1)
        tweak_grid.addWidget(
            QtGui.QLabel("Graphical Clock"),
            11, 0, 1, 2
        )
        tweak_grid.addWidget(self.settings_dialog.ac_check, 12, 1)

        another_vbox = QtGui.QVBoxLayout(calculations_page)
        gbox2 = QtGui.QGroupBox("Orbs")
        another_vbox.addWidget(gbox2)
        ggbox2 = QtGui.QGridLayout(gbox2)

        self.settings_dialog.orbs = {}

        for x, i in enumerate(list(clnxcfg.orbs.keys())):
            self.settings_dialog.orbs[i] = QtGui.QDoubleSpinBox(calculations_page)
            self.settings_dialog.orbs[i].setRange(0, 10)
            ggbox2.addWidget(QtGui.QLabel(i.title()), x, 0, 1, 5)
            ggbox2.addWidget(self.settings_dialog.orbs[i], x, 5, 1, 1)

        self.update_settings_widgets()

## systray
#http://stackoverflow.com/questions/893984/pyqt-show-menu-in-a-system-tray-application
#http://www.itfingers.com/Question/758256/pyqt4-minimize-to-tray

    def make_tray_icon(self):
        self.trayIcon = QtGui.QSystemTrayIcon(QtGui.QIcon(clnxcfg.main_icons['logo']), app)
        menu = QtGui.QMenu()
        quitAction = QtGui.QAction(self.tr("&Quit"), self)
        quitAction.triggered.connect(QtGui.qApp.quit)
        showaction = menu.addAction("&Show", self.show)
        showaction.setIcon(QtGui.QIcon.fromTheme("show-menu"))
        setaction = menu.addAction("&Settings", self.settings_dialog.open)
        setaction.setIcon(QtGui.QIcon.fromTheme("preferences-other"))
        menu.addAction(quitAction)
        quitAction.setIcon(QtGui.QIcon.fromTheme("application-exit"))
        self.trayIcon.setContextMenu(menu)
        self.trayIcon.activated.connect(self.__icon_activated)
        self.trayIcon.show()

    def _ChronosLNX__icon_activated(self, reason):
        if reason == QtGui.QSystemTrayIcon.DoubleClick:
            if self.isHidden():
                self.show()
            else:
                self.hide()

    def closeEvent(self, event):
        if self.trayIcon.isVisible():
            self.hide()
            event.ignore()

##misc
#http://www.saltycrane.com/blog/2008/01/python-variable-scope-notes/

    def show_about(self):
        QtGui.QMessageBox.about(
            self,
            "About {0}".format(APPNAME),
            (
                "<center><big><b>{0} {1}</b></big>"
                "<br />{2}<br />(C) <a href=\"mailto:{3}\">{4}</a>"
                " {5}<br /><a href = \"{6}\">{0} Homepage</a>"
                "</center>"
            ).format(
                APPNAME,
                APPVERSION,
                DESCRIPTION,
                EMAIL,
                AUTHOR,
                YEAR,
                PAGE
            )
        )

    def show_help(self):
        print("Stubbing out")

    def update(self):
        self.now = clnxcfg.observer.obvdate
        update_planets_and_cusps(
            self.now,
            clnxcfg.observer,
            self.houses,
            self.zodiac
        )
        #self.astroClock.signData = [self.houses,self.zodiac]
        if self.now >= self.astro_day.next_sunrise:
            self.update_hours()
        if self.now >= self.moonToday.model().get_date(self.moonToday.model().rowCount()-1):
            self.update_moon_cycle()
        now_hms = (self.now.hour, self.now.minute, self.now.second)
        if self.prevtime == (23, 59, 59) and now_hms == (0, 0, 0):
            self.calendar.remarkToday()
        self.phour = self.hoursToday.grab_nearest_hour(self.now)
        self.check_alarm()
        if clnxcfg.show_house_of_moment:
            hom = self.zodiac[0].m.house_info.num
            if hom == 1:
                suffix = "st"
            elif hom == 2:
                suffix = "nd"
            elif hom == 3:
                suffix = "rd"
            else:
                suffix = "th"
            house_of_moment_string = "<br />The sun is in the {0}<sup>{1}</sup> house".format(hom, suffix)
        else:
            house_of_moment_string = ""
        if clnxcfg.show_sign:
            sign_string = "<br />The sign of the month is {0}".format(self.zodiac[0].m.signData.name)
        else:
            sign_string = ""
        if clnxcfg.show_moon:
            phase = grab_phase(self.now)
            moon_phase = "<br />{0}: {1} illuminated".format(
                state_to_string(phase, swisseph.MOON),
                phase[2]
            )
        else:
            moon_phase = ""

        #probably get boolean of day/night out of model?
        planets_string = "Day of {0}, the hour of {1}".format(self.pday, self.phour)

        total_string = "{0}{1}{2}{3}".format(
            planets_string,
            sign_string,
            moon_phase,
            house_of_moment_string
        )

        if clnxcfg.current_theme == "None":
            sysicon = QtGui.QIcon(grab_icon_path("misc", "chronoslnx"))
        else:
            sysicon = clnxcfg.main_icons[self.phour]
        self.trayIcon.setToolTip(
            "{0}\n{1}".format(
                self.now.strftime("%Y/%m/%d - %H:%M:%S"),
                sub("</?sup>", "", total_string).replace("<br />", "\n")
            )
        )
        self.trayIcon.setIcon(sysicon)
        #self.todayPicture.setPixmap(clnxcfg.main_pixmaps[str(self.phour)])
        self.todayOther.setText("{0}<br />{1}".format(self.now.strftime("%H:%M:%S"), total_string))
        self.prevtime = now_hms

    def event_trigger(self, event_type, text, planet_trigger):
        if event_type == "Save to file":
            print_to_file(self, text, self.now)
        elif event_type == "Command":
            call([split(text)])
        else: #event_type == "Textual reminder"
            self.show_notification("Reminder", text, planet_trigger)

    def parse_phour_args(self, string):
        alist = None
        args = len(findall("%\(prev\)s|%\(next\)s", string))
        model = self.hoursToday.tree.model().sourceModel()
        if args == 2:
            if model.last_index > 0:
                idx = model.last_index - 1
            else:
                idx = model.last_index + 6
            prev_hour = model.get_planet(idx)
            alist = {'prev': prev_hour, "next": self.phour}
        elif args == 1:
            if match("%\(prev\)s"):
                if model.last_index > 0:
                    idx = model.last_index - 1
                else:
                    idx = model.last_index + 6
                prev_hour = model.get_planet(idx)
                alist = {"prev": prev_hour}
            else:
                alist = {"next": self.phour}
        return alist, args

    def parse_hour_args(self, string):
        alist = None
        args = len(findall("%\(prev\)s|%\(next\)s", string))
        if args == 2:
            if self.now.hour == 0:
                prev_hour = 23
            else:
                prev_hour = self.now.hour - 1
            alist = {'prev': prev_hour, "next": self.now.hour}
        elif args == 1:
            if match("%\(prev\)s"):
                if self.now.hour == 0:
                    prev_hour = 23
                else:
                    prev_hour = self.now.hour - 1
                alist = {"prev": prev_hour}
            else:
                alist = {"next": self.now.hour}
        return alist, args

    def check_alarm(self):
        for i in range(clnxcfg.todays_schedule.rowCount()):
            hour_trigger = False
            pt = False
            filtered_idx = clnxcfg.todays_schedule.index(i, 0)
            real_row = clnxcfg.todays_schedule.mapToSource(filtered_idx).row()

            enabled_item = clnxcfg.schedule.item(real_row, 0)
            if enabled_item.checkState() == QtCore.Qt.Checked:
                hour_item = clnxcfg.schedule.item(real_row, 2).data(QtCore.Qt.UserRole)
                txt = clnxcfg.schedule.item(real_row, 4).data(QtCore.Qt.EditRole)
                args = 0
                if isinstance(hour_item, QtCore.QTime):
                    hour_trigger = compare_to_the_second(
                        self.now,
                        hour_item.hour(),
                        hour_item.minute(),
                        0
                    )
                else:
                    if hour_item == "Every planetary hour":
                        phm = self.hoursToday.tree.model().sourceModel()
                        dt = phm.get_date(phm.last_index)
                        hour_trigger = compare_to_the_second(self.now, dt.hour, dt.minute, dt.second+1)
                        if hour_trigger:
                            pt = True
                            alist, args = self.parse_phour_args(txt)
                    elif self.phour == hour_item:
                        phm = self.hoursToday.tree.model().sourceModel()
                        dt = phm.get_date(phm.last_index)
                        hour_trigger = compare_to_the_second(self.now, dt.hour, dt.minute, dt.second+1)
                        pt = True
                    elif hour_item == "When the sun rises":
                        hour_trigger = compare_to_the_second(
                            self.now,
                            self.astro_day.sunrise.hour,
                            self.astro_day.sunrise.minute,
                            self.astro_day.sunrise.second
                        )
                    elif hour_item == "When the sun sets":
                        hour_trigger = compare_to_the_second(
                            self.now,
                            self.astro_day.sunset.hour,
                            self.astro_day.sunset.minute,
                            self.minute.second
                        )
                    elif hour_item == "Every normal hour":
                        hour_trigger = compare_to_the_second(
                            self.now,
                            self.now.hour,
                            0,
                            0
                        )
                        alist, args = self.parse_hour_args(txt)

                if hour_trigger:
                    event_type_item = clnxcfg.schedule.item(real_row, 3).data(QtCore.Qt.EditRole)
                    if args > 0:
                        self.event_trigger(event_type_item, txt % alist, pt)
                    else:
                        self.event_trigger(event_type_item, txt, pt)

def main():
    global app, clnxcfg, pynf

    app = QtGui.QApplication(sys.argv)
    app.setApplicationName(APPNAME)
    app.setApplicationVersion(APPVERSION)

    if os.name == 'nt':
        QtGui.QIcon.setThemeSearchPaths(['/icons'])

    app.setQuitOnLastWindowClosed(False)
    clnxcfg = ChronosLNXConfig()

    app.setWindowIcon(clnxcfg.main_icons['logo'])
    try:
        retcode = call(['which', 'notify-send'])
        pynf = True if retcode == 0 else False
    except Exception as e:
        pynf = False
    if not pynf:
        print("Warning, couldn't find notify-send! On Linux systems, the notifications might look ugly.")
    chronoslnx = ChronosLNX()
    chronoslnx.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
