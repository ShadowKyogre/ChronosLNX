#!/usr/bin/env python

"""
geolocationwidget.py

A custom widget for specifying geographical locations.

Copyright (C) 2008 Nokia Corporation and/or its subsidiary(-ies).
Contact: Qt Software Information (qt-info@nokia.com)

This file is part of the documentation of Qt. It was originally
published as part of Qt Quarterly.

Commercial Usage
Licensees holding valid Qt Commercial licenses may use this file in
accordance with the Qt Commercial License Agreement provided with the
Software or, alternatively, in accordance with the terms contained in
a written agreement between you and Nokia.


GNU General Public License Usage
Alternatively, this file may be used under the terms of the GNU
General Public License versions 2.0 or 3.0 as published by the Free
Software Foundation and appearing in the file LICENSE.GPL included in
the packaging of this file.  Please review the following information
to ensure GNU General Public Licensing requirements will be met:
http://www.fsf.org/licensing/licenses/info/GPLv2.html and
http://www.gnu.org/copyleft/gpl.html.  In addition, as a special
exception, Nokia gives you certain additional rights. These rights
are described in the Nokia Qt GPL Exception version 1.3, included in
the file GPL_EXCEPTION.txt in this package.

Qt for Windows(R) Licensees
As a special exception, Nokia, as the sole copyright holder for Qt
Designer, grants users of the Qt/Eclipse Integration plug-in the
right for the Qt/Eclipse Integration to link to functionality
provided by Qt Designer and its related libraries.

If you are unsure which license is appropriate for your use, please
contact the sales department at qt-sales@nokia.com.
"""

from PyQt4.QtCore import Qt, pyqtProperty, pyqtSignature, SIGNAL
from PyQt4.QtGui import QDoubleSpinBox, QGridLayout, QLabel, QWidget


class GeoLocationWidget(QWidget):

    """GeoLocationWidget(QWidget)
    
    Provides a custom geographical location widget.
    """
    
    __pyqtSignals__ = ("latitudeChanged(double)", "longitudeChanged(double)")
    
    def __init__(self, parent = None):
    
        QWidget.__init__(self, parent)
        
        latitudeLabel = QLabel(self.tr("Latitude:"))
        self.latitudeSpinBox = QDoubleSpinBox()
        self.latitudeSpinBox.setRange(-90.0, 90.0)
        self.latitudeSpinBox.setDecimals(5)
        
        longitudeLabel = QLabel(self.tr("Longitude:"))
        self.longitudeSpinBox = QDoubleSpinBox()
        self.longitudeSpinBox.setRange(-180.0, 180.0)
        self.longitudeSpinBox.setDecimals(5)
        
        elevationLabel = QLabel(self.tr("Elevation"))
        self.elevationSpinBox = QDoubleSpinBox()
        self.elevationSpinBox.setRange(-418.0, 8850.0)
        self.elevationSpinBox.setDecimals(5)

        self.connect(self.latitudeSpinBox, SIGNAL("valueChanged(double)"),
                     self, SIGNAL("latitudeChanged(double)"))
        self.connect(self.longitudeSpinBox, SIGNAL("valueChanged(double)"),
                     self, SIGNAL("longitudeChanged(double)"))
        self.connect(self.elevationSpinBox, SIGNAL("valueChanged(double)"),
                     self, SIGNAL("elevationChanged(double)"))

        layout = QGridLayout(self)
        layout.addWidget(latitudeLabel, 0, 0)
        layout.addWidget(self.latitudeSpinBox, 0, 1)
        layout.addWidget(longitudeLabel, 1, 0)
        layout.addWidget(self.longitudeSpinBox, 1, 1)
        layout.addWidget(elevationLabel, 2, 0)
        layout.addWidget(self.elevationSpinBox, 2, 1)
    
    # The latitude property is implemented with the latitude() and setLatitude()
    # methods, and contains the latitude of the user.
    
    def latitude(self):
        return self.latitudeSpinBox.value()
    
    @pyqtSignature("setLatitude(double)")
    def setLatitude(self, latitude):
        if latitude != self.latitudeSpinBox.value():
            self.latitudeSpinBox.setValue(latitude)
            self.emit(SIGNAL("latitudeChanged(double)"), latitude)
    
    latitude = pyqtProperty("double", latitude, setLatitude)
    
    # The longitude property is implemented with the longitude() and setlongitude()
    # methods, and contains the longitude of the user.
    
    def longitude(self):
        return self.longitudeSpinBox.value()
    
    @pyqtSignature("setLongitude(double)")
    def setLongitude(self, longitude):
        if longitude != self.longitudeSpinBox.value():
            self.longitudeSpinBox.setValue(longitude)
            self.emit(SIGNAL("longitudeChanged(double)"), longitude)
    
    longitude = pyqtProperty("double", longitude, setLongitude)
    
    def elevation(self):
        return self.elevationSpinBox.value()

    @pyqtSignature("setElevation(double)")
    def setElevation(self, elevation):
        if elevation != self.elevationSpinBox.value():
            self.elevationSpinBox.setValue(elevation)
            self.emit(SIGNAL("elevationChanged(double)"), elevation)
    
    elevation = pyqtProperty("double", elevation, setElevation)