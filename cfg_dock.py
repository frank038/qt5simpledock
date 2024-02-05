# icon button max size to get from application (even number)
button_size=56
# padding - space between button and icon (size icon: button_size - button_padding)
button_padding=8
#########
# show the application menu: 0 no - 1 left - 2 right
use_menu=1
# this window width
menu_width=800
# this window height
menu_height=650
# menu position pad - bottom
menu_padx=8
menu_pady=14
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
search_field_bg="#D6D3D3"
# in the form "#XXXXXX" or "rgb(X, X, X)" or "colour name"
scroll_handle_col="#B5B5B5"
# highlight color - in the form "#rrggbb or "" for default #DF5E0B
item_highlight_color="#B5B5B5"
# show this action in the menu: 0 no - 1 yes
SEND_TO_DESKTOP=0
# desktop name
DESKTOP_NAME="Desktop"
#########
#### clock - calendar
# show the clock - calendar: 0 no - 1 left - 2 right
use_clock=2
# show the name of the day: 0 no - 1 yes
day_name=1
# time in AM/PM format: 0 no - 1 yes
USE_AP = 0
# the calendar ics file to read or leave "" empty
calendar_file=""
# in the form "#XXXXXX" or "colour name"
calendar_appointment_day_color="#00AA00"
# in the form "#XXXXXX" or "colour name"
appointment_border_color="gray"
#
appointment_border_radius="15"
#
appointment_window_size=400
# font to be used in the label
calendar_label_font=""
# font size
calendar_label_font_size=9
# font weight: Thin 0 - ExtraLight 12 - Light 25 - Normal 50 - Medium 57 - DemiBold 63 - Bold 75 - ExtraBold 81 - Black 87
calendar_label_font_weight=75
# font italic: 0 no - 1 yes
calendar_label_font_italic=0
# in the form "#XXXXXX" or "colour name"
calendar_label_font_color="red"
#
appointment_char="✔"
# commad to launch after a double click on an event, or leave "" empty
event_command=""
# command to execute after double clicking a date in the calendar
date_command=event_command
# more pixels from panel or screen border
cgapw=10
cgaph=10
############
# show virtual desktops: 0 no - 1 yes
virtual_desktops=0
# use the builtin tray: 0 no - 1 yes
use_tray=1
# tray icon size (even number)
tbutton_size = button_size
# the width of the dock: 0 to full width
dock_width=0
# the height of the dock
dock_height=60
# window fixed position: 0 no - 1 yes - 2 yes but does not reserve any spaces
fixed_position=1
# position: 0 top - 1 bottom
dock_position=1
# tasklist position: 0 left - 1 center - 2 right
tasklist_position=1
# space to reserve on desktop if not fixed: it will not covered by windows
reserved_space=5
# theme style: "" to use the default theme
theme_style=""
# icon theme: "" to use the default theme
icon_theme=""
# the background colour of each button in the tasklist or "" for default #DF5E0B
button_background_color=""
# use with a compositor: 0 no - 1 yes
# this option add rounded borders
with_compositor=0
# border radius
border_radius=15
# amount of effect
blur_radius=15
# enable transparency: 0 no - 1 yes
# a compositor is required; the with_compositor option is not mandatory
with_transparency=0
# application to be skipped from the dock (executables between double quotes with comma separator)
SKIP_APP=[]
# some window managers could behave differently on minimizing and or activating: 1 yes - 0 no
alternate_wm=0
# track screen resolution changes: 0 no - 1 yes
SCRN_RES=0
# 2 top - 3 bottom
panel_pos=3
######### label1
# exec label1 script: 0 to disable - 1 yes
label1_script=1
# seconds to wait for executing the script again
label1_interval=1
# use html tags instead of plain text - override the next label1 options
label1_use_richtext=0
# label2 color: "" to default or in the form "#XXXXXX" "colour name"
label1_color="green"
# font to be used in the label
label1_font=""
# font size
label1_font_size=24
# font weight: Thin 0 - ExtraLight 12 - Light 25 - Normal 50 - Medium 57 - DemiBold 63 - Bold 75 - ExtraBold 81 - Black 87
label1_font_weight=75
# font italic: 0 no - 1 yes
label1_font_italic=0
######### label2
# execute label2 script: 0 to disable - 1 yes
label2_script=1
# seconds to wait for executing the script again
label2_interval=3
# use html tags instead of plain text - override the next label2 options
label2_use_richtext=0
# label2 color: "" to default or in the form "#XXXXXX" or "colour name"
label2_color="white"
# font to be used in the label
label2_font=""
# font size
label2_font_size=20
# font weight: Thin 0 - ExtraLight 12 - Light 25 - Normal 50 - Medium 57 - DemiBold 63 - Bold 75 - ExtraBold 81 - Black 87
label2_font_weight=75
# font italic: 0 no - 1 yes
label2_font_italic=0
##########
#
shutdown_command="/usr/bin/systemctl poweroff"
#
restart_command="/usr/bin/systemctl reboot"
#
logout_command=""
### custom commands
# write a command or leave "" to disable
custom_command1=""
custom_command1_name=""
custom_command1_icon="icons/Missed.svg"
#
custom_command2=""
custom_command2_name=""
custom_command2_icon="icons/Missed.svg"
#
custom_command3=""
custom_command3_name=""
custom_command3_icon="icons/Missed.svg"
