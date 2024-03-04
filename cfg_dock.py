# the height of the dock
dock_height=42
# icon button max size to get from application (even number)
button_size=40
# program launchers button size
pbutton_size=30
# padding - space between button and icon (size icon: button_size - button_padding)
button_padding=2
# show virtual desktops: 0 no - 1 yes
virtual_desktops=0
# use the builtin tray: 0 no - 1 yes
use_tray=1
# tray icon size (even number)
tbutton_size = dock_height-2
# position: 0 top - 1 bottom
dock_position=1
# tasklist position: 0 left - 1 center
tasklist_position=0
# theme style: "" to use the default theme
theme_style=""
# icon theme: "" to use the default theme
icon_theme=""
# the colour of the pressed menu and bookmark button: "" for the default or in the form #7F7F7F
button_menu_selected_color=""
# the background colour of each button in the tasklist or "" for default #DF5E0B
button_background_color="#FFA500"
# # border radius
# border_radius=15
# # amount of effect
# blur_radius=15
# application to be skipped from the dock (executables between double quotes with comma separator)
SKIP_APP=[]
# centralize elements menu, app launchers, tasklist: 0 no - 1 yes - 2 resize the dock to the minimum width
CENTRALIZE_EL=2
# increase the value to better centralize elements (L left, R right): 1 or > 1
CENTRALIZE_GAP_L=1
CENTRALIZE_GAP_R=1
# close the menu and the clock applet if focus is lost on another window: 0 no - 1 yes
LOST_FOCUS_CLOSE=1
# play sounds as a window opens or closes: 0 no - 1 use external player - 2 use internal player
PLAY_SOUND=1
# audio player: "NAME" or ""
A_PLAYER="aplay"
# use internal clipboard
USE_CLIPBOARD=1
# use internal audio control - experimental
USE_AUDIO=1
# volume step: %
AUDIO_STEP=5
# starting audio level: 0-100
AUDIO_START_LEVEL=30
# show the microphone icon - experimental - USE_AUDIO is required
USE_MICROPHONE=1
# audio control panel command
MIXER_CONTROL="pavucontrol-qt"
# custom widgets at left
USE_CUSTOM_WIDGET_LEFT=0
# custom widgets at right
USE_CUSTOM_WIDGET_RIGHT=0
######### MENU ##########
# show the application menu: 0 no - 1 left - 2 right
use_menu=1
# this window width
menu_width=800
# menu position pad - bottom
menu_padx=4
menu_pady=4
# menu category icon size
menu_icon_size=36
# app icon size
menu_app_icon_size=36
# service menu icon size
service_icon_size=20
# service menu border colour
service_border_color="gray"
# program used to add applications OR "" - full path
app_prog="./appmenu.py"
# program used to modify a desktop file OR ""
app_mod_prog=app_prog
# search field background colour: colour (in the form "#xxxxxx") OR ""
search_field_bg=""
# in the form "#XXXXXX" or "rgb(X, X, X)" or "colour name"
scroll_handle_col="#B5B5B5"
# highlight color - in the form "#rrggbb or "" for default #DF5E0B
item_highlight_color=""
# show this action in the menu: 0 no - 1 yes
SEND_TO_DESKTOP=0
# desktop name
DESKTOP_NAME="Desktop"
# terminal program
USER_TERMINAL=""
#########
########## CLOCK - CALENDAR ##########
# show the clock - calendar: 0 no - 1 left - 2 right
use_clock=2
# clock font
clock_font=""
clock_font_size=12
# Thin 0 - ExtraLight 12 - Light 25 - Normal 50 - Medium 57 - DemiBold 63 - Bold 75 - ExtraBold 81 - Black 87
clock_font_weight=50
# 0 no - 1 yes
clock_font_italic=0
# show the name of the day: 0 no - 1 yes
day_name=0
# time in AM/PM format: 0 no - 1 yes
USE_AP = 0
# the calendar ics file to read or leave "" empty
calendar_file=""
# in the form "#XXXXXX" or "colour name"
calendar_appointment_day_color="#00AA00"
# highlight color - in the form "#rrggbb or "" for default #DF5E0B
citem_highlight_color=""
# border thickness
appointment_border_size=3
# in the form "#XXXXXX" or "colour name"
appointment_border_color="gray"
#
appointment_border_radius="15"
#
appointment_window_size=400
# font to be used in the label
calendar_label_font=""
# font size
calendar_label_font_size=18
# font weight: Thin 0 - ExtraLight 12 - Light 25 - Normal 50 - Medium 57 - DemiBold 63 - Bold 75 - ExtraBold 81 - Black 87
calendar_label_font_weight=75
# font italic: 0 no - 1 yes
calendar_label_font_italic=0
# in the form "#XXXXXX" or "colour name"
calendar_label_font_color=""
#
appointment_char="✔"
# commad to launch after a double click on an event, or leave "" empty
event_command=""
# command to execute after double clicking a date in the calendar
date_command=event_command
# more pixels from panel or screen border
clock_gapx=4
clock_gapy=4
############
######### label0 - at far left
# exec label1 script: 0 to disable - 1 yes
label0_script=0
# seconds to wait for executing the script again
label0_interval=1
# use html tags instead of plain text - override the next label1 options
label0_use_richtext=0
# label2 color: "" to default or in the form "#XXXXXX" "colour name"
label0_color="green"
# font to be used in the label
label0_font=""
# font size
label0_font_size=12
# font weight: Thin 0 - ExtraLight 12 - Light 25 - Normal 50 - Medium 57 - DemiBold 63 - Bold 75 - ExtraBold 81 - Black 87
label0_font_weight=75
# font italic: 0 no - 1 yes
label0_font_italic=0
# command to execute
label0_command1=""
# command to execute - center mouse button
label0_command2=""
######### label1 - at right
# exec label1 script: 0 to disable - 1 yes
label1_script=0
# seconds to wait for executing the script again
label1_interval=1
# use html tags instead of plain text - override the next label1 options
label1_use_richtext=0
# label2 color: "" to default or in the form "#XXXXXX" "colour name"
label1_color="red"
# font to be used in the label
label1_font=""
# font size
label1_font_size=12
# font weight: Thin 0 - ExtraLight 12 - Light 25 - Normal 50 - Medium 57 - DemiBold 63 - Bold 75 - ExtraBold 81 - Black 87
label1_font_weight=75
# font italic: 0 no - 1 yes
label1_font_italic=0
# command to execute
label1_command1=""
# command to execute - center mouse button
label1_command2=""
######### label2 - at right
# execute label2 script: 0 to disable - 1 yes
label2_script=0
# seconds to wait for executing the script again
label2_interval=3
# use html tags instead of plain text - override the next label2 options
label2_use_richtext=0
# label2 color: "" to default or in the form "#XXXXXX" or "colour name"
label2_color="gray"
# font to be used in the label
label2_font=""
# font size
label2_font_size=12
# font weight: Thin 0 - ExtraLight 12 - Light 25 - Normal 50 - Medium 57 - DemiBold 63 - Bold 75 - ExtraBold 81 - Black 87
label2_font_weight=75
# font italic: 0 no - 1 yes
label2_font_italic=0
# command to execute - left mouse button
label2_command1=""
# command to execute - center mouse button
label2_command2=""
######### label3 - at left
# exec label1 script: 0 to disable - 1 yes
label3_script=0
# seconds to wait for executing the script again
label3_interval=1
# use html tags instead of plain text - override the next label1 options
label3_use_richtext=0
# label2 color: "" to default or in the form "#XXXXXX" "colour name"
label3_color="brown"
# font to be used in the label
label3_font=""
# font size
label3_font_size=12
# font weight: Thin 0 - ExtraLight 12 - Light 25 - Normal 50 - Medium 57 - DemiBold 63 - Bold 75 - ExtraBold 81 - Black 87
label3_font_weight=75
# font italic: 0 no - 1 yes
label3_font_italic=0
# command to execute
label3_command1=""
# command to execute - center mouse button
label3_command2=""
########## service commands
# one word or script - /usr/bin/systemctl poweroff
shutdown_command="xterm"
# one word or script - /usr/bin/systemctl reboot
restart_command="xterm"
# one word or script
logout_command="xterm"
##### custom commands
# one word command - with full path eventually
# command and name mandatory
COMM1_COMMAND="xterm"
COMM1_ICON=""
COMM1_NAME="XTERM"
COMM1_TOOLTIP=""
#
COMM2_COMMAND=""
COMM2_ICON=""
COMM2_NAME=""
COMM2_TOOLTIP=""
#
COMM3_COMMAND=""
COMM3_ICON=""
COMM3_NAME=""
COMM3_TOOLTIP=""
#


