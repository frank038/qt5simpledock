# qt5simpledock
A simple dock.

Free to use and modify.

This program needs:
- python3
- pyqt5
- python3-xlib
- python3-ewmh.


Features:
- application menu (can add or modify application entries; bookmarks; search functionality)
- clock/calendar (can read an ics file; can launch an external program for adding/modifying events by double clicking in a day cell, or even event)
- virtual desktops (if supported by the window manager)
- application launchers (using the contextual menu, applications can be pinned and unpinned - a valid desktop file is required; the file delete_me in the folder 'applications' needs to be deleted before using this program)
- task list with icon support and application comment while hovering on it
- three slots for periodical custom messagges (just modify the files in the script folder; they accept both plain text or rich text; see the sample files); can execute programs double clicking with the left mouse button or the right mouse button. 
- systemtray icons support
- closing applications by right mouse clicking on its icon
- closing and restarting this program by right mouse clicking
- customizations in the cfg_dock file.

In the image below from the left: the dock with the virtual desktops, one application launcher, the tasklist with two programs in it and two messages.
![My image](https://github.com/frank038/qt5simpledock/blob/main/screenshot.png)
