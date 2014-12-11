#!/usr/bin/python
from PyQt4 import QtCore,QtGui
from .astro_rewrite import *
##Custom Widgets for both normal and planetary sensitive data

class PlanetDateEditor(QtGui.QWidget):
	def __init__(self, parent = None):
		super().__init__(parent)
		inputstuff=QtGui.QGridLayout(self)
		self.day=QtGui.QComboBox(self)
		self.day.addItem("Sun")
		self.day.addItem("Moon")
		self.day.addItem("Mars")
		self.day.addItem("Mercury")
		self.day.addItem("Jupiter")
		self.day.addItem("Venus")
		self.day.addItem("Saturn")
		self.day.addItem("Everyday")
		self.day.addItem("Weekends")
		self.day.addItem("Weekdays")
		self.day.addItem("Custom")
		inputstuff.addWidget(self.day,0,0)

		self.dateplanned=QtGui.QDateEdit(self)
		#self.dateplanned.setCalendarPopup (True)
		self.dateplanned.setDisplayFormat("MM/dd/yyyy")
		self.dateplanned.hide()
		inputstuff.addWidget(self.dateplanned,0,1)
		self.day.activated.connect(self.checkSwitch)
		inputstuff.setContentsMargins(0, 0, 0, 0)
		inputstuff.setHorizontalSpacing(0)

#http://developer.qt.nokia.com/faq/answer/how_can_i_make_a_qcombobox_have_multiple_selection

	def checkSwitch(self,idx):
		if idx==10:
			self.dateplanned.show()
		else:
			self.dateplanned.hide()

	def curDate(self):
		return self.dateplanned.date()

	def setDate(self,date):
		self.dateplanned.setDate(date)

	def text(self):
		return self.day.currentText()

	def setText(self,text):
		self.day.setCurrentIndex(self.day.findText(text))

class PlanetHourEditor(QtGui.QWidget):
	def __init__(self, parent = None):
		super().__init__(parent)
		inputstuff=QtGui.QGridLayout(self)
		self.time=QtGui.QComboBox(self)
		self.time.addItem("Sun")
		self.time.addItem("Moon")
		self.time.addItem("Mars")
		self.time.addItem("Mercury")
		self.time.addItem("Jupiter")
		self.time.addItem("Venus")
		self.time.addItem("Saturn")
		self.time.addItem("Every planetary hour")
		self.time.addItem("Every normal hour")
		self.time.addItem("When the the sun rises")
		self.time.addItem("When the the sun sets")
		self.time.addItem("Custom")
		inputstuff.addWidget(self.time,0,0)
		self.timeplanned=QtGui.QTimeEdit(self)
		self.timeplanned.setDisplayFormat("HH:mm")
		self.timeplanned.hide()
		inputstuff.addWidget(self.timeplanned,0,1)
		self.time.activated.connect(self.checkSwitch)
		inputstuff.setContentsMargins(0, 0, 0, 0)
		inputstuff.setHorizontalSpacing(0)

	def checkSwitch(self,idx):
		if idx==11:
			self.timeplanned.show()
		else:
			self.timeplanned.hide()

	def curTime(self):
		return self.timeplanned.time()

	def setTime(self,time):
		self.timeplanned.setTime(time)

	def text(self):
		return self.time.currentText()

	def setText(self,text):
		self.time.setCurrentIndex(self.time.findText(text))

##Delegates to place the needed widgets in

class EventTypeEditorDelegate(QtGui.QStyledItemDelegate):
	def createEditor(self, parent, option, index):
		event_type=QtGui.QComboBox(parent)
		event_type.addItem("Textual reminder")
		event_type.addItem("Save to file")
		event_type.addItem("Command")
		return event_type

	def setEditorData(self, editor, index):
		value = index.model().data(index, QtCore.Qt.EditRole)
		editor.setCurrentIndex(editor.findText(value))

	def setModelData(self, editor, model, index):
		model.setData(index, editor.currentText(), QtCore.Qt.EditRole)

	def updateEditorGeometry(self, editor, option, index):
		editor.setGeometry(option.rect)

class EventParamEditorDelegate(QtGui.QStyledItemDelegate):
	def createEditor(self, parent, option, index):
		didx=index.model().index(index.row(),index.column()-1)
		event_type=index.model().data(didx, QtCore.Qt.EditRole)
		if (event_type=="Save to file"):
			combo=QtGui.QComboBox(parent)
			combo.addItem("All")
			combo.addItem("Planetary Hours")
			combo.addItem("Planetary Signs")
			combo.addItem("Moon Cycle")
			return combo
		else:
			return QtGui.QLineEdit(parent)

	def setEditorData(self, editor, index):
		value = index.model().data(index, QtCore.Qt.EditRole)
		if isinstance(editor,QtGui.QComboBox):
			editor.setCurrentIndex(editor.findText(value))
		else:
			editor.insert(value)

	def setModelData(self, editor, model, index):
		if isinstance(editor,QtGui.QComboBox):
			model.setData(index, editor.currentText(), QtCore.Qt.EditRole)
		else:
			model.setData(index, editor.text(), QtCore.Qt.EditRole)

	def updateEditorGeometry(self, editor, option, index):
		editor.setGeometry(option.rect)

class TriggerEditorDelegate(QtGui.QStyledItemDelegate):
	def createEditor(self, parent, option, index):
		p=TriggerEditor(parent)
		p.setAutoFillBackground(True)
		return p

	def setEditorData(self, editor, index):
		value = index.model().data(index, QtCore.Qt.UserRole)
		if isinstance(value, QtCore.QDate):
			editor.setText("Custom")
			editor.setDate(value)
			editor.dateplanned.show()
		else:
			editor.setText(value)

	def setModelData(self, editor, model, index):
		if not editor.dateplanned.isHidden():
				model.setData(index, editor.curDate(), QtCore.Qt.UserRole)
				model.setData(index, editor.curDate().toString("MM/dd/yyyy"), QtCore.Qt.EditRole)
		else:
				model.setData(index, editor.text(), QtCore.Qt.UserRole)
				model.setData(index, editor.text(), QtCore.Qt.EditRole)

	def updateEditorGeometry(self, editor, option, index):
		editor.setGeometry(option.rect)

class DateEditorDelegate(QtGui.QStyledItemDelegate):
	def createEditor(self, parent, option, index):
		p=PlanetDateEditor(parent)
		p.setAutoFillBackground(True)
		return p

	def setEditorData(self, editor, index):
		value = index.model().data(index, QtCore.Qt.UserRole)
		if isinstance(value, QtCore.QDate):
			editor.setText("Custom")
			editor.setDate(value)
			editor.dateplanned.show()
		else:
			editor.setText(value)

	def setModelData(self, editor, model, index):
		if not editor.dateplanned.isHidden():
				model.setData(index, editor.curDate(), QtCore.Qt.UserRole)
				model.setData(index, editor.curDate().toString("MM/dd/yyyy"), QtCore.Qt.EditRole)
		else:
				model.setData(index, editor.text(), QtCore.Qt.UserRole)
				model.setData(index, editor.text(), QtCore.Qt.EditRole)

	def updateEditorGeometry(self, editor, option, index):
		editor.setGeometry(option.rect)

class TimeEditorDelegate(QtGui.QStyledItemDelegate):
	def createEditor(self, parent, option, index):
		return PlanetHourEditor(parent)

	def setEditorData(self, editor, index):
		value = index.model().data(index, QtCore.Qt.UserRole)
		if isinstance(value, QtCore.QTime):
			editor.setText("Custom")
			editor.setTime(value)
			editor.timeplanned.show()
		else:
			editor.setText(value)

	def setModelData(self, editor, model, index):
		if not editor.timeplanned.isHidden():
			model.setData(index, editor.curTime(), QtCore.Qt.UserRole)
			model.setData(index, editor.curTime().toString("HH:mm"), QtCore.Qt.EditRole)
		else:
			model.setData(index, editor.text(), QtCore.Qt.UserRole)
			model.setData(index, editor.text(), QtCore.Qt.EditRole)

	def updateEditorGeometry(self, editor, option, index):
		editor.setGeometry(option.rect)

##The convenience treeview which automagically searches for the appropriate date

class DayEventsModel(QtGui.QSortFilterProxyModel):
	def __init__(self, *args):
		super().__init__(*args)
		self.date=None
		self.wday=None
		self.exact_day_type=None

	def filterAcceptsRow(self,sourceRow,sourceParent):
		if self.date == None:
			return True
		index1=self.sourceModel().index(sourceRow,1)
		data=self.sourceModel().data(index1, QtCore.Qt.UserRole)
		if isinstance(data, QtCore.QDate):
			return data.toPyDate() == self.date
		else:
			data=self.sourceModel().data(index1, QtCore.Qt.EditRole)
			if data == "Everyday":
				return True
			elif data == "Weekends":
				return self.wday == 0 or self.wday == 6
			elif data == "Weekdays":
				return 1 <= self.wday <= 5
			else:
				return data == self.exact_day_type

	def setDate(self,date):
		self.date=date
		self.wday=int(date.strftime('%w'))
		self.exact_day_type=get_planet_day(self.wday)
		self.invalidateFilter()

class EventsList(QtGui.QWidget):
	def __init__(self, *args):
		super().__init__(*args)

		a_vbox=QtGui.QVBoxLayout(self)
		editbuttons=QtGui.QHBoxLayout()

		newbutton=QtGui.QPushButton("New",self)
		newbutton.clicked.connect(self.add)

		deletebutton=QtGui.QPushButton("Delete",self)
		deletebutton.clicked.connect(self.delete)

		enablebutton=QtGui.QPushButton("Enable All", self)
		enablebutton.clicked.connect(lambda: self.toggleAll(True))

		disablebutton=QtGui.QPushButton("Disable All", self)
		disablebutton.clicked.connect(lambda: self.toggleAll(False))

		editbuttons.addWidget(newbutton)
		editbuttons.addWidget(deletebutton)
		editbuttons.addWidget(enablebutton)
		editbuttons.addWidget(disablebutton)

		a_vbox.addLayout(editbuttons)

		self.tree=QtGui.QTableView(self)
		self.tree.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

		dateeditor=DateEditorDelegate(self.tree)
		timeeditor=TimeEditorDelegate(self.tree)
		eventtypeeditor=EventTypeEditorDelegate(self.tree)
		eventparameditor=EventParamEditorDelegate(self.tree)

		self.tree.setSortingEnabled(True)

		self.tree.setItemDelegateForColumn(1,dateeditor)
		self.tree.setItemDelegateForColumn(2,timeeditor)
		self.tree.setItemDelegateForColumn(3,eventtypeeditor)
		self.tree.setItemDelegateForColumn(4,eventparameditor)
		a_vbox.addWidget(self.tree)

	def toggleAll(self, value=None):
		for i in range(self.tree.model().rowCount()):
			idx = self.tree.model().index(i,0)
			if value:
				self.tree.model().setData(idx, QtCore.Qt.Checked, QtCore.Qt.CheckStateRole)
			elif value is not None:
				self.tree.model().setData(idx, QtCore.Qt.Unchecked, QtCore.Qt.CheckStateRole)
			else:
				if item.checkState() == QtCore.Checked:
					self.tree.model().setData(idx, QtCore.Qt.Unchecked, QtCore.Qt.CheckStateRole)
				else:
					self.tree.model().setData(idx, QtCore.Qt.Checked, QtCore.Qt.CheckStateRole)

	def add(self):
		item=QtGui.QStandardItem()
		item.setCheckable(True)
		item.setEditable(False)
		item2=QtGui.QStandardItem("Everyday")
		item3=QtGui.QStandardItem("Sun")
		item4=QtGui.QStandardItem("Textual reminder")
		item5=QtGui.QStandardItem("This is filler text")

		if isinstance(self.tree.model(), DayEventsModel):
			self.tree.model().sourceModel().appendRow([item,item2,item3,item4,item5])
			self.tree.model().invalidateFilter()
		else:
			self.tree.model().appendRow([item,item2,item3,item4,item5])

	def delete(self):
		item=self.tree.currentIndex()
		if isinstance(self.tree.model(), DayEventsModel):
			trueitem=self.tree.model().mapToSource(item)
			self.tree.model().sourceModel().takeRow(trueitem.row())
			self.tree.model().invalidateFilter()
		else:
			self.tree.model().takeRow(item.row())
