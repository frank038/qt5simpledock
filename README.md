# qt5simpledock
A simple dock.

Free to use and modify.

This application is a panel with a lot of features.

This program needs:
- python3
- pyqt5
- python3-xlib
- python3-xdg
- pyqt5-multimedia (optional) or aplay (optional).


Features:
- application menu (can add or modify application entries; bookmarks; search functionality; custom button with menu; system buttons)
- clock/calendar (can read an ics file; can launch an external program for adding/modifying events by double clicking in a day cell, or in a shown event; in the form: PROGRAM yyyymmdd)
- clock: can be setted a timer for one alarm for the day (right click on the time, also for deleting it); the alarm event is stored in a file for future use; delete the alarm the same way
- virtual desktops (if supported by the window manager)
- application launchers (using the contextual menu of each menu item entry, applications can be pinned and unpinned - a valid desktop file is required; the file delete_me in the folder 'applications' needs to be deleted before using this program)
- task list with icon support and application comment while hovering on it
- four slots for periodical custom messagges (just modify the files in the script folder; they accept both plain text or rich text; see the sample files); can execute programs by double clicking with the left mouse button or single click with the middle mouse button. 
- two slots for custom widgets in the dock, left and right
- systemtray icons support
- integrated clipboard (text and images)
- closing applications by right mouse clicking on its icon
- closing and restarting this program by right mouse clicking
- can play sounds when a window opens or closes
- experimental support for volume: the main volume can be changed; left mouse click to show a popup; central mouse click to toggle mute/unmute; right click to show the output devices: can be switched to select the proper output device (e.g. from speakers to headset and viceversa); option in the config file
- experimental support for microphones: if enabled, an icon is shown; right click to show a dialot containing the attached microphones to the computer; they can be disabled/enabled by the user; option in the config file
- notification manager for my program qt5notification; notifications can be disabled and re-enabled at any time
- customizations and options in the cfg_dock file.

In the image below from the left: the dock with the virtual desktops, one application launcher, the tasklist with two programs in it and two messages. (The following picture is a very old image of the dock)
![My image](https://github.com/frank038/qt5simpledock/blob/main/screenshot.png)
