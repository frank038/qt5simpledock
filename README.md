# qt5simpledock
A simple dock.
 V. 0.9.2

Free to use and modify.

Works fine with Xfwm4 and Openbox.

This program needs:
- python3
- pyqt5
- python3-xlib
- python3-ewmh
- optional xdotool for some window managers that need a different way in iconifying.

Features:
- virtual desktops
- application launchers (using the contextual menu, applications can be pinned and unpinned - a valid desktop file is required; the file delete_me in the folder 'applications' needs to be deleted before using this program)
- task list with icon support and application comment while hovering on it
- two slots for periodical custom messagges (just modify the files in the script folder; they accept both plain text or rich text; see the sample files)
- systemtray icons support
- closing applications by right mouse clicking on its icon
- closing and restarting this program by right mouse clicking
- customizations in the cfg_dock file
- this program can be used with a compositor for enabling rounded corners and transparency.

In the image below from the left: the dock with the virtual desktops, one application launcher, the tasklist with two programs in it and two messages.
![My image](https://github.com/frank038/qt5simpledock/blob/main/screenshot.png)

In this image: with_compositor and with_transparency options both enabled; with_transparency option enabled only. A compositor is required for rounded corners and transparency.

![My image](https://github.com/frank038/qt5simpledock/blob/main/screenshot1.png)
