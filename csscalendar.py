from PyQt4 import QtGui,QtCore

class CSSCalendar(QtGui.QCalendarWidget):
	"""A CalendarWidget that supports CSS theming"""
	def __init__(self, *args):
		QtGui.QCalendarWidget.__init__(self, *args)
		self.__useCSS=False

	def useCSS(self):
		return self.__useCSS

	def setUseCSS(self, css):
		self.__useCSS=css
		print(self.__useCSS)
		self.__updateAppearance()

	def __updateAppearance(self):
		children=self.findChildren (QtGui.QToolButton)
		if self.__useCSS:
			#explicitly set the arrow type of the next month
			#and previous month buttons
			children[0].setArrowType(QtCore.Qt.LeftArrow)
			children[1].setArrowType(QtCore.Qt.RightArrow)
		else:
			children[0].setArrowType(QtCore.Qt.NoArrow)
			children[1].setArrowType(QtCore.Qt.NoArrow)
			emptyFormat=QtGui.QTextCharFormat()
			wendFormat=QtGui.QTextCharFormat()
			wendFormat.setForeground(QtGui.QColor("red"))
			for i in range(1,8):
				if i <= 5:
					self.setWeekdayTextFormat(i,emptyFormat)
				else:
					self.setWeekdayTextFormat(i,wendFormat)
			self.setHeaderTextFormat(emptyFormat)

	def __setWeekNFill(self, fill):
		b=self.headerTextFormat()
		b.setBackground(fill)
		self.setHeaderTextFormat(b)

	def __setWeekNFG(self, fg):
		b=self.headerTextFormat()
		b.setForeground(fg)
		self.setHeaderTextFormat(b)

	def __setDayFG(self, day, fg):
		b=self.weekdayTextFormat(day)
		b.setForeground(fg)
		self.setWeekdayTextFormat(day,b)

	def __setDayFill(self, day, fill):
		b=self.weekdayTextFormat(day)
		b.setBackground(fill)
		self.setWeekdayTextFormat(day,b)

	def __dayFG(self, day):
		return self.weekdayTextFormat(day).foreground()

	def __dayFill(self, day):
		return self.weekdayTextFormat(day).background()

	def __weekNFill(self):
		return self.headerTextFormat().background()

	def __weekNFG(self):
		return self.headerTextFormat().foreground()

	sundayFill=QtCore.pyqtProperty("QBrush", \
		lambda self: self.__dayFill(QtCore.Qt.Sunday), \
		lambda self,fill: self.__setDayFill(QtCore.Qt.Sunday,fill))
	mondayFill=QtCore.pyqtProperty("QBrush", \
		lambda self: self.__dayFill(QtCore.Qt.Monday), \
		lambda self,fill: self.__setDayFill(QtCore.Qt.Monday,fill))
	tuesdayFill=QtCore.pyqtProperty("QBrush", \
		lambda self: self.__dayFill(QtCore.Qt.Tuesday), \
		lambda self,fill: self.__setDayFill(QtCore.Qt.Tuesday,fill))
	wednesdayFill=QtCore.pyqtProperty("QBrush", \
		lambda self: self.__dayFill(QtCore.Qt.Wednesday), \
		lambda self,fill: self.__setDayFill(QtCore.Qt.Wednesday,fill))
	thursdayFill=QtCore.pyqtProperty("QBrush", \
		lambda self: self.__dayFill(QtCore.Qt.Thursday), \
		lambda self,fill: self.__setDayFill(QtCore.Qt.Thursday,fill))
	fridayFill=QtCore.pyqtProperty("QBrush", \
		lambda self: self.__dayFill(QtCore.Qt.Friday), \
		lambda self,fill: self.__setDayFill(QtCore.Qt.Friday,fill))
	saturdayFill=QtCore.pyqtProperty("QBrush", \
		lambda self: self.__dayFill(QtCore.Qt.Saturday), \
		lambda self,fill: self.__setDayFill(QtCore.Qt.Saturday,fill))

	sundayFG=QtCore.pyqtProperty("QBrush", \
		lambda self: self.__dayFG(QtCore.Qt.Sunday), \
		lambda self,fill: self.__setDayFG(QtCore.Qt.Sunday,fill))
	mondayFG=QtCore.pyqtProperty("QBrush", \
		lambda self: self.__dayFG(QtCore.Qt.Monday), \
		lambda self,fill: self.__setDayFG(QtCore.Qt.Monday,fill))
	tuesdayFG=QtCore.pyqtProperty("QBrush", \
		lambda self: self.__dayFG(QtCore.Qt.Tuesday), \
		lambda self,fill: self.__setDayFG(QtCore.Qt.Tuesday,fill))
	wednesdayFG=QtCore.pyqtProperty("QBrush", \
		lambda self: self.__dayFG(QtCore.Qt.Wednesday), \
		lambda self,fill: self.__setDayFG(QtCore.Qt.Wednesday,fill))
	thursdayFG=QtCore.pyqtProperty("QBrush", \
		lambda self: self.__dayFG(QtCore.Qt.Thursday), \
		lambda self,fill: self.__setDayFG(QtCore.Qt.Thursday,fill))
	fridayFG=QtCore.pyqtProperty("QBrush", \
		lambda self: self.__dayFG(QtCore.Qt.Friday), \
		lambda self,fill: self.__setDayFG(QtCore.Qt.Friday,fill))
	saturdayFG=QtCore.pyqtProperty("QBrush", \
		lambda self: self.__dayFG(QtCore.Qt.Saturday), \
		lambda self,fill: self.__setDayFG(QtCore.Qt.Saturday,fill))

	weekNFG=QtCore.pyqtProperty("QBrush", __weekNFG, __setWeekNFG)
	weekNFill=QtCore.pyqtProperty("QBrush", __weekNFill, __setWeekNFill)

	useCSS=QtCore.pyqtProperty("bool", useCSS, setUseCSS)