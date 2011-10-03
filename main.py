#!/usr/bin/env python
import os
import gtk
import gobject
import re
#from datetime import datetime, timedelta, date
import ephem
import ConfigParser
from astro import *
import datetimetz

class ChronosLNX:
	def __init__(self):
		self.now = datetimetz.now()
		self.load_config()
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.set_title("Chronos Linux")
		self.window.connect("delete-event", self.delete_event)
		self.window.set_border_width(15)
		self.window.set_icon_from_file(os.path.abspath("%s/planets/%s.png" %(os.sys.path[0],"chronoslnx")))
		self.window.set_resizable(False)
		self.make_menu()

		# Create a horizontal packing box to hold the three clock
		# |-----|--------|
		# | CAL | PLOCK  |
		# |     |--------|
		# | xx  |  HRS   |
		# |-----|--------|
		# value frames and add it to the window
		hbox1 = gtk.HBox(False, 2)
		vbox = gtk.VBox(False, 2)
		hbox2 = gtk.HBox(False, 2)
		clock_details = gtk.VBox(False, 2)
		self.clock_details = gtk.VBox(False, 2)
		settings_button = gtk.Button("Settings")
		#print_button = gtk.Button("Print Planetary Hours")
		#moon_button = gtk.Button("See Phases of the Moon")
		about_button = gtk.Button("About")
		about_button.connect('clicked', self.show_about)
		settings_button.connect('clicked', self.show_settings)
		
		self.pday = get_planet_day(int(self.now.strftime('%w')))
		self.prepare_hours()
		self.make_tree()
		
		index=self.grab_nearest_hour()
		self.hours_display.get_selection().select_path(index)
		self.phour = self.model[index][2]
		planets_string = "This is the day of %s, the hour of %s" %(self.pday, self.phour)
		sign_string="The sign of the month is %s" %(calculate_sign(self.now))
		moon_phase=grab_moon_phase(self.now)
		self.label = gtk.Label("%s\n%s\n%s\n%s" %(self.now.strftime("%H:%M:%S"), 
			sign_string, moon_phase, planets_string))
		sysicon=os.path.abspath("%s/planets/%s.png" %(os.sys.path[0],self.phour.lower()))
		self.image = gtk.image_new_from_pixbuf(gtk.gdk.pixbuf_new_from_file_at_size(sysicon, 64, 64))
		self.calendar = gtk.Calendar()
		self.calendar.connect("button-release-event", self.display_calendar_menu)
		self.window.add(hbox1)
		hbox1.add(vbox)
		hbox1.add(clock_details)
		hbox2.add(self.image)
		hbox2.add(self.label)
		clock_details.add(hbox2)
		clock_details.add(self.clock_details)
		vbox.add(self.calendar)
		vbox.add(settings_button)
		#vbox.add(print_button)
		#vbox.add(moon_button)
		vbox.add(about_button)

		# Make a single call to show everything we have assembled
		self.window.show_all()
		self.make_tray_icon()
		

		# Call the update function in one second (1000 milliseconds)
		gobject.timeout_add(1000, self.update)
		
		#gtk.quit_add(level, save_settings)
	def make_menu(self):
		self.menu = gtk.Menu()
		show_item = gtk.ImageMenuItem("_Show")
		settings_item = gtk.ImageMenuItem("S_ettings")
		quit_item = gtk.ImageMenuItem("_Quit")
		#show_item.set_image(gtk.image_new_from_icon_name("gtk-ok", size[0]))
		settings_item.set_image(gtk.image_new_from_icon_name("gnome-settings", gtk.ICON_SIZE_MENU))
		quit_item.set_image(gtk.image_new_from_icon_name("application-exit", gtk.ICON_SIZE_MENU))
		self.menu.append(show_item)
		self.menu.append(settings_item)
		self.menu.append(quit_item)
		self.menu.show_all()
		quit_item.connect("activate", self.quit_program)
		show_item.connect("activate", self.display_dialog)
		settings_item.connect("activate", self.show_settings)
		
		self.calendar_menu = gtk.Menu()
		moon_item = gtk.ImageMenuItem("_Moon Cycle for this date")
		hours_item = gtk.ImageMenuItem("_Planetary Hours for this date")
		constellation_item = gtk.ImageMenuItem("_Constellations for this date")
		moon_item.connect("activate", self.get_moon_timeline)
		hours_item.connect("activate", self.get_date_hours)
		constellation_item.connect("activate", self.get_constellations)
		self.calendar_menu.append(moon_item)
		self.calendar_menu.append(hours_item)
		self.calendar_menu.append(constellation_item)
		self.calendar_menu.show_all()

	def reset_calendar(self):
		self.calendar.select_month(self.now.month - 1, self.now.year)
		self.calendar.select_day(self.now.day)

	def make_date(self):
		selection=self.calendar.get_date()
		target_date=datetime.strptime("%s/%s/%s" %(selection[0], selection[1] + 1, selection[2]), "%Y/%m/%d").replace(tzinfo=LocalTimezone())
		return target_date

	def get_moon_timeline(self, widget):
		target_date=self.make_date()
		self.reset_calendar()
		prev_new=ephem.localtime(ephem.previous_new_moon(target_date))
		full=ephem.localtime(ephem.next_full_moon(target_date)).replace(tzinfo=LocalTimezone())
		new_m=ephem.localtime(ephem.next_new_moon(target_date)).replace(tzinfo=LocalTimezone())
		length = (new_m - prev_new) / 29
		model = gtk.ListStore(gtk.gdk.Pixbuf, gobject.TYPE_PYOBJECT, gobject.TYPE_STRING, gobject.TYPE_STRING)
		select_this = -1
		for i in range (0,30):
			cycling=prev_new + length * i
			if cycling.timetuple().tm_yday == target_date.timetuple().tm_yday:
				select_this = i
			state_line=grab_moon_phase(cycling)
			state=re.split(":",state_line)
			percent=re.split(" ",state[1])
			model.append([None, cycling, state[0], percent[1]])

		#size = gtk.icon_size_lookup(gtk.ICON_SIZE_MENU)

		scrolled = gtk.ScrolledWindow()
		scrolled.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
		scrolled.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC

		hours_window= gtk.Dialog("Moon phase cycle for %s" %(target_date.strftime("%Y/%m/%d")), None,
		    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
		hours_display = gtk.TreeView(model)
		times = gtk.TreeViewColumn('Time')
		
		cell = gtk.CellRendererText()
		times.pack_start(cell, False)
		times.set_cell_data_func(cell, self.get_time)
		
		hours_display.append_column(times)
		name = gtk.TreeViewColumn('Phase')

		cell = gtk.CellRendererText()
		name.pack_start(cell, False)
		name.add_attribute(cell, "text", 2)
		hours_display.append_column(name)

		detail = gtk.TreeViewColumn('Illumination')
		cell = gtk.CellRendererText()
		detail.pack_start(cell)
		detail.add_attribute(cell,"text", 3)
		hours_display.append_column(detail)

		hours_display.get_selection().select_path(select_this)

		scrolled.add(hours_display)
		hours_window.vbox.add(gtk.Label("Moon phase cycle for %s\n\
Please note that it doesn't show the exact\
 illumination if you selected today, which is %s" %(target_date.strftime("%Y/%m/%d"), self.now.strftime("%Y/%m/%d"))))
		hours_window.vbox.add(scrolled)
		hours_window.show_all()
		hours_window.run()
		hours_window.destroy()

	def load_config(self):
		if os.name == 'nt':
			config_file = os.path.expanduser("~/.chronoslnx/config.ini")
		else:
			try:
				from xdg import BaseDirectory
			except ImportError:
				config_file = os.path.expanduser("~/.config/chronoslnx/config.ini")
			else:
				config_file=BaseDirectory.load_first_config('chronoslnx/config.ini')
		self.config = ConfigParser.SafeConfigParser()
		self.config.read(config_file)
		if not self.config.has_option('Location', 'latitude'):
		      self.config.set('Location', 'latitude', '0.0')
		if not self.config.has_option('Location', 'longitude'):
		      self.config.set('Location', 'longitude', '0.0')
		if not self.config.has_option('Location', 'elevation'):
		      self.config.set('Location', 'elevation', '0.0')
		self.latitude=self.config.getfloat('Location', 'latitude')
		self.longitude=self.config.getfloat('Location', 'longitude')
		self.elevation=self.config.getfloat('Location', 'elevation')

	def get_constellations(self, widget):
		target_date=self.make_date()
		self.reset_calendar()
		constellations=get_ruling_constellations_for_date(target_date)
		model = gtk.ListStore(gtk.gdk.Pixbuf, gobject.TYPE_STRING, gobject.TYPE_STRING)
		size = gtk.icon_size_lookup(gtk.ICON_SIZE_MENU)
		for i in constellations:
			icon=os.path.abspath("%s/planets/%s.png" %(os.sys.path[0],i.lower()))
			pixbuf=gtk.gdk.pixbuf_new_from_file_at_size(icon, size[0], size[0])
			model.append([pixbuf, i, constellations[i][1]])
		scrolled = gtk.ScrolledWindow()
		scrolled.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
		scrolled.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC

		hours_window= gtk.Dialog("Specific Constellations for %s" %(target_date.strftime("%Y/%m/%d")), None,
		    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
		hours_display = gtk.TreeView(model)
		
		name = gtk.TreeViewColumn('Planet')

		cell = gtk.CellRendererPixbuf() #planet icon
		name.pack_start(cell, False)
		name.add_attribute(cell, "pixbuf", 0)

		cell = gtk.CellRendererText() #Planet Name
		name.pack_start(cell)
		name.add_attribute(cell,"text", 1)
		hours_display.append_column(name)

		times = gtk.TreeViewColumn('Constellation')
		cell = gtk.CellRendererText() #daylight
		times.pack_start(cell, False)
		times.add_attribute(cell,"text",2)
		hours_display.append_column(times)

		scrolled.add(hours_display)
		hours_window.vbox.add(gtk.Label("Ruling constellations for %s" %(target_date.strftime("%Y/%m/%d"))))
		hours_window.vbox.add(scrolled)
		hours_window.show_all()
		hours_window.run()
		hours_window.destroy()

	def get_date_hours(self, widget):
		target_date=self.make_date()
		self.reset_calendar()
		sunrise,sunset,next_sunrise=get_sunrise_and_sunset(target_date, self.latitude, self.longitude, self.elevation)
		pday = get_planet_day(int(target_date.strftime('%w')))
		planetary_hours = hours_for_day(target_date,self.latitude, self.longitude,self.elevation)
		size = gtk.icon_size_lookup(gtk.ICON_SIZE_MENU)
		model = gtk.ListStore(gtk.gdk.Pixbuf, gobject.TYPE_PYOBJECT, gobject.TYPE_STRING, gobject.TYPE_BOOLEAN)
		for i in range(0,24):
			icon=os.path.abspath("%s/planets/%s.png" %(os.sys.path[0],planetary_hours[i][1].lower()))
			pixbuf=gtk.gdk.pixbuf_new_from_file_at_size(icon, size[0], size[0])
			model.append([pixbuf, planetary_hours[i][0], planetary_hours[i][1], planetary_hours[i][2]])
		scrolled = gtk.ScrolledWindow()
		scrolled.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
		scrolled.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC

		hours_window= gtk.Dialog("Specific Hours for %s" %(target_date.strftime("%Y/%m/%d")), None,
		    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
		hours_display = gtk.TreeView(model)
		times = gtk.TreeViewColumn('Time')
		cell = gtk.CellRendererPixbuf() #daylight
		times.pack_start(cell, False)
		times.set_cell_data_func(cell, self.get_daylight)
		
		cell = gtk.CellRendererText()
		times.pack_start(cell, False)
		times.set_cell_data_func(cell, self.get_time)
		
		hours_display.append_column(times)
		name = gtk.TreeViewColumn('Planet')

		cell = gtk.CellRendererPixbuf() #planet icon
		name.pack_start(cell, False)
		name.add_attribute(cell, "pixbuf", 0)

		cell = gtk.CellRendererText() #Planet Name
		name.pack_start(cell)
		name.add_attribute(cell,"text", 2)
		hours_display.append_column(name)
		
		scrolled.add(hours_display)
		hours_window.vbox.add(gtk.Label("Sunrise begins at %s\nSunset begins at %s\nNext day begins at %s" %(sunrise.ctime(), sunset.ctime(), next_sunrise.ctime())))
		hours_window.vbox.add(scrolled)
		hours_window.show_all()
		hours_window.run()
		hours_window.destroy()

	def display_calendar_menu(self,widget,event):
		if event.button == 3:
			self.calendar_menu.popup(None, None, None, event.button, event.time)

	def make_tray_icon(self):
		self.status_icon = gtk.StatusIcon()
		sysicon=os.path.abspath("%s/planets/%s.png" %(os.sys.path[0],self.phour.lower()))
		self.status_icon.set_from_file(sysicon)
		self.status_icon.connect('activate', self.display_dialog)
		self.status_icon.connect('popup-menu', self.display_menu)
	
	def show_about(self,widget):
		about_window= gtk.AboutDialog()
		about_window.set_program_name("ChronosLNX")
		about_window.set_version("0.1")
		about_window.set_copyright("(c) ShadowKyogre")
		about_window.set_comments("A simple tool for checking planetary hours and the moon phase.")
		about_window.set_website("https://github.com/ShadowKyogre/ChronosLNX")
		icon=os.path.abspath("%s/planets/%s.png" %(os.sys.path[0],"chronoslnx"))
		pixbuf=gtk.gdk.pixbuf_new_from_file_at_size(icon, 64, 64)
		about_window.set_logo(pixbuf)
		about_window.run()
		about_window.destroy()
	
	def show_settings(self,widget):
		settings_window= gtk.Dialog("Settings", None,
		    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
		    (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
		      gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
		
		hbox=gtk.HBox(True)
		label=gtk.Label("Latitude")
		settings_window.lat_box=gtk.SpinButton(None,1.0,7)
		settings_window.lat_box.set_range(-90.00,90.00)
		settings_window.lat_box.set_value(self.latitude)
		settings_window.lat_box.set_increments(5.0,10.0)
		settings_window.lat_box.set_update_policy(gtk.UPDATE_IF_VALID)
		hbox.add(label)
		hbox.add(settings_window.lat_box)
		settings_window.vbox.add(hbox)
		
		hbox=gtk.HBox(True)
		label=gtk.Label("Longitude")
		settings_window.lon_box=gtk.SpinButton(None,1.0,7)
		settings_window.lon_box.set_range(-180.00,180.00)
		settings_window.lon_box.set_value(self.longitude)
		settings_window.lon_box.set_increments(5.0,15.0)
		settings_window.lon_box.set_update_policy(gtk.UPDATE_IF_VALID)
		hbox.add(label)
		hbox.add(settings_window.lon_box)
		settings_window.vbox.add(hbox)
		
		hbox=gtk.HBox(True)
		label=gtk.Label("Elevation")
		settings_window.elv_box=gtk.SpinButton(None,1.0,7)
		settings_window.elv_box.set_range(-418.0,8850.00)
		settings_window.elv_box.set_value(self.elevation)
		settings_window.elv_box.set_increments(10.0,20.0)
		settings_window.elv_box.set_update_policy(gtk.UPDATE_IF_VALID)
		hbox.add(label)
		hbox.add(settings_window.elv_box)
		settings_window.vbox.add(hbox)
		
		tooltips = gtk.Tooltips()
		tooltips.set_tip(settings_window.lat_box, "Negative indicates south.\nMust be between -90 and 90 inclusive.")
		tooltips.set_tip(settings_window.lon_box,"Negative indicates west.\nMust be between -180 and 180 inclusive.")
		tooltips.set_tip(settings_window.elv_box,"Negative indicates below sea level.\nMust be between -418 and 8850 inclusive, in meters.")
		
		settings_window.connect('response', self.settings_change)
		settings_window.show_all()
		settings_window.run()

	def prepare_hours(self):
		self.sunrise,self.sunset,self.next_sunrise=get_sunrise_and_sunset(self.now, self.latitude, self.longitude, self.elevation)
		self.pday = get_planet_day(int(self.now.strftime('%w')))
		if self.now < self.sunrise:
			planetary_hours = hours_for_day(self.now-timedelta(days=1),self.latitude, self.longitude,self.elevation)
		else:
			planetary_hours = hours_for_day(self.now,self.latitude, self.longitude,self.elevation)
		size = gtk.icon_size_lookup(gtk.ICON_SIZE_MENU)
		if not hasattr(self, 'model'):
			self.model = gtk.ListStore(gtk.gdk.Pixbuf, gobject.TYPE_PYOBJECT, gobject.TYPE_STRING, gobject.TYPE_BOOLEAN)
		for i in range(0,24):
			icon=os.path.abspath("%s/planets/%s.png" %(os.sys.path[0],planetary_hours[i][1].lower()))
			pixbuf=gtk.gdk.pixbuf_new_from_file_at_size(icon, size[0], size[0])
			self.model.append([pixbuf, planetary_hours[i][0], planetary_hours[i][1], planetary_hours[i][2]])
	
	def get_daylight(self, column, cell_renderer,model, iter):
		size = gtk.icon_size_lookup(gtk.ICON_SIZE_MENU)
		if model.get_value(iter, 3) == True:
			icon=os.path.abspath("%s/planets/%s.png" %(os.sys.path[0],"day"))
			pyobj2=gtk.gdk.pixbuf_new_from_file_at_size(icon, size[0], size[0])
			cell_renderer.set_property('pixbuf', pyobj2)
		else:
			icon=os.path.abspath("%s/planets/%s.png" %(os.sys.path[0],"night"))
			pyobj2=gtk.gdk.pixbuf_new_from_file_at_size(icon, size[0], size[0])
			cell_renderer.set_property('pixbuf', pyobj2)
		return
	
	def get_time (self, column, cell_renderer, model, iter):
		pyobj = model.get_value(iter, 1)
		cell_renderer.set_property('text', pyobj.strftime("%Y/%m/%d %H:%M:%S"))
		return

	def make_tree(self):
		scrolled = gtk.ScrolledWindow()
		scrolled.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
		scrolled.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC
		
		self.modelfilter = self.model.filter_new()
		self.modelfilter.set_visible_func(self.search_hours)
		
		self.combo_filter = gtk.combo_box_new_text()
		self.combo_filter.append_text("Sun")
		self.combo_filter.append_text("Venus")
		self.combo_filter.append_text("Mercury")
		self.combo_filter.append_text("Moon")
		self.combo_filter.append_text("Saturn")
		self.combo_filter.append_text("Jupiter")
		self.combo_filter.append_text("Mars")
		self.combo_filter.connect('changed', self.force_search)
		
		self.hours_display = gtk.TreeView(self.model)

		times = gtk.TreeViewColumn('Time')
		cell = gtk.CellRendererPixbuf() #daylight
		times.pack_start(cell, False)
		times.set_cell_data_func(cell, self.get_daylight)
		
		cell = gtk.CellRendererText()
		times.pack_start(cell, False)
		times.set_cell_data_func(cell, self.get_time)
		
		self.hours_display.append_column(times)

		name = gtk.TreeViewColumn('Planet')

		cell = gtk.CellRendererPixbuf() #planet icon
		name.pack_start(cell, False)
		name.add_attribute(cell, "pixbuf", 0)
		#name.set_cell_data_func(cell, self.get_daylight)

		cell = gtk.CellRendererText() #Planet Name
		name.pack_start(cell)
		name.add_attribute(cell,"text", 2)

		self.hours_display.append_column(name)
		self.hours_display.set_size_request(100, 150)
		
		scrolled.add(self.hours_display)
		self.clock_details.add(gtk.Label("Pick a planet to view specific hours for."))
		self.clock_details.add(self.combo_filter)
		self.clock_details.add(scrolled)

		#note: the print hours function allows one to view hours for different dates
		#another note: the button for the
	
	def force_search(self, widget):
		scrolled = gtk.ScrolledWindow()
		scrolled.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
		scrolled.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC
		hours_window= gtk.Dialog("Specific Hours for %s" %(self.combo_filter.get_active_text()), None,
		    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
		self.modelfilter.refilter()
		hours_display = gtk.TreeView(self.modelfilter)
		times = gtk.TreeViewColumn('Time')
		cell = gtk.CellRendererPixbuf() #daylight
		times.pack_start(cell, False)
		times.set_cell_data_func(cell, self.get_daylight)
		
		cell = gtk.CellRendererText()
		times.pack_start(cell, False)
		times.set_cell_data_func(cell, self.get_time)
		
		hours_display.append_column(times)
		name = gtk.TreeViewColumn('Planet')

		cell = gtk.CellRendererPixbuf() #planet icon
		name.pack_start(cell, False)
		name.add_attribute(cell, "pixbuf", 0)

		cell = gtk.CellRendererText() #Planet Name
		name.pack_start(cell)
		name.add_attribute(cell,"text", 2)
		hours_display.append_column(name)
		
		scrolled.add(hours_display)
		hours_window.vbox.add(scrolled)
		hours_window.show_all()
		hours_window.run()
		hours_window.destroy()

	def search_hours(self, tree, iter):
		search_term = self.combo_filter.get_active_text()
		if search_term == None:
			return False
		if self.model.get_value(iter, 2) == search_term:
			return True
		else:
			return False

	def update_hours(self):
		self.model.clear()
		self.prepare_hours()

	def quit_program (self, widget):
	    gtk.main_quit()

	def delete_event(self,window,event):
		#http://www.jezra.net/blog/minimizeclose_to_system_tray_in_Python_GTK
		self.window.hide_on_delete()
		return True

	def display_menu(self,status, button, activate_time):
		#self.menu.popup(None, None, gtk.status_icon_position_menu, button, activate_time)
		self.menu.popup(None, None, None, button, activate_time)

	def display_dialog(self,status):
		if status == self.status_icon:
			if not self.window.get_property('visible'):
				self.window.present()
			else:
				self.window.hide()
		else:
			self.window.present()
	
	def settings_change(self, widget, response_id):
		if response_id == gtk.RESPONSE_ACCEPT:
			self.config.set('Location', 'latitude', str(widget.lat_box.get_value()))
			self.config.set('Location', 'longitude', str(widget.lon_box.get_value()))
			self.config.set('Location', 'elevation', str(widget.elv_box.get_value()))
			self.config.write(open(BaseDirectory.load_first_config('chronoslnx/config.ini'), 'w'))
			self.latitude=self.config.getfloat('Location', 'latitude')
			self.longitude=self.config.getfloat('Location', 'longitude')
			self.elevation=self.config.getfloat('Location', 'elevation')
			self.update_hours()
		if response_id == gtk.RESPONSE_REJECT:
			widget.destroy()
	
	# This routine is called when the timer goes off. We use it to
	# find out the time and update the clock display

	def update(self):
		self.now = datetimetz.now()
		if self.now > self.next_sunrise:
			self.update_hours()
		index=self.grab_nearest_hour()
		self.hours_display.get_selection().select_path(index)
		self.phour = self.model[index][2]
		planets_string = "This is the day of %s, the hour of %s" %(self.pday, self.phour)
		moon_phase=grab_moon_phase(self.now)
		sign_string="The sign of the month is %s" %(calculate_sign(self.now))
		self.label.set_text("%s\n%s\n%s\n%s" %(self.now.strftime("%H:%M:%S"), 
			sign_string, moon_phase, planets_string))
		self.status_icon.set_tooltip("%s - %s\n%s\n%s\n%s" %(self.now.strftime("%Y/%m/%d"), self.now.strftime("%H:%M:%S"), 
			sign_string, moon_phase, planets_string))
		sysicon=os.path.abspath("%s/planets/%s.png" %(os.sys.path[0],self.phour.lower()))
		self.status_icon.set_from_file(sysicon)
		self.image.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file_at_size(sysicon, 64, 64))
		return True

	def grab_nearest_hour(self):
		for i in range(0,24):
			if i+1 > 23:
				break
			if self.model[i][1] <= self.now and self.model[i+1][1] > self.now:
				return i
		return -1

if __name__ == "__main__":
	ChronosLNX()
	gtk.main()
