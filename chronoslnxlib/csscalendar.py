from PyQt4 import QtGui, QtCore
import calendar
from datetime import date as pydate

def _isToday(date):
    return date == pydate.today()

class TodayDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.coltoday = QtGui.QPalette().midlight().color()
        #col=self.coltoday.color()
        self.coltoday.setAlpha(64)

    def paint(self, painter, option, idx):
        super().paint(painter, option, idx)
        date = idx.data(QtCore.Qt.UserRole)
        if idx.data(QtCore.Qt.UserRole+1):
            painter.save()
            painter.setPen(self.coltoday)
            optrect=option.rect
            rect = QtCore.QRectF(optrect.x(), optrect.y(), 
                                 optrect.width()-2, optrect.height()-2)
            painter.drawRect(rect)
            painter.restore()

class CSSCalendar(QtGui.QWidget):
    currentPageChanged = QtCore.pyqtSignal(int,int)
    """A CalendarWidget that supports CSS theming"""
    def __init__(self, *args,**kwargs):
        super().__init__(*args)
        self.__useCSS = False
        layout = QtGui.QGridLayout(self)
        layout.setSpacing(0)
        self._monthBox = QtGui.QComboBox(self)
        self._monthBox.addItems(calendar.month_name[1:])
        self._goForward = QtGui.QToolButton()
        self._goBackward = QtGui.QToolButton()
        self._yearBox = QtGui.QLineEdit(self)
        self._table = QtGui.QTableWidget(6,7)

        self._table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self._table.setHorizontalHeaderLabels(calendar.day_abbr[6:]+calendar.day_abbr[:6])
        self._table.verticalHeader().hide()
        self._table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self._table.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self._table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self._table.setShowGrid(False)
        self._delegate = TodayDelegate()
        self._table.setItemDelegate(self._delegate)

        self._goForward.clicked.connect(self.nextPage)
        self._goBackward.clicked.connect(self.prevPage)
        self._goBackward.setArrowType(QtCore.Qt.LeftArrow)
        self._goForward.setArrowType(QtCore.Qt.RightArrow)
        self._monthBox.activated[int].connect(self.setMonth)

        layout.addWidget(self._goBackward,0,0)
        layout.addWidget(self._monthBox,0,1,1,3)
        layout.addWidget(self._yearBox,0,4,1,1)
        layout.addWidget(self._goForward,0,5)
        layout.addWidget(self._table,1,0,4,6)

        self.weekdayBGs = [QtGui.QBrush() for i in range(7)]
        self.weekdayFGs = [QtGui.QBrush() for i in range(7)]
        self._calendar = calendar.Calendar(6)
        self._date = None
        self.date = pydate.today()
        self._yearBox.textEdited.connect(self.setYear)
        self._yearBox.setInputMask("000D")
        self._yearBox.setMaxLength(4)

    def yearShown(self):
        return int(self._yearBox.text())

    def monthShown(self):
        return self._monthBox.currentIndex()+1

    def setYear(self, year):
        iyear = int(year)
        self.setCurrentPage(iyear,self.date.month)

    def prevPage(self):
        if self._date.month == 1:
            #self.currentPageChanged.emit(self._date.year-1,12)
            self.setCurrentPage(self._date.year-1,12)
        else:
            #self.currentPageChanged.emit(self._date.year,self._date.month-1)
            self.setCurrentPage(self._date.year,self._date.month-1)

    def nextPage(self):
        if self._date.month == 12:
            #self.currentPageChanged.emit(self._date.year+1,11)
            self.setCurrentPage(self._date.year+1,1)
        else:
            #self.currentPageChanged.emit(self._date.year,self._date.month+1)
            self.setCurrentPage(self._date.year,self._date.month+1)

    def setMonth(self, monthidx):
        self.currentPageChanged.emit(self._date.year,monthidx+1)
        try:
            self.date = self.date.replace(month=monthidx+1)
        except ValueError as e:
            _, monthdays = calendar.monthrange(year, month)
            self.date = self.date.replace(month=monthidx+1, day=monthdays)

    def setCurrentPage(self, year, month):
        try:
            idate = self.date.replace(year=year, month=month)
        except ValueError as e:
            _, monthdays = calendar.monthrange(year, month)
            idate = self.date.replace(year = year, month = month, day = monthdays)
        self.currentPageChanged.emit(idate.year, idate.month)
        self.date = idate

    def date(self):
        return self._date
    
    def setDate(self, newdate):
        refill = self._date is None or newdate.month != self._date.month or newdate.year!=self._date.year
        self._date = newdate
        self._yearBox.setText(str(self._date.year))
        self._monthBox.setCurrentIndex(self._date.month-1)
        if refill:
            self._refillCells()

    date = QtCore.pyqtProperty(pydate, date, setDate)

    def remarkToday(self):
        if self._todayItem is not None:
            self._todayItem.setData(QtCore.Qt.UserRole+1, False)
            nextcol = self._todayItem.column() + 1
            nextcolmodu = nextcol % 7
            row = self._todayItem.row()
            if nextcol != nextcolmodu:
                row += 1
            if row <= self._table.rowCount():
                self._todayItem = self._table.item(row, nextcolmodu)
            else:
                self._todayItem = None

    def _modifyDayItem(self, item):
        date = item.data(QtCore.Qt.UserRole)
        isToday = _isToday(date)
        item.setData(QtCore.Qt.UserRole+1, isToday)

    def _refillCells(self):
        monthdates = list(self._calendar.itermonthdates(self._date.year, self._date.month))
        thisday = pydate.today()
        weeks = len(monthdates)
        self._table.setRowCount(int(weeks/7))
        idxs = None
        for i in range(weeks):
            item = QtGui.QTableWidgetItem()
            item.setText(str(monthdates[i].day))
            item.setData(QtCore.Qt.UserRole, monthdates[i])
            item.setData(QtCore.Qt.TextAlignmentRole, QtCore.Qt.AlignCenter)
            if self.useCSS:
                item.setForeground(self.weekdayFGs[i%7])
                item.setBackground(self.weekdayBGs[i%7])
            if monthdates[i] == self._date:
                idxs = (i/7,i%7)
            self._modifyDayItem(item)
            if item.data(QtCore.Qt.UserRole+1):
                self._todayItem = item
            self._table.setItem(i/7,i%7,item)
        self._table.setCurrentCell(*idxs)
        self._table.resizeColumnsToContents()
        self._table.resizeRowsToContents()

    def useCSS(self):
        return self.__useCSS

    def setUseCSS(self, css):
        self.__useCSS = css
        if not self.__useCSS:
            transparent = QtGui.QColor()
            transparent.setAlpha(0)
            brush = QtGui.QBrush(transparent)
            col = self._table.palette().text()
            fg = QtGui.QBrush(col)
            for i in range(self._table.rowCount()):
                for j in range(7):
                    self._table.item(i, j).setForeground(fg)
                    self._table.item(i, j).setBackground(brush)
        else:
            for i in range(self._table.rowCount()):
                for day in range(1, 8):
                    fg=self.weekdayFGs[day-1]
                    fill=self.weekdayBGs[day-1]
                    self._table.item(i, day-1).setForeground(fg)
                    self._table.item(i, day-1).setBackground(fill)

    def setDayFG(self, day, fg):
        self.weekdayFGs[day-1] = fg
        for i in range(self._table.rowCount()):
            self._table.item(i,day-1).setForeground(fg)

    def setDayFill(self, day, fill):
        self.weekdayBGs[day-1] = fill
        for i in range(self._table.rowCount()):
            self._table.item(i,day-1).setBackground(fill)

    def _dayFG(self, day):
        return self.weekdayFGs[day-1]

    def _dayFill(self, day):
        return self.weekdayBGs[day-1]

    sundayFill = QtCore.pyqtProperty(
        "QBrush",
        lambda self: self._dayFill(QtCore.Qt.Sunday),
        lambda self, fill: self._setDayFill(QtCore.Qt.Sunday, fill)
    )
    mondayFill = QtCore.pyqtProperty(
        "QBrush",
        lambda self: self._dayFill(QtCore.Qt.Monday), 
        lambda self, fill: self._setDayFill(QtCore.Qt.Monday,fill)
    )
    tuesdayFill = QtCore.pyqtProperty(
        "QBrush",
        lambda self: self._dayFill(QtCore.Qt.Tuesday), 
        lambda self,fill: self._setDayFill(QtCore.Qt.Tuesday,fill)
    )
    wednesdayFill = QtCore.pyqtProperty(
        "QBrush",
        lambda self: self._dayFill(QtCore.Qt.Wednesday), 
        lambda self,fill: self._setDayFill(QtCore.Qt.Wednesday,fill)
    )
    thursdayFill = QtCore.pyqtProperty(
        "QBrush",
        lambda self: self._dayFill(QtCore.Qt.Thursday), 
        lambda self,fill: self._setDayFill(QtCore.Qt.Thursday,fill)
    )
    fridayFill = QtCore.pyqtProperty(
        "QBrush",
        lambda self: self._dayFill(QtCore.Qt.Friday), 
        lambda self,fill: self._setDayFill(QtCore.Qt.Friday,fill)
    )
    saturdayFill = QtCore.pyqtProperty(
        "QBrush",
        lambda self: self._dayFill(QtCore.Qt.Saturday), 
        lambda self,fill: self._setDayFill(QtCore.Qt.Saturday,fill)
    )

    sundayFG = QtCore.pyqtProperty(
        "QBrush",
        lambda self: self._dayFG(QtCore.Qt.Sunday), 
        lambda self,fill: self._setDayFG(QtCore.Qt.Sunday,fill)
    )
    mondayFG = QtCore.pyqtProperty(
        "QBrush",
        lambda self: self.__dayFG(QtCore.Qt.Monday), 
        lambda self,fill: self._setDayFG(QtCore.Qt.Monday,fill)
    )
    tuesdayFG = QtCore.pyqtProperty(
        "QBrush",
        lambda self: self._dayFG(QtCore.Qt.Tuesday), 
        lambda self,fill: self._setDayFG(QtCore.Qt.Tuesday,fill)
    )
    wednesdayFG = QtCore.pyqtProperty(
        "QBrush",
        lambda self: self._dayFG(QtCore.Qt.Wednesday), 
        lambda self,fill: self._setDayFG(QtCore.Qt.Wednesday,fill)
    )
    thursdayFG = QtCore.pyqtProperty(
        "QBrush",
        lambda self: self._dayFG(QtCore.Qt.Thursday), 
        lambda self,fill: self._setDayFG(QtCore.Qt.Thursday,fill)
    )
    fridayFG = QtCore.pyqtProperty(
        "QBrush",
        lambda self: self._dayFG(QtCore.Qt.Friday), 
        lambda self,fill: self._setDayFG(QtCore.Qt.Friday,fill)
    )
    saturdayFG = QtCore.pyqtProperty(
        "QBrush",
        lambda self: self._dayFG(QtCore.Qt.Saturday), 
        lambda self,fill: self._setDayFG(QtCore.Qt.Saturday,fill)
    )
    '''
    weekNFG=QtCore.pyqtProperty("QBrush", _weekNFG, _setWeekNFG)
    weekNFill=QtCore.pyqtProperty("QBrush", _weekNFill, _setWeekNFill)
    '''
    useCSS = QtCore.pyqtProperty("bool", useCSS, setUseCSS)
