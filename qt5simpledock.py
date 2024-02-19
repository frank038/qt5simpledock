#!/usr/bin/env python3

# V 0.9.28

from PyQt5 import QtCore, QtGui, QtWidgets
import sys, os, time
import shutil
from Xlib.display import Display
import Xlib
from Xlib import X, Xatom, Xutil, error
# from Xlib.ext import damage
import Xlib.protocol.event as pe
import subprocess
from xdg import DesktopEntry
from xdg import IconTheme
from ewmh import EWMH
ewmh = EWMH()
from cfg_dock import *
if use_clock:
    import datetime

curr_path = os.getcwd()

################## MENU
sys.path.append("modules")
from pop_menu import getMenu
menu_is_changed = 0

#### main application categories
Development = []
Education = []
Game = []
Graphics = []
Multimedia = []
Network = []
Office = []
Settings = []
System = []
Utility = []
Other = []

# the dirs of the application files
# only one directory for user
app_dirs_user = [os.path.join(os.path.expanduser("~"), ".local/share/applications")]
app_dirs_system = ["/usr/share/applications", "/usr/local/share/applications"]

# populate the menu
def on_pop_menu(app_dirs_user, app_dirs_system):
    #
    global Development
    Development = []
    global Education
    Education = []
    global Game
    Game = []
    global Graphics
    Graphics = []
    global Multimedia
    Multimedia = []
    global Network
    Network = []
    global Office
    Office = []
    global Settings
    Settings = []
    global System
    System = []
    global Utility
    Utility = []
    global Other
    Other = []
    #
    menu_prog = 0
    app_prog = 1
    if app_prog:
        menu_prog = 1
    menu_app = getMenu(app_dirs_user, app_dirs_system, menu_prog)
    menu = menu_app.list_one
    for el in menu:
        cat = el[1]
        if cat == "Multimedia":
            # label - executable - icon - comment - path - terminal - file full path
            Multimedia.append([el[0],el[2],el[3],el[4],el[5],el[6],el[7]])
        elif cat == "Development":
            Development.append([el[0],el[2],el[3],el[4],el[5],el[6],el[7]])
        elif cat == "Education":
            Education.append([el[0],el[2],el[3],el[4],el[5],el[6],el[7]])
        elif cat == "Game":
            Game.append([el[0],el[2],el[3],el[4],el[5],el[6],el[7]])
        elif cat == "Graphics":
            Graphics.append([el[0],el[2],el[3],el[4],el[5],el[6],el[7]])
        elif cat == "Network":
            Network.append([el[0],el[2],el[3],el[4],el[5],el[6],el[7]])
        elif cat == "Office":
            Office.append([el[0],el[2],el[3],el[4],el[5],el[6],el[7]])
        elif cat == "Settings":
            Settings.append([el[0],el[2],el[3],el[4],el[5],el[6],el[7]])
        elif cat == "System":
            System.append([el[0],el[2],el[3],el[4],el[5],el[6],el[7]])
        elif cat == "Utility":
            Utility.append([el[0],el[2],el[3],el[4],el[5],el[6],el[7]])
        else:
            Other.append([el[0],el[2],el[3],el[4],el[5],el[6],el[7]])
    #
    global menu_is_changed
    if menu_is_changed == 1:
        menu_is_changed = 0
    elif menu_is_changed > 1:
        menu_is_changed = 0
        on_pop_menu(app_dirs_user, app_dirs_system)

on_pop_menu(app_dirs_user, app_dirs_system)

#################

################
# load the database
fopen = calendar_file

class sEvent:
    SUMMARY=None
    DESCRIPTION=None
    DTSTART=None

list_events_all = []
#
def get_events():
    _events = None
    if os.path.exists(fopen):
        try:
            with open(fopen, "r") as f:
                _events = f.readlines()
        except:
            pass
    else:
        return
    #
    if _events is None:
        return
    if _events == []:
        return
    #
    s_event = None
    for el in _events:
        if el.strip("\n") == "BEGIN:VEVENT":
            s_event = sEvent()
        elif el.strip("\n")[0:8] == "SUMMARY:":
            s_event.SUMMARY = el.strip("\n")[8:]
        elif el.strip("\n")[0:12] == "DESCRIPTION:":
            s_event.DESCRIPTION = el.strip("\n")[12:]
        elif el.strip("\n")[0:8] == "DTSTART:":
            s_event.DTSTART = el.strip("\n")[8:]
        elif el.strip("\n") == "END:VEVENT":
            list_events_all.append(s_event)
            s_event = None
        elif el.strip("\n") == "END:VCALENDAR":
            s_event = None
            break
    
get_events()

#################
# width and height of the program
WINW = 0
WINH = 0

dock_width = 0
# fixed_position = 1

this_window = None
this_windowID = None

### TRAY
P_HEIGHT        = dock_height   # Panel height
TRAY_I_HEIGHT   = min(tbutton_size, button_size)   # System tray icon height (usually 16 or 24)
TRAY_I_WIDTH    = min(tbutton_size, button_size)   # System tray icon width  (usually 16 or 24)
TRAY            = 1             # System tray section
tray_already_used = 0
#############
stopCD = 0
data_run = 1

def play_sound(_sound):
    if not shutil.which(A_PLAYER):
        return
    sound_full_path = os.path.join(curr_path, "sounds", _sound)
    command = [A_PLAYER, sound_full_path]
    try:
        subprocess.Popen(command, 
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT)
    except: pass
    return

# 
class winThread(QtCore.QThread):
    
    sig = QtCore.pyqtSignal(list)
    
    def __init__(self, display, parent=None):
        super(winThread, self).__init__(parent)
        self.display = display
        self.root = self.display.screen().root
        #
        self.win_l = []
        #
        mask = (X.SubstructureNotifyMask | X.PropertyChangeMask | X.StructureNotifyMask | X.ExposureMask)
        self.root.change_attributes(event_mask=mask)
    
    ##### 
    def getProp(self, disp, win, prop):
        try:
            p = win.get_full_property(disp.intern_atom('_NET_WM_' + prop), 0)
            return [None] if (p is None) else p.value
        except:
            return [None]

    def run(self):
        while True:
            event = self.display.next_event()
            #
            # properties
            if (event.type == X.PropertyNotify):
                if event.atom == self.display.intern_atom('_NET_NUMBER_OF_DESKTOPS'):
                    vd_v = self.root.get_full_property(self.display.intern_atom('_NET_NUMBER_OF_DESKTOPS'), X.AnyPropertyType).value
                    number_of_virtual_desktops = vd_v.tolist()[0]
                    self.sig.emit(["DESKTOP_NUMBER", number_of_virtual_desktops])
                # change the current desktop
                elif event.atom == self.display.intern_atom("_NET_CURRENT_DESKTOP"):
                    cvd_v = self.root.get_full_property(self.display.intern_atom("_NET_CURRENT_DESKTOP"), X.AnyPropertyType).value
                    active_virtual_desktop = cvd_v.tolist()[0]
                    self.sig.emit(["ACTIVE_VIRTUAL_DESKTOP", active_virtual_desktop])
                # active window changed
                elif event.atom == self.display.intern_atom('_NET_ACTIVE_WINDOW'):
                    self.sig.emit(["ACTIVE_WINDOW_CHANGED", ""])
                #
                elif event.atom == self.display.intern_atom('_NET_CLIENT_LIST'):
                    self.sig.emit(["NETLIST"])
                # screen resolution
                elif event.atom == self.display.intern_atom('_NET_DESKTOP_GEOMETRY'):
                    self.sig.emit(["SCREEN_CHANGED"])
            #
            elif event.type == X.ClientMessage:
                #
                fmt, data = event.data
                if event.client_type == self.display.intern_atom('_NET_WM_STATE'):
                    if fmt == 32 and data[1] == self.display.intern_atom("_NET_WM_STATE_DEMANDS_ATTENTION"):
                        if data[0] == 1:
                            self.sig.emit(["URGENCY", 1, event.window])
                        elif data[0] == 0:
                            self.sig.emit(["URGENCY", 0, event.window])
                        # toggle urgency
                        elif data[0] == 2:
                            self.sig.emit(["URGENCY", 2, event.window])
            # 
            elif event.type == X.UnmapNotify:
                if event.window == self.root or event.window == None:
                    continue
                try:
                    attrs = event.window.get_attributes()
                    if hasattr(attrs, "override_redirect"):
                        attrs = event.window.get_attributes()
                        if attrs.override_redirect:
                            continue
                except:
                    pass
                try:
                    if hasattr(event.window.get_wm_state(), "state"):
                        if event.window.get_wm_state().state == 0:
                            continue
                except:
                    pass
                self.sig.emit(["UNMAPMAP", event.window, 0])
            #
            elif event.type == X.MapNotify:
                if event.window == self.root or event.window == None:
                    continue
                try:
                    attrs = event.window.get_attributes()
                    if hasattr(attrs, "override_redirect"):
                        attrs = event.window.get_attributes()
                        if attrs.override_redirect:
                            continue
                except:
                    pass
                self.sig.emit(["UNMAPMAP", event.window, 1])
            # elif event.type == self.display.extension_event.DamageNotify:
                # print("damage event from main::", event.window.id)
            #
            # elif event.type == X.Expose:
                # # self.sig.emit(["EXPOSE"])
            #
            if stopCD:
                break
        if stopCD:
            return


######################

# label executors
class label1Thread(QtCore.QThread):
    
    label1sig = QtCore.pyqtSignal(list)
    
    def __init__(self, label1_data):
        super(label1Thread, self).__init__()
        self.label1_data = label1_data
    
    def run(self):
        while data_run:
            data = subprocess.check_output([self.label1_data[0]], shell=True, encoding='utf-8').strip("\n")
            self.label1sig.emit([data])
            time.sleep(self.label1_data[1])
            if not data_run:
                break


# screen resolution changed
class winThread2(QtCore.QThread):
    
    sig = QtCore.pyqtSignal(list)
    
    def __init__(self, display, parent=None):
        super(winThread2, self).__init__(parent)
        self.display = display
        self.root = self.display.screen().root
        #
        self.win_l = []
        self.root.change_attributes(event_mask=X.PropertyChangeMask)
        
    #
    def run(self):
        while True:
            event = self.display.next_event()
            if event.type == X.ConfigureNotify:
                self.sig.emit([root.get_geometry().width, root.get_geometry().height])
    

class SecondaryWin(QtWidgets.QWidget):
    def __init__(self, position):
        super(SecondaryWin, self).__init__()
        # super().__init__()
        self.position = position
        self.setWindowTitle("qt5simpledock")
        #
        self.display = Display()
        self.root = self.display.screen().root
        #
        self.is_started = 1
        # # the pointer entered the panel
        # self.is_entered = 0
        # demand attention: window:type - 1 add - 0 remove - 2 toggle
        self.attention_windows = {}
        # list of windows demanding attention
        self.list_uitem = []
        # taskbar button in clicked state
        self.taskb_btn = None
        ## the number of virtual desktops
        global virtual_desktops
        if virtual_desktops:
            try:
                atom_vs = self.display.intern_atom('_NET_NUMBER_OF_DESKTOPS')
                vd_v = self.root.get_full_property(atom_vs, X.AnyPropertyType).value
                self.num_virtual_desktops = vd_v.tolist()[0]
                # the active virtual desktop - 0 is 1 etc.
                atom_cvd = self.display.intern_atom("_NET_CURRENT_DESKTOP")
                vd_cv = self.root.get_full_property(atom_cvd, X.AnyPropertyType).value
                self.active_virtual_desktop = vd_cv.tolist()[0]
                # actual virtual desktop
                self.actual_virtual_desktop = self.active_virtual_desktop
            except:
                virtual_desktops = 0
                self.active_virtual_desktop = 0
                self.actual_virtual_desktop = 0
        else:
            self.active_virtual_desktop = 0
            self.actual_virtual_desktop = 0
        #######
        screen = app.primaryScreen()
        self.screen_size = screen.size()
        #
        # 0 top - 1 bottom
        if self.position in [0,1]:
            self.abox = QtWidgets.QHBoxLayout()
            self.abox.setContentsMargins(0,0,10,0)
            self.abox.setDirection(QtWidgets.QBoxLayout.LeftToRight)
            self.abox.setSpacing(0)
            self.setLayout(self.abox)
            #
            if label0_script:
                self.labelw0 = QtWidgets.QLabel()
                # self.labelw0.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
                self.abox.insertWidget(0, self.labelw0)
                if label1_use_richtext:
                    self.labelw0.setTextFormat(QtCore.Qt.RichText)
                else:
                    if label0_color:
                        self.labelw0.setStyleSheet("color: {}".format(label0_color))
                    tfont = QtGui.QFont()
                    if label0_font:
                        tfont.setFamily(label0_font)
                    if label0_font_size:
                        tfont.setPointSize(label0_font_size)
                    if label0_font_weight:
                        tfont.setWeight(label0_font_weight)
                    if label0_font_italic:
                        tfont.setItalic(label0_font_italic)
                    self.labelw0.setFont(tfont)
                # 
                self.labelw0.mouseDoubleClickEvent = self.on_labelw0
                self.label0thread = label1Thread(["scripts/./label0.sh", label0_interval])
                self.label0thread.label1sig.connect(self.on_label0)
                self.label0thread.start()
            ##### clock
            self.cw_is_shown = None
            self.cwin_is_shown = None
            if use_clock:
                self.cbox = QtWidgets.QHBoxLayout()
                self.cbox.setContentsMargins(4,0,4,0)
                self.tlabel = QtWidgets.QLabel("")
                tfont = QtGui.QFont()
                if calendar_label_font:
                    tfont.setFamily(calendar_label_font)
                tfont.setPointSize(calendar_label_font_size)
                tfont.setWeight(calendar_label_font_weight)
                tfont.setItalic(calendar_label_font_italic)
                self.tlabel.setFont(tfont)
                if calendar_label_font_color:
                    self.tlabel.setStyleSheet("QLabel {0} color: {1};{2}".format("{", calendar_label_font_color, "}"))
                    # self.tlabel.setStyleSheet("QLabel {0} color: {1}; {2} QLabel::hover {0} background-color: lightgrey; border: 2px lightgrey; border-radius: 15px;{2}".format("{", calendar_label_font_color, "}"))
                # else:
                    # self.tlabel.setStyleSheet("QLabel::hover { background-color: lightgrey; border: 2px lightgrey; border-radius: 15px;}")
                #self.tlabel.setAlignment(QtCore.Qt.AlignCenter)
                self.cbox.addWidget(self.tlabel)
                #
                if USE_AP:
                    cur_time = QtCore.QTime.currentTime().toString("hh:mm ap")
                else:
                    cur_time = QtCore.QTime.currentTime().toString("hh:mm")
                if day_name:
                    curr_date = QtCore.QDate.currentDate().toString("ddd d")
                    self.tlabel.setText(" "+curr_date+"  "+cur_time+" ")
                else:
                    self.tlabel.setText(" "+cur_time+" ")
                    curr_date = QtCore.QDate.currentDate().toString("ddd d")
                    self.tlabel.setToolTip(" "+curr_date+" ")
                #
                tfont = QtGui.QFont()
                if clock_font:
                    tfont.setFamily(clock_font)
                if clock_font_size:
                    tfont.setPointSize(clock_font_size)
                if clock_font_weight:
                    tfont.setWeight(clock_font_weight)
                if clock_font_italic:
                    tfont.setItalic(clock_font_italic)
                #
                # if clock_font:
                self.tlabel.setFont(tfont)
                #
                timer = QtCore.QTimer(self)
                timer.timeout.connect(self.update_label)
                timer.start(60 * 1000)
                #
                self.tlabel.setContentsMargins(0,0,0,0)
                self.tlabel.mousePressEvent = self.on_tlabel
                #
                if use_clock == 1:
                    self.abox.insertLayout(1, self.cbox)
            ##########
            if CENTRALIZE_EL == 1:
                self.abox.addStretch(1)
                if CENTRALIZE_GAP_L > 0:
                    clabell = QtWidgets.QLabel()
                    clabell.setText(" "*CENTRALIZE_GAP_L)
                    self.abox.insertWidget(2, clabell)
            # else:
                # self.abox.addStretch(0)
            ## menu
            self.mw_is_shown = None
            if use_menu:
                self.mbtnbox = QtWidgets.QHBoxLayout()
                self.mbtnbox.setContentsMargins(4,0,4,0)
                #self.mbtnbox.setSpacing(4)
                if use_menu == 1:
                    self.abox.insertLayout(3, self.mbtnbox)
                # the window menu
                self.mbutton = QtWidgets.QPushButton(flat=True)
                self.mbutton.setFlat(True)
                self.mbutton.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
                self.mbutton.setIcon(QtGui.QIcon("icons/menu.png"))
                self.mbutton.setIconSize(QtCore.QSize(button_size, button_size))
                self.mbtnbox.addWidget(self.mbutton)
                # self.btn_style_sheet(self.mbutton)
                self.mbutton.clicked.connect(self.on_click)
            ## virtual desktop box
            if virtual_desktops:
                self.virtbox = QtWidgets.QHBoxLayout()
                self.virtbox.setContentsMargins(0,0,0,0)
                self.virtbox.setSpacing(4)
                self.virtbox.desk = "v"
                self.abox.insertLayout(4, self.virtbox)
                #
                vbtn = QtWidgets.QPushButton()
                vbtn.setFlat(True)
                # vbtn.setAutoExclusive(True)
                vbtn.setCheckable(True)
                vbtn.setFixedSize(QtCore.QSize(int(dock_height*1.3), dock_height))
                #
                # if virtual_desktops:
                self.virtbox.addWidget(vbtn)
                # else:
                    # self.abox.addSpacing(8)
                    # self.abox.insertSpacing(100, 8)
                vbtn.desk = 0
                vbtn.clicked.connect(self.on_vbtn_clicked)
                self.on_virt_desk(self.num_virtual_desktops)
            #
            ## program box
            self.prog_box = QtWidgets.QHBoxLayout()
            self.prog_box.setContentsMargins(4,0,4,0)
            self.prog_box.setSpacing(4)
            self.prog_box.desk = "p"
            #self.prog_box.setAlignment(QtCore.Qt.AlignCenter)
            self.abox.insertLayout(5, self.prog_box)
            # self.abox.setAlignment(self.prog_box, QtCore.Qt.AlignVCenter)
            ## add the applications to prog_box
            progs = os.listdir("applications")
            # args to remove from the exec entry
            execArgs = [" %f", " %F", " %u", " %U", " %d", " %D", " %n", " %N", " %k", " %v"]
            if progs:
                for ffile in progs:
                    pexec = ""
                    entry = DesktopEntry.DesktopEntry(os.path.join("applications", ffile))
                    fname = entry.getName()
                    icon = entry.getIcon()
                    pexec_temp = entry.getExec()
                    #
                    if pexec_temp:
                        for aargs in execArgs:
                            if aargs in pexec_temp:
                                pexec_temp = pexec_temp.strip(aargs)
                        pexec = pexec_temp.split()[0]
                    else:
                        continue
                    fpath = ""
                    fpath = entry.getPath()
                    #
                    self.pbtn = QtWidgets.QPushButton()
                    self.pbtn.setFlat(True)
                    picon = QtGui.QIcon.fromTheme(icon)
                    if picon.isNull():
                        image = QtGui.QImage(icon)
                        if image.isNull():
                            image = QtGui.QImage("icons/unknown.svg")
                        pixmap = QtGui.QPixmap(image)
                        picon = QtGui.QIcon(pixmap)
                    self.pbtn.setFixedSize(QtCore.QSize(pbutton_size, pbutton_size))
                    self.pbtn.setIcon(picon)
                    self.pbtn.setToolTip(fname or pexec)
                    self.pbtn.setIconSize(QtCore.QSize(pbutton_size, pbutton_size))
                    self.pbtn.pexec = pexec_temp
                    self.pbtn.pdesktop = ffile
                    self.pbtn.ppath = fpath
                    self.prog_box.addWidget(self.pbtn, alignment=QtCore.Qt.AlignCenter)
                    self.pbtn.clicked.connect(self.on_pbtn)
                    self.pbtn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
                    self.pbtn.customContextMenuRequested.connect(self.pbtnClicked)
            #
            ## tasklist
            self.ibox = QtWidgets.QHBoxLayout()
            # (int left, int top, int right, int bottom)
            self.ibox.setContentsMargins(4,0,4,0)
            self.ibox.setSpacing(4)
            if tasklist_position == 0:
                self.ibox.setAlignment(QtCore.Qt.AlignLeft)
                # #
                # pframe = QtWidgets.QFrame()
                # pframe.setFrameShape(QtWidgets.QFrame.VLine)
                # self.ibox.addWidget(pframe)
            elif tasklist_position == 1:
                self.ibox.setAlignment(QtCore.Qt.AlignCenter)
                if CENTRALIZE_EL == 0:
                    self.abox.addStretch(1)
            # elif tasklist_position == 2:
                # self.ibox.setAlignment(QtCore.Qt.AlignRight)
                # self.ibox.setDirection(QtWidgets.QBoxLayout.RightToLeft)
            # the first virtual desktop
            self.ibox.desk = 0
            self.abox.insertLayout(6, self.ibox)
            # # fake button
            # self.fake_btn = QtWidgets.QPushButton()
            # self.fake_btn.setAutoExclusive(True)
            # self.fake_btn.setCheckable(True)
            # self.fake_btn.setFixedSize(QtCore.QSize(1,1))
            # self.fake_btn.setFlat(True)
            # self.fake_btn.winid = 1
            # self.fake_btn.desktop = 0
            # self.fake_btn.setVisible(False)
            # self.ibox.addWidget(self.fake_btn)
            # # if dock_width == 0:
            # #self.abox.setStretchFactor(self.ibox,1)
        #
        ################################
        # winid - desktop
        self.list_prog = []
        # desktop in which the program appeared
        on_desktop = 0
        winid_list_temp = self.root.get_full_property(self.display.intern_atom('_NET_CLIENT_LIST'), X.AnyPropertyType)
        if winid_list_temp:
            winid_list = winid_list_temp.value
            for winid in winid_list:
                window = self.display.create_resource_object('window', winid)
                #
                try:
                    prop = window.get_full_property(self.display.intern_atom('_NET_WM_WINDOW_TYPE'), X.AnyPropertyType)
                except:
                    prop = None
                #
                if prop:
                    if self.display.intern_atom('_NET_WM_WINDOW_TYPE_DOCK') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_DESKTOP') in prop.value.tolist():
                        continue
                    # elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_DIALOG') in prop.value.tolist():
                        # continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_UTILITY') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_TOOLBAR') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_MENU') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_SPLASH') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_DND') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_NOTIFICATION') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_DROPDOWN_MENU') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_COMBO') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_POPUP_MENU') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_TOOLTIP') in prop.value.tolist():
                        continue
                #
                # if self.display.intern_atom('_NET_WM_WINDOW_TYPE_NORMAL') in prop.value.tolist():
                try:
                    # if not self.display.intern_atom("_NET_WM_STATE_SKIP_TASKBAR") in window.get_full_property(self.display.intern_atom("_NET_WM_STATE"), Xatom.ATOM).value:
                    _wst = window.get_full_property(self.display.intern_atom("_NET_WM_STATE"), Xatom.ATOM)
                    if _wst:
                        if self.display.intern_atom("_NET_WM_STATE_SKIP_TASKBAR") in _wst.value:
                            return
                    try:
                        _ppp = self.getProp(self.display,window,'DESKTOP')
                    except:
                        _ppp = [0]
                    #
                    if _ppp and _ppp[0]:
                        on_desktop = _ppp[0]
                    else:
                        on_desktop = 0
                    # the exec name
                    win_exec = "Unknown"
                    win_name_t = window.get_wm_class()
                    if win_name_t is not None:
                        win_exec = str(win_name_t[0])
                    # else:
                        # win_exec = "Unknown"
                    #
                    self.list_prog.append([winid, on_desktop, win_exec])
                except:
                    pass
        #
        # # current window active - window id
        # self.curr_win_active = None
        self.wid_l = []
        # the right mouse button is pressed for menu
        self.right_button_pressed = 0
        #############
        # self.list_prog: winid - desktop
        icon_icon = None
        for pitem in self.list_prog:
            self.on_dock_items(pitem)
        # the active window
        self.get_active_window_first()
        ####
        # this program wid
        self.this_window = None
        # 
        self.on_leave = None
        ####### X events
        self.mythread = winThread(Display())
        self.mythread.sig.connect(self.threadslot)
        self.mythread.start()
        ########
        #
        #if CENTRALIZE_EL == 1:
        if CENTRALIZE_GAP_R > 0:
            clabelr = QtWidgets.QLabel()
            clabelr.setText(" "*CENTRALIZE_GAP_R)
            self.abox.insertWidget(7, clabelr)
        # 
        self.abox.addStretch(1)
        #
        if label1_script:
            self.labelw1 = QtWidgets.QLabel()
            self.labelw1.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
            self.abox.insertWidget(8, self.labelw1)
            if label1_use_richtext:
                self.labelw1.setTextFormat(QtCore.Qt.RichText)
            else:
                if label1_color:
                    self.labelw1.setStyleSheet("color: {}".format(label1_color))
                tfont = QtGui.QFont()
                if label1_font:
                    tfont.setFamily(label1_font)
                if label1_font_size:
                    tfont.setPointSize(label1_font_size)
                if label1_font_weight:
                    tfont.setWeight(label1_font_weight)
                if label1_font_italic:
                    tfont.setItalic(label1_font_italic)
                self.labelw1.setFont(tfont)
            # 
            self.labelw1.mouseDoubleClickEvent = self.on_labelw1
            # self.l1p = QtCore.QProcess()
            # self.l1p.readyReadStandardOutput.connect(self.p1ready)
            # self.l1p.finished.connect(self.p1finished)
            # self.l1p.start("scripts/./label1.sh")
            #
            self.label1thread = label1Thread(["scripts/./label1.sh", label1_interval])
            self.label1thread.label1sig.connect(self.on_label1)
            self.label1thread.start()
        #
        # label 2
        if label2_script:
            self.labelw2 = QtWidgets.QLabel()
            self.labelw2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
            self.abox.insertWidget(9, self.labelw2)
            if label2_use_richtext:
                self.labelw2.setTextFormat(QtCore.Qt.RichText)
            else:
                if label2_color:
                    self.labelw2.setStyleSheet("color: {}".format(label2_color))
                tfont = QtGui.QFont()
                if label2_font:
                    tfont.setFamily(label2_font)
                if label2_font_size:
                    tfont.setPointSize(label2_font_size)
                if label2_font_weight:
                    tfont.setWeight(label2_font_weight)
                if label2_font_italic:
                    tfont.setItalic(label2_font_italic)
                self.labelw2.setFont(tfont)
            ###
            self.labelw2.mouseDoubleClickEvent = self.on_labelw2
            ###
            # self.l2p = QtCore.QProcess()
            # self.l2p.readyReadStandardOutput.connect(self.p2ready)
            # self.l2p.finished.connect(self.p2finished)
            # self.l2p.start("scripts/./label2.sh")
            #
            self.label2thread = label1Thread(["scripts/./label2.sh", label2_interval])
            self.label2thread.label1sig.connect(self.on_label2)
            self.label2thread.start()
        #
        #### tray section
        global use_tray
        # check if another tray is active
        selection = self.display.intern_atom("_NET_SYSTEM_TRAY_S%d" % self.display.get_default_screen())
        if self.display.get_selection_owner(selection) != X.NONE:
            global tray_already_used
            tray_already_used = 1
            use_tray = 0
        #
        if use_tray:
            # self.tframe = QtWidgets.QFrame()
            # self.tframe.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
            # # self.tframe.setStyleSheet("background: palette(window); border-top-left-radius:{0}px; border-top-right-radius:{0}px".format(border_radius))
            #
            self.frame_box = QtWidgets.QHBoxLayout()
            self.frame_box.setContentsMargins(0,0,0,0)
            self.frame_box.setSpacing(0)
            # self.tframe.setLayout(self.frame_box)
            self.tray_box = self.frame_box
            #
            # self.abox.insertWidget(10, self.tframe)
            self.abox.insertLayout(10, self.frame_box)
            # frame widget counter
            self.frame_counter = 0
            # widget background color
            bcolor = self.palette().color(QtGui.QPalette.Background).name()
            #
            self.tthread = trayThread(1, bcolor, data_run)
            self.tthread.sig.connect(self.tthreadslot)
            self.tthread.start()
        #
        # clock at right
        if use_clock == 2:
            self.abox.insertLayout(11, self.cbox)
        # menu at right
        if use_menu == 2:
            self.abox.insertLayout(12, self.mbtnbox)
        #
        # if not fixed_position:
            # QtCore.QTimer.singleShot(1500, self.on_leave_event)
        # #
        # if dock_width:
            # self.on_move_win()
        #
    
    # double click on label 0
    def on_labelw0(self, e):
        comm = None
        if e.button() == QtCore.Qt.LeftButton:
            comm = label0_command1
        elif e.button() == QtCore.Qt.MiddleButton:
            comm = label0_command2
        if comm:
            try:
                subprocess.Popen([comm])
            except:
                pass
        # QtWidgets.QLabel.mouseDoubleClickEvent(self, e)
    
        
    # click on label 1
    def on_labelw1(self, e):
        comm = None
        if e.button() == QtCore.Qt.LeftButton:
            comm = label1_command1
        elif e.button() == QtCore.Qt.MiddleButton:
            comm = label1_command2
        if comm:
            try:
                subprocess.Popen([comm])
            except:
                pass
    
    # click on label 2
    def on_labelw2(self, e):
        comm = None
        if e.button() == QtCore.Qt.LeftButton:
            comm = label2_command1
        elif e.button() == QtCore.Qt.MiddleButton:
            comm = label2_command2
        if comm:
            try:
                subprocess.Popen([comm])
            except:
                pass
    
    # click on tlabel
    def on_tlabel(self, e):
        if e.button() == QtCore.Qt.LeftButton:
            if self.cw_is_shown is not None:
                self.cw_is_shown.close()
                self.cw_is_shown = None
                return
            cw = calendarWin(self)
            cw.show()
            self.cw_is_shown = cw
    
    # label time    
    def update_label(self):
        if USE_AP:
            cur_time = QtCore.QTime.currentTime().toString("hh:mm ap")
        else:
            cur_time = QtCore.QTime.currentTime().toString("hh:mm")
        #
        if day_name:
            curr_date = QtCore.QDate.currentDate().toString("ddd d")
            self.tlabel.setText(" "+curr_date+"  "+cur_time+" ")
        else:
            self.tlabel.setText(" "+cur_time+" ")
    
    # click on menu button
    def on_click(self):
        sender_button = self.sender()
        #
        if self.mw_is_shown is not None:
            self.mw_is_shown.close()
            self.mw_is_shown = None
            return
        mw = menuWin(self)
        self.mw_is_shown = mw
    
    def tthreadslot(self, aa):
        if aa[0] == "a":
            self.tadd(aa[1])
        elif aa[0] == "b":
            self.tremove(aa[1])
        elif aa[0] == "c":
            self.tupdate(aa[1], aa[2])
    
    def tadd(self, wid):
        fwin = QtGui.QWindow.fromWinId(wid)
        # fwin.setMinimumSize(QtCore.QSize(tbutton_size, tbutton_size))
        # fwin.setGeometry(QtCore.QRect(0,0,tbutton_size,tbutton_size))
        # fwin.resize(tbutton_size, tbutton_size)
        # fwin.setFlags(QtCore.Qt.FramelessWindowHint)
        fwin.setFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.ForeignWindow)
        fwidget = QtWidgets.QWidget.createWindowContainer(fwin)
        fwidget.setAutoFillBackground(True)
        #fwidget.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        fwidget.setContentsMargins(0,0,0,0)
        fwidget.setMinimumSize(QtCore.QSize(tbutton_size, tbutton_size))
        fwidget.setMaximumSize(QtCore.QSize(tbutton_size, tbutton_size))
        #fwidget.resize(fwidget.sizeHint())
        #fwidget.resize(tbutton_size, tbutton_size)
        fwidget.id = wid
        self.tray_box.update()
        #
        self.tray_box.addWidget(fwidget, 1, QtCore.Qt.AlignCenter)
        for i in range(self.tray_box.count()):
            widget = self.tray_box.itemAt(i).widget()
        #
        # self.on_move_win()
    
    def tremove(self, wid):
        for i in range(self.tray_box.count()):
            if self.tray_box.itemAt(i) != None:
                widget = self.tray_box.itemAt(i).widget()
                if widget and widget.id == wid:
                    self.tray_box.removeWidget(widget)
        # 
        self.tray_box.update()
        #
        # self.on_move_win()
    
    # def tupdate(self, wid):
    def tupdate(self, win, bcolor):
        wid = win.id
        for i in range(self.tray_box.count()):
            if self.tray_box.itemAt(i) != None:
                widget = self.tray_box.itemAt(i).widget()
                if widget and widget.id == wid:
                    self.tray_box.update()
                    widget.update()
                    win.change_attributes(background_pixel = bcolor)
                    Display().sync()
                    widget.update()
                    self.tray_box.update()
                    win.unmap()
                    win.map()
                    Display().sync()
                    widget.hide()
                    widget.show()
                    widget.update()
                    self.tray_box.update()
                    widget.repaint()
                    break

    def resizeEvent(self, event):
        self.update()
    
    def on_label0(self, data):
        if data:
            self.labelw0.setText(data[0])
    
    def on_label1(self, data):
        if data:
            self.labelw1.setText(data[0])
    
    # def p1ready(self):
        # result = self.l1p.readAllStandardOutput().data().decode().strip("\n")
        # self.labelw1.setText(result)
    
    # def p1finished(self):
        # self.l1p.close()
        # del self.l1p
    
    def on_label2(self, data):
        if data:
            self.labelw2.setText(data[0])
    
    # def p2ready(self):
        # result = self.l2p.readAllStandardOutput().data().decode().strip("\n")
        # self.labelw2.setText(result)
    
    # def p2finished(self):
        # self.l2p.close()
        # del self.l2p
    
    # launch the application from the prog_box
    def on_pbtn(self):
        prog = self.sender().pexec
        path = self.sender().ppath
        # pp = QtCore.QProcess()
        # pp.setWorkingDirectory(os.getenv("HOME"))
        # pp.startDetached(prog)
        # subprocess.Popen(prog, cwd=os.getenv("HOME"))
        # subprocess.run(prog, cwd=os.getenv("HOME"))
        if path:
            os.system("cd {} && {} & cd {} &".format(path, prog, os.getenv("HOME")))
        else:
            os.system("cd {} && {} &".format(os.getenv("HOME"), prog))
    
    # to get a window property
    def getProp(self, disp, win, prop):
        try:
            p = win.get_full_property(disp.intern_atom('_NET_WM_' + prop), 0)
            return [None] if (p is None) else p.value
        except:
            return [None]
    
    def contextMenuEvent(self, event):
        contextMenu = QtWidgets.QMenu(self)
        reloadAct = contextMenu.addAction("Reload")
        quitAct = contextMenu.addAction("Exit")
        action = contextMenu.exec_(self.mapToGlobal(event.pos()))
        if action == quitAct:
            self.winClose()
        elif action == reloadAct:
            self.restart()
    
    def winClose(self):
        global stopCD
        stopCD = 1
        global data_run
        data_run = 0
        QtWidgets.qApp.quit()

    def restart(self):
        QtCore.QCoreApplication.quit()
        status = QtCore.QProcess.startDetached(sys.executable, sys.argv)
    
    def threadslot(self, data):
        if data:
            if data[0] == "NEWWINDOW":
                self.on_new_window()
            # active window
            elif data[0] == "ACTIVE_WINDOW_CHANGED":
                self.get_active_window()
            # number of virtual desktops
            elif data[0] == "DESKTOP_NUMBER":
                if virtual_desktops:
                    self.virtual_desktops_changed(data[1])
            # current virtual desktop changed
            elif data[0] == "ACTIVE_VIRTUAL_DESKTOP":
                if virtual_desktops:
                    self.active_virtual_desktop_changed(data[1])
                    self.active_virtual_desktop = data[1]
            # net list
            elif data[0] == "NETLIST":
                self.net_list()
            #
            elif data[0] == "URGENCY":
                self._urgency(data[1], data[2])
            #
            elif data[0] == "SCREEN_CHANGED":
                self._screen_changed()
            #
            elif data[0] == "UNMAPMAP":
                self._unmapmap(data[1], data[2])
            # #
            # elif data[0] == "EXPOSE":
                # self.adjustSize()
                # self.updateGeometry()
                # # # self.resize(self.sizeHint())
                # # self.resize(self.sizeHint().width(), dock_height)
    
    # hide the button from the taskbar when unmapped or unhide it
    def _unmapmap(self, win, _type):
        for i in range(self.ibox.count()):
            item = self.ibox.itemAt(i).widget()
            if not item:
                continue
            if isinstance(item, QtWidgets.QPushButton):
                if item.winid == win.id:
                    if _type == 0:
                        item.setVisible(False)
                    elif _type == 1:
                        item.setVisible(True)
                    break
    
    def _screen_changed(self):
        global WINW
        global WINH
        _size = screen.size()
        #
        NW = _size.width()
        NH = _size.height()
        #
        if NW != WINW or NH != WINH:
            WINW = NW
            WINH = NH
            # if dock_width:
                # WINW = dock_width
            if dock_position == 1:
                sy = WINH - dock_height
            elif dock_position == 0:
                sy = 0
            self.setGeometry(0, sy, WINW, dock_height)
            self.updateGeometry()
    
    
    def on_urgency(self, _n, item):
        if _n == 1:
            if self.list_uitem:
                # only one window with attention flag
                self.utimer.stop()
                self.list_uitem[0].setStyleSheet("border-color: {}; border=none".format(self.palette().color(QtGui.QPalette.Background).name()))
                self.list_uitem = []
            #
            self.utimer = QtCore.QTimer()
            self.utimer.setInterval(500)
            self._ut = 0
            self.list_uitem.append(item)
            self.utimer.timeout.connect(lambda:self.f_on_urgency(item))
            #
            self.utimer.start()
        #
        elif _n == 0:
            if item in self.list_uitem:
                self.list_uitem.remove(item)
                self.utimer.stop()
                try:
                    item.setStyleSheet("border-color: {}; border=none".format(self.palette().color(QtGui.QPalette.Background).name()))
                    # del self._ut
                except:
                    pass
        
    def f_on_urgency(self, item):
        try:
            if self._ut == 0 or (self._ut % 2) == 0:
                item.setStyleSheet("border: 2px solid; border-radius: 2px; border-color: red;")
                self._ut += 1
            elif self._ut == 1 or (self._ut % 2) != 0:
                item.setStyleSheet("border-color: {}; border=none".format(self.palette().color(QtGui.QPalette.Background).name()))
                self._ut += 1
            # timer limit 3 sec.
            if self._ut == 6:
                item.setStyleSheet("border: 2px solid; border-radius: 2px; border-color: red;")
                self.utimer.stop()
                # the active window
                try:
                    window_active_id_tmp = self.root.get_full_property(self.display.intern_atom('_NET_ACTIVE_WINDOW'), X.AnyPropertyType)
                    if window_active_id_tmp:
                        window_active_id = window_active_id_tmp.value[0]
                        if window_active_id == item.winid:
                            item.setStyleSheet("border-color: {}; border=none".format(self.palette().color(QtGui.QPalette.Background).name()))
                            return
                except:
                    return
        except:
            self.utimer.stop()
            if item in self.list_uitem:
                self.list_uitem.remove(item)
            # del self._ut
        
    
    # urgency flag
    def _urgency(self, _type, win):
        # do not use get_wm_hints(): gives not updated values
        if _type == 1 or _type == 2:
            # if not (win.id in self.attention_windows):
                # self.attention_windows[win.id] = _type
            # # skip active window
            # try:
                # window_active_id_tmp = self.root.get_full_property(self.display.intern_atom('_NET_ACTIVE_WINDOW'), X.AnyPropertyType)
                # if window_active_id_tmp:
                    # window_active_id = window_active_id_tmp.value[0]
                    # if window_active_id == win.id:
                        # return
            # except:
                # return
            #
            for i in range(self.ibox.count()):
                item = self.ibox.itemAt(i).widget()
                if not item:
                    continue
                if isinstance(item, QtWidgets.QPushButton):
                    if item.winid == win.id:
                        self.on_urgency(1, item)
                        break
        elif _type == 0:
            # if (win.id in self.attention_windows):
                # del self.attention_windows[win.id]
            #
            for i in range(self.ibox.count()):
                item = self.ibox.itemAt(i).widget()
                if not item:
                    continue
                if isinstance(item, QtWidgets.QPushButton):
                    if item.winid == win.id:
                        self.on_urgency(0, item)
                        break
        # elif _type == 2:
            # if not (win.id in self.attention_windows):
                # self.attention_windows[win.id] = _type
                # for i in range(self.ibox.count()):
                    # item = self.ibox.itemAt(i).widget()
                    # if not item:
                        # continue
                    # if isinstance(item, QtWidgets.QPushButton):
                        # if item.winid == win.id:
                            # self.on_urgency(1, item)
                            # break
            # elif (win.id in self.attention_windows):
                # del self.attention_windows[win.id]
                # for i in range(self.ibox.count()):
                    # item = self.ibox.itemAt(i).widget()
                    # if not item:
                        # continue
                    # if isinstance(item, QtWidgets.QPushButton):
                        # if item.winid == win.id:
                            # self.on_urgency(0, item)
                            # break
    
    # number of virtual desktops changed
    def virtual_desktops_changed(self, ndesks):
        self.on_virt_desk(ndesks)
    
    # current virtual desktop changed
    def active_virtual_desktop_changed(self, ndesk):
        for i in range(self.virtbox.count()):
            vbtn = self.virtbox.itemAt(i).widget()
            if isinstance(vbtn, QtWidgets.QPushButton):
                if vbtn.desk == ndesk:
                    vbtn.setChecked(True)
                else:
                    vbtn.setChecked(False)
        self.actual_virtual_desktop = ndesk
        
    def net_list(self):
        window_list = []
        xlist = self.root.get_full_property(self.display.intern_atom('_NET_CLIENT_LIST'), Xatom.WINDOW)
        if xlist:
            window_list = xlist.value.tolist()
        self.on_new_window(window_list)
        self.delete_window_destroyed(window_list)
        # self.get_active_window()
            
    # a new window has apparead
    def on_new_window(self, window_list):
        for w in window_list:
            #
            if this_windowID not in self.wid_l:
                self.wid_l.append(this_windowID)
            if w not in self.wid_l:
                window = self.display.create_resource_object('window', w)
                ########### skip unmanaged windows
                try:
                    prop = window.get_full_property(self.display.intern_atom('_NET_WM_WINDOW_TYPE'), X.AnyPropertyType)
                except:
                    prop = None
                #
                if prop:
                    if self.display.intern_atom('_NET_WM_WINDOW_TYPE_DOCK') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_DESKTOP') in prop.value.tolist():
                        continue
                    # elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_DIALOG') in prop.value.tolist():
                        # continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_UTILITY') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_TOOLBAR') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_MENU') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_SPLASH') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_DND') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_NOTIFICATION') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_DROPDOWN_MENU') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_COMBO') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_POPUP_MENU') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_TOOLTIP') in prop.value.tolist():
                        continue
                    # else:
                        #
                        # if self.display.intern_atom('_NET_WM_WINDOW_TYPE_NORMAL') in prop.value.tolist():
                        ###########
                #
                try:
                    # if not self.display.intern_atom("_NET_WM_STATE_SKIP_TASKBAR") in window.get_full_property(self.display.intern_atom("_NET_WM_STATE"), Xatom.ATOM).value:
                    _wst = window.get_full_property(self.display.intern_atom("_NET_WM_STATE"), Xatom.ATOM)
                    if _wst:
                        if self.display.intern_atom("_NET_WM_STATE_SKIP_TASKBAR") in _wst.value:
                            return
                    #
                    try:
                        _ppp = self.getProp(self.display, window,'DESKTOP')
                    except:
                        _ppp = [0]
                    if _ppp and _ppp[0]:
                        on_desktop = _ppp[0]
                    else:
                        on_desktop = 0
                    # the exec name
                    win_exec = "Unknown"
                    win_name_t = window.get_wm_class()
                    if win_name_t is not None:
                        win_exec = str(win_name_t[0])
                    # else:
                        # win_exec = "Unknown"
                    #
                    self.on_dock_items([w, on_desktop, win_exec])
                except:
                    pass

    
    # a window has been destroyed
    def delete_window_destroyed(self, window_list):
        is_changed = 0
        for w in self.wid_l:
            if w not in window_list:
                self.wid_l.remove(w)
                self.on_remove_win(w)
                #
                if PLAY_SOUND:
                    play_sound("window-close.wav")
                is_changed = 1
        # 
        # if is_changed or self.is_started:
            # if dock_width:
                # self.on_move_win()

    # 1
    # add or remove virtual desktops
    def on_virt_desk(self, ndesks):
        curr_ndesks = self.virtbox.count()
        n = ndesks - curr_ndesks
        if n > 0:
            for i in range(n):
                vbtn = QtWidgets.QPushButton()
                vbtn.setFlat(True)
                vbtn.setFixedSize(QtCore.QSize(int(dock_height*1.3), dock_height))
                # vbtn.setAutoExclusive(True)
                vbtn.setCheckable(True)
                #
                vbtn.clicked.connect(self.on_vbtn_clicked)
                vbtn.desk = (curr_ndesks + i)
                if virtual_desktops:
                    self.virtbox.addWidget(vbtn)
        elif n < 0:
            # remove the virtual desktop widget
            for i in range(abs(n)):
                item = self.virtbox.itemAt(curr_ndesks-1-i).widget()
                if isinstance(item, QtWidgets.QPushButton):
                    self.virtbox.removeWidget(item)
                    item.deleteLater()
        # check the button
        for i in range(self.virtbox.count()):
            item = self.virtbox.itemAt(i).widget()
            if isinstance(item, QtWidgets.QPushButton):
                if item.desk == self.active_virtual_desktop:
                    item.setChecked(True)
                else:
                    item.setChecked(False)
    
    #
    def _icon_name_from_desktop(self, _prog):
        execArgs = [" %f", " %F", " %u", " %U", " %d", " %D", " %n", " %N", " %k", " %v"]
        _app_dirs = app_dirs_system+app_dirs_user
        #
        for ddir in _app_dirs:
            if not os.path.exists(ddir):
                continue
            _list_d = os.listdir(ddir)
            for ffile in _list_d:
                if ffile.split(".")[-1] != "desktop":
                    continue
                file_path = os.path.join(ddir, ffile)
                try:
                    entry = DesktopEntry.DesktopEntry(file_path)
                    ftype = entry.getType()
                    if ftype != "Application":
                        continue
                    _exec = entry.getTryExec()
                    #
                    if not _exec:
                        # _exec = entry.getExec().split(" ")[0]
                        _exec_tmp = entry.getExec()
                        if _exec_tmp:
                            for aargs in execArgs:
                                if aargs in _exec_tmp:
                                    _exec_tmp = _exec_tmp.strip(aargs)
                            _exec = _exec_tmp.split()[0]
                    #
                    if _exec == _prog:
                        ficon = entry.getIcon()
                        if ficon:
                            return ficon
                except:
                    pass
        #
        return 0
            
    
    # 2
    # add a button
    def on_dock_items(self, pitem):
        if pitem[2] in SKIP_APP:
            return
        winid = pitem[0]
        self.wid_l.append(winid)
        #
        licon = None
        ret = self._icon_name_from_desktop(pitem[2])
        if ret:
            if QtGui.QIcon.hasThemeIcon(ret):
                licon = QtGui.QIcon.fromTheme(ret)
        #
        if not licon:
            window = self.display.create_resource_object('window', winid)
            icon_name_tmp = window.get_full_property(self.display.intern_atom('WM_ICON_NAME'), 0)
            #
            if icon_name_tmp:
                if hasattr(icon_name_tmp, "value"):
                    wicon = icon_name_tmp.value.decode()
                    if QtGui.QIcon.hasThemeIcon(wicon):
                        licon = QtGui.QIcon.fromTheme(wicon)
                    else:
                        icon_name_tmp = window.get_full_property(self.display.intern_atom('_NET_WM_ICON_NAME'), 0)
                        #
                        if icon_name_tmp:
                            if hasattr(icon_name_tmp, "value"):
                                wicon = icon_name_tmp.value.decode()
                                if QtGui.QIcon.hasThemeIcon(wicon):
                                    licon = QtGui.QIcon.fromTheme(wicon)
                                else:
                                    licon = None
            #
            if not licon:
                # window = self.display.create_resource_object('window', winid)
                #
                win_name_class_tmp = window.get_wm_class()
                if not win_name_class_tmp:
                    win_name_class = ""
                else:
                    win_name_class = win_name_class_tmp[0]
                #
                if win_name_class and QtGui.QIcon.hasThemeIcon(win_name_class):
                    licon = QtGui.QIcon.fromTheme(win_name_class)
                #
                if not licon:
                    icon_icon = window.get_full_property(self.display.intern_atom('_NET_WM_ICON'), 0)
                    #
                    icon_data = None
                    target = button_size
                    icon_lista = []
                    if icon_icon is not None:
                    # if not licon:
                        data = icon_icon.value[:]
                        icon_width  = data[0]
                        icon_height = data[1]
                        icon_image  = data[2:data[0]*data[1]+2].tobytes()  
                        icon_data = [icon_width,icon_height,icon_image]
                        #
                        w = 0
                        h = 0
                        len_data = len(data)
                        datat = data
                        ii = 1
                        while ii:
                            len_data = len(datat)
                            w = datat[0]
                            h = datat[1]
                            icon_lista.append([w, h])
                            if (w*h+2) < len_data: 
                                if datat[w*h+2] > 0:
                                    datat = datat[w*h+2:]
                            else:
                                ii = 0
                        #
                        if icon_lista:
                            item_idx = -1
                            if target > max(icon_lista)[0]:
                                target = max(icon_lista)[0]
                            for item in icon_lista:
                                if item[0] > (target - 1):
                                    item_idx = icon_lista.index(item)
                                    break
                            if item_idx > -1:
                                start_idx = 0
                                for i in range(item_idx):
                                    ww = icon_lista[i][0]
                                    hh = icon_lista[i][1]
                                    i_size = (ww*hh+2)
                                    start_idx += i_size
                            #
                            dataa = data[start_idx:]
                            wa = dataa[0]
                            ha = dataa[1]
                            icon_image = dataa[2:dataa[0]*dataa[1]+2].tobytes()
                            icon_data = [wa, ha, icon_image]

                            #### pbtn.setIcon(picon)
                            if icon_data:
                                w = icon_data[0]
                                h = icon_data[1]
                                img = icon_data[2]
                                image = QtGui.QImage(img, w, h, QtGui.QImage.Format_ARGB32)
                            else:
                                image = QtGui.QImage("icons/unknown.svg")
                        else:
                            image = QtGui.QImage("icons/unknown.svg")
                        #
                        pixmap = QtGui.QPixmap(image)
                        licon = QtGui.QIcon(pixmap)
        #
        btn = QtWidgets.QPushButton()
        btn.setCheckable(True)
        btn.setFlat(True)
        ############
        hpalette = self.palette().dark().color().name()
        csaa = ("QPushButton::checked { border: none;")
        csab = ("background-color: {};".format(hpalette))
        csac = ("border-radius: 2px; border-style: outset; padding: 0px;")
        csad = ("text-align: center; }")
        #
        csae = ("QPushButton { text-align: center; padding: 0px;}")
        csaf1 = ("QPushButton::hover:!pressed {")
        if button_background_color:
            csaf2 = ("background-color: {};".format(button_background_color))
        else:
            btn_bg_clr = self.palette().highlight().color().name()
            csaf2 = ("background-color: {};".format(btn_bg_clr))
        csaf3 = ("border-radius: 2px;"
        "border-style: outset;"
        "padding: 0px;"
        "text-align: center;"
        "padding: 0px;"
        "}")
        csaf = csaf1+csaf2+csaf3
        csa = csaa+csab+csac+csad+csae+csaf
        btn.setStyleSheet(csa)
        ###########
        # btn.setAutoExclusive(True)
        btn.clicked.connect(self.on_btn_clicked)
        # btn.setFixedSize(QtCore.QSize(dock_height, dock_height))
        btn.setFixedSize(QtCore.QSize(button_size, button_size))
        btn.setIcon(licon)
        # btn.setIconSize(QtCore.QSize(dock_height-8, dock_height-8))
        btn.setIconSize(QtCore.QSize(button_size-button_padding, button_size-button_padding))
        # btn.setMinimumSize(QtCore.QSize(button_size, button_size))
        btn.winid = pitem[0]
        btn.desktop = pitem[1]
        btn.pexec = pitem[2]
        btn.installEventFilter(self)
        #
        if pitem[1] == 0 or pitem[1] == None:
            self.ibox.addWidget(btn)
        elif pitem[1] > 0:
            self.ibox.insertWidget(pitem[1] * 100, btn)
        #
        if PLAY_SOUND:
            play_sound("window-new.wav")
        #
        btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        btn.customContextMenuRequested.connect(self.btnClicked)
    
    # 3
    # get the active window when this program starts
    # set checked the button
    def get_active_window_first(self):
        window_id_temp = self.root.get_full_property(self.display.intern_atom('_NET_ACTIVE_WINDOW'), X.AnyPropertyType)
        #
        if window_id_temp == None:
            return
        #
        if window_id_temp.value.tolist() == []:
            return
        #
        if window_id_temp:
            window_id = window_id_temp.value[0]
            for i in range(self.ibox.count()):
                item = self.ibox.itemAt(i).widget()
                if not item:
                    continue
                if isinstance(item, QtWidgets.QPushButton):
                    if item.winid == window_id:
                        item.setChecked(True)
                        self.taskb_btn = item
                        break
    
    # 4
    def on_btn_clicked(self):
        btn = self.sender()
        #
        # same virtual desktop
        if btn.desktop != self.active_virtual_desktop:
            ewmh.setCurrentDesktop(btn.desktop)
            ewmh.display.flush()
        #
        window = self.display.create_resource_object('window', btn.winid)
        active_window_id = self.root.get_full_property(self.display.intern_atom('_NET_ACTIVE_WINDOW'), X.AnyPropertyType).value[0]
        ## its the actual active window, minimize
        if btn.winid == active_window_id:
            # 1 add - 2 toggle - 0 remove
            # self.NET_WM_STATE = self.display.intern_atom("_NET_WM_STATE")
            # self.WM_HIDDEN = self.display.intern_atom("_NET_WM_STATE_HIDDEN")
            self.WM_CHANGE_STATE = self.display.intern_atom("WM_CHANGE_STATE")
            #
            # wm_state = self.NET_WM_STATE
            # wm_state2 = self.WM_HIDDEN
            # _data = [2, wm_state2, 0, 0, 0]
            wm_state3 = self.WM_CHANGE_STATE
            _data = [3, 0, 0, 0, 0]
            sevent = pe.ClientMessage(
            window = window,
            client_type = wm_state3,
            data=(32, (_data))
            )
            mask = (X.SubstructureRedirectMask | X.SubstructureNotifyMask)
            self.root.send_event(event=sevent, event_mask=mask)
            self.display.flush()
            self.display.sync()
        # raise and or bring to top
        else:
            wm_state = self.display.intern_atom("_NET_WM_STATE")
            _atm = self.display.intern_atom('_NET_ACTIVE_WINDOW')
            # _data = [1, X.CurrentTime,window.id,0,0]
            _data = [0,0,0,0,0]
            sevent = pe.ClientMessage(
            window = window,
            client_type = _atm,
            data=(32, (_data))
            )
            mask = (X.SubstructureRedirectMask | X.SubstructureNotifyMask)
            self.root.send_event(event=sevent, event_mask=mask)
            self.display.flush()
            self.display.sync()
            # return
        # # different virtual desktop
        # else:
            # # change the virtual desktop
            # if btn.desktop:
                # if btn.desktop >= 0:
                    # ewmh.setCurrentDesktop(btn.desktop)
                    # ewmh.display.flush()
            # # needed
            # ewmh.display.sync()
            # # self.get_active_window()
            
            #############
    
    # 5    
    # get the active window
    def get_active_window(self):
        # return
        window_id_temp = self.root.get_full_property(self.display.intern_atom('_NET_ACTIVE_WINDOW'), X.AnyPropertyType)
        if window_id_temp == None:
            return
        if window_id_temp.value.tolist() == []:
            return
        if window_id_temp:
            window_id = window_id_temp.value[0]
            # no active window
            if window_id == 0:
                # self.fake_btn.setChecked(True)
                if self.taskb_btn:
                    self.taskb_btn.setChecked(False)
                self.taskb_btn = None
            #
            else:
                window = self.display.create_resource_object('window', window_id)
                is_found = 0
                for i in range(self.ibox.count()):
                    btn = self.ibox.itemAt(i).widget()
                    if isinstance(btn, QtWidgets.QPushButton):
                        if btn.winid == window_id:
                            if self.taskb_btn:
                                self.taskb_btn.setChecked(False)
                                self.taskb_btn = None
                            btn.setChecked(True)
                            self.taskb_btn = btn
                            is_found = 1
                            # # remove urgency
                            # if btn in self.list_uitem:
                                # self.list_uitem.remove(btn)
                                # btn.setStyleSheet("border-color: {}; border=none".format(self.palette().color(QtGui.QPalette.Background).name()))
                            #
                            break
                if not is_found:
                    # in case no window has been activated
                    # self.fake_btn.setChecked(True)
                    if self.taskb_btn:
                        self.taskb_btn.setChecked(False)
                    self.taskb_btn = None
        
    # 6
    # remove the buttons
    def on_remove_win(self, pitem):
        ibox_num = self.ibox.count()
        for i in range(ibox_num):
            item = self.ibox.itemAt(i).widget()
            if isinstance(item, QtWidgets.QPushButton):
                winid = item.winid
                if pitem == winid:
                    self.ibox.removeWidget(item)
                    item.deleteLater()
                    break
    
    # check if the application is already in the launcher
    def on_pin(self, pexec):
        if pexec == "Unknown":
            return 0
        ## add the applications to prog_box
        progs = os.listdir("applications")
        if progs:
            for ffile in progs:
                entry = DesktopEntry.DesktopEntry(os.path.join("applications", ffile))
                pgexec_temp = ""
                try:
                    pgexec_temp = entry.getTryExec()
                except:
                    pass
                if pgexec_temp:
                    pgexec = os.path.basename(pgexec_temp)
                else:
                    pgexec = entry.getExec().split()[0]
                # the program is already pinned
                if pgexec == pexec:
                    return 0
            #
            return 1
        #
        else:
            return 1
        
    # add the application in the launcher
    def on_pin_add_pin(self, pexec):
        app_dirs = app_dirs_system+app_dirs_user
        # full desktop file path - exec - name - icon
        app_found = []
        # args to remove from the exec entry
        execArgs = [" %f", " %F", " %u", " %U", " %d", " %D", " %n", " %N", " %k", " %v"]
        for ddir in app_dirs:
            if os.path.exists(ddir):
                ffiles = os.listdir(ddir)
                for ffile in ffiles:
                    if ffile.split(".")[-1] != "desktop":
                        continue
                    #
                    try:
                        pgexec = None
                        entry = DesktopEntry.DesktopEntry(os.path.join(ddir, ffile))
                        pgexec = entry.getTryExec()
                        #
                        if not pgexec:
                            pgexeca = entry.getExec()
                            if pgexeca:
                                for aargs in execArgs:
                                    if aargs in pgexeca:
                                        pgexeca = pgexeca.strip(aargs)
                                pgexec = pgexeca.split()[0]
                        # 
                        if pgexec:
                            if os.path.basename(pgexec) == pexec:
                                fname = entry.getName()
                                ficon = entry.getIcon()
                                fpath = entry.getPath()
                                # desktop file - exec - name - icon - program path
                                app_found.append([os.path.join(ddir, ffile), pexec, fname, ficon or "unknown", fpath or ""])
                                break
                        else:
                            continue
                            # dlg = showDialog(1, "File desktop not found.", self)
                            # result = dlg.exec_()
                            # dlg.close()
                            # return
                    except Exception as E:
                        dlg = showDialog(1, str(E), self)
                        result = dlg.exec_()
                        dlg.close()
                        return
        #
        if len(app_found) == 1:
            # copy the application in the folder applications
            shutil.copy(app_found[0][0], "applications"+"/"+os.path.basename(app_found[0][0]))
            # add the button
            pbtn = QtWidgets.QPushButton()
            pbtn.setFlat(True)
            icon = app_found[0][3]
            fname = app_found[0][2]
            fpath = app_found[0][4]
            picon = QtGui.QIcon.fromTheme(icon)
            if picon.isNull():
                picon = QIcon(icon)
            if picon.isNull():
                picon = QIcon("icons/unknown.svg")
            pbtn.setFixedSize(QtCore.QSize(button_size, button_size))
            pbtn.setIcon(picon)
            pbtn.setIconSize(pbtn.size())
            pbtn.setToolTip(fname or pexec)
            pbtn.setIcon(picon)
            pbtn.pexec = app_found[0][1]
            pbtn.pdesktop = os.path.basename(app_found[0][0])
            pbtn.ppath = fpath
            self.prog_box.addWidget(pbtn)
            pbtn.clicked.connect(self.on_pbtn)
            pbtn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            pbtn.customContextMenuRequested.connect(self.pbtnClicked)
        elif len(app_found) > 1:
            idx = None
            dlg = chooseDialog(app_found, self)
            result = dlg.exec_()
            if result == QtWidgets.QDialog.Accepted:
                # index - string
                idx = int(dlg.getItem())
                dlg.close()
            else:
                dlg.close()
            if idx:
                shutil.copy(app_found[idx][0], "applications"+"/"+os.path.basename(app_found[idx][0]))
                # add the button
                pbtn = QtWidgets.QPushButton()
                pbtn.setFlat(True)
                icon = app_found[idx][3]
                fname = app_found[idx][2]
                if picon.isNull():
                    picon = QIcon(icon)
                if picon.isNull():
                    picon = QIcon("icons/unknown.svg")
                pbtn.setFixedSize(QtCore.QSize(button_size, button_size))
                pbtn.setIcon(picon)
                pbtn.setIconSize(pbtn.size())
                pbtn.setToolTip(fname or pexec)
                pbtn.setIcon(picon)
                pbtn.pexec = app_found[0][1]
                pbtn.pdesktop = os.path.basename(app_found[idx][0])
                pbtn.ppath = fpath
                self.prog_box.addWidget(pbtn)
                pbtn.clicked.connect(self.on_pbtn)
                pbtn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
                pbtn.customContextMenuRequested.connect(self.pbtnClicked)
        elif len(app_found) == 0:
            # message
            dlg = showDialog(1, "File desktop not found.", self)
            result = dlg.exec_()
            dlg.close()
    
    # right menu of each launcher program button
    def pbtnClicked(self, QPos):
        pbtn = self.sender()
        # create context menu
        self.pbtnMenu = QtWidgets.QMenu(self)
        self.unpin_prog = QtWidgets.QAction("Unpin")
        self.pbtnMenu.addAction(self.unpin_prog)
        self.unpin_prog.triggered.connect(lambda:self.on_unpin_prog(pbtn.pdesktop))
        # show context menu
        self.pbtnMenu.exec_(self.sender().mapToGlobal(QPos)) 
    
    # unpin the program from the launchbar
    def on_unpin_prog(self, pdesktop):
        try:
            os.remove("applications"+"/"+pdesktop)
            for i in range(len(self.prog_box)):
                item = self.prog_box.itemAt(i)
                if isinstance(item.widget(), QtWidgets.QPushButton):
                    widget = item.widget()
                    if widget.pdesktop == pdesktop:
                        item.widget().deleteLater()
                        break
        except Exception as E:
            # message
            dlg = showDialog(1, str(E), self)
            result = dlg.exec_()
            dlg.close()
    
    # right menu of each application button
    def btnClicked(self, QPos):
        self.right_button_pressed = 1
        btn = self.sender()
        # create context menu
        self.btnMenu = QtWidgets.QMenu(self)
        self.close_prog = QtWidgets.QAction("Close")
        self.btnMenu.addAction(self.close_prog)
        self.close_prog.triggered.connect(lambda:self.on_close_prog(btn))
        # 
        ret = self.on_pin(btn.pexec)
        if ret:
            self.pin_ac = QtWidgets.QAction("Pin")
            self.btnMenu.addAction(self.pin_ac)
            self.pin_ac.triggered.connect(lambda:self.on_pin_add_pin(btn.pexec))
        self.btnMenu.addSeparator()
        self.restart_app_action = QtWidgets.QAction("Reload")
        self.btnMenu.addAction(self.restart_app_action)
        self.restart_app_action.triggered.connect(self.restart)
        self.close_app_action = QtWidgets.QAction("Exit")
        self.btnMenu.addAction(self.close_app_action)
        self.close_app_action.triggered.connect(self.winClose)
        # show context menu
        self.btnMenu.exec_(btn.mapToGlobal(QPos)) 
        
    
    # def close_window(self, win):
    def on_close_prog(self, btn):
        win = self.display.create_resource_object('window', btn.winid)
        #
        _DELETE_PROTOCOL = 0
        #
        protc = win.get_wm_protocols()
        if protc:
            for iitem in protc.tolist():
                if iitem == self.display.intern_atom('WM_DELETE_WINDOW'):
                    _DELETE_PROTOCOL = 1
                    break
        #
        if _DELETE_PROTOCOL == 0:
            ppid = self.getProp(win, 'PID')
            if ppid:
                # 9 signal.SIGKILL - 15 signal.SIGTERM
                os.kill(ppid[0], 15)
                return
            #
            win.kill_client()
            return
        #
        c_type1 = self.display.intern_atom('WM_DELETE_WINDOW')
        c_type = self.display.intern_atom('WM_PROTOCOLS')
        data = (32, [c_type1, 0,0,0,0])
        sevent = pe.ClientMessage(
        window = win,
        client_type = c_type,
        data = data
        )
        self.display.send_event(win, sevent)
        # self.display.flush()
        self.display.sync()
    
    
    def eventFilter(self, widget, event):
        if isinstance(widget, QtWidgets.QPushButton):
            if event.type() == QtCore.QEvent.HoverEnter:
                if not self.right_button_pressed:
                    winid = widget.winid
                    window = self.display.create_resource_object('window', winid)
                    try:
                        win_name = window.get_full_property(self.display.intern_atom('_NET_WM_NAME'), 0).value
                        widget.setToolTip(str(win_name.decode(encoding='UTF-8')))
                    except: pass
        else:
            return False
        return super(SecondaryWin, self).eventFilter(widget, event)
    
    
    # the virtual desktop button
    def on_vbtn_clicked(self):
        self.sender().setChecked(True)
        vdesk = self.sender().desk
        # ewmh.setCurrentDesktop(vdesk)
        # ewmh.display.flush()
        # virtual desktops
        ctype = self.display.intern_atom('_NET_CURRENT_DESKTOP')
        data = [vdesk, X.CurrentTime, 0,0,0]
        ev = pe.ClientMessage(window=self.root, client_type=ctype, data=(32,(data)))
        #
        mask = (X.SubstructureRedirectMask|X.SubstructureNotifyMask)
        self.root.send_event(ev, event_mask=mask)
        self.display.flush()
        
    
    # # move the window when a button is added or removed
    # def on_move_win(self):
        # # if dock_width:
            # # QtWidgets.QApplication.processEvents()
            # # self.adjustSize()
            # # self.updateGeometry()
            # # # self.resize(self.sizeHint())
            # # self.resize(self.sizeHint().width(), dock_height)
        # #
        # # if self.position in [2,3]:
            # # pass
        # # el
        # if self.position in [0,1]:
            # # if dock_width:
                # # sx = int((self.screen_size.width() - self.size().width())/2)
            # # else:
            # sx = int((self.screen_size.width() - WINW)/2)
            # if sec_position == 0:
                # sy = 0
            # elif sec_position == 1:
                # if self.on_leave:
                    # sy = self.screen_size.height() - WINH
                # else:
                    # sy = self.screen_size.height() - reserved_space
            # # 
            # # if not fixed_position:
                # # self.move(sx, sy)
            # # else:
            # self.move(sx , sy - WINH)
    
    # # raise the dock
    # def enterEvent(self, event):
        # if not fixed_position:
            # if self.on_leave:
                # self.on_leave.stop()
                # self.on_leave.deleteLater()
                # self.on_leave = None
            # #
            # # if dock_width:
                # # sx = int((self.screen_size.width() - self.size().width())/2)
            # # else:
            # sx = int((self.screen_size.width() - WINW)/2)
            # if sec_position == 2:
                # sy = 0
            # elif sec_position == 3:
                # sy = self.screen_size.height() - WINH
            # # 
            # self.move(sx, sy)
            # # ewmh.setWmState(this_window, 0, '_NET_WM_STATE_BELOW')
            # # ewmh.setWmState(this_window, 1, '_NET_WM_STATE_ABOVE')
            # # ewmh.display.flush()
            # # ewmh.display.sync()
        # return super(SecondaryWin, self).enterEvent(event)

    # def leaveEvent(self, event):
        # if not fixed_position:
            # self.on_leave = QtCore.QTimer()
            # self.on_leave.timeout.connect(self.on_leave_event)
            # self.on_leave.start(2000)
        # return super(SecondaryWin, self).leaveEvent(event)
    
    # # lower the dock
    # def on_leave_event(self):
        # # ewmh.setWmState(this_window, 0, '_NET_WM_STATE_ABOVE')
        # # ewmh.setWmState(this_window, 1, '_NET_WM_STATE_BELOW')
        # #
        # # if dock_width:
            # # sx = int((self.screen_size.width() - self.size().width())/2)
        # # else:
        # sx = int((self.screen_size.width() - WINW)/2)
        # #
        # if sec_position == 2:
            # sy = 0
        # elif sec_position == 3:
            # sy = self.screen_size.height()
        # # 
        # self.move(sx, sy - reserved_space)
        # #
        # # ewmh.display.flush()
        # # ewmh.display.sync()
        # self.on_leave = None
    

############## TRAY

class trayThread(QtCore.QThread):
    sig = QtCore.pyqtSignal(list)
    
    def __init__(self, frame_id, bcolor, data_run, parent=None):
        super(trayThread, self).__init__(parent)
        self.frame_id = frame_id
        self.bcolor = bcolor
        self.data_run = data_run
        self.trays = []
        self.error   = error.CatchError()        # Error Handler/Suppressor
        #
        self.display = Display()                 # Display obj
        self.screen  = self.display.screen()     # Screen obj
        self.root    = self.screen.root          # Display root
        self._OPCODE = self.display.intern_atom("_NET_SYSTEM_TRAY_OPCODE")
        manager      = self.display.intern_atom("MANAGER")
        selection    = self.display.intern_atom("_NET_SYSTEM_TRAY_S%d" % self.display.get_default_screen())
        ## Selection owner window
        self.selowin = self.root.create_window(-1, -1, 1, 1, 0, self.screen.root_depth)
        # self.selowin = self.root.create_window(0, 0, tbutton_size, tbutton_size, 0, self.screen.root_depth)
        self.selowin.set_selection_owner(selection, X.CurrentTime)
        self.sendEvent(self.root, manager,[X.CurrentTime, selection, self.selowin.id], (X.StructureNotifyMask))
        #
        # tray icon background color
        colormap = self.screen.default_colormap
        self.background = colormap.alloc_named_color(self.bcolor).pixel
        #
        self.pid = -1
        self._is_unmap = None
        

    def sendEvent(self, win, ctype, data, mask=None):
        data = (data+[0]*(5-len(data)))[:5]
        ev = pe.ClientMessage(window=win, client_type=ctype, data=(32,(data)))
        #
        if not mask:
            mask = (X.SubstructureRedirectMask|X.SubstructureNotifyMask)
        self.root.send_event(ev, event_mask=mask)
    

    def loop(self, dsp, root, win):
        #
        while self.data_run:
            e = self.display.next_event()
            #
            if e.type == X.ConfigureNotify:
                e.window.configure(onerror=self.error, width=tbutton_size, height=tbutton_size)
            elif e.type == X.ClientMessage:
                if e.window == self.selowin:
                    data = e.data[1][1] # opcode
                    task = e.data[1][2] # taskid
                    if e.client_type == self._OPCODE and data == 0:
                        obj = dsp.create_resource_object("window", task)
                        ##
                        if e.window.id in self.trays:
                            self.sig.emit(["b", e.window.id])
                            continue
                        ########
                        obj.change_attributes(event_mask=(X.PropertyChangeMask | X.ExposureMask|X.StructureNotifyMask))
                        # tray icon background color - useless
                        obj.change_attributes(background_pixel = self.background)
                        #
                        self.trays.append(obj.id)
                        self.sig.emit(["a", obj.id])
                        # reset
                        self.pid = -1
            #
            elif e.type == X.UnmapNotify:
                self._is_unmap = e.window
            ## an applet is been removed from the systray
            elif e.type == X.DestroyNotify:
                # delete the object from the list if it is a member
                if e.window.id in self.trays:
                    self.trays.remove(e.window.id)
                    self.sig.emit(["b", e.window.id])
            #
            elif e.type == X.Expose:
                # for the tray apps messages
                if self._is_unmap:
                    if self._is_unmap == e.window:
                        self._is_unmap = None
                        continue
                #
                self.sig.emit(["c", e.window, self.background])
            # elif e.type == self.display.extension_event.DamageNotify:
                # print("damage for applet::", e)
            # properties
            elif (e.type == X.PropertyNotify):
                if e.atom == self.display.intern_atom("WM_ICON_NAME") or e.atom == self.display.intern_atom("_NET_WM_ICON_NAME") or e.atom == self.display.intern_atom("_NET_WM_USER_TIME"):
                    e.window.change_attributes(background_pixel = self.background)
                    self.display.flush()
                    self.display.sync()
            #
            if self.data_run == 0:
                break
        #
        if self.data_run == 0:
            return
    
    
    def run(self):
        while self.data_run:
            try:
                self.loop(self.display, self.root, self.selowin)
            except Exception as E:
                # print("Some problems with the systray:", str(E))
                pass
            #
            if self.data_run == 0:
                break
        #
        if self.data_run == 0:
            return

###################

class chooseDialog(QtWidgets.QDialog):
    def __init__(self, progs, parent):
        super().__init__(parent)
        self.setWindowTitle("Info")
        self.progs = progs
        QBtn = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        self.buttonBox = QtWidgets.QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        self.layout = QtWidgets.QVBoxLayout()
        message = QtWidgets.QLabel("Choose which application to add:")
        self.layout.addWidget(message)
        #
        self.TWD = QtWidgets.QTreeWidget()
        self.TWD.setHeaderLabels(["Applications"])
        self.TWD.setAlternatingRowColors(False)
        self.TWD.itemClicked.connect(self.fitem)
        self.layout.addWidget(self.TWD)
        #
        self.item_accepted = None
        for iitem in self.progs:
            idx = self.progs.index(iitem)
            tl = QtWidgets.QTreeWidgetItem([" ".join(iitem[1]), str(idx)])
            self.TWD.addTopLevelItem(tl)
        #
        self.layout.addWidget(self.buttonBox)
        #
        self.setLayout(self.layout)
        self.adjustSize()
        self.updateGeometry()
        self.resize(self.sizeHint())
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def fitem(self, item, col):
        self.item_accepted = item.text(1)
    
    def getItem(self):
        return self.item_accepted


class showDialog(QtWidgets.QDialog):
    def __init__(self, dtype, lcontent, parent):
        super().__init__(parent)
        
        self.setWindowTitle("Info")
        
        if dtype == 1:
            QBtn = QtWidgets.QDialogButtonBox.Ok
        elif dtype == 2:
            QBtn = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel

        self.buttonBox = QtWidgets.QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QtWidgets.QVBoxLayout()
        lay2 = QtWidgets.QHBoxLayout()
        self.layout.addLayout(lay2)
        licon = QtWidgets.QLabel()
        licon.setPixmap(QtGui.QPixmap("icons/user.png"))
        lay2.addWidget(licon)
        message = QtWidgets.QLabel(lcontent)
        lay2.addWidget(message, QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
        
        self.adjustSize()
        self.updateGeometry()
        self.resize(self.sizeHint())
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())



# menu
class menuWin(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(menuWin, self).__init__(parent)
        self.window = parent
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool)
        # self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint)
        ####### 
        self.mainBox = QtWidgets.QHBoxLayout()
        self.setLayout(self.mainBox)
        #
        sw = menu_width
        sh = 200
        sx = 0
        sy = 0
        #
        parent_geom = self.window.geometry()
        win_height = parent_geom.height()
        screensize = app.primaryScreen()
        #
        # if dock_position == 1:
        # left
        if use_menu == 1:
            if CENTRALIZE_EL == 1:
                sx = int((screensize.size().width() - menu_width)/2)
            elif CENTRALIZE_EL == 0:
                sx = parent_geom.x() + menu_padx
        # right
        elif use_menu == 2:
            sx = screensize.size().width() - menu_width - menu_padx
        #
        # if dock_position == 1:
            # sx += menu_padx
            # sy -= menu_pady
        # elif dock_position == 0:
            # pass
        #
        # self.setGeometry(sx,sy,sw,sh)
        #
        self.hbox = QtWidgets.QHBoxLayout()
        # 
        self.mainBox.setContentsMargins(2,2,2,2)
        self.mainBox.addLayout(self.hbox)
        #
        ##### left box
        self.lbox = QtWidgets.QVBoxLayout()
        self.lbox.setContentsMargins(0,0,0,0)
        self.hbox.addLayout(self.lbox)
        #
        self.listWidget = QtWidgets.QListWidget(self)
        self.listWidget.itemClicked.connect(self.listwidgetclicked)
        self.lbox.addWidget(self.listWidget)
        hpalette = self.palette().highlight().color().name()
        csaa = ("QListWidget::item:hover {")
        csab = ("background-color: {};".format(hpalette))
        csac = ("}")
        csa = csaa+csab+csac
        self.listWidget.setStyleSheet(csa)
        ###########
        cssa = ("QScrollBar:vertical {"
    "border: 0px solid #999999;"
    "background:white;"
    "width:8px;"
    "margin: 0px 0px 0px 0px;"
"}"
"QScrollBar::handle:vertical {")       
        cssb = ("min-height: 0px;"
    "border: 0px solid red;"
    "border-radius: 4px;"
    "background-color: {};".format(scroll_handle_col))
        cssc = ("}"
"QScrollBar::add-line:vertical {"       
    "height: 0px;"
    "subcontrol-position: bottom;"
    "subcontrol-origin: margin;"
"}"
"QScrollBar::sub-line:vertical {"
    "height: 0 px;"
    "subcontrol-position: top;"
    "subcontrol-origin: margin;"
"}")
        css = cssa+cssb+cssc
        self.listWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.listWidget.verticalScrollBar().setStyleSheet(css)
        ###########
        self.line_edit = QtWidgets.QLineEdit("")
        self.line_edit.setFrame(True)
        if search_field_bg:
            self.line_edit.setStyleSheet("background-color: {}".format(search_field_bg))
        #
        self.line_edit.textChanged.connect(self.on_line_edit)
        self.line_edit.setClearButtonEnabled(True)
        self.lbox.addWidget(self.line_edit)
        # self.line_edit.setFocus(True)
        self.listWidget.setFocus(True)
        self.listWidget.setIconSize(QtCore.QSize(menu_app_icon_size, menu_app_icon_size))
        ##### right box
        self.rbox = QtWidgets.QVBoxLayout()
        self.rbox.setContentsMargins(0,0,0,0)
        self.hbox.addLayout(self.rbox)
        #############
        self.fake_btn = QtWidgets.QPushButton()
        self.fake_btn.setCheckable(True)
        self.fake_btn.setAutoExclusive(True)
        self.rbox.addWidget(self.fake_btn)
        self.fake_btn.hide()
        #
        self.pref = QtWidgets.QPushButton("Bookmarks")
        self.pref.setIcon(QtGui.QIcon("icons/bookmark.svg"))
        self.pref.setIconSize(QtCore.QSize(menu_icon_size, menu_icon_size))
        self.pref.setFlat(True)
        #
        hpalette = self.palette().mid().color().name()
        csaa = ("QPushButton::hover:!pressed { border: none;")
        csab = ("background-color: {};".format(hpalette))
        csac = ("border-radius: 3px;")
        csad = ("text-align: left; }")
        csae = ("QPushButton { text-align: left;  padding: 5px;}")
        csaf = ("QPushButton::checked { text-align: left; ")
        csag = ("background-color: {};".format(self.palette().midlight().color().name()))
        csah = ("padding: 5px; border-radius: 3px;}")
        csa = csaa+csab+csac+csad+csae+csaf+csag+csah
        self.pref.setStyleSheet(csa)
        #
        # self.pref.setStyleSheet("QPushButton { text-align: left; }")
        # self.pref.setStyleSheet("text-align: left;")
        self.pref.setCheckable(True)
        self.pref.setAutoExclusive(True)
        self.pref.clicked.connect(self.on_pref_clicked)
        self.rbox.addWidget(self.pref)
        #############
        sepLine = QtWidgets.QFrame()
        sepLine.setFrameShape(QtWidgets.QFrame.HLine)
        sepLine.setFrameShadow(QtWidgets.QFrame.Plain)
        self.rbox.addWidget(sepLine)
        #
        self.rboxBtn = QtWidgets.QVBoxLayout()
        self.rboxBtn.setContentsMargins(0,0,0,0)
        self.rbox.addLayout(self.rboxBtn)
        #
        self.populate_menu()
        #
        self.rbox.addStretch(1)
        #
        sepLine2 = QtWidgets.QFrame()
        sepLine2.setFrameShape(QtWidgets.QFrame.HLine)
        sepLine2.setFrameShadow(QtWidgets.QFrame.Plain)
        sepLine2.setContentsMargins(0,0,0,0)
        self.rbox.addWidget(sepLine2)
        ##### buttons
        self.btn_box = QtWidgets.QHBoxLayout()
        # self.btn_box.setContentsMargins(0,0,0,2)
        self.rbox.addLayout(self.btn_box)
        ## custom commands
        self.commBtn = QtWidgets.QPushButton(QtGui.QIcon("icons/list-commands.svg"), "")
        self.commBtn.setFlat(True)
        self.commBtn.setStyleSheet("border: none;")
        self.commBtn.setIconSize(QtCore.QSize(service_icon_size, service_icon_size))
        self.commMenu = QtWidgets.QMenu()
        self.commMenu.setToolTipsVisible(True)
        self.commBtn.setMenu(self.commMenu)
        #
        if COMM1_COMMAND or COMM2_COMMAND or COMM3_COMMAND:
            # self.btn_box.addWidget(self.commBtn)
            #
            if COMM1_COMMAND:
                if COMM1_ICON:
                    icon = QtGui.QIcon(COMM1_ICON)
                    if icon.isNull():
                        icon = QtGui.QIcon("icons/none.svg")
                else:
                    icon = QtGui.QIcon("icons/none.svg")
                baction = self.commMenu.addAction(icon, COMM1_NAME, lambda:self._on_change(COMM1_COMMAND))
                if COMM1_TOOLTIP:
                    baction.setToolTip(COMM1_TOOLTIP)
            if COMM2_COMMAND:
                if COMM2_ICON:
                    icon = QtGui.QIcon(COMM2_ICON)
                    if icon.isNull():
                        icon = QtGui.QIcon("icons/none.svg")
                else:
                    icon = QtGui.QIcon("icons/none.svg")
                baction = self.commMenu.addAction(icon, COMM2_NAME, lambda:self._on_change(COMM2_COMMAND))
                if COMM2_TOOLTIP:
                    baction.setToolTip(COMM2_TOOLTIP)
            if COMM3_COMMAND:
                if COMM3_ICON:
                    icon = QtGui.QIcon(COMM3_ICON)
                    if icon.isNull():
                        icon = QtGui.QIcon("icons/none.svg")
                else:
                    icon = QtGui.QIcon("icons/none.svg")
                baction = self.commMenu.addAction(icon, COMM3_NAME, lambda:self._on_change(COMM3_COMMAND))
                if COMM3_TOOLTIP:
                    baction.setToolTip(COMM3_TOOLTIP)
        # self.combobtn.currentIndexChanged[str].connect(self._on_change) 
        #
        ## add custom applications
        if app_prog:
            self.menu_btn = QtWidgets.QPushButton()
            self.menu_btn.setFlat(True)
            self.menu_btn.setStyleSheet("border: none;")
            self.menu_btn.setToolTip("Modify the menu")
            self.menu_btn.setIcon(QtGui.QIcon("icons/menu.png"))
            self.menu_btn.setIconSize(QtCore.QSize(service_icon_size, service_icon_size))
            self.menu_btn.setFlat(False)
            #
            self.menu_btn.clicked.connect(self.f_appWin)
            self.btn_box.addWidget(self.menu_btn)
        # menu
        if COMM1_COMMAND or COMM2_COMMAND or COMM3_COMMAND:
            self.btn_box.addWidget(self.commBtn)
        # logout button
        if logout_command:
            self.lo_cmd_btn = QtWidgets.QPushButton()
            self.lo_cmd_btn.setFlat(True)
            self.lo_cmd_btn.setStyleSheet("border: none;")
            self.lo_cmd_btn.setToolTip("Logout")
            self.lo_cmd_btn.setIcon(QtGui.QIcon("icons/system-logout.svg"))
            self.lo_cmd_btn.setIconSize(QtCore.QSize(service_icon_size, service_icon_size))
            self.lo_cmd_btn.setFlat(False)
            #
            self.lo_cmd_btn.clicked.connect(lambda x: self._on_cmd_service("Logout?", logout_command))
            self.btn_box.addWidget(self.lo_cmd_btn)
        # restart button
        if restart_command:
            self.rs_cmd_btn = QtWidgets.QPushButton()
            self.rs_cmd_btn.setFlat(True)
            self.rs_cmd_btn.setStyleSheet("border: none;")
            self.rs_cmd_btn.setToolTip("Restart")
            self.rs_cmd_btn.setIcon(QtGui.QIcon("icons/system-restart.svg"))
            self.rs_cmd_btn.setIconSize(QtCore.QSize(service_icon_size, service_icon_size))
            self.rs_cmd_btn.setFlat(False)
            #
            self.rs_cmd_btn.clicked.connect(lambda x: self._on_cmd_service("Restart?", restart_command))
            self.btn_box.addWidget(self.rs_cmd_btn)
        # shutdown button
        if shutdown_command:
            self.st_cmd_btn = QtWidgets.QPushButton()
            self.st_cmd_btn.setFlat(True)
            self.st_cmd_btn.setStyleSheet("border: none;")
            self.st_cmd_btn.setToolTip("Shutdown")
            self.st_cmd_btn.setIcon(QtGui.QIcon("icons/system-shutdown.svg"))
            self.st_cmd_btn.setIconSize(QtCore.QSize(service_icon_size, service_icon_size))
            self.st_cmd_btn.setFlat(False)
            #
            self.st_cmd_btn.clicked.connect(lambda x: self._on_cmd_service("Shutdown?", shutdown_command))
            self.btn_box.addWidget(self.st_cmd_btn)
        #
        sepLine2 = QtWidgets.QFrame()
        sepLine2.setFrameShape(QtWidgets.QFrame.HLine)
        sepLine2.setFrameShadow(QtWidgets.QFrame.Plain)
        sepLine2.setContentsMargins(0,0,0,0)
        sepLine2.setStyleSheet("QFrame{border: None; background-color: transparent;}")
        self.rbox.addWidget(sepLine2)
        #
        self.hide()
        self.setGeometry(sx,sy,sw,sh)
        self.show()
        self.updateGeometry()
        #
        if dock_position == 1:
            sy = screensize.size().height() - parent_geom.height() - self.geometry().height() - menu_pady
        elif dock_position == 0:
            sy = parent_geom.height() + menu_pady
        self.move(sx,sy)
        #
        if self.window.cw_is_shown:
            self.window.cw_is_shown.close()
            self.window.cw_is_shown = None
        if self.window.cwin_is_shown:
            self.window.cwin_is_shown.close()
            self.window.cwin_is_shown = None
        #
        self.emulate_clicked(self.pref, 100)
        self.pref.setChecked(True)
        #
        if item_highlight_color:
            ics = "QListWidget:item::hover:!pressed { "+"background-color: {}".format(item_highlight_color)+";}"
            self.listWidget.setStyleSheet(ics)
        #
        self.listWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.listWidget.customContextMenuRequested.connect(self.itemClicked)
        # the bookmark button has been pressed
        self.itemBookmark = 1
        # while an item is been searching
        self.itemSearching = 0
        if LOST_FOCUS_CLOSE == 1:
            self.installEventFilter(self)
        #
        # self.setAttribute(QtCore.Qt.WA_X11NetWmWindowTypeDock)
    
    #
    # def custom_comm(self, comm):
    def _on_change(self, comm):
        self.close()
        self.window.mw_is_shown = None
        #
        _ret = 0
        if shutil.which(comm):
            try:
                subprocess.Popen(["{}".format(comm)])
            except Exception as E:
                _ret = str(E)
        #
        if _ret:
            dlg = showDialog(1, "Command not found: {}".format(_ret), self.window)
            result = dlg.exec_()
            if result == QtWidgets.QDialog.Accepted:
                dlg.close()
            else:
                dlg.close()
    
    #
    def _on_cmd_service(self, _msg, _cmd):
        self.close()
        self.window.mw_is_shown = None
        dlg = showDialog(2, _msg, self.window)
        result = dlg.exec_()
        _ret = 0
        if result == QtWidgets.QDialog.Accepted:
            try:
                subprocess.Popen(["{}".format(_cmd)])
            except Exception as E:
                _ret = str(E)
        #
        dlg.close()
        #
        if _ret:
            dlg = showDialog(1, "Command not found: {}".format(_ret), self.window)
            result = dlg.exec_()
            if result == QtWidgets.QDialog.Accepted:
                dlg.close()
            else:
                dlg.close()

    
    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.WindowDeactivate:
            if self.window.mw_is_shown:
                self.window.mw_is_shown.close()
                self.window.mw_is_shown = None
                return True
        return False
    
    #
    def f_appWin(self):
        os.system("{} &".format(app_prog))
        self.close()
        self.window.mw_is_shown = None
    
    # button category clicked
    def itemClicked(self, QPos):
        self.itemSearching = 0
        item_idx = self.listWidget.indexAt(QPos)
        _item = self.listWidget.itemFromIndex(item_idx)
        if _item == None:
            self.listWidget.clearSelection()
            self.listWidget.clearFocus()
            return
        if self.itemBookmark:
            self.listItemRightClickedToRemove(QPos)
        else:
            self.listItemRightClicked(QPos)
    
    def emulate_clicked(self, button, ms):
        QtCore.QTimer.singleShot(ms, button.clicked.emit)
    
    #
    def on_line_edit(self, text):
        self.listWidget.clear()
        self.fake_btn.setChecked(True)
        self.search_program(text)
        
    
    # seeking in the program lists
    def search_program(self, text):
        self.itemBookmark = 0
        self.itemSearching = 1
        if len(text) == 0:
            self.listWidget.clear()
            # self.emulate_clicked(self.pref, 100)
            # self.pref.setChecked(True)
        elif len(text) > 2:
            self.listWidget.clear()
            app_list = ["Development", "Education","Game",
                        "Graphics", "Multimedia", "Network",
                        "Office","Settings","System","Utility", "Other"]
            #
            for ell in app_list:
                if globals()[ell] == []:
                    continue
                for el in globals()[ell]:
                    if (text.casefold() in el[1].casefold()) or (text.casefold() in el[3].casefold()):
                        # exe_path = sh_which(el[1].split(" ")[0])
                        # file_info = QtCore.QFileInfo(exe_path)
                        # if exe_path:
                        # search for the icon by executable
                        icon = QtGui.QIcon.fromTheme(el[1])
                        if icon.isNull() or icon.name() == "":
                            # set the icon by desktop file - not full path
                            icon = QtGui.QIcon.fromTheme(el[2])
                            if icon.isNull() or icon.name() == "":
                                # set the icon by desktop file - full path
                                if os.path.exists(el[2]):
                                    icon = QtGui.QIcon(el[2])
                                    if icon.isNull():
                                        # set a generic icon
                                        icon = QtGui.QIcon("icons/none.svg")
                                        litem = QtWidgets.QListWidgetItem(icon, el[0])
                                        litem.picon = "none"
                                    else:
                                        litem = QtWidgets.QListWidgetItem(icon, el[0])
                                        litem.picon = el[2]
                                else:
                                    # set a generic icon
                                    icon = QtGui.QIcon("icons/none.svg")
                                    litem = QtWidgets.QListWidgetItem(icon, el[0])
                                    litem.picon = "none"
                            else:
                                litem = QtWidgets.QListWidgetItem(icon, el[0])
                                litem.picon = icon.name()
                        else:
                            litem = QtWidgets.QListWidgetItem(icon, el[0])
                            litem.picon = el[1]
                        
                        # set the exec name as property
                        litem.exec_n = el[1]
                        litem.ppath = el[4]
                        litem.setToolTip(el[3])
                        litem.tterm = el[5]
                        litem.fpath = el[6]
                        self.listWidget.addItem(litem)
                            #
                    self.listWidget.scrollToTop()
        else:
            self.listWidget.clear()
    
    # populate the main categories
    def populate_menu(self):
        # remove all widgets
        for i in reversed(range(self.rboxBtn.count())): 
            self.rboxBtn.itemAt(i).widget().deleteLater()
        #
        app_list = ["Development", "Education","Game",
                    "Graphics", "Multimedia", "Network",
                    "Office","Settings","System","Utility","Other"]
        for el in app_list:
            if globals()[el] == []:
                continue
            btn = QtWidgets.QPushButton(el)
            btn.setIcon(QtGui.QIcon("icons/{}".format(el+".svg")))
            btn.setIconSize(QtCore.QSize(menu_icon_size, menu_icon_size))
            btn.setFlat(True)
            # btn.setStyleSheet("QPushButton { text-align: left; }")
            btn.setStyleSheet("text-align: left;")
            ##########
            hpalette = self.palette().mid().color().name()
            csaa = ("QPushButton::hover:!pressed { border: none;")
            csab = ("background-color: {};".format(hpalette))
            csac = ("border-radius: 3px;")
            csad = ("text-align: left; }")
            csae = ("QPushButton { text-align: left;  padding: 5px;}")
            csaf = ("QPushButton::checked { text-align: left; ")
            csag = ("background-color: {};".format(self.palette().midlight().color().name()))
            csah = ("padding: 5px; border-radius: 3px;}")
            csa = csaa+csab+csac+csad+csae+csaf+csag+csah
            btn.setStyleSheet(csa)
            ##########
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            self.rboxBtn.addWidget(btn)
            btn.clicked.connect(self.on_btn_clicked)
            
    
    # category button clicked - populate the selected category
    def on_btn_clicked(self):
        # clear the search field
        if self.line_edit.text():
            self.line_edit.disconnect()
            self.line_edit.clear()
            self.line_edit.setClearButtonEnabled(False)
            self.line_edit.setClearButtonEnabled(True)
            self.line_edit.textChanged.connect(self.on_line_edit)
            self.itemSearching = 0
        #
        self.itemBookmark = 0
        cat_name = self.sender().text()
        # remove the ampersand eventually added by alien programs
        if "&" in cat_name:
            cat_name = cat_name.strip("&")
        #
        cat_list = globals()[cat_name]
        self.listWidget.clear()
        # 
        for el in cat_list:
            # 0 name - 1 executable - 2 icon - 3 comment - 4 path
            # exe_path = sh_which(el[1].split(" ")[0])
            # file_info = QtCore.QFileInfo(exe_path)
            #
            # if exe_path:
            # search for the icon by executable
            icon = QtGui.QIcon.fromTheme(el[1])
            if icon.isNull() or icon.name() == "":
                # set the icon by desktop file - not full path
                icon = QtGui.QIcon.fromTheme(el[2])
                if icon.isNull() or icon.name() == "":
                    # set the icon by desktop file - full path
                    if os.path.exists(el[2]):
                        icon = QtGui.QIcon(el[2])
                        if icon.isNull():
                            # set a generic icon
                            icon = QtGui.QIcon("icons/none.svg")
                            litem = QtWidgets.QListWidgetItem(icon, el[0])
                            litem.picon = "none"
                        else:
                            litem = QtWidgets.QListWidgetItem(icon, el[0])
                            litem.picon = el[2]
                    else:
                        # set a generic icon
                        icon = QtGui.QIcon("icons/none.svg")
                        litem = QtWidgets.QListWidgetItem(icon, el[0])
                        litem.picon = "none"
                else:
                    litem = QtWidgets.QListWidgetItem(icon, el[0])
                    litem.picon = icon.name()
            else:
                litem = QtWidgets.QListWidgetItem(icon, el[0])
                litem.picon = el[1]
            
            # set the exec name as property
            litem.exec_n = el[1]
            litem.ppath = el[4]
            litem.setToolTip(el[3])
            litem.tterm = el[5]
            litem.fpath = el[6]
            self.listWidget.addItem(litem)
                #
        self.listWidget.scrollToTop()
        self.listWidget.setFocus(True)
    
    # add the bookmark after right click
    def listItemRightClicked(self, QPos):
        # check if a bookmark is already present
        item_idx = self.listWidget.indexAt(QPos)
        _item = self.listWidget.itemFromIndex(item_idx)
        pret = self.check_bookmarks(_item)
        #
        self.listMenu= QtWidgets.QMenu()
        if pret == 1:
            item_b = self.listMenu.addAction("Add to bookmark")
        if SEND_TO_DESKTOP:
            item_d = self.listMenu.addAction("Send to the {}".format(DESKTOP_NAME))
        else:
            item_d = "None"
        if app_mod_prog:
            item_m = self.listMenu.addAction("Modify")
        else:
            item_m = "None"
        #
        action = self.listMenu.exec_(self.listWidget.mapToGlobal(QPos))
        if pret == 1 and action == item_b:
            item_idx = self.listWidget.indexAt(QPos)
            _item = self.listWidget.itemFromIndex(item_idx)
            if _item == None:
                return
            # 
            new_book = str(int(time.time()))
            icon_name = _item.picon
            # ICON - NAME - EXEC - TOOLTIP - PATH - TERMINAL
            new_book_content = """{0}
{1}
{2}
{3}
{4}
{5}""".format(icon_name, _item.text(), _item.exec_n, _item.toolTip() or _item.text(), _item.ppath, str(_item.tterm))
            with open(os.path.join("bookmarks", new_book), "w") as fbook:
                fbook.write(new_book_content)
        # send to the Desktop action
        elif action == item_d:
            item_idx = self.listWidget.indexAt(QPos)
            _item = self.listWidget.itemFromIndex(item_idx)
            item_name = _item.text()
            item_icon = _item.picon
            item_exec = _item.exec_n
            item_term = _item.tterm
            # create a desktop file
            dest_file = os.path.join(os.path.expanduser("~"), DESKTOP_NAME, item_name)
            with open(dest_file+".desktop", "w") as ff:
                ff.write("[Desktop Entry]\n")
                ff.write("Type=Application\n")
                ff.write("Name={}\n".format(item_name))
                ff.write("Exec={}\n".format(item_exec))
                ff.write("Icon={}\n".format(item_icon))
                ff.write("Terminal={}\n".format(item_term))
        # modify action
        elif action == item_m:
            item_idx = self.listWidget.indexAt(QPos)
            _item = self.listWidget.itemFromIndex(item_idx)
            # item desktop file full path
            item_fpath = _item.fpath
            os.system("{} {} &".format(app_prog, item_fpath))
        #
        self.listWidget.clearSelection()
        self.listWidget.clearFocus()
        self.listWidget.setFocus(True)
    
    # check whether the bookmark already exists
    def check_bookmarks(self, _item):
        is_found = 0
        if _item == None:
            return 1
        list_prog = os.listdir("bookmarks")
        if not list_prog:
            return 1
        for el in list_prog:
            cnt = []
            file_to_read = os.path.join("bookmarks", el)
            with open(file_to_read, "r") as f:
                cnt = f.readlines()
            #
            if cnt[2].strip("\n") == _item.exec_n:
                is_found = 1
        #
        if is_found:
            return 3
        else:
            return 1
    
    # execute the program from the menu
    def listwidgetclicked(self, item):
        # self.p = QtCore.QProcess()
        # self.p.setWorkingDirectory(os.getenv("HOME"))
        # # self.p.start(str(item.exec_n))
        # self.p.startDetached(str(item.exec_n))
        if item.tterm:
            tterminal = None
            if USER_TERMINAL:
                tterminal = USER_TERMINAL
            else:
                try:
                    tterminal = os.environ['TERMINAL']
                except KeyError:
                    pass
            #
            if not tterminal or not sh_which(tterminal):
                MyDialog("Error", "Terminal not found or not setted.", self)
                return
            else:
                try:
                    os.system("cd {} && {} -e {} & cd {}".format(str(item.ppath), tterminal, str(item.exec_n), os.getenv("HOME")))
                except Exception as E:
                    MyDialog("Error", "Terminal error: {}.".format(str(E)), self)
        else:
            if item.ppath:
                os.system("cd {} && {} & cd {} &".format(str(item.ppath), str(item.exec_n), os.getenv("HOME")))
            else:
                os.system("cd {} && {} &".format(os.getenv("HOME"), str(item.exec_n)))
        # close the menu window
        if self.window.mw_is_shown is not None:
            self.window.mw_is_shown.close()
            self.window.mw_is_shown = None
    
    # the bookmark button - populate
    def on_pref_clicked(self):
        # clear the search field
        if self.line_edit.text():
            self.line_edit.clear()
            self.itemSearching = 0
        #
        self.itemBookmark = 1
        self.listWidget.clear()
        # self.line_edit.clear()
        bookmark_files = os.listdir("bookmarks")
        prog_list = []
        #
        for bb in bookmark_files:
            with open(os.path.join("bookmarks",bb), "r") as fbook:
                cnt = fbook.readlines()
                # add the filename
                cnt.append(bb)
                prog_list.append(cnt)
        # populate listWidget
        # ICON - NAME - EXEC - TOOLTIP - PATH - TERMINAL
        for el in prog_list:
            ICON = el[0].strip("\n")
            NAME = el[1].strip("\n")
            EXEC = el[2].strip("\n")
            TOOLTIP = el[3].strip("\n")
            PATH = el[4].strip("\n")
            TTERM = el[5].strip("\n")
            # FILENAME = el[6].strip("\n")
            # # 
            # if len(el) > 5:
                # PATH_TEMP = el[4].strip("\n")
                # FILENAME = el[5].strip("\n")
                # if PATH_TEMP:
                    # PATH = PATH_TEMP
            # else:
                # FILENAME = el[4].strip("\n")
                # PATH = ""
            #
            # exe_path = sh_which(EXEC.split(" ")[0])
            # file_info = QtCore.QFileInfo(exe_path)
            # if file_info.exists():
                # if os.path.exists(ICON):
                    # icon = QtGui.QIcon(ICON)
                # else:
                    # icon = QtGui.QIcon.fromTheme(ICON)
                    # if icon.name() == "none":
                        # icon = QtGui.QIcon("icons/none.svg")
            icon = QtGui.QIcon.fromTheme(ICON)
            if icon.isNull():
                icon = QtGui.QIcon(icon)
            if icon.isNull():
                QtGui.QIcon("icons/none.svg")
            litem = QtWidgets.QListWidgetItem(icon, NAME)
            litem.lbookmark = bb
            litem.exec_n = EXEC
            litem.ppath = PATH
            litem.setToolTip(TOOLTIP)
            if TTERM == "True":
                litem.tterm = True
            else:
                litem.tterm = False
            self.listWidget.addItem(litem)
            #
        self.listWidget.sortItems(QtCore.Qt.AscendingOrder)
        self.listWidget.scrollToTop()
        if self.listWidget.count():
            self.listWidget.item(0).setSelected(False)
            self.listWidget.setFocus(True)
        
    #
    def listItemRightClickedToRemove(self, QPos):
        self.listMenuR= QtWidgets.QMenu()
        item_b = self.listMenuR.addAction("Remove from bookmark")
        action = self.listMenuR.exec_(self.listWidget.mapToGlobal(QPos))
        if action == item_b:
            item_idx = self.listWidget.indexAt(QPos)
            item_row = item_idx.row()
            _item = self.listWidget.item(item_row)
            item_removed = self.listWidget.takeItem(item_row)
            #
            try:
                os.remove(os.path.join("bookmarks",str(_item.lbookmark)))
            except:
                pass

# popup per calendar
class calendarWin(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(calendarWin, self).__init__(parent)
        self.window = parent
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool)
        # self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint)
        ####### box 
        mainBox = QtWidgets.QHBoxLayout()
        self.setLayout(mainBox)
        ## 
        self.hbox = QtWidgets.QHBoxLayout()
        mainBox.addLayout(self.hbox)
        self.hbox.setContentsMargins(2,2,2,2)
        mainBox.setContentsMargins(0,0,0,0)
        
        #### 
        self.vbox_1 = QtWidgets.QVBoxLayout()
        self.vbox_1.setContentsMargins(0,0,0,0)
        self.hbox.addLayout(self.vbox_1)
        #
        self.scroll = QtWidgets.QScrollArea()
        self.widget = QtWidgets.QWidget()
        self.vbox = QtWidgets.QVBoxLayout()
        self.widget.setLayout(self.vbox)
        # 
        self.ldatebox = QtWidgets.QHBoxLayout()
        self.ldatebox.setContentsMargins(0,0,0,0)
        self.vbox_1.addLayout(self.ldatebox)
        #
        tomonth = datetime.datetime.now().strftime("%B")
        toyear = str(datetime.datetime.now().year)
        #
        self.mlabel = QtWidgets.QLabel(tomonth+" "+toyear)
        self.mlabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.mlabel.setAlignment(QtCore.Qt.AlignCenter)
        self.mlabel.mousePressEvent = self.go_today 
        #
        self.pmonth = QtWidgets.QPushButton()
        self.pmonth.setIcon(QtGui.QIcon("icons/go-prev.png"))
        self.pmonth.setFlat(True)
        #
        self.nmonth = QtWidgets.QPushButton()
        self.nmonth.setIcon(QtGui.QIcon("icons/go-next.png"))
        self.nmonth.setFlat(True)
        #
        self.pmonth.clicked.connect(self.on_prev_month)
        self.nmonth.clicked.connect(self.on_next_month)
        #
        self.ldatebox.addWidget(self.pmonth)
        self.ldatebox.addWidget(self.mlabel)
        self.ldatebox.addWidget(self.nmonth)
        #
        self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedWidth(appointment_window_size)
        self.scroll.setWidget(self.widget)
        #
        cssa = ("QScrollBar:vertical {"
    "border: 0px solid #999999;"
    "background:white;"
    "width:8px;"
    "margin: 0px 0px 0px 0px;"
"}"
"QScrollBar::handle:vertical {")       
        cssb = ("min-height: 0px;"
    "border: 0px solid red;"
    "border-radius: 4px;"
    "background-color: {};".format(scroll_handle_col))
        cssc = ("}"
"QScrollBar::add-line:vertical {"       
    "height: 0px;"
    "subcontrol-position: bottom;"
    "subcontrol-origin: margin;"
"}"
"QScrollBar::sub-line:vertical {"
    "height: 0 px;"
    "subcontrol-position: top;"
    "subcontrol-origin: margin;"
"}")
        css = cssa+cssb+cssc
        self.scroll.setStyleSheet(css)
        #
        self.vbox_1.addWidget(self.scroll)
        
        ################ the calendar
        thisMonth = QtCore.QDate().currentDate().month()
        thisYear = QtCore.QDate().currentDate().year()
        l_e = []
        # 
        for ev in list_events_all:
            tdata = ev.DTSTART
            ttime = ("{}:{}".format(tdata[9:11], tdata[11:13]))
            tdate = QtCore.QDate.fromString(ev.DTSTART[0:8], 'yyyyMMdd')
            l_e.append((tdate, ttime+" "+ev.SUMMARY, ev.DESCRIPTION))
        #
        l_e.sort()
        ###
        self.calendar = Calendar(self, l_e, self.vbox)
        self.calendar.setContentsMargins(0,0,0,0)
        self.calendar.setNavigationBarVisible(False)
        self.calendar.setVerticalHeaderFormat(QtWidgets.QCalendarWidget.NoVerticalHeader)
        self.calendar.currentPageChanged.connect(self.calendar_month_changed)
        self.hbox.addWidget(self.calendar)
        self.show()
        #
        if self.window.mw_is_shown:
            self.window.mw_is_shown.close()
            self.window.mw_is_shown = None
        if self.window.cwin_is_shown:
            self.window.cwin_is_shown.close()
            self.window.cwin_is_shown = None
        #
        # cwWidth = self.width()
        # cwHeight = self.height()
        # cwX = int((WINW-cwWidth)/2)
        # win_height = self.window.size().height()
        # cwY = win_height
        #
        cwX = 0
        cwY = 0
        screensize = app.primaryScreen()
        #
        if use_clock == 1:
            cwX = clock_gapx
        if use_clock == 2:
            cwX = screensize.size().width() - self.width() - clock_gapx
        #
        if dock_position == 1:
            cwY = screensize.size().height() - self.height() - self.window.height() - clock_gapy
        elif dock_position == 0:
            cwY = self.window.height() + clock_gapy
        #
        self.setGeometry(cwX, cwY, -1,-1)
        #
        if LOST_FOCUS_CLOSE == 1:
            self.installEventFilter(self)
    
    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.WindowDeactivate:
            if self.window.cw_is_shown:
                self.window.cw_is_shown.close()
                self.window.cw_is_shown = None
                return True
        return False
    
    # selecting a day in the calendar could change the month view
    def calendar_month_changed(self, cyear, cmonth):
        tomonth = datetime.datetime(cyear, cmonth, 1).strftime("%B")
        self.mlabel.setText(tomonth+" "+str(cyear))
    
    #
    def go_today(self, e):
        to_day = QtCore.QDate().currentDate()
        self.calendar.setSelectedDate(to_day)
        tomonth = datetime.datetime.now().strftime("%B")
        toyear = str(datetime.datetime.now().year)
        self.mlabel.setText(tomonth+" "+toyear)
        
    #
    def on_prev_month(self):
        thisMonth = QtCore.QDate().currentDate().month()
        thisYear = QtCore.QDate().currentDate().year()
        selectedDate = self.calendar.selectedDate()
        selectedMonth = selectedDate.month()
        selectedYear = selectedDate.year()
        thisDay = 1
        if selectedMonth == 1:
            selectedYear -= 1
            selectedMonth = 13
        if (thisMonth == selectedMonth - 1) and (thisYear == selectedYear):
            thisDay = QtCore.QDate().currentDate().day()
        #
        self.calendar.setSelectedDate(QtCore.QDate(selectedYear, selectedMonth-1, thisDay))
        #
        nmonth2 = datetime.datetime.strptime(str(selectedMonth-1), '%m')
        nmonth = nmonth2.strftime('%B')
        self.mlabel.setText(str(nmonth)+" "+str(selectedYear))
    # 
    def on_next_month(self):
        thisMonth = QtCore.QDate().currentDate().month()
        thisYear = QtCore.QDate().currentDate().year()
        selectedDate = self.calendar.selectedDate()
        selectedMonth = selectedDate.month()
        selectedYear = selectedDate.year()
        thisDay = 1
        if selectedMonth == 12:
            selectedYear += 1
            selectedMonth = 0
        if (thisMonth == selectedMonth+1) and (thisYear == selectedYear):
            thisDay = QtCore.QDate().currentDate().day()
        #
        self.calendar.setSelectedDate(QtCore.QDate(selectedYear, selectedMonth+1, thisDay))
        #
        nmonth2 = datetime.datetime.strptime(str(selectedMonth+1), '%m')
        nmonth = nmonth2.strftime('%B')
        self.mlabel.setText(str(nmonth)+" "+str(selectedYear))
        

class ClickLabel(QtWidgets.QLabel):
    # clicked = QtCore.pyqtSignal()
    
    def mouseDoubleClickEvent(self, event):
        if event_command:
            try:
                # output format: 20220301
                cdate = self.cdate.toString('yyyyMMdd')
                subprocess.Popen([event_command, cdate])
            except:
                pass
            # except Exception as E:
                # MyDialog("Error", str(E), self)
        # self.clicked.emit()
        QtWidgets.QLabel.mousePressEvent(self, event)      



class Calendar(QtWidgets.QCalendarWidget):
  
    # constructor
    def __init__(self, parent=None, c_dict=None, vbox=None):
        super(Calendar, self).__init__(parent)
        self.parent = parent
        self.events = c_dict
        self.cvbox = vbox
        self.color3 = QtGui.QColor(calendar_appointment_day_color)
        if citem_highlight_color:
            ics = "QTableView{selection-background-color: "+"{}".format(citem_highlight_color)+"}"
            self.setStyleSheet(ics)
        # day in the month - single click
        self.clicked.connect(self.showDate)
        # day in the month - double click
        self.activated.connect(self.activatedDate)
        # year or month changed by user
        self.currentPageChanged.connect(self.pageChanded)
        # today
        c_today = self.selectedDate()
        self.popCalEv(c_today)
        #
        self.vw = self.findChild(QtWidgets.QTableView)
        self.vw.viewport().installEventFilter(self)
        #
    
    #
    def popCalEv(self, date):
        # remove all the existent widgets
        for i in reversed(range(self.cvbox.count())): 
            w = self.cvbox.itemAt(i).widget()
            if w is not None:
                w.deleteLater()
        #
        self.cvbox.addStretch()
        self.events_date = []
        for item in self.events:
            self.events_date.append(item[0])
            if item[0] == date:
                label = ClickLabel()
                label.setText(appointment_char+" "+item[1])
                label.cdate = item[0]
                label.setWordWrap(True)
                label.setStyleSheet(""" QLabel {0}
                      border: {1}px solid;                                                                                                            
                      border-radius: {2}px;
                      border-color: {3}; {4}                                                                                                                
                      """.format("{", appointment_border_size, appointment_border_radius, appointment_border_color, "}")) 
                label.setToolTip(item[2])
                self.cvbox.addWidget(label)
    
    # day of the month changed by user
    def showDate(self, date):
        self.popCalEv(date)
    
    #
    def activatedDate(self, date):
        if date_command:
            try:
                # output format: 20220301
                cdate = date.toString('yyyyMMdd')
                subprocess.Popen([date_command, cdate])
            except:
                pass
            # except Exception as E:
                # MyDialog("Error", str(E), self)
    
    def pageChanded(self, year, month):
        date = self.selectedDate()
        self.popCalEv(date)
    
    def paintCell(self, painter, rect, date):
        super().paintCell(painter, rect, date)
        if date in self.events_date:
            psize = 20
            startPoint = QtCore.QPoint(rect.x()+rect.width(), rect.y()+rect.height()-psize)
            controlPoint1 = QtCore.QPoint(rect.x()+rect.width(), rect.y()+rect.height())
            controlPoint2 = QtCore.QPoint(rect.x()+rect.width()-psize, rect.y()+rect.height())
            endPoint = QtCore.QPoint(rect.x(), rect.y())
            #
            path = QtGui.QPainterPath(startPoint)
            path.lineTo(controlPoint1)
            path.lineTo(controlPoint2)
            painter.fillPath(path, self.color3)


################
if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    #
    if tray_already_used:
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("Tray already in use.")
        msg.setInformativeText("The tray will be disabled.")
        msg.setWindowTitle("Info")
        msg.exec_()
    ########### sec_window
    sec_position = 1
    sec_window = SecondaryWin(sec_position)
    sec_window.setWindowFlags(sec_window.windowFlags() | QtCore.Qt.WindowDoesNotAcceptFocus)
    sec_window.setAttribute(QtCore.Qt.WA_AlwaysShowToolTips, True)
    sec_window.setAttribute(QtCore.Qt.WA_X11NetWmWindowTypeDock)
    screen = app.primaryScreen()
    size = screen.size()
    # if dock_width:
        # WINW = dock_width
    # else:
    WINW = size.width()
    WINH = dock_height
    this_windowID = int(sec_window.winId())
    _display = Display()
    this_window = _display.create_resource_object('window', this_windowID)
    # always above
    ewmh.setWmState(this_window, 1, '_NET_WM_STATE_ABOVE')
    ewmh.display.flush()
    #
    # # _NET_WM_DESKTOP 0xFFFFFFFF indicates that the window SHOULD appear on all desktops.
    # wm_state = _display.intern_atom('_NET_WM_DESKTOP')
    # _data = [0xFFFFFFFF,0,0,0,0]
    # #
    # sevent = pe.ClientMessage(
            # window = this_window,
            # client_type = wm_state,
            # data=(32, (_data))
            # )
    # mask = (X.SubstructureRedirectMask | X.SubstructureNotifyMask)
    # _display.screen().root.send_event(event=sevent, event_mask=mask)
    # _display.flush()
    #
    # reserved space
    L = 0
    R = 0
    T = 0
    B = 0
    #
    if dock_position == 1:
        B = dock_height
        # 
        this_window.change_property(_display.intern_atom('_NET_WM_STRUT'),
                                    _display.intern_atom('CARDINAL'),
                                    32, [L, R, T, B])
        # #
        # x = 0
        # # y = x+WINW-1
        # y = WINH - dock_height
        # # left, right, top, bottom,
        # # left_start_y, left_end_y, right_start_y, right_end_y,
        # # top_start_x, top_end_x, bottom_start_x, bottom_end_x
        # this_window.change_property(_display.intern_atom('_NET_WM_STRUT_PARTIAL'),
                            # _display.intern_atom('CARDINAL'), 32,
                           	# [L, R, T, B, 0, 0, 0, 0, x, y, T, B],
                           	# X.PropModeReplace)
    elif dock_position == 0:
        T = dock_height
        # 
        this_window.change_property(_display.intern_atom('_NET_WM_STRUT'),
                                    _display.intern_atom('CARDINAL'),
                                    32, [L, R, T, B])
        # #
        # x = 0
        # y = 0
        # lys1 = 0
        # lye1 = 0
        # rys = 0
        # rye = 0
        # tsx = 0
        # tex = 0
        # # left, right, top, bottom,
        # # left_start_y, left_end_y, right_start_y, right_end_y,
        # # top_start_x, top_end_x, bottom_start_x, bottom_end_x
        # this_window.change_property(_display.intern_atom('_NET_WM_STRUT_PARTIAL'),
                            # _display.intern_atom('CARDINAL'), 32,
                           	# [L, R, T, B, 0, 0, 0, 0, x, y, T, B],
                           	# X.PropModeReplace)
    
    
    # this_window.change_property(_display.intern_atom("_NET_WM_WINDOW_TYPE"),
    #         Xatom.ATOM, 32, [_display.intern_atom("_NET_WM_WINDOW_TYPE_DOCK")])
    
    _display.sync()
    #
    # sec_window.show()
    #
    sx = 0
    if dock_position == 1:
        sy = size.height() - dock_height
    elif dock_position == 0:
        sy = 0
    sw = WINW
    sh = WINH
    sec_window.setGeometry(sx, sy, sw, sh)
    #
    sec_window.show()
    #
    #############
    # # move and center the window
    # if sec_position in [2, 3]:
        # pass
    # elif sec_position in [0,1]:
        # sx = int((size.width() - WINW)/2)
        # if not fixed_position:
            # if sec_position == 0:
                # sy = 0
            # elif sec_position == 1:
                # sy = size.height() - WINH
        # else:
            # sy = size.height() - WINH
        # # 
        # sec_window.resize(WINW, WINH)
        # sec_window.move(sx, sy)
        # sec_window.setMaximumWidth(size.width())
    ############
    # set new style globally
    if theme_style:
        s = QtWidgets.QStyleFactory.create(theme_style)
        app.setStyle(s)
    # set the icon style globally
    if icon_theme:
        QtGui.QIcon.setThemeName(icon_theme)
    ################
    # some applications has been added or removed
    def directory_changed(edir):
        global menu_is_changed
        menu_is_changed += 1
        if menu_is_changed == 1:
            on_directory_changed()
    # check for changes in the application directories
    fPath = app_dirs_system + app_dirs_user
    fileSystemWatcher = QtCore.QFileSystemWatcher(fPath)
    fileSystemWatcher.directoryChanged.connect(directory_changed)
    ################
    # ewmh.setWmState(this_window, 1, '_NET_WM_STATE_STICKY')
    # ewmh.setWmState(this_window, 1, '_NET_WM_STATE_SKIP_TASKBAR')
    # ewmh.setWmState(this_window, 1, '_NET_WM_STATE_SKIP_PAGER')
    # ewmh.display.flush()
    # ewmh.display.sync()
    ################
    # 
    ret = app.exec_()
    stopCD = 1
    sys.exit(ret)
    
################################## END #################################
