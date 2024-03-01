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
- four slots for periodical custom messagges (just modify the files in the script folder; they accept both plain text or rich text; see the sample files); can execute programs double clicking with the left mouse button or the middle mouse button. 
- two slots for custom widgets in the dock, left and right
- systemtray icons support
- integrated clipboard (text and images)
- closing applications by right mouse clicking on its icon
- closing and restarting this program by right mouse clicking
- can play sounds when a window opens or closes
- experimental, initial support for audio: the main volume can be changed; left mouse click to show a popup; central mouse click to toggle mute/unmute; if a microphone is enabled, an icon is shown (its name will be shown in the tooltip); these options must be enabled in the config file; 
- customizations in the cfg_dock file.

In the image below from the left: the dock with the virtual desktops, one application launcher, the tasklist with two programs in it and two messages.
![My image](https://github.com/frank038/qt5simpledock/blob/main/screenshot.png)
