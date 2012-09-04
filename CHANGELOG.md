09/04/2012
====
* Fix a typo in Observer class that prevented the date conversion from naive datetimes
* Allow date to be readable in config even without QSettings and move the app starting to a main() function

09/02/2012
====
* more safe joining of paths in chronosconfig

08/30/2012
====
* fix typo regarding observer property in chronostext.py

08/29/2012
====
* splash on so random timezone for the default 'baby'

07/02/2012
====
* the system's timezone
* Version bump
* Remove toPyObject() for tabgroup retrieval
* formatting in python 3.

06/30/2012
====
* Remove unneeded toString() calls in eventplanner.py
* skip over it
* More portability updates and removed some more toPyObject calls
* Add the portability changes from openastro's zonetab.py to this one

06/28/2012
====
* Add changelog generated from git commits
* Provide encoding in order to convert the css file to a string
* are coming from
* Since the planetary hour string is a native python string now, use .lower() instead of .toLower()

06/19/2012
====
* Forgot to remove the additional toPyObject here

06/17/2012
====
* Remove this cruft
* Initial Python3 port, seems to work pretty well

03/14/2012
====
* Remove unnecessary prints

02/14/2012
====
* Some tweaks to make the numerous dockwindows more managable if one is looking at multiple stuff

02/13/2012
====
* Forgot to do it to this one
* Delete the docks brought by the calendar, allow main dock widgets to be hidden
* verbump
* forgot this
* Fix 'hitbox' issues and dockify the layout

02/09/2012
====
* Add titles to house and aspectarian dialogs. Also set the window icon at the application level.
* Properly initialize the application name

02/08/2012
====
* forgot to switch the order around hupdup
* Just a slight tweak regarding icon lookup

02/07/2012
====
* Turn off the QT_GLIB thing specifically for this program
* Add closing clause to the wrapper class around QDialog to make sure this bug does not appear again

02/06/2012
====
* Do not close when last dialog is closed. May also help with KDE bug.
* Setting a parent for the calendar menu does seem to fix it...
* Progress is the same for both north and south node >>
* Added some stuff on the README

02/03/2012
====
* Make sure orbs are set for only natal data viewing and use a simpler check for the presence of a usable table

01/23/2012
====
* be sure to close schedule after writing it too
* Be sure to close file after outputting the data
* Allow overriding Qt Icon theme if it isn't automatically detected
* When getting sign data as text, DON'T increment by days. It's supposed to be hours
* Update sign saving and actually use datetimes to feed into text gathering thing
* Force non-native dialogs to fix crashing under non-DE environments. Hopefully there's a cleaner way to get around this...

01/22/2012
====
* Two fixes: incorrect detection of month on calendar row 5 and finally got rid of that annoying bug where it would freeze upon day change. Also, fixed committer info that was on laptop.
* Fix displaying systray message if libnotify isn't available

01/04/2012
====
* Don't accidentally make a tuple instead of a string when copying the sample schedule

11/29/2011
====
* Remove weird header thing that I accidentally pushed
* Don't assume current dir == app dir
* Don't assume current dir == app dir
* Don't need to pull app dir and ini dir due to prefix registration
* put executable flag back on
* forgot to remove that too
* Updating *.desktop files
* So many needed to be pushed updates DX

11/08/2011
====
* Polish the frack out of this

11/06/2011
====
* more fixes
* Quick fix
* More helpful tooltips and performance improvements

11/02/2011
====
* Fix a quick thing regarding grand crosses
* Woot, now with comparisons

11/01/2011
====
* Now the aspect detector is ready. Still can't do comparisons yet.

10/31/2011
====
* Make this far more efficient. Also, aspect grid toy

10/30/2011
====
* Hurp durp, needed to add dates for copied source stuff
* Whoops
* More fixes, also, putting local copy of zone.tab for non Linux users
* Shortcut shell files and some code cleanup
* Adding zonetab from openastro and working on natal information. For now, solar returns and lunar returns still are not on calendar.
* Quick fix

10/29/2011
====
* Quick fixes
* Quick fixes and starting on transits implementation
* Solar and lunar return function prototypes AND changed treeview to tableview for more sane editing
* Adding nodes, sign icons, and starting up on writing the super graphical representation

10/27/2011
====
* Remember to close swisseph
* Tweaked full moon methods a bit and added more precision
* Finished making precise method
* Get started on making the simplified formula more precise. Also, be more memory friendly.
* Thinking too hard w/moon phases

10/25/2011
====
* More code cleaning and a default file showing some examples
* Updating
* Clean this up
* Now we're going to use dateutil
* Finally switched this stuff to pyswisseph
* Note to self: find out how to get speed. Also remove random print statement
* Quick fix
* Fancy
* Fix this zodiac mess

10/24/2011
====
* Let's make this method Pythonic
* Remove this redundancy

10/23/2011
====
* Fix house of moment method...again
* Fix house of moment method...again
* Fix house of moment method
* Fix typo
* Commenting out the help button until it gets implemented
* Fix up desktop files a bit and got planetary hour trigger working

10/22/2011
====
* Updating API and trying to get this every planetary hour alarm working

10/20/2011
====
* Another quick fix
* Quick fixes

10/19/2011
====
* Qt4 port is official. Also, removing *.desktop that floated around.
* Forgot to add exec perms because of USB drive
* Added some more triggers and house of moment stuff. Also, checkboxes galore

10/17/2011
====
* Fixed slight bug with no directory to store the schedule in. Also, added special case *.desktop for Arch Linux.

10/14/2011
====
* Make sure schedule file is updated when row changes

10/13/2011
====
* Bugfix for closing settings dialog closing program when main window isn't open
* make these timeouts same time
* Why pass date if it's already in self?
* Finished writing event triggers

10/12/2011
====
* Sorting and icons ahoy\!

10/11/2011
====
* Qt4 port complete, placing it here to keep separate from normal program

10/03/2011
====
* Putting desktop file in Accessories section, and fixed README typo

10/02/2011
====
* typo
* typo
* typo
* Quick fix
* Mark this as executable
* Removing datetime dependency for now
* Updating README
* Adding platform independence, please test
* make this dst aware
* Moving screenshots
* Some more screenshots

10/01/2011
====
* Tooltips
* Give reasonable size to times list
* Fixed elevation issue
* Fixed a few issues
* cropped screenshots
* taking out random file
* replacing stuff here

