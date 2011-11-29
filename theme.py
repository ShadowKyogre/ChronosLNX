from PyQt4 import QtGui,QtCore

def parseBG(themecfg):
	themecfg.beginGroup("bg")
	bg_type=str(themecfg.value("type").toString())
	fill=QtGui.QBrush()
	if bg_type == "radial":
		fill=QtGui.QRadialGradient()
		print list(themecfg.childKeys())
		x=themecfg.value("start/x").toDouble()[0]
		y=themecfg.value("start/y").toDouble()[0]
		ex=themecfg.value("end/x").toDouble()[0]
		ey=themecfg.value("end/y").toDouble()[0]
		length=themecfg.value("length").toDouble()[0]
		fill.setSpread(themecfg.value("spread").toInt()[0])
		fill.setCenter(x,y)
		fill.setFocalPoint(ex,ey)
		fill.setRadius(length)
		stuff=themecfg.beginReadArray("colors")
		for i in xrange(stuff):
			themecfg.setArrayIndex(i)
			pos=themecfg.value("pos").toInt()[0]
			col=QtGui.QColor(themecfg.value("value").toString())
			fill.setColorAt(pos,col)
		themecfg.endArray()
	elif bg_type == "conical":
		fill=QtGui.QConicalGradient()
		x=themecfg.value("start/x").toDouble()[0]
		y=themecfg.value("start/y").toDouble()[0]
		length=themecfg.value("length").toDouble()[0]
		fill.setSpread(themecfg.value("spread").toInt()[0])
		fill.setCenter(x,y)
		fill.setAngle(length)
		stuff=themecfg.beginReadArray("colors")
		for i in xrange(stuff):
			themecfg.setArrayIndex(i)
			pos=themecfg.value("pos").toInt()[0]
			col=QtGui.QColor(themecfg.value("value").toString())
			fill.setColorAt(pos,col)
		themecfg.endArray()
	elif bg_type == "linear":
		fill=QtGui.QLinearGradient()
		x=themecfg.value("start/x").toDouble()[0]
		y=themecfg.value("start/y").toDouble()[0]
		ex=themecfg.value("end/x").toDouble()[0]
		ey=themecfg.value("end/y").toDouble()[0]
		fill.setSpread(themecfg.value("spread").toInt()[0])
		fill.setStart(x,y)
		fill.setFinalStop(ex,ey)
		stuff=themecfg.beginReadArray("colors")
		for i in xrange(stuff):
			themecfg.setArrayIndex(i)
			pos=themecfg.value("pos").toInt()[0]
			col=QtGui.QColor(themecfg.value("value").toString())
			fill.setColorAt(pos,col)
		themecfg.endArray()
	elif bg_type == "flat":
		fill=QtGui.QColor(themecfg.value("bg/color").toString())
	themecfg.endGroup()
	return fill

class ClockTheme:
	def __init__(self):
		self.outer={}
		self.inner={}
		self.aspects={}

		themecfg=QtCore.QSettings("skin:wheel.ini", QtCore.QSettings.IniFormat)
		themecfg.beginGroup("Current Planets")
		self.__parseCircle(self.outer,themecfg)
		themecfg.endGroup()
		themecfg.beginGroup("Natal Planets")
		self.__parseCircle(self.inner,themecfg)
		themecfg.endGroup()
		themecfg.beginGroup("Aspects")
		for i in themecfg.childKeys():
			self.aspects[str(i)]=QtGui.QColor(themecfg.value(i).toString())
		themecfg.endGroup()

	def __parseCircle(self, circle, themecfg):
		circle['pen']=QtGui.QColor(themecfg.value("outline").toString())
		circle['houses']=QtGui.QColor(themecfg.value("houses").toString())
		circle['fill']=parseBG(themecfg)
