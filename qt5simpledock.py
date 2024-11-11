#!/usr/bin/env python3

# 0.9.42

from PyQt5.QtCore import (QThread,pyqtSignal,Qt,QTimer,QTime,QDate,QSize,QRect,QCoreApplication,QEvent,QPoint,QFileSystemWatcher,QProcess,QFileInfo,QFile,QDateTime)
from PyQt5.QtWidgets import (QWidget,QHBoxLayout,QBoxLayout,QLabel,QPushButton,QSizePolicy,QMenu,QVBoxLayout,QTabWidget,QListWidget,QScrollArea,QListWidgetItem,QDialog,QMessageBox,QMenu,qApp,QAction,QDialogButtonBox,QTreeWidget,QTreeWidgetItem,QDesktopWidget,QLineEdit,QFrame,QCalendarWidget,QTableView,QStyleFactory,QApplication,QButtonGroup,QRadioButton,QSlider,QTextEdit,QTextBrowser,QDateTimeEdit,QCheckBox,QComboBox)
from PyQt5.QtGui import (QFont,QIcon,QImage,QPixmap,QPalette,QWindow,QColor,QPainterPath)
import sys, os, time
import shutil
from Xlib.display import Display
import Xlib
from Xlib import X, Xatom, Xutil, error
import Xlib.protocol.event as pe
import subprocess
from xdg import DesktopEntry
from xdg import IconTheme
from ewmh import EWMH
ewmh = EWMH()
from cfg_dock import *

QIcon.setFallbackSearchPaths(["/usr/share/pixmaps"])

if PLAY_SOUND == 2:
    from PyQt5.QtMultimedia import QSound

if use_clock or USE_NOTIFICATION:
    import datetime

if use_webcam:
    import pyudev
    import pyinotify
    _notifier = None

if button_size > dock_height:
    button_size = dock_height

app = None

WINW = 0
WINH = 0

curr_path = os.getcwd()

if USE_NOTIFICATION:
    if not os.path.exists(USE_NOTIFICATION):
        try:
            os.makedirs(USE_NOTIFICATION)
        except:
            USE_NOTIFICATION = 0

if USE_CLIPBOARD:
    from pathlib import Path
    from cfg_clipboard import *
    #
    STORE_IMAGES = STORE_IMAGES
    ccdir = os.getcwd()
    clips_path = os.path.join(ccdir, "clips")
    images_path = os.path.join(ccdir, "images")
    def cr_clips_images():
        if Path(clips_path).exists() == False:
            try:
                os.mkdir(clips_path)
            except Exception as E:
                app = QApplication(sys.argv)
                fm = firstMessage("Error", str(E)+"\n\n    Exiting...")
                sys.exit(app.exec_())
        #
        if Path(images_path).exists() == False:
            try:
                os.mkdir(images_path)
            except Exception as E:
                app = QApplication(sys.argv)
                fm = firstMessage("Error", str(E)+"\n\n    Exiting...")
                sys.exit(app.exec_())
    cr_clips_images()
    #
    CWINW = 600
    CWINH = 600
    try:
        ffile = open(os.path.join(ccdir, "clipprogsize.cfg"), "r")
        CWINW, CWINH = ffile.readline().split(";")
        CWINW = int(CWINW)
        CWINH = int(CWINH)
        ffile.close()
    except:
        CWINW = 600
        CWINH = 600
    #
    DWINW = 400
    DWINH = 400
    #
    try:
        ffile = open(os.path.join(ccdir, "previewsize.cfg"), "r")
        DWINW, DWINH = ffile.readline().split(";")
        DWINW = int(DWINW)
        DWINH = int(DWINH)
        ffile.close()
    except:
        DWINW = 400
        DWINH = 400
    #
    dialWidth = 500
    #
    # store each preview
    CLIPS_DICT = {}
    ### clips
    clips_temp = os.listdir(clips_path)
    for iitem in sorted(clips_temp, reverse=False):
        iitem_text = ""
        try:
            tfile = open(os.path.join(clips_path, iitem), "r")
            iitem_text = tfile.read()
            tfile.close()
        except Exception as E:
            app = QApplication(sys.argv)
            fm = firstMessage("Error", str(E)+"\n\n    Exiting...")
            sys.exit(app.exec_())
        #
        if len(iitem_text) > int(CHAR_PREVIEW):
            text_prev = iitem_text[0:int(CHAR_PREVIEW)]+" [...]"
            CLIPS_DICT[iitem] = [text_prev]
        else:
            CLIPS_DICT[iitem] = [iitem_text]
    #

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

# this_window = None
this_windowID = None

### TRAY
TRAY            = 1
tray_already_used = 0
#############
stopCD = 0
data_run = 1

def play_sound(_sound):
    _sound = os.path.join(curr_path,"sounds",_sound)
    if PLAY_SOUND == 1:
        if not shutil.which(A_PLAYER):
            return
        command = [A_PLAYER, _sound]
        try:
            subprocess.Popen(command, 
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT)
        except: pass
    elif PLAY_SOUND == 2:
        QSound.play(_sound)
    return

# 
class winThread(QThread):
    
    sig = pyqtSignal(list)
    
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
            #
            if stopCD:
                break
        if stopCD:
            return


######################

# label executors
class label1Thread(QThread):
    
    label1sig = pyqtSignal(list)
    
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


class SecondaryWin(QWidget):
    
    webcam_signal = pyqtSignal(list)
    
    def __init__(self, position, _app, _close_signal, _parent):
        super(SecondaryWin, self).__init__()
        global app
        app = _app
        self.position = position
        self._close_signal = _close_signal
        self._parent = _parent
        #
        self.setWindowFlags(self.windowFlags() | Qt.WindowDoesNotAcceptFocus | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_X11NetWmWindowTypeDock)
        self.setAttribute(Qt.WA_AlwaysShowToolTips, True)
        self.setWindowTitle("qt5dock-1")
        #
        self._initializations()
        #
        self.display = Display()
        self.root = self.display.screen().root
        #
        self.is_started = 1
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
        # 0 top - 1 bottom
        if self.position in [0,1]:
            self.abox = QHBoxLayout()
            self.abox.setContentsMargins(0,0,0,0)
            self.abox.setSpacing(0)
            self.setLayout(self.abox)
            #
            self.labelw0_state = 0
            self.labelw0 = QLabel()
            self.labelw0.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
            self.abox.insertWidget(0, self.labelw0)
            self.labelw0.hide()
            self._on_label_0(label0_script,label0_interval,label0_use_richtext,label0_color,label0_font,label0_font_size,label0_font_weight,label0_font_italic,label0_command1,label0_command2)
            #
            ##### clock
            self.cw_is_shown = None
            if use_clock:
                self.cbox = QHBoxLayout()
                self.cbox.setContentsMargins(4,0,4,0)
                self.tlabel = QLabel("")
                tfont = QFont()
                if calendar_label_font:
                    tfont.setFamily(calendar_label_font)
                tfont.setPointSize(calendar_label_font_size)
                tfont.setWeight(calendar_label_font_weight)
                tfont.setItalic(calendar_label_font_italic)
                self.tlabel.setFont(tfont)
                if calendar_label_font_color:
                    self.tlabel.setStyleSheet("QLabel {0} color: {1};{2}".format("{", calendar_label_font_color, "}"))
                #
                self.cbox.addWidget(self.tlabel)
                #
                if USE_AP:
                    cur_time = QTime.currentTime().toString("hh:mm ap")
                else:
                    cur_time = QTime.currentTime().toString("hh:mm")
                if day_name:
                    curr_date = QDate.currentDate().toString("ddd d")
                    self.tlabel.setText(" "+curr_date+"  "+cur_time+" ")
                else:
                    self.tlabel.setText(" "+cur_time+" ")
                    self.tlabel.installEventFilter(self)
                #
                tfont = QFont()
                if clock_font:
                    tfont.setFamily(clock_font)
                if clock_font_size:
                    tfont.setPointSize(clock_font_size)
                if clock_font_weight:
                    tfont.setWeight(clock_font_weight)
                if clock_font_italic:
                    tfont.setItalic(clock_font_italic)
                #
                self.tlabel.setFont(tfont)
                #
                timer = QTimer(self)
                timer.timeout.connect(self.update_label)
                timer.start(60 * 1000)
                #
                self.tlabel.setContentsMargins(0,0,0,0)
                self.tlabel.mousePressEvent = self.on_tlabel
            ##########
            if CENTRALIZE_EL == 1 or CENTRALIZE_EL == 2:
                self.abox.addStretch(1)
            ## menu
            self.mw_is_shown = None
            if use_menu:
                self.mbtnbox = QHBoxLayout()
                self.mbtnbox.setContentsMargins(4,0,4,0)
                if use_menu == 1:
                    self.abox.insertLayout(3, self.mbtnbox)
                # the window menu
                self.mbutton = QPushButton(flat=True)
                self.mbutton.setStyleSheet("border: none;")
                self.mbutton.setFlat(True)
                self.mbutton.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
                self.mbutton.setIcon(QIcon("icons/menu.png"))
                self.mbutton.setIconSize(QSize(button_size, button_size))
                self.mbtnbox.addWidget(self.mbutton)
                self.mbutton.clicked.connect(self.on_click)
            #
            self.labelw3_state = 0
            self.labelw3 = QLabel()
            self.labelw3.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
            self.abox.insertWidget(4, self.labelw3)
            self.labelw3.hide()
            self._on_label_3(label3_script,label3_interval,label3_use_richtext,label3_color,label3_font,label3_font_size,label3_font_weight,label3_font_italic,label3_command1,label3_command2)
            #
            if USE_CUSTOM_WIDGET_LEFT:
                from widgets1 import widgets_left 
                self.abox.insertWidget(5, widgets_left())
            ## virtual desktop box
            if virtual_desktops:
                self.virtbox = QHBoxLayout()
                self.virtbox.setContentsMargins(0,0,0,0)
                self.virtbox.setSpacing(4)
                self.virtbox.desk = "v"
                self.abox.insertLayout(6, self.virtbox)
                #
                vbtn = QPushButton()
                vbtn.setFlat(True)
                vbtn.setCheckable(True)
                vbtn.setFixedSize(QSize(int(dock_height*1.3), dock_height))
                #
                self.virtbox.addWidget(vbtn)
                vbtn.desk = 0
                vbtn.clicked.connect(self.on_vbtn_clicked)
                self.on_virt_desk(self.num_virtual_desktops)
            #
            ## program box
            self.prog_box = QHBoxLayout()
            self.prog_box.setContentsMargins(4,0,4,0)
            self.prog_box.setSpacing(4)
            self.prog_box.desk = "p"
            self.abox.insertLayout(7, self.prog_box)
            #
            if tasklist_position == 0:
                sepLine1 = QFrame()
                sepLine1.setFrameShape(QFrame.VLine)
                sepLine1.setFrameShadow(QFrame.Plain)
                sepLine1.setContentsMargins(0,4,0,4)
                self.prog_box.addWidget(sepLine1)
            #
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
                    tterm = ""
                    tterm = entry.getTerminal()
                    #
                    self.pbtn = QPushButton()
                    self.pbtn.setStyleSheet("border: none;")
                    self.pbtn.setFlat(True)
                    picon = QIcon.fromTheme(icon)
                    if picon.isNull():
                        image = QImage(icon)
                        if image.isNull():
                            image = QImage("icons/unknown.svg")
                        pixmap = QPixmap(image)
                        picon = QIcon(pixmap)
                    #
                    self.pbtn.setIconSize(QSize(pbutton_size, pbutton_size))
                    self.pbtn.setIcon(picon)
                    self.pbtn.setToolTip(fname or pexec)
                    self.pbtn.pexec = pexec_temp
                    self.pbtn.pdesktop = ffile
                    self.pbtn.ppath = fpath
                    self.pbtn.tterm = tterm
                    self.prog_box.addWidget(self.pbtn, alignment=Qt.AlignCenter)
                    self.pbtn.clicked.connect(self.on_pbtn)
                    self.pbtn.setContextMenuPolicy(Qt.CustomContextMenu)
                    self.pbtn.customContextMenuRequested.connect(self.pbtnClicked)
            #
            self.sepLine2 = QFrame()
            self.sepLine2.setFrameShape(QFrame.VLine)
            self.sepLine2.setFrameShadow(QFrame.Plain)
            self.sepLine2.setContentsMargins(0,4,0,4)
            self.prog_box.addWidget(self.sepLine2)
            if len(progs) == 0:
                self.sepLine2.hide()
            #
            ## tasklist
            self.ibox = QHBoxLayout()
            # (int left, int top, int right, int bottom)
            _ipad = 0
            self.ibox.setContentsMargins(4,_ipad,4,_ipad)
            self.ibox.setSpacing(4)
            if tasklist_position == 0:
                self.ibox.setAlignment(Qt.AlignLeft)
            elif tasklist_position == 1:
                self.ibox.setAlignment(Qt.AlignCenter)
                if CENTRALIZE_EL == 0:
                    self.abox.addStretch(1)
            # the first virtual desktop
            self.ibox.desk = 0
            self.abox.insertLayout(9, self.ibox)
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
                    #
                    self.list_prog.append([winid, on_desktop, win_exec])
                except:
                    pass
        # windows in dock
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
        if CENTRALIZE_EL == 2 or CENTRALIZE_EL == 0:
            self.abox.addStretch(1)
        #
        self.labelw1_state = 0
        self.labelw1 = QLabel()
        self.labelw1.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        self.abox.insertWidget(11, self.labelw1)
        self.labelw1.hide()
        self._on_label_1(label1_script,label1_interval,label1_use_richtext,label1_color,label1_font,label1_font_size,label1_font_weight,label1_font_italic,label1_command1,label1_command2)
        #
        self.labelw2_state = 0
        self.labelw2 = QLabel()
        self.labelw2.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        self.abox.insertWidget(12, self.labelw2)
        self.labelw2.hide()
        self._on_label_2(label2_script,label2_interval,label2_use_richtext,label2_color,label2_font,label2_font_size,label2_font_weight,label2_font_italic,label2_command1,label2_command2)
        #
        # audio - 14
        # needed for right click event
        self.btn_audio = None
        if USE_AUDIO:
            self.audiobox = QHBoxLayout()
            self.audiobox.setContentsMargins(0,0,0,0)
            self.abox.insertLayout(14, self.audiobox)
            self.btn_audio = QPushButton()
            self.btn_audio.setFlat(True)
            self.btn_audio.setStyleSheet("border: none;")
            self.btn_audio.setIconSize(QSize(button_size, button_size))
            _icon = "audio-volume-muted"
            iicon = QIcon.fromTheme(_icon, QIcon("icons/audio-volume-muted.svg"))
            self.btn_audio.setIcon(iicon)
            self.btn_audio.setToolTip("No audio devices")
            self.audiobox.insertWidget(0, self.btn_audio)
            #
            self.btn_audio.winid = -999
            self.btn_audio.value = [-999, -999]
            self.btn_audio.installEventFilter(self)
            # left click menu
            self.mmenu = QMenu()
            self.maudiobox = QVBoxLayout()
            self.maudiobox.setContentsMargins(4,4,4,4)
            self.mmenu.setLayout(self.maudiobox)
            #
            self.mslider = QSlider(Qt.Horizontal)
            self.mslider.setFocusPolicy(Qt.StrongFocus)
            self.mslider.setTickPosition(QSlider.TicksBothSides)
            self.mslider.setMinimum(0)
            self.mslider.setMaximum(100)
            self.mslider.setTickInterval(10)
            self.mslider.setSingleStep(AUDIO_STEP)
            self.mslider.setPageStep(AUDIO_STEP)
            self.mslider.valueChanged.connect(self.on_vslider_changed)
            self.maudiobox.addWidget(self.mslider)
            self.mbtn = QPushButton("Volume control")
            self.mbtn.clicked.connect(self.on_mbtn_mixer)
            self.maudiobox.addWidget(self.mbtn)
            self.mmenu.adjustSize()
            self.mmenu.updateGeometry()
            # right click menu
            self.amenu = QMenu()
            self.laudiobox = QVBoxLayout()
            self.laudiobox.setContentsMargins(4,4,4,4)
            self.amenu.setLayout(self.laudiobox)
            #
            self.abtn = QPushButton("Set as default")
            self.abtn.clicked.connect(self.on_abtn_clicked)
            self.laudiobox.addWidget(self.abtn)
            # the stored sink in the file
            self.start_sink_name = None
            #
            import pulsectl as _pulse
            self.pulse = _pulse.Pulse()
            #
            # default sink name
            self.default_sink_name = None
            self.card_list = None
            # ??
            self.AUDIO_START_LEVEL = AUDIO_START_LEVEL
            self._on_start_vol()
            # needed for right click event
            self.btn_mic = None
            #
            # buttons style
            hpalette = self.palette().mid().color().name()
            csaa = ("QPushButton::hover:!pressed { border: none;")
            csab = ("background-color: {};".format(hpalette))
            csac = ("border-radius: 3px;")
            csad = ("text-align: center; }")
            csae = ("QPushButton { text-align: center;  padding: 5px; border: 1px solid #7F7F7F;")
            csae1 = ("background-color: '{}';".format(self.palette().midlight().color().name()))
            csae2 = (" }")
            csaf = ("QPushButton::checked { text-align: center; ")
            if button_menu_selected_color == "":
                csag = ("background-color: {};".format(self.palette().midlight().color().name()))
            else:
                csag = ("background-color: {};".format(button_menu_selected_color))
            csah = ("padding: 5px; border-radius: 3px;}")
            self.btn_csa = csaa+csab+csac+csad+csae+csae1+csae2+csaf+csag+csah
            self.abtn.setStyleSheet(self.btn_csa)
            self.mbtn.setStyleSheet(self.btn_csa)
            #
            if USE_MICROPHONE:
                #
                self.btn_mic = QPushButton()
                self.btn_mic.setFlat(True)
                self.btn_mic.setIconSize(QSize(button_size, button_size))
                self.btn_mic.setStyleSheet("border: none;")
                self.audiobox.insertWidget(1, self.btn_mic)
                self.btn_mic.winid = -666
                self.btn_mic.installEventFilter(self)
                self.btn_mic.hide()
                #
                _icon = "audio-input-microphone"
                iicon = None
                iicon = QIcon.fromTheme(_icon, QIcon("icons/audio-input-microphone.svg"))
                if iicon and not iicon.isNull():
                    self.btn_mic.setIcon(iicon)
                #
                # right click menu
                self.micmenu = QMenu()
                self.micbox = QVBoxLayout()
                self.micbox.setContentsMargins(4,4,4,4)
                self.micmenu.setLayout(self.micbox)
                #
                # self._on_start_mic()
                #
                self.on_microphone()
            #
            self.athread = audioThread(_pulse)
            self.athread.sig.connect(self.athreadslot)
            self.athread.start()
        #
        # clipboard
        if USE_CLIPBOARD:
            self.btn_clip = QPushButton(icon=QIcon("icons/qpasteboard.png"))
            self.btn_clip.setFlat(True)
            self.btn_clip.setIconSize(QSize(button_size-button_padding, button_size-button_padding))
            self.btn_clip.setStyleSheet("border: none;")
            self._is_clipboard_shown = 0
            self.actual_clip = None
            self.btn_clip.clicked.connect(self.on_clipboard)
            self.btn_clip.setContextMenuPolicy(Qt.CustomContextMenu)
            self.btn_clip.customContextMenuRequested.connect(self.on_clipboard2)
            #
            self.abox.insertWidget(15, self.btn_clip)
            #
            self.stop_tracking = 0
            app.clipboard().changed.connect(self.clipboardChanged)
            #
            self.menu = QMenu()
            #
            self.settingAction = self.menu.addAction("Stop tracking")
            self.settingAction.triggered.connect(self.stoptracking)
            #
            if STORE_IMAGES:
                self.imageAction = self.menu.addAction("Store images")
            else:
                self.imageAction = self.menu.addAction("Store images (stopped)")
            self.imageAction.triggered.connect(self.storeImages)
        ############# webcam
        if use_webcam:
            self.wbox = QHBoxLayout()
            self.wbox.setContentsMargins(0,0,0,0)
            self.wbox.setSpacing(0)
            self.abox.insertLayout(16, self.wbox)
            self.list_camera_start = []
            self.list_camera = []
            self.context = pyudev.Context()
            self.on_use_webcam_start()
        ############### battery
        if use_battery_info and use_clock:
            self.btn_batt = QPushButton()
            self.btn_batt.type = "bat"
            self.btn_batt.installEventFilter(self)
            self.btn_batt.setFlat(True)
            self.btn_batt.setStyleSheet("border: none;")
            self.btn_batt.setIconSize(QSize(button_size-button_padding, button_size-button_padding))
            batt_icon = QIcon("icons/battery-missing.png")
            self.btn_batt.setIcon(batt_icon)
            self.btn_batt.setToolTip("No battery")
            self.abox.insertWidget(17, self.btn_batt)
            self.last_battery_value = 0
            self.on_battery()
        ############### tray section
        global use_tray
        # check if another tray is active
        selection = self.display.intern_atom("_NET_SYSTEM_TRAY_S%d" % self.display.get_default_screen())
        if self.display.get_selection_owner(selection) != X.NONE:
            global tray_already_used
            tray_already_used = 1
            use_tray = 0
        #
        if use_tray:
            self.frame_box = QHBoxLayout()
            self.frame_box.setContentsMargins(0,int((dock_height-button_size)/2),0,0)
            #
            self.frame_box.setSpacing(0)
            self.tray_box = self.frame_box
            self.frame_box.setAlignment(Qt.AlignCenter)
            self.abox.insertLayout(18, self.frame_box)
            # frame widget counter
            self.frame_counter = 0
            # widget background color
            bcolor = self.palette().color(QPalette.Background).name()
            #
            self.tthread = trayThread(1, bcolor, data_run)
            self.tthread.sig.connect(self.tthreadslot)
            self.tthread.start()
        #
        if USE_CUSTOM_WIDGET_RIGHT:
            from widgets2 import widgets_right
            self.abox.insertWidget(20, widgets_right())
        # clock at right
        if use_clock == 2:
            self.abox.insertLayout(21, self.cbox)
        # menu at right
        if use_menu == 2:
            self.abox.insertLayout(22, self.mbtnbox)
        #
        if CENTRALIZE_EL == 1:
            self.abox.addStretch(1)
        elif CENTRALIZE_EL == 2:
            # the main window to the center
            self.main_window_center()
        ###### notification manager
        self.mn_is_shown = None
        if USE_NOTIFICATION != 0:
            self.btn_not = QPushButton()
            self.btn_not.setFlat(True)
            self.btn_not.setIconSize(QSize(button_size-button_padding, button_size-button_padding))
            self.btn_not.setStyleSheet("border: none;")
            self.btn_not.clicked.connect(self.on_notification)
            if use_menu == 2:
                if virtual_desktops == 1:
                    self.abox.insertWidget(3, self.btn_not)
                else:
                    self.abox.insertWidget(2, self.btn_not)
            else:
                self.abox.insertWidget(17, self.btn_not)
            # set the icon
            self.btn_not_icon()
        #######
        # file and directory watchers
        if use_menu:
            def on_directory_changed():
                on_pop_menu(app_dirs_user, app_dirs_system)
            # some applications has been added or removed
            def directory_changed(edir):
                if USE_NOTIFICATION != 0 and edir == USE_NOTIFICATION:
                    self.btn_not_icon()
                    return
                global menu_is_changed
                menu_is_changed += 1
                if menu_is_changed == 1:
                    on_directory_changed()
            #
            # check for changes in the application directories
            fPath = app_dirs_system + app_dirs_user
            self.fileSystemWatcher = QFileSystemWatcher(fPath)
            self.fileSystemWatcher.directoryChanged.connect(directory_changed)
        #
        if use_clock:
            def file_changed(efile):
                global list_events_all
                list_events_all = []
                get_events()
            #
            # check for changes in the calendar file
            if os.path.exists(fopen):
                epath = QFileInfo(QFile(fopen)).absoluteFilePath()
                self.fileSystemWatcher.addPath(epath)
                self.fileSystemWatcher.fileChanged.connect(file_changed)
        #
        if USE_NOTIFICATION != 0:
            if os.path.exists(USE_NOTIFICATION):
                self.fileSystemWatcher.addPath(USE_NOTIFICATION)
        # timer
        if PLAY_ALARM > 0:
            # timer object
            self.mytimer = None
            # time string
            self._mytimer = ""
            self._set_timer(None)
        
    #
    def _on_label_0(self,label0_script,label0_interval,label0_use_richtext,label0_color,label0_font,label0_font_size,label0_font_weight,label0_font_italic,label0_command1,label0_command2):
        #
        if label0_script:
            if label0_use_richtext:
                self.labelw0.setTextFormat(Qt.RichText)
            else:
                if label0_color:
                    self.labelw0.setStyleSheet("color: {}".format(label0_color))
                tfont = QFont()
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
            #
            self.label0thread = label1Thread(["scripts/./label0.sh", label0_interval])
            self.label0thread.label1sig.connect(self.on_label0)
            self.label0thread.start()
            #
            self.labelw0_state = 1
            self.labelw0.show()
    
    #
    def _on_label_1(self,label1_script,label1_interval,label1_use_richtext,label1_color,label1_font,label1_font_size,label1_font_weight,label1_font_italic,label1_command1,label1_command2):
        #
        if label1_script:
            if label1_use_richtext:
                self.labelw1.setTextFormat(Qt.RichText)
            else:
                if label1_color:
                    self.labelw1.setStyleSheet("color: {}".format(label1_color))
                tfont = QFont()
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
            #
            self.label1thread = label1Thread(["scripts/./label1.sh", label1_interval])
            self.label1thread.label1sig.connect(self.on_label1)
            self.label1thread.start()
            #
            self.labelw1_state = 1
            self.labelw1.show()
    
    #
    def _on_label_2(self,label2_script,label2_interval,label2_use_richtext,label2_color,label2_font,label2_font_size,label2_font_weight,label2_font_italic,label2_command1,label2_command2):
        #
        if label2_script:
            if label2_use_richtext:
                self.labelw2.setTextFormat(Qt.RichText)
            else:
                if label2_color:
                    self.labelw2.setStyleSheet("color: {}".format(label2_color))
                tfont = QFont()
                if label2_font:
                    tfont.setFamily(label2_font)
                if label2_font_size:
                    tfont.setPointSize(label2_font_size)
                if label2_font_weight:
                    tfont.setWeight(label2_font_weight)
                if label2_font_italic:
                    tfont.setItalic(label2_font_italic)
                self.labelw2.setFont(tfont)
            # 
            self.labelw2.mouseDoubleClickEvent = self.on_labelw2
            #
            self.label2thread = label1Thread(["scripts/./label2.sh", label2_interval])
            self.label2thread.label1sig.connect(self.on_label2)
            self.label2thread.start()
            #
            self.labelw2_state = 1
            self.labelw2.show()
    
    #
    def _on_label_3(self,label3_script,label3_interval,label3_use_richtext,label3_color,label3_font,label3_font_size,label3_font_weight,label3_font_italic,label3_command1,label3_command2):
        #
        if label3_script:
            if label3_use_richtext:
                self.labelw3.setTextFormat(Qt.RichText)
            else:
                if label3_color:
                    self.labelw3.setStyleSheet("color: {}".format(label3_color))
                tfont = QFont()
                if label3_font:
                    tfont.setFamily(label3_font)
                if label3_font_size:
                    tfont.setPointSize(label3_font_size)
                if label3_font_weight:
                    tfont.setWeight(label3_font_weight)
                if label3_font_italic:
                    tfont.setItalic(label3_font_italic)
                self.labelw3.setFont(tfont)
            # 
            self.labelw3.mouseDoubleClickEvent = self.on_labelw3
            #
            self.label3thread = label1Thread(["scripts/./label3.sh", label3_interval])
            self.label3thread.label1sig.connect(self.on_label3)
            self.label3thread.start()
            #
            self.labelw3_state = 1
            self.labelw3.show()
    
    
    def _initializations(self):
        # set new style globally
        if theme_style:
            s = QStyleFactory.create(theme_style)
            app.setStyle(s)
        # set the icon style globally
        if icon_theme:
            QIcon.setThemeName(icon_theme)
        ################
        self.setMinimumHeight(dock_height)
        self.setMaximumHeight(dock_height)
        #
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_menu)
        
    def _on_menu(self, QPos):
        pbtn = self.sender()
        # create context menu
        selfMenu = QMenu(self)
        # time label
        # timer
        wl = self.childAt(QPos.x(), QPos.y())
        if wl == self.tlabel:
            # timer
            if PLAY_ALARM > 0:
                if self.mytimer == None:
                    self._add_timer = QAction("Set the timer")
                    selfMenu.addAction(self._add_timer)
                    self._add_timer.triggered.connect(self.on_add_timer)
                elif isinstance(self.mytimer, QTimer):
                    self._add_timer = QAction("Delete timer "+self._mytimer)
                    selfMenu.addAction(self._add_timer)
                    self._add_timer.triggered.connect(self.on_delete_timer)
        # volume button
        elif wl == self.btn_audio:
            return
        elif wl == self.btn_mic:
            return
        # else:
        elif wl == None:
            # scripts
            self._reload_scripts = QAction("Reload scripts")
            selfMenu.addAction(self._reload_scripts)
            self._reload_scripts.triggered.connect(self.on_reload_scripts)
            # # mute notifications
            # self._disable_notifications = QAction("Notifications off/on")
            # selfMenu.addAction(self._disable_notifications)
            # self._disable_notifications.triggered.connect(self.on_disable_notifications)
            # exit
            selfMenu.addSeparator()
            reloadAction = QAction("Reload", self)
            reloadAction.triggered.connect(self.restart)
            selfMenu.addAction(reloadAction)
            exitAction = QAction("Exit", self)
            exitAction.triggered.connect(self.winClose)
            selfMenu.addAction(exitAction)
        # show the context menu
        selfMenu.exec_(self.sender().mapToGlobal(QPos)) 
        
    def on_add_timer(self):
        self.TW = TimerWindow(self)
        self.TW.show()
    
    def on_delete_timer(self):
        self.mytimer.stop()
        try:
            self.mytimer.deleteLater()
        except:
            pass
        del self.mytimer
        self.mytimer = None
        self._mytimer = None
        os.remove(os.path.join(curr_path,"mytimer"))
    
    # _data: date,time,sound,notification,dialog
    def _set_timer(self, _data):
        if _data == None:
            _file = os.path.join(curr_path,"mytimer")
            if os.path.exists(_file):
                _data2 = None
                with open(os.path.join(curr_path, "mytimer"), "r") as _f:
                    _data2 = _f.readlines()
                #
                if _data2:
                    _date = _data2[0].strip("\n")
                    _date2 = QDate.fromString(_date,"yyyy.MM.dd")
                    # skip if timer is not set to today
                    if _date2 != QDateTime.currentDateTime().date():
                        os.remove(os.path.join(curr_path, "mytimer"))
                        return
                    _time = _data2[1].strip("\n")
                    _time2 = QTime.fromString(_time)
                    _current_time = QTime.currentTime()
                    #
                    _sound = _data2[2].strip("\n")
                    _notification = _data2[3].strip("\n")
                    _dialog = _data2[4].strip("\n")
                    _data3 = [_sound,_notification,_dialog]
                    # future timer
                    if _time2 > _current_time:
                        _t = _current_time.secsTo(_time2)
                        if _t:
                            try:
                                self.mytimer = QTimer()
                                self.mytimer.singleShot(_t*1000, lambda : self.on_set_timer(_data3))
                                self._mytimer = str(_time)
                            except Exception as E:
                                MyDialog("Error", str(E), None)
                    else:
                        os.remove(os.path.join(curr_path, "mytimer"))
                        return
                else:
                    os.remove(os.path.join(curr_path, "mytimer"))
                    return
        else:
            _time = _data[1]
            _time2 = QTime.fromString(_time)
            _current_time = QTime.currentTime()
            if _time2 > _current_time:
                _t = _current_time.secsTo(_time2)
                if _t:
                    try:
                        self.mytimer = QTimer()
                        self.mytimer.singleShot(_t*1000, lambda : self.on_set_timer(_data[2:]))
                        self._mytimer = str(QTime.fromString(_time).toString("HH:mm"))
                    except Exception as E:
                        MyDialog("Error", str(E), None)
            else:
                MyDialog("Error", "Wrong time.", None)
                
    def on_set_timer(self,_data):
        my_sound = _data[0]
        my_notification = _data[1]
        my_dialog = _data[2]
        #
        if my_sound:
            try:
                play_sound("alarm-clock.wav")
            except:
                MyDialog("Info","Alarm is set",None)
        # if my_notification:
            # if shutil.which("notify-send"):
                # try:
                    # os.system("notify-send -i sounds/notifications_on.svg -u critical 'Alarm is set.'")
                # except:
                    # MyDialog("Info","Alarm is set",None)
            # else:
                # MyDialog("Info","Alarm is set",None)
        if my_dialog:
            MyDialog("Info","Alarm is set",None)
        #
        os.remove(os.path.join(curr_path,"mytimer"))
        try:
            self.mytimer.deleteLater()
        except:
            pass
        del self.mytimer
        self._mytimer = None
        self.mytimer = None
            
    
    def on_reload_scripts(self):
        del sys.modules["cfg_dock"]
        import cfg_dock
        #
        if cfg_dock.label1_script == 0 and self.labelw1_state == 1:
            self.label1thread.terminate()
            self.label1thread.quit()
            self.label1thread.exit()
            aa = 1
            while aa:
                time.sleep(1)
                if not self.label1thread.isRunning():
                    aa = 0
            #
            self.labelw1.hide()
            self.labelw1_state = 0
        elif cfg_dock.label1_script == 1 and self.labelw1_state == 0:
            self._on_label_1(cfg_dock.label1_script,cfg_dock.label1_interval,cfg_dock.label1_use_richtext,cfg_dock.label1_color,cfg_dock.label1_font,cfg_dock.label1_font_size,cfg_dock.label1_font_weight,cfg_dock.label1_font_italic,cfg_dock.label1_command1,cfg_dock.label1_command2)
        #
        if cfg_dock.label2_script == 0 and self.labelw2_state == 1:
            self.label2thread.terminate()
            self.label2thread.quit()
            self.label2thread.exit()
            aa = 1
            while aa:
                time.sleep(1)
                if not self.label2thread.isRunning():
                    aa = 0
            #
            self.labelw2.hide()
            self.labelw2_state = 0
        elif cfg_dock.label2_script == 1 and self.labelw2_state == 0:
            self._on_label_2(cfg_dock.label2_script,cfg_dock.label2_interval,cfg_dock.label2_use_richtext,cfg_dock.label2_color,cfg_dock.label2_font,cfg_dock.label2_font_size,cfg_dock.label2_font_weight,cfg_dock.label2_font_italic,cfg_dock.label2_command1,cfg_dock.label2_command2)
        #
        if cfg_dock.label3_script == 0 and self.labelw3_state == 1:
            self.label3thread.terminate()
            self.label3thread.quit()
            self.label3thread.exit()
            aa = 1
            while aa:
                time.sleep(1)
                if not self.label3thread.isRunning():
                    aa = 0
            #
            self.labelw3.hide()
            self.labelw3_state = 0
        elif cfg_dock.label3_script == 1 and self.labelw3_state == 0:
            self._on_label_3(cfg_dock.label3_script,cfg_dock.label3_interval,cfg_dock.label3_use_richtext,cfg_dock.label3_color,cfg_dock.label3_font,cfg_dock.label3_font_size,cfg_dock.label3_font_weight,cfg_dock.label3_font_italic,cfg_dock.label3_command1,cfg_dock.label3_command2)
        #
        if cfg_dock.label0_script == 0 and self.labelw0_state == 1:
            self.label0thread.terminate()
            self.label0thread.quit()
            self.label0thread.exit()
            aa = 1
            while aa:
                time.sleep(1)
                if not self.label0thread.isRunning():
                    aa = 0
            #
            self.labelw0.hide()
            self.labelw0_state = 0
        elif cfg_dock.label0_script == 1 and self.labelw0_state == 0:
            self._on_label_0(cfg_dock.label0_script,cfg_dock.label0_interval,cfg_dock.label0_use_richtext,cfg_dock.label0_color,cfg_dock.label0_font,cfg_dock.label0_font_size,cfg_dock.label0_font_weight,cfg_dock.label0_font_italic,cfg_dock.label0_command1,cfg_dock.label0_command2)


############### battery ################
    
    # tooltip data
    def _get_battery_data(self):
        _data = None
        _status = None
        try:
            _comm = ["cat", "/sys/class/power_supply/BAT0/capacity"]
            _data = subprocess.check_output(_comm, shell=False, encoding='utf-8').strip("\n")
            _comm = ["cat", "/sys/class/power_supply/BAT0/status"]
            _status = subprocess.check_output(_comm, shell=False, encoding='utf-8').strip("\n")
        except:
            pass
        #
        return (_data, _status)
    
    # tray data
    def _get_battery_data_tray(self):
        _data = None
        #_status = None
        try:
            _comm = ["cat", "/sys/class/power_supply/BAT0/capacity"]
            _data = subprocess.check_output(_comm, shell=False, encoding='utf-8').strip("\n")
        except:
            pass
        #
        return _data
    
    # main
    def on_battery(self):
        if not os.path.exists("/sys/class/power_supply/BAT0"):
            return
        _data = None
        # _data, _status = self._get_battery_data_tray()
        _data = self._get_battery_data_tray()
        #
        if not _data:
            return
        try:
            if not isinstance(int(_data), int):
                return
        except:
            return
        if _data < 0 or _data > 100:
            return
        #
        # Discharging - Charging
        _data = int(_data)
        #
        _temp_value = self.last_battery_value
        self.last_battery_value = _data
        # self.last_battery_status = _status
        if 100 > _data >= 95:
            if 100 > _temp_value >= 95:
                return
            #
            _ic = "icons/battery-full.png"
            _icon = QIcon(_ic)
        elif 95 > _data >= 50:
            if 95 > _temp_value >= 50:
                return
            #
            _ic = "icons/battery-good.png"
            _icon = QIcon(_ic)
        elif 50 > _data >= 25:
            if 50 > _temp_value >= 25:
                return
            #
            _ic = "icons/battery-low.png"
            _icon = QIcon(_ic)
        elif 25 > _data >= 10:
            if 25 > _temp_value >= 10:
                return
            #
            _ic = "icons/battery-caution.png"
            _icon = QIcon(_ic)
        elif 10 > _data >= 1:
            if 10 > _temp_value >= 1:
                return
            #
            _ic = "icons/battery-caution.png"
            _icon = QIcon(_ic)
        elif 1 > _data >= 0:
            if 1 > _temp_value >= 0:
                return
            #
            _ic = "icons/battery-empty.png"
            _icon = QIcon(_ic)
        # 
        self.btn_batt.setIcon(_icon)

############### webcam #################
    
    # 4 - device: open or close
    def on_use_webcam(self, _list):
        if _list[0] == "change_state":
            _dev,_action = _list[1]
        else:
            return
        #
        if _action == "open":
            _num_items = self.wbox.count()
            for i in range(_num_items):
                item = self.wbox.itemAt(i).widget()
                if isinstance(item, QPushButton):
                    wbtn_icon = QIcon("icons/camera-web.png")
                    _tooltp = item.toolTip()
                    item.setToolTip(_tooltp+"\n (In use) ")
                    item.setIcon(wbtn_icon)
                    item.show()
                break
        #
        elif _action == "close":
            _num_items = self.wbox.count()
            for i in range(_num_items):
                item = self.wbox.itemAt(i).widget()
                if isinstance(item, QPushButton):
                    for el in self.list_camera:
                        if el[0] == _dev:
                            dd = el
                    venprod = "{}:{}".format(dd[2],dd[3])
                    # do not show icon for webcam attached but not in use
                    if venprod in show_webcam_skip:
                        wbtn_icon = QIcon()
                        item.setIcon(wbtn_icon)
                        item.hide()
                    # show the icon
                    else:
                        wbtn_icon = QIcon("icons/camera-web-1.png")
                        _tooltp_tmp = item.toolTip()
                        _tooltp = _tooltp_tmp.split("\n")[0]
                        item.setToolTip(_tooltp)
                        item.setIcon(wbtn_icon)
                break
    
    # 3 - device: open or close
    def on_dev_change(self, _dev, _action):
        for dd in self.list_camera:
            if dd[0] == _dev:
                self.webcam_signal.emit(["change_state",[_dev,_action]])
            break
    
    # 0 - when this program starts
    def on_use_webcam_start(self):
        for device in self.context.list_devices(subsystem='video4linux'):
            if 'DEVNAME' in device.properties:
                if device.get('ID_V4L_CAPABILITIES') == ":capture:":
                    _model_name = device.get('ID_V4L_PRODUCT')
                    if not _model_name:
                        _model_name = device.get('ID_MODEL')
                    self.list_camera_start.append([device.get('DEVNAME'), _model_name, device.get('ID_MODEL_ID'), device.get('ID_VENDOR_ID')])
        #
        monitor = pyudev.Monitor.from_netlink(self.context)
        monitor.filter_by(subsystem='video4linux')
        self.observer = pyudev.MonitorObserver(monitor, self.mediaEvent)
        self.observer.daemon
        self.observer.start()
        #
        # device open or closed
        class EventHandler(pyinotify.ProcessEvent):
            def my_init(self, _obj):
                self._obj = _obj
            def process_IN_OPEN(self, event):
                self._obj(event.pathname, "open")
            def process_IN_CLOSE_WRITE(self, event):
                self._obj(event.pathname, "close")
        #
        # webcam open or close
        self.wm = pyinotify.WatchManager()
        self.mask = pyinotify.IN_OPEN | pyinotify.IN_CLOSE_WRITE
        notifier = pyinotify.ThreadedNotifier(self.wm, EventHandler(_obj=self.on_dev_change))
        global _notifier
        _notifier = notifier
        # to qt5desktop2.py
        self._close_signal.emit(notifier)
        ########
        for dd in self.list_camera_start:
            self.on_add_webcam(dd)
        #
        notifier.start()
        ########
        # _success = 0
        if self.list_camera_start:
            for vv in self.list_camera_start:
                wdd = self.wm.add_watch(vv[0], self.mask, rec=False)
                # (>0) 1 success - negative not success
                if wdd[vv[0]]:
                    # _success = 1
                    self.list_camera.append(vv)
        #############
        self.webcam_signal.connect(self.signal_webcam)
       
    # signal - webcam added or its state changed
    def signal_webcam(self, _list):
        if _list[0] == "new":
            self.on_add_webcam(_list[1])
            self.list_camera.append(_list[1])
        elif _list[0] == "change_state":
            self.on_use_webcam(_list)
    
    # 2 - at start or after adding a new webcam - icon in the bar
    def on_add_webcam(self, dd):
        venprod = "{}:{}".format(dd[2],dd[3])
        # skip unwanted webcam
        if venprod in show_only_active_skip:
            return
        #
        wbtn = QPushButton()
        wbtn.setFlat(True)
        wbtn.setStyleSheet("border: none;")
        wbtn.dev = dd[0]
        #
        _ddd = dd[0].split("/")[2]
        _comm_path = os.path.join(os.getcwd(), "check_webcam.sh")
        _comm = [_comm_path, _ddd]
        # a webcam is working
        _is_found = 0
        try:
            _data = subprocess.check_output(_comm, shell=False, encoding='utf-8', cwd=os.getcwd()).strip("\n")
            if _data:
                _is_found = 1
        except:
            _is_found = 0
        #
        if _is_found == 1:
            wbtn_icon = QIcon("icons/camera-web.png")
            wbtn.setToolTip(dd[1]+"\n (In use) ")
        else:
            if venprod in show_webcam_skip:
                wbtn_icon = QIcon()
            else:
                wbtn_icon = QIcon("icons/camera-web-1.png")
                wbtn.setToolTip(dd[1])
        wbtn.setIconSize(QSize(button_size-button_padding, button_size-button_padding))
        wbtn.setIcon(wbtn_icon)
        self.wbox.addWidget(wbtn)
        if venprod in show_webcam_skip and _is_found == 0:
            wbtn.hide()
        
    # detect adding or removing of webcam
    def mediaEvent(self, action, device):
        if action == "add":
            if 'DEVNAME' in device.properties:
                if device.get('ID_V4L_CAPABILITIES') == ":capture:":
                    _model_name = device.get('ID_V4L_PRODUCT')
                    if not _model_name:
                        _model_name = device.get('ID_MODEL')
                    self.on_camera(device.get('DEVNAME'), _model_name, device.get('ID_MODEL_ID'), device.get('ID_VENDOR_ID'))
        elif action == "remove":
            self.on_camera2(device.get('DEVNAME'))
           
    # 1 - new webcam added
    def on_camera(self, _dev, _name, _model, _vendor):
        dd = [_dev, _name, _model, _vendor]
        wdd = self.wm.add_watch(_dev, self.mask, rec=False)
        # (>0) 1 success - negative not success
        if wdd[_dev]:
            self.webcam_signal.emit(["new",dd])
            
        
    # webcam removed
    def on_camera2(self, _dev):
        for dd in self.list_camera:
            if dd[0] == _dev:
                _num_items = self.wbox.count()
                for i in range(_num_items):
                    item = self.wbox.itemAt(i).widget()
                    if isinstance(item, QPushButton):
                        self.wbox.removeWidget(item)
                        item.deleteLater()
                        #
                        self.list_camera.remove(dd)
        return
        
########################################

############### notifications ##########
    
    def btn_not_icon(self):
        if DO_NOT_DISTURB:
            if os.path.exists(DO_NOT_DISTURB):
                _nfile = "notificationdonotuse_"+str(DO_NOT_DISTURB_TYPE)
                if os.path.exists(os.path.join(DO_NOT_DISTURB, _nfile)):
                    self.btn_not.setIcon(QIcon("icons/notifications_disabled.svg"))
                    return
        #
        if len(os.listdir(USE_NOTIFICATION)) > 0:
           self.btn_not.setIcon(QIcon("icons/notifications_on.svg"))
        else:
            self.btn_not.setIcon(QIcon("icons/notifications_off.svg"))
    
    def on_disable_notifications(self):
        try:
            _nfile_name = "notificationdonotuse_"+str(DO_NOT_DISTURB_TYPE)
            _nfile = os.path.join(DO_NOT_DISTURB, _nfile_name)
            if os.path.exists(_nfile):
                os.remove(_nfile)
            else:
                os.mknod(_nfile)
            self.btn_not_icon()
        except Exception as E:
            MyDialog("Error", str(E), None)
    
    def on_notification(self):
        sender_button = self.sender()
        #
        if self.mn_is_shown is not None:
            self.mn_is_shown.close()
            self.mn_is_shown = None
            return
        mn = menuNotification(self)
        self.mn_is_shown = mn


############### audio ################
    
    # at this program start
    def _on_start_vol(self):
        # card list
        self.card_list = self.pulse.card_list()
        # # default sink name
        self.default_sink_name = None
        try:
            _sink_list = self.pulse.sink_list()
        except:
            self._reload_pulse()
        # the default sink stored
        try:
            _server_info = self.pulse.server_info()
            self.default_sink_name = _server_info.default_sink_name
            del _server_info
        except:
            self._reload_pulse()
        #
        _sink_name = self.default_sink_name
        try:
            _sink_file_path = os.path.join(curr_path,"sink_default")
            if os.path.exists(_sink_file_path):
                with open(_sink_file_path, "r") as _f:
                    _sink_name = _f.readline()
                self.start_sink_name = _sink_name.strip("\n")
        except Exception as E:
            MyDialog("Error", str(E),None)
        #
        if self.start_sink_name:
            if self.start_sink_name != "auto_null":
                self.default_sink_name = self.start_sink_name
        #
        for el in self.pulse.sink_list():
            if el.name == _sink_name and el.name != "auto_null":
                self.pulse.sink_default_set(el)
                break
        #
        if self.AUDIO_START_LEVEL:
            if not isinstance(self.AUDIO_START_LEVEL,int):
                self.AUDIO_START_LEVEL = 20
            if self.AUDIO_START_LEVEL > 100 or self.AUDIO_START_LEVEL < 0:
                self.AUDIO_START_LEVEL = 20
            if self.default_sink_name:
                for ell in _sink_list:
                    if ell.name == self.default_sink_name:
                        _vol = round(self.AUDIO_START_LEVEL/100, 2)
                        try:
                            self.pulse.volume_set_all_chans(ell, _vol)
                        except:
                            pass
        # # right click menu - volume
        # self.on_populate_amenu()
        # set the icon and tooltip - volume
        self._set_volume()
    
    # rebuild the volume menu
    def on_populate_amenu(self):
        try:
            _sink_list = self.pulse.sink_list()
        except:
            self._reload_pulse()
            return
        for i in range(self.laudiobox.count()):
            if self.laudiobox.itemAt(i) != None:
                widget = self.laudiobox.itemAt(i).widget()
                if isinstance(widget, QRadioButton):
                    self.laudiobox.removeWidget(widget)
                    self.laudiobox.takeAt(i)
                    widget.deleteLater()
                    widget = None
        #
        try:
            _sink_file_path = os.path.join(curr_path,"sink_default")
            if os.path.exists(_sink_file_path):
                with open(_sink_file_path, "r") as _f:
                    _sink_name = _f.readline()
                self.start_sink_name = _sink_name.strip("\n")
        except Exception as E:
            MyDialog("Error", str(E),None)
        #
        for ell in _sink_list:
            rb0 = QRadioButton(ell.description)
            self.laudiobox.addWidget(rb0)
            rb0.item = ell.name
            if ell.name == self.default_sink_name:
                rb0.setChecked(True)
                if ell.name == self.start_sink_name:
                    self.abtn.setText("Remove as default")
                else:
                    self.abtn.setText("Set as default")
            rb0.clicked.connect(self.on_rb0_clicked)
        
    # 
    def on_rb0_clicked(self, _bool):
        _item = None
        try:
            _sink_list = self.pulse.sink_list()
        except:
            self._reload_pulse()
            return
        if hasattr(self.sender(), "item"):
            _item = self.sender().item
        if not _item:
            return
        #
        _sink = None
        for ell in _sink_list:
            if ell.name == _item:
                _sink = ell
                break
        #
        try:
            self.pulse.sink_default_set(_sink)
            self.default_sink_name = _item
        except:
            self._reload_pulse()
        self.amenu.close()
        
    
    # the default sink stored
    def on_abtn_clicked(self):
        if not self.default_sink_name or self.default_sink_name == "auto_null":
            return
        #
        if self.abtn.text() == "Remove as default":
            try:
                os.remove(os.path.join(curr_path,"sink_default"))
                self.start_sink_name = None
            except Exception as E:
                MyDialog("Error", str(E), None)
        else:
            try:
                with open(os.path.join(curr_path,"sink_default"), "w") as _f:
                    _f.write(str(self.default_sink_name))
            except Exception as E:
                MyDialog("Error", str(E), None)
        #
        self.amenu.close()
    
    #
    # def _on_start_mic(self):
        # self.on_populate_micmenu()
    
    # show or hide the microphone icon
    def on_microphone(self):
        try:
            _source_list = self.pulse.source_list()
        except:
            self._reload_pulse()
            return
        #
        _count = 0
        for el in _source_list:
            if not el.name.endswith(".monitor"):
                _count += 1
        if _count > 0:
            self.btn_mic.show()
            return
        #
        self.btn_mic.hide()
    
    def on_populate_micmenu(self):
        try:
            _source_list = self.pulse.source_list()
        except:
            self._reload_pulse()
            return
        #
        for i in range(self.micbox.count()):
            if self.micbox.itemAt(i) != None:
                widget = self.micbox.itemAt(i).widget()
                if isinstance(widget, QCheckBox):
                    self.micbox.removeWidget(widget)
                    self.micbox.takeAt(i)
                    widget.deleteLater()
                    widget = None
        #
        for el in _source_list:
            # skip monitors
            if not el.name.endswith(".monitor"):
                rb1 = QCheckBox(el.description)
                rb1.setTristate(False)
                rb1.item = el.name
                rb1.setChecked(False)
                self.micbox.addWidget(rb1)
                #
                if el.mute == 0:
                    rb1.setChecked(True)
                rb1.stateChanged.connect(self.on_rb1_clicked)
        #
        self.on_microphone()
    
    #
    def on_microphone_changed(self):
        return
        # try:
            # _source_list = self.pulse.source_list()
        # except:
            # self._reload_pulse()
            # return
        # # widgets
        # _list_chbtn = []
        # for i in range(self.micbox.count()):
            # if self.micbox.itemAt(i) != None:
                # widget = self.micbox.itemAt(i).widget()
                # if isinstance(widget, QCheckBox):
                    # _list_chbtn.append(widget)
        # #
        # for ell in _source_list:
            # if ell.name.endswith('monitor'):
                # continue
            # for ww in _list_chbtn:
                # if ww.item == ell.name:
                    # _state = ell.mute
                    # ww.setChecked(not _state)
    
    # mic
    def on_rb1_clicked(self, _bool):
        if hasattr(self.sender(), "item"):
            _item = self.sender().item
        else:
            return
        _source = None
        try:
            for el in self.pulse.source_list():
                if el.name == _item:
                    _source = el
                    break
            if _source:
                self._mute_mic(_source, self.sender().isChecked())
        except:
            self._reload_pulse()
    
    # mute mic
    def _mute_mic(self, _source, _state):
        _mute_state = not _state
        try:
            self.pulse.mute(_source, mute=_mute_state)
        except:
            self._reload_pulse()
    
    # right click menu - mic
    def on_mic2(self, _pos):
        self.on_populate_micmenu()
        #
        self.micmenu.adjustSize()
        self.micmenu.updateGeometry()
        menu_width = self.micmenu.geometry().width()
        menu_height = self.micmenu.geometry().height()
        #
        x = _pos.x()
        y = _pos.y()
        if dock_position == 0:
            y = dock_height + menu_padx
        elif dock_position == 1:
            y = WINH-dock_height-menu_height-menu_padx
        #
        x1 = int(menu_width/2)
        if (x>int(WINW/2)):
            if x+x1+menu_padx>WINW:
                x = WINW-menu_width-menu_padx
            else:
                x = x-int(menu_width/2)
        elif (x<int(WINW/2)) and x < x1:
            x = x1
        self.micmenu.exec_(QPoint(x,y))
        
    #
    def athreadslot(self, _list):
        if _list[0] == "remove-sink":
            self.on_list_audio(_list[1], 101)
        elif _list[0] == "new-sink":
            self.on_list_audio(_list[1], 102)
        elif _list[0] == "change-sink":
            self.on_list_audio(_list[1], 103)
        elif _list[0] == "remove-source":
            self.on_list_audio(_list[1], 201)
        elif _list[0] == "new-source":
            self.on_list_audio(_list[1], 202)
        # elif _list[0] == "change-source":
            # self.on_list_audio(_list[1], 203)
    
    def on_list_audio(self, _el, _t):
        # sink: remove - new
        if _t in [101,102]:
            # self.on_populate_amenu()
            self._set_volume()
        # volume changed
        elif _t == 103:
            self._set_volume()
        # # change on stream or output device - more info missed
        # elif _t == 301:
            # pass
        # source
        elif _t in [201,202]:
            if USE_MICROPHONE:
                # self.on_populate_micmenu()
                self.on_microphone()
        # elif _t == 203:
            # if USE_MICROPHONE:
                # self.on_microphone_changed()
    #
    def _set_volume(self):
        _sink = None
        try:
            for el in self.pulse.sink_list():
                if el.name == self.default_sink_name:
                    _sink = el
                    break
        except:
            self._reload_pulse()
            return
        #
        if _sink:
            # 
            _volume = _sink.volume.values
            _level = int(round(max(_volume), 2)*100)
            _mute = _sink.mute
            # _description = _sink.description
            #
            if self.btn_audio.value == [int(_level), _mute]:
                return
            #
            iicon = None
            #
            if 0 <= _level < 31:
                _icon = "audio-volume-low"
                iicon = QIcon.fromTheme(_icon, QIcon("icons/audio-volume-low.svg"))
            elif 31 < _level < 61:
                _icon = "audio-volume-medium"
                iicon = QIcon.fromTheme(_icon, QIcon("icons/audio-volume-medium.svg"))
            elif 31 < _level < 61:
                _icon = "audio-volume-high"
                iicon = QIcon.fromTheme(_icon, QIcon("icons/audio-volume-high.svg"))
            elif _level <= 100:
                _icon = "audio-volume-overamplified"
                iicon = QIcon.fromTheme(_icon, QIcon("icons/audio-volume-overamplified.svg"))
            #
            if _mute == 1:
                _icon = "audio-volume-muted"
                iicon = QIcon.fromTheme(_icon, QIcon("icons/audio-volume-muted.svg"))
            #
            if iicon and not iicon.isNull():
                self.btn_audio.setIcon(iicon)
                self.btn_audio.value = [int(_level), _mute]
                if _sink.description == "Dummy Output":
                    self.btn_audio.setToolTip("{}:{}".format("Dummy Output", _level))
                else:
                    if _mute:
                        _msg = str(_level)+"  (muted)"
                    else:
                        _msg = str(_level)
                    self.btn_audio.setToolTip(" {} ".format(_msg))
        #
        else:
            _icon = "audio-volume-muted"
            iicon = QIcon.fromTheme(_icon, QIcon("icons/audio-volume-muted.svg"))
            self.btn_audio.setIcon(iicon)
            self.btn_audio.value = [-999, -999]
            self.btn_audio.setToolTip("No audio devices")
    
    #
    def on_mbtn_mixer(self):
        try:
            if MIXER_CONTROL:
                os.system("{} &".format(MIXER_CONTROL))
            self.mmenu.close()
        except Exception as E:
            MyDialog("Error", str(E),self)
        
    # mouse wheel
    def on_vslider_changed(self):
        self.on_volume_change("slider")
    
    # left click
    def on_volume1(self, _pos):
        sdink = None
        try:
            _sink_list = self.pulse.sink_list()
        except:
            self._reload_pulse()
            return
        for el in _sink_list:
            if el.name == self.default_sink_name:
                dsink = el
                break
        #
        if dsink == None:
            self.mslider.setEnabled(False)
            return
        elif dsink.name == "auto_null":
            self.mslider.setEnabled(False)
        elif self.mslider.isEnabled() == False:
            self.mslider.setEnabled(True)
        #
        if self.mslider.isEnabled() == True:
            _mute_state = dsink.mute
            if _mute_state == 1:
                self.mslider.setEnabled(False)
            elif self.mslider.isEnabled() == False:
                self.mslider.setEnabled(True)
        # decimal
        _vol = round(self.pulse.volume_get_all_chans(dsink),2)
        self.mslider.setValue(int(_vol*100))
        #
        self.mmenu.adjustSize()
        self.mmenu.updateGeometry()
        menu_width = self.mmenu.geometry().width()
        menu_height = self.mmenu.geometry().height()
        #
        x = _pos.x()
        y = _pos.y()
        if dock_position == 0:
            y = dock_height + menu_padx
        elif dock_position == 1:
            y = WINH-dock_height-menu_height-menu_padx
        #
        x1 = int(menu_width/2)
        if (x>int(WINW/2)):
            if x+x1+menu_padx>WINW:
                x = WINW-menu_width-menu_padx
            else:
                x = x-int(menu_width/2)
        elif (x<int(WINW/2)) and x < x1:
            x = x1
        self.mmenu.exec_(QPoint(x,y))
    
    # right click
    def on_volume2(self, _pos):
        self.on_populate_amenu()
        #
        self.amenu.adjustSize()
        self.amenu.updateGeometry()
        menu_width = self.amenu.geometry().width()
        menu_height = self.amenu.geometry().height()
        #
        x = _pos.x()
        y = _pos.y()
        if dock_position == 0:
            y = dock_height + menu_padx
        elif dock_position == 1:
            y = WINH-dock_height-menu_height-menu_padx
        #
        x1 = int(menu_width/2)
        if (x>int(WINW/2)):
            if x+x1+menu_padx>WINW:
                x = WINW-menu_width-menu_padx
            else:
                x = x-int(menu_width/2)
        elif (x<int(WINW/2)) and x < x1:
            x = x1
        self.amenu.exec_(QPoint(x,y))
    
    # event.angleDelta() : negative down - positive up
    def on_volume_change(self, _direction):
        dsink = None
        try:
            _sink_list = self.pulse.sink_list()
        except:
            self._reload_pulse()
            return
        for el in _sink_list:
            if el.name == self.default_sink_name:
                dsink = el
                break
        if dsink == None:
            return
        #
        _vol = None
        if _direction == "slider":
            if dsink:
                _vol = round(((self.mslider.value()//AUDIO_STEP)*AUDIO_STEP)/100, 2)
        else:
            # volume : 0.0 - 1.0
            if _direction.y() < 0:
                if dsink:
                    try:
                        _vol = round(self.pulse.volume_get_all_chans(dsink),2) - (AUDIO_STEP/100)
                    except:
                        self._reload_pulse()
                        return
                    if _vol < 0:
                        _vol = 0
            # volume +
            elif _direction.y() > 0:
                if dsink:
                    try:
                        _vol = round(self.pulse.volume_get_all_chans(dsink),2) + (AUDIO_STEP/100)
                    except:
                        self._reload_pulse()
                        return
                    if _vol > 1:
                        _vol = 1.0
        #
        if _vol:
            try:
                self.pulse.volume_set_all_chans(dsink, _vol)
                self._set_volume()
            except:
                self._reload_pulse()
    
    def _mute_audio(self):
        _sink = None
        try:
            _sink_list = self.pulse.sink_list()
        except:
            self._reload_pulse()
            return
        for el in _sink_list:
            if el.name == self.default_sink_name:
                _sink = el
                break
        if not _sink:
            return
        _mute_state = not _sink.mute
        try:
            self.pulse.mute(_sink, mute=_mute_state)
        except:
            self._reload_pulse()
        self._set_volume()
    
    def _reload_pulse(self):
        del self.pulse
        self.pulse = _pulse.Pulse()
    
############# audio end ##############

############# clipboard ##############
    def stoptracking(self, action):
        if self.stop_tracking:
            self.settingAction.setText("Stop tracking")
            icon = QIcon("icons/qpasteboard.png")
            self.stop_tracking = 0
        else:
            self.settingAction.setText("Start tracking")
            icon = QIcon("icons/qpasteboard-stop.png")
            self.stop_tracking = 1
        #
        self.btn_clip.setIcon(icon)
    
    def storeImages(self, mode):
        global STORE_IMAGES
        STORE_IMAGES = not STORE_IMAGES
        if STORE_IMAGES:
            self.imageAction.setText("Store images")
        else:
            self.imageAction.setText("Store images (stopped)")
    
    def clipboardChanged(self, mode):
        #
        if mode == 0 and not self.stop_tracking:
            if SKIP_FILES:
                if app.clipboard().mimeData().hasFormat("x-special/gnome-copied-files"):
                    return
            #
            if app.clipboard().mimeData().hasFormat("text/plain"):
                text = app.clipboard().text()
                # skip if too large
                if len(text) > CLIP_MAX_SIZE:
                    # self.tray.showMessage("Info", "Text too large.")
                    MyDialog("Info", "Text lenght too large.", None)
                    return
                #
                if text and text != self.actual_clip:
                    idx = time_now = str(int(time.time()))
                    i = 0
                    while os.path.exists(os.path.join(clips_path, time_now)):
                        sleep(0.1)
                        time_now = str(int(time.time()))
                        i += 1
                        if i == 10:
                            break
                        return
                    #
                    try:
                        ff = open(os.path.join(clips_path, idx), "w")
                        ff.write(text)
                        ff.close()
                        self.actual_clip = text
                    except Exception as E:
                        MyDialog("Error", str(E), None)
                        return
                    #
                    if len(text) > int(CHAR_PREVIEW):
                        text_prev = text[0:int(CHAR_PREVIEW)]+" [...]"
                        CLIPS_DICT[str(idx)] = [text_prev]
                    else:
                        CLIPS_DICT[str(idx)] = [text]
                    # remove older entries
                    if HISTORY_SIZE:
                        list_clips = sorted(os.listdir(clips_path), reverse=True)
                        num_clips = len(list_clips)
                        #
                        if num_clips > int(HISTORY_SIZE):
                            iitem = list_clips[-1]
                            try:
                                os.remove(os.path.join(clips_path, iitem))
                            except Exception as E:
                                MyDialog("Error", str(E), None)
                                return
            #
            elif app.clipboard().mimeData().hasFormat("image/png"):
                if STORE_IMAGES:
                    image = app.clipboard().image()
                    if image.isNull():
                        return
                    #
                    idx = time_now = str(int(time.time()))
                    i = 0
                    while os.path.exists(os.path.join(clips_path, time_now)):
                        sleep(0.1)
                        time_now = str(int(time.time()))
                        i += 1
                        if i == 10:
                            break
                        return
                    #
                    try:
                        image.save(os.path.join(images_path, idx), IMAGE_FORMAT)
                    except Exception as E:
                        MyDialog("Error", str(E), None)
    
    def on_clipboard(self):
        if self._is_clipboard_shown == 0:
            self.mainCLipWidget()
        else:
            try:
                self._is_clipboard_shown = 0
                self.cwindow.close()
            except:
                pass
    
    def on_clipboard2(self, point):
        self.menu.exec_(self.sender().mapToGlobal(point))
        
    def on_label_text(self, lbl, num, text):
        lbl.setText("<b>{}</b> {}".format(num, text))
        lbl.setAlignment(Qt.AlignCenter)
    
    # the main clipboard window
    def mainCLipWidget(self):
        self.item_text_num = 0
        self.item_image_num = 0
        #
        self.cwindow = QWidget()
        self.cwindow.setWindowIcon(QIcon("icons/clipman.svg"))
        self.cwindow.setContentsMargins(0,0,0,0)
        self.cwindow.resize(CWINW, CWINH)
        self.cwindow.setAttribute(Qt.WA_DeleteOnClose)
        self.cwindow.setWindowTitle("qt5clipboard-1")
        #
        if CLIP_REMOVE_DECO == 1:
            self.cwindow.setWindowFlags(Qt.CustomizeWindowHint | Qt.FramelessWindowHint | Qt.Tool)
        #
        self.cwindow.destroyed.connect(self._cw_destroied)
        #
        self.mainBox = QHBoxLayout()
        self.mainBox.setContentsMargins(2,2,2,2)
        self.cwindow.setLayout(self.mainBox)
        #
        hpalette = self.palette().mid().color().name()
        csaa = ("QPushButton::hover:!pressed { border: none;")
        csab = ("background-color: {};".format(hpalette))
        csac = ("border-radius: 3px;")
        csad = ("text-align: center; }")
        csae = ("QPushButton { text-align: center;  padding: 5px; border: 1px solid #7F7F7F;}")
        csaf = ("QPushButton::checked { text-align: center; ")
        csag = ("background-color: {};".format(self.palette().midlight().color().name()))
        csah = ("padding: 5px; border-radius: 3px;}")
        self.csa22 = csaa+csab+csac+csad+csae+csaf+csag+csah
        ####### left
        self.leftBox = QVBoxLayout()
        self.mainBox.addLayout(self.leftBox)
        #
        self.historyLBL = QLabel()
        self.on_label_text(self.historyLBL, 0, "in history")
        self.leftBox.addWidget(self.historyLBL)
        #
        if STORE_IMAGES:
            self.imageLBL = QLabel()
            self.on_label_text(self.imageLBL, 0, "images")
            self.leftBox.addWidget(self.imageLBL)
        #
        self.clearBTN = QPushButton("Empty history")
        self.clearBTN.setFlat(True)
        self.clearBTN.setStyleSheet(self.csa22)
        self.clearBTN.clicked.connect(self.on_clear_history)
        self.leftBox.addWidget(self.clearBTN)
        #
        self.leftBox.addStretch()
        #
        self.closeBTN = QPushButton("Close")
        self.closeBTN.setFlat(True)
        self.closeBTN.setStyleSheet(self.csa22)
        self.closeBTN.clicked.connect(self.on_cwindow_close)
        self.leftBox.addWidget(self.closeBTN)
        ####### right
        self.ctab = QTabWidget()
        self.ctab.setMovable(False)
        self.mainBox.addWidget(self.ctab)
        self.ctab.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        #
        self.textLW = QListWidget()
        self.textLW.setSelectionMode(1)
        self.textLW.itemClicked.connect(self.on_item_clicked)
        self.ctab.addTab(self.textLW, "Text")
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
        css22 = cssa+cssb+cssc
        self.textLW.verticalScrollBar().setStyleSheet(css22)
        ####
        # texts
        self.actual_clip = None
        list_items = sorted(CLIPS_DICT, reverse=True)
        #
        for iitem in list_items:
            iitem_text = CLIPS_DICT[iitem][0]
            self.on_add_item(iitem_text, iitem)
        #
        self.on_label_text(self.historyLBL, self.item_text_num, "in history")
        # images
        if STORE_IMAGES:
            image_temp = os.listdir(images_path)
            if image_temp:
                for iimage in image_temp:
                    iwidget = QWidget()
                    ilayout = QVBoxLayout()
                    ilayout.setContentsMargins(2,2,2,2)
                    btn_layout = QHBoxLayout()
                    btn_layout.setContentsMargins(0,0,0,0)
                    iwidget.setLayout(ilayout)
                    #
                    image_scroll = QScrollArea()
                    image_scroll.setWidgetResizable(True)
                    pimage = QPixmap(os.path.join(images_path, iimage))
                    limage = QLabel()
                    limage.setPixmap(pimage)
                    image_scroll.setWidget(limage)
                    ilayout.addWidget(image_scroll)
                    #
                    apply_btn = QPushButton()
                    apply_btn.setIcon(QIcon("icons/apply.png"))
                    apply_btn.setFlat(True)
                    apply_btn.setToolTip("Copy this image")
                    apply_btn.clicked.connect(self.on_apply_image)
                    btn_layout.addWidget(apply_btn)
                    #
                    save_btn = QPushButton()
                    save_btn.setIcon(QIcon("icons/save.png"))
                    save_btn.setFlat(True)
                    save_btn.setToolTip("Save this image")
                    save_btn.clicked.connect(self.on_save_image)
                    btn_layout.addWidget(save_btn)
                    #
                    delete_btn = QPushButton()
                    delete_btn.setIcon(QIcon("icons/remove.png"))
                    delete_btn.setFlat(True)
                    delete_btn.setToolTip("Delete this image")
                    delete_btn.clicked.connect(self.on_delete_image)
                    btn_layout.addWidget(delete_btn)
                    #
                    ilayout.addLayout(btn_layout)
                    #
                    iwidget.iimage = iimage
                    iwidget.pimage = pimage
                    self.ctab.insertTab(1, iwidget, "Image")
                    #
                    self.item_image_num += 1
            #
            if self.item_image_num == 1:
                self.on_label_text(self.imageLBL, self.item_image_num, "image")
            else:
                self.on_label_text(self.imageLBL, self.item_image_num, "images")
        #
        self.cwindow.show()
        self._is_clipboard_shown = 1
    
    def _cw_destroied(self):
        self._is_clipboard_shown = 0
    
    def on_cwindow_close(self):
        new_w = self.cwindow.size().width()
        new_h = self.cwindow.size().height()
        global CWINW
        global CWINH
        #
        if new_w != int(CWINW) or new_h != int(CWINH):
            try:
                ifile = open("clipprogsize.cfg", "w")
                ifile.write("{};{}".format(new_w, new_h))
                ifile.close()
                CWINW = new_w
                CWINH = new_h
            except:
                pass
        #
        self.cwindow.close()
        self._is_clipboard_shown = 0
    
    #
    def on_add_item(self, text, idx):
        lw = QListWidgetItem()
        widgetItem = QWidget()
        widgetTXT =  QLabel(text=text)
        #
        previewBTN = QPushButton()
        previewBTN.setIcon(QIcon("icons/preview.png"))
        previewBTN.setFlat(True)
        previewBTN.clicked.connect(lambda:self.on_preview(idx))
        previewBTN.setToolTip("Preview")
        #
        removeBTN = QPushButton()
        removeBTN.setIcon(QIcon("icons/list-remove.png"))
        removeBTN.setFlat(True)
        removeBTN.clicked.connect(lambda:self.on_delete_item(idx))
        removeBTN.setToolTip("Delete this item")
        #
        widgetItemL = QHBoxLayout()
        widgetItemL.addWidget(widgetTXT)
        widgetItemL.addStretch()
        widgetItemL.addWidget(previewBTN)
        widgetItemL.addWidget(removeBTN)
        #
        widgetItem.setLayout(widgetItemL)  
        lw.setSizeHint(widgetItem.sizeHint())
        #
        lw.idx = idx
        #
        self.textLW.addItem(lw)
        self.textLW.setItemWidget(lw, widgetItem)
        #
        self.item_text_num += 1
    
    def on_preview(self, idx):
        self.dialogp = QDialog()
        self.dialogp.resize(int(DWINW), int(DWINH))
        self.dialogp.setContentsMargins(0,0,0,0)
        self.dialogp.setWindowTitle("Preview")
        self.dialogp.setWindowIcon(QIcon("icons/clipman.svg"))
        # self.dialogp.setModal(True)
        self.dialogp.setWindowModality(1)
        self.dialogp.setAttribute(Qt.WA_DeleteOnClose)
        #
        layout = QVBoxLayout()
        layout.setContentsMargins(2,2,2,2)
        self.dialogp.setLayout(layout)
        #
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        layout.addWidget(scrollArea)
        #
        textW = QLabel()
        scrollArea.setWidget(textW)
        textW.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        text = ""
        with open(os.path.join(clips_path, idx), "r") as ff:
            text = ff.read()
        textW.setText(text)
        textW.setTextInteractionFlags(Qt.TextSelectableByMouse)
        #
        closeDBTN = QPushButton("Close")
        # closeDBTN.clicked.connect(self.dialogp.close)
        closeDBTN.clicked.connect(self.on_close_preview)
        layout.addWidget(closeDBTN)
        #
        self.dialogp.show()
    
    
    def on_close_preview(self):
        new_w = self.dialogp.size().width()
        new_h = self.dialogp.size().height()
        global DWINW
        global DWINH
        if new_w != DWINW or new_h != DWINH:
            try:
                with open(os.path.join(ccdir, "previewsize.cfg"), "w") as ff:
                    ff.write("{};{}".format(new_w, new_h))
                #
                DWINW = new_w
                DWINH = new_h
            except Exception as E:
                MyDialog("Error", str(E), self.cwindow)
        self.dialogp.close()
    
    # text
    def on_delete_item(self, idx):
        time.sleep(0.1)
        num_items = self.textLW.count()
        itemW = None
        _item_num = None
        #
        for i in range(num_items):
            if self.textLW.item(i).idx == idx:
                itemW = self.textLW.item(i)
                _item_num = i
                break
        if itemW:
            # remove the file
            try:
                os.remove(os.path.join(clips_path, str(itemW.idx)))
            except Exception as E:
                MyDialog("Error", str(E), self.cwindow)
                return
            #
            del CLIPS_DICT[str(itemW.idx)]
            self.textLW.takeItem(self.textLW.row(itemW))
            del itemW
            #
            self.item_text_num -= 1
            self.on_label_text(self.historyLBL, self.item_text_num, "in history")
            #
            if _item_num != 0:
                if CLIPS_DICT:
                    self.actual_clip = CLIPS_DICT[self.textLW.item(0).idx][0]
    
    def on_item_clicked(self, iitem):
        clip_text = ""
        ff = open(os.path.join(clips_path, iitem.idx), "r")
        clip_text = ff.read()
        ff.close()
        # 
        if clip_text == self.actual_clip:
            app.clipboard().setText(clip_text)
        else:
            # remove the clip file
            try:
                os.remove(os.path.join(clips_path, str(iitem.idx)))
            except Exception as E:
                MyDialog("Error", str(E), self.cwindow)
                return
            self.actual_clip = clip_text
            self.textLW.takeItem(self.textLW.row(iitem))
            del CLIPS_DICT[iitem.idx]
            del iitem
            app.clipboard().setText(clip_text)
            ####
            idx = time_now = str(int(time.time()))
            i = 0
            while os.path.exists(os.path.join(clips_path, time_now)):
                sleep(0.1)
                time_now = str(int(time.time()))
                i += 1
                if i == 10:
                    break
                return
            #
            try:
                ff = open(os.path.join(clips_path, idx), "w")
                ff.write(clip_text)
                ff.close()
            except Exception as E:
                MyDialog("Error", str(E), self.cwindow)
                return
            #
            if len(clip_text) > int(CHAR_PREVIEW):
                text_prev = clip_text[0:int(CHAR_PREVIEW)]+" [...]"
                CLIPS_DICT[str(idx)] = [text_prev]
            else:
                CLIPS_DICT[str(idx)] = [clip_text]
            ####
        self.cwindow.close()
        self._is_clipboard_shown = 0
        
    def on_apply_image(self):
        try:
            curr_idx = self.ctab.currentIndex()
            pimage = self.ctab.widget(curr_idx).pimage
            app.clipboard().setPixmap(pimage)
        except Exception as E:
            MyDialog("Error", str(E), self.cwindow)
    
    def on_save_image(self):
        try:
            curr_idx = self.ctab.currentIndex()
            iimage = self.ctab.widget(curr_idx).iimage
            iname = "Image_"+str(int(time.time()))
            shutil.copy(os.path.join(images_path, iimage), os.path.join( os.path.expanduser("~"), iname ) )
            MyDialog("Info", "\n{}\nsaved in your home folder.".format(iname), self.cwindow)
        except Exception as E:
            MyDialog("Error", str(E), self.cwindow)
    
    def on_delete_image(self):
        time.sleep(0.1)
        try:
            curr_idx = self.ctab.currentIndex()
            twidget = self.ctab.widget(curr_idx)
            os.remove(os.path.join(images_path, twidget.iimage))
            self.ctab.removeTab(curr_idx)
            twidget.deleteLater()
            self.item_image_num -= 1
            if self.item_image_num == 1:
                self.on_label_text(self.imageLBL, self.item_image_num, "image")
            else:
                self.on_label_text(self.imageLBL, self.item_image_num, "images")
        except Exception as E:
            MyDialog("Error", str(E), self.cwindow)
    
    def on_clear_history(self):
        ret = MyDialog("Question", "Remove all the items?", self.cwindow)
        if ret.retval == QMessageBox.Yes:
            global CLIPS_DICT
            try:
                clips_temp = os.listdir(clips_path)
                if clips_temp:
                    for iitem in clips_temp:
                        os.remove(os.path.join(clips_path, iitem))
                        del CLIPS_DICT[iitem]
                #
                self.textLW.clear()
            except Exception as E:
                MyDialog("Error", str(E), self.cwindow)
            try:
                #
                images_temp = os.listdir(images_path)
                if images_temp:
                    for iitem in images_temp:
                        os.remove(os.path.join(images_path, iitem))
            except Exception as E:
                MyDialog("Error", str(E), self.cwindow)
            #
            self.textLW.clear()
            self.actual_clip = None
            #
            self.cwindow.close()
            self._is_clipboard_shown = 0

############# clipboard end ############## 
    
    # double click on label 0
    def on_labelw0(self, e):
        comm = None
        if e.button() == Qt.LeftButton:
            comm = label0_command1
        elif e.button() == Qt.MiddleButton:
            comm = label0_command2
        if comm:
            try:
                subprocess.Popen([comm])
            except:
                pass
        # QLabel.mouseDoubleClickEvent(self, e)
    
        
    # click on label 1
    def on_labelw1(self, e):
        comm = None
        if e.button() == Qt.LeftButton:
            comm = label1_command1
        elif e.button() == Qt.MiddleButton:
            comm = label1_command2
        if comm:
            try:
                subprocess.Popen([comm])
            except:
                pass
    
    # click on label 2
    def on_labelw2(self, e):
        comm = None
        if e.button() == Qt.LeftButton:
            comm = label2_command1
        elif e.button() == Qt.MiddleButton:
            comm = label2_command2
        if comm:
            try:
                subprocess.Popen([comm])
            except:
                pass
    
    # click on label 3
    def on_labelw3(self, e):
        comm = None
        if e.button() == Qt.LeftButton:
            comm = label3_command1
        elif e.button() == Qt.MiddleButton:
            comm = label3_command2
        if comm:
            try:
                subprocess.Popen([comm])
            except:
                pass
    
    # click on tlabel
    def on_tlabel(self, e):
        if e.button() == Qt.LeftButton:
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
            cur_time = QTime.currentTime().toString("hh:mm ap")
        else:
            cur_time = QTime.currentTime().toString("hh:mm")
        #
        if day_name:
            curr_date = QDate.currentDate().toString("ddd d")
            self.tlabel.setText(" "+curr_date+"  "+cur_time+" ")
        else:
            self.tlabel.setText(" "+cur_time+" ")
        # battery
        if use_battery_info:
            self.on_battery()
    
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
        fwin = QWindow.fromWinId(wid)
        fwin.setFlags(Qt.FramelessWindowHint | Qt.ForeignWindow)
        fwidget = QWidget.createWindowContainer(fwin)
        fwidget.setAutoFillBackground(True)
        tbutton_size2 = min(tbutton_size, button_size)
        if tbutton_size2 < button_size:
            tbutton_padding = ((button_size-tbutton_size2))
        else:
            tbutton_padding = button_padding
        fwidget.setContentsMargins(0,int(tbutton_padding/2),0,int(tbutton_padding/2))
        fwidget.setFixedSize(QSize(tbutton_size2-int(tbutton_padding/2),tbutton_size2-int(tbutton_padding/2)))
        fwidget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        fwidget.id = wid
        self.tray_box.update()
        #
        self.tray_box.addWidget(fwidget, 1, Qt.AlignCenter)
        # the main window to the center
        self.main_window_center()
    
    def tremove(self, wid):
        for i in range(self.tray_box.count()):
            if self.tray_box.itemAt(i) != None:
                widget = self.tray_box.itemAt(i).widget()
                if widget and widget.id == wid:
                    self.tray_box.removeWidget(widget)
                    widget.deleteLater()
                    break
        # 
        self.tray_box.update()
        self.tray_box.activate()
        # the main window to the center
        self.main_window_center()
    
    def tupdate(self, win, bcolor):
        wid = win.id
        for i in range(self.tray_box.count()):
            if self.tray_box.itemAt(i) != None:
                widget = self.tray_box.itemAt(i).widget()
                if widget and widget.id == wid:
                    self.tray_box.update()
                    widget.update()
                    win.change_attributes(background_pixel = bcolor)
                    widget.update()
                    self.tray_box.update()
                    win.unmap()
                    win.map()
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
    
    def on_label2(self, data):
        if data:
            self.labelw2.setText(data[0])
    
    def on_label3(self, data):
        if data:
            self.labelw3.setText(data[0])
    
    # launch the application from the prog_box
    def on_pbtn(self):
        prog = self.sender().pexec
        path = self.sender().ppath
        term = self.sender().tterm
        #
        tterminal = USER_TERMINAL
        if not tterminal:
            try:
                tterminal = os.environ['TERMINAL']
            except KeyError:
                tterminal = None
        #
        if path:
            if term:
                if not tterminal:
                    MyDialog("Info", "Terminal not setted in the config file.", self.cwindow)
                    return
                #
                try:
                    os.system("cd {} && {} -e {} & cd {}".format(path, tterminal, prog, os.getenv("HOME")))
                except Exception as E:
                    MyDialog("Error", str(E), self)
            else:
                try:
                    os.system("cd {} && {} & cd {} &".format(path, prog, os.getenv("HOME")))
                except Exception as E:
                    MyDialog("Error", str(E), self)
        else:
            if term:
                if not tterminal:
                    MyDialog("Info", "Terminal not setted in the config file.", self.cwindow)
                    return
                try:
                    os.system("cd {} && {} -e {} & cd {}".format(path, tterminal, prog, os.getenv("HOME")))
                except Exception as E:
                    MyDialog("Error", str(E), self)
            else:
                try:
                    os.system("cd {} && {} &".format(os.getenv("HOME"), prog))
                except Exception as E:
                    MyDialog("Error", str(E), self)
    
    # to get a window property
    def getProp(self, disp, win, prop):
        try:
            p = win.get_full_property(disp.intern_atom('_NET_WM_' + prop), 0)
            return [None] if (p is None) else p.value
        except:
            return [None]
    
    def winClose(self):
        global stopCD
        stopCD = 1
        global data_run
        data_run = 0
        qApp.quit()

    def restart(self):
        QCoreApplication.quit()
        status = QProcess.startDetached(sys.executable, sys.argv)
    
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
            elif data[0] == "UNMAPMAP":
                self._unmapmap(data[1], data[2])
    
    # hide the button from the taskbar when unmapped or unhide it
    def _unmapmap(self, win, _type):
        for i in range(self.ibox.count()):
            item = self.ibox.itemAt(i).widget()
            if not item:
                continue
            if isinstance(item, QPushButton):
                if item.winid == win.id:
                    if _type == 0:
                        item.setVisible(False)
                    elif _type == 1:
                        item.setVisible(True)
                    break
    
    def on_urgency(self, _n, item):
        if _n == 1:
            if self.list_uitem:
                # only one window with attention flag
                self.utimer.stop()
                self.list_uitem[0].setStyleSheet("border-color: {}; border=none".format(self.palette().color(QPalette.Background).name()))
                self.list_uitem = []
            #
            self.utimer = QTimer()
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
                    item.setStyleSheet("border-color: {}; border=none".format(self.palette().color(QPalette.Background).name()))
                except:
                    pass
        
    def f_on_urgency(self, item):
        try:
            if self._ut == 0 or (self._ut % 2) == 0:
                item.setStyleSheet("border: 2px solid; border-radius: 2px; border-color: red;")
                self._ut += 1
            elif self._ut == 1 or (self._ut % 2) != 0:
                item.setStyleSheet("border-color: {}; border=none".format(self.palette().color(QPalette.Background).name()))
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
                            item.setStyleSheet("border-color: {}; border=none".format(self.palette().color(QPalette.Background).name()))
                            return
                except:
                    return
        except:
            self.utimer.stop()
            if item in self.list_uitem:
                self.list_uitem.remove(item)
        
    
    # urgency flag
    def _urgency(self, _type, win):
        # do not use get_wm_hints(): gives not updated values
        if _type == 1 or _type == 2:
            for i in range(self.ibox.count()):
                item = self.ibox.itemAt(i).widget()
                if not item:
                    continue
                if isinstance(item, QPushButton):
                    if item.winid == win.id:
                        self.on_urgency(1, item)
                        break
        elif _type == 0:
            for i in range(self.ibox.count()):
                item = self.ibox.itemAt(i).widget()
                if not item:
                    continue
                if isinstance(item, QPushButton):
                    if item.winid == win.id:
                        self.on_urgency(0, item)
                        break
    
    # number of virtual desktops changed
    def virtual_desktops_changed(self, ndesks):
        self.on_virt_desk(ndesks)
    
    # current virtual desktop changed
    def active_virtual_desktop_changed(self, ndesk):
        for i in range(self.virtbox.count()):
            vbtn = self.virtbox.itemAt(i).widget()
            if isinstance(vbtn, QPushButton):
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
                    #
                    self.on_dock_items([w, on_desktop, win_exec])
                except:
                    pass

    
    # a window has been destroyed
    def delete_window_destroyed(self, window_list):
        for w in self.wid_l:
            if w not in window_list:
                self.wid_l.remove(w)
                self.on_remove_win(w)
                break
    
    # 1
    # add or remove virtual desktops
    def on_virt_desk(self, ndesks):
        curr_ndesks = self.virtbox.count()
        n = ndesks - curr_ndesks
        if n > 0:
            for i in range(n):
                vbtn = QPushButton()
                vbtn.setFlat(True)
                vbtn.setFixedSize(QSize(int(dock_height*1.3), dock_height))
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
                if isinstance(item, QPushButton):
                    self.virtbox.removeWidget(item)
                    item.deleteLater()
        # check the button
        for i in range(self.virtbox.count()):
            item = self.virtbox.itemAt(i).widget()
            if isinstance(item, QPushButton):
                if item.desk == self.active_virtual_desktop:
                    item.setChecked(True)
                else:
                    item.setChecked(False)
        # the main window to the center
        self.main_window_center()
    
    #
    def _icon_name_from_desktop(self, _prog):
        execArgs = [" %f", " %F", " %u", " %U", " %d", " %D", " %n", " %N", " %k", " %v"]
        _app_dirs = app_dirs_user+app_dirs_system
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
                    if os.path.basename(_exec) == _prog:
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
            if QIcon.hasThemeIcon(ret):
                licon = QIcon.fromTheme(ret)
            else:
                try:
                    licon = QIcon(ret)
                except:
                    pass
        #
        if not licon or licon.isNull():
            window = self.display.create_resource_object('window', winid)
            icon_name_tmp = window.get_full_property(self.display.intern_atom('_NET_WM_ICON_NAME'), 0)
            #
            if icon_name_tmp:
                if hasattr(icon_name_tmp, "value"):
                    try:
                        wicon = icon_name_tmp.value.decode()
                    except:
                        try:
                            icon_name_tmp = window.get_full_property(self.display.intern_atom('WM_ICON_NAME'), 0)
                            wicon = icon_name_tmp.value.decode()
                        except:
                            pass
                    #
                    if QIcon.hasThemeIcon(wicon):
                        licon = QIcon.fromTheme(wicon)
                    else:
                        licon = None
        #
        if not licon or licon.isNull():
            window = self.display.create_resource_object('window', winid)
            #
            win_name_class_tmp = window.get_wm_class()
            if not win_name_class_tmp:
                win_name_class = ""
            else:
                win_name_class = win_name_class_tmp[0]
            #
            if win_name_class and QIcon.hasThemeIcon(win_name_class):
                licon = QIcon.fromTheme(win_name_class)
        #
        if not licon or licon.isNull():
            icon_icon = window.get_full_property(self.display.intern_atom('_NET_WM_ICON'), 0)
            #
            icon_data = None
            target = button_size
            icon_lista = []
            if icon_icon is not None:
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
                    ####
                    if icon_data:
                        w = icon_data[0]
                        h = icon_data[1]
                        img = icon_data[2]
                        image = QImage(img, w, h, QImage.Format_ARGB32)
                    else:
                        image = QImage("icons/unknown.svg")
                else:
                    image = QImage("icons/unknown.svg")
                #
                pixmap = QPixmap(image)
                licon = QIcon(pixmap)
        #
        btn = QPushButton()
        btn.setContentsMargins(0,0,0,0)
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
        _ipad = 0
        btn.setFixedSize(QSize(button_size-_ipad, button_size-_ipad))
        btn.setIcon(licon)
        btn.setIconSize(QSize(button_size-button_padding-_ipad, button_size-button_padding-_ipad))
        btn.winid = pitem[0]
        btn.desktop = pitem[1]
        btn.pexec = pitem[2]
        btn.installEventFilter(self)
        #
        if pitem[1] == 0 or pitem[1] == None:
            self.ibox.addWidget(btn)
        elif pitem[1] > 0:
            self.ibox.insertWidget(pitem[1] * 100, btn, alignment=Qt.AlignCenter)
        #
        if PLAY_SOUND:
            play_sound("window-new.wav")
        #
        btn.setContextMenuPolicy(Qt.CustomContextMenu)
        btn.customContextMenuRequested.connect(self.btnClicked)
        # the main window to the center
        self.main_window_center()
    
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
                if isinstance(item, QPushButton):
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
            self.WM_CHANGE_STATE = self.display.intern_atom("WM_CHANGE_STATE")
            #
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
    
    # 5    
    # get the active window
    def get_active_window(self):
        window_id_temp = self.root.get_full_property(self.display.intern_atom('_NET_ACTIVE_WINDOW'), X.AnyPropertyType)
        if window_id_temp == None:
            return
        if window_id_temp.value.tolist() == []:
            return
        if window_id_temp:
            window_id = window_id_temp.value[0]
            # no active window
            if window_id == 0:
                if self.taskb_btn:
                    self.taskb_btn.setChecked(False)
                self.taskb_btn = None
            #
            else:
                window = self.display.create_resource_object('window', window_id)
                ######## check self.taskb_btn is still present
                _btn_found = 0
                for i in range(self.ibox.count()):
                    if self.ibox.itemAt(i).widget() == self.taskb_btn:
                        _btn_found = 1
                        break
                #
                if _btn_found == 0:
                    self.taskb_btn = None
                ########
                is_found = 0
                for i in range(self.ibox.count()):
                    btn = self.ibox.itemAt(i).widget()
                    if isinstance(btn, QPushButton):
                        if btn.winid == window_id:
                            if self.taskb_btn:
                                if self.taskb_btn:
                                    self.taskb_btn.setChecked(False)
                                    self.taskb_btn = None
                            #
                            btn.setChecked(True)
                            self.taskb_btn = btn
                            is_found = 1
                            #
                            break
                if not is_found:
                    # in case no window has been activated
                    if self.taskb_btn:
                        self.taskb_btn.setChecked(False)
                    self.taskb_btn = None
        
    # 6
    # remove the buttons
    def on_remove_win(self, pitem):
        ibox_num = self.ibox.count()
        for i in range(ibox_num):
            item = self.ibox.itemAt(i).widget()
            if isinstance(item, QPushButton):
                winid = item.winid
                if pitem == winid:
                    self.ibox.removeWidget(item)
                    item.deleteLater()
                    #
                    if PLAY_SOUND:
                        play_sound("window-close.wav")
                    break
        # the main window to the center
        self.main_window_center()
    
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
        
    # right menu of each launcher program button
    def pbtnClicked(self, QPos):
        pbtn = self.sender()
        # create context menu
        self.pbtnMenu = QMenu(self)
        self.unpin_prog = QAction("Unpin")
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
                if isinstance(item.widget(), QPushButton):
                    widget = item.widget()
                    if widget.pdesktop == pdesktop:
                        item.widget().deleteLater()
                        break
        except Exception as E:
            # message
            dlg = showDialog(1, str(E), self)
            result = dlg.exec_()
            dlg.close()
        #
        if len(os.listdir("applications")) == 0:
            self.sepLine2.hide()
        # the main window to the center
        self.main_window_center()
    
    # right menu of each application button
    def btnClicked(self, QPos):
        self.right_button_pressed = 1
        btn = self.sender()
        # create context menu
        self.btnMenu = QMenu(self)
        self.close_prog = QAction("Close")
        self.btnMenu.addAction(self.close_prog)
        self.close_prog.triggered.connect(lambda:self.on_close_prog(btn))
        # show context menu
        self.btnMenu.exec_(btn.mapToGlobal(QPos)) 
        
    
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
        if isinstance(widget, QPushButton):
            if event.type() == QEvent.HoverEnter:
                if hasattr(widget, "type"):
                    if widget.type == "bat":
                        _data, _status = self._get_battery_data()
                        _tooltip = " {} \n {} ".format(_data, _status)
                        widget.setToolTip(_tooltip)
                        return True
                if not self.right_button_pressed:
                    winid = widget.winid
                    window = self.display.create_resource_object('window', winid)
                    try:
                        win_name = window.get_full_property(self.display.intern_atom('_NET_WM_NAME'), 0).value
                        widget.setToolTip(str(win_name.decode(encoding='UTF-8')))
                    except: pass
            elif event.type() == QEvent.Wheel:
                if widget.winid == -999:
                    # event.angleDelta() : negative down - positive up
                    self.on_volume_change(event.angleDelta())
            elif event.type() == QEvent.MouseButtonPress:
                # volume button
                if widget.winid == -999:
                    if event.button() == Qt.MiddleButton:
                        self._mute_audio()
                        return True
                    elif event.button() == Qt.LeftButton:
                        self.on_volume1(widget.mapToGlobal(event.pos()))
                        return True
                    elif event.button() == Qt.RightButton:
                        self.on_volume2(widget.mapToGlobal(event.pos()))
                        return True
                # mic button
                elif widget.winid == -666:
                    if event.button() == Qt.RightButton:
                        self.on_mic2(widget.mapToGlobal(event.pos()))
                        return True
                    # elif event.button() == Qt.LeftButton:
                        # self.on_mic1(widget.mapToGlobal(event.pos()))
                        # return True
        elif isinstance(widget, QLabel):
            if event.type() == QEvent.Enter:
                curr_date = QDate.currentDate().toString("ddd d")
                widget.setToolTip(" "+curr_date+" ")
                return True
        else:
            return False
        return super(SecondaryWin, self).eventFilter(widget, event)
    
    
    # the virtual desktop button
    def on_vbtn_clicked(self):
        self.sender().setChecked(True)
        vdesk = self.sender().desk
        # virtual desktops
        ctype = self.display.intern_atom('_NET_CURRENT_DESKTOP')
        data = [vdesk, X.CurrentTime, 0,0,0]
        ev = pe.ClientMessage(window=self.root, client_type=ctype, data=(32,(data)))
        #
        mask = (X.SubstructureRedirectMask|X.SubstructureNotifyMask)
        self.root.send_event(ev, event_mask=mask)
        self.display.flush()
        
    # the main window to the center
    def main_window_center(self):
        return
    
############## audio

class audioThread(QThread):
    sig = pyqtSignal(list)
    
    def __init__(self, _pulse, parent=None):
        super(audioThread, self).__init__(parent)
        self.pulse = _pulse
    
    def run(self):
        with self.pulse.pulsectl.Pulse('event-audio') as pulse:
            #
            def audio_events(ev):
                # sink
                if ev.facility == pulse.event_facilities[6]:
                    # volume change
                    if ev.t == self.pulse.PulseEventTypeEnum.change:
                        self.sig.emit(["change-sink", ev.index])
                    elif ev.t == self.pulse.PulseEventTypeEnum.remove:
                        self.sig.emit(["remove-sink", ev.index])
                    elif ev.t == self.pulse.PulseEventTypeEnum.new:
                        self.sig.emit(["new-sink", ev.index])
                # source
                elif ev.facility == pulse.event_facilities[8]:
                    # if ev.t == self.pulse.PulseEventTypeEnum.change:
                        # self.sig.emit(["change-source", ev.index])
                    # el
                    if ev.t == self.pulse.PulseEventTypeEnum.remove:
                        self.sig.emit(["remove-source", ev.index])
                    elif ev.t == self.pulse.PulseEventTypeEnum.new:
                        self.sig.emit(["new-source", ev.index])
            #
            pulse.event_mask_set('sink', 'source')
            pulse.event_callback_set(audio_events)
            # pulse.event_listen(timeout=10)
            pulse.event_listen()


############## TRAY

class trayThread(QThread):
    sig = pyqtSignal(list)
    
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
                e.window.configure(onerror=self.error, width=tbutton_size-4, height=tbutton_size-4)
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
                pass
            #
            if self.data_run == 0:
                break
        #
        if self.data_run == 0:
            return

###################

class chooseDialog(QDialog):
    def __init__(self, progs, parent):
        super().__init__(parent)
        self.setWindowTitle("Info")
        self.progs = progs
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        self.layout = QVBoxLayout()
        message = QLabel("Choose which application to add:")
        self.layout.addWidget(message)
        #
        self.TWD = QTreeWidget()
        self.TWD.setHeaderLabels(["Applications", "Name"])
        self.TWD.setAlternatingRowColors(False)
        self.TWD.itemClicked.connect(self.fitem)
        self.layout.addWidget(self.TWD)
        #
        self.item_accepted = None
        for iitem in self.progs:
            idx = self.progs.index(iitem)
            tl = QTreeWidgetItem([" ".join(iitem[1]), str(iitem[2]), str(idx)])
            self.TWD.addTopLevelItem(tl)
        #
        self.layout.addWidget(self.buttonBox)
        #
        self.setLayout(self.layout)
        self.adjustSize()
        self.updateGeometry()
        self.resize(self.sizeHint())
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def fitem(self, item, col):
        self.item_accepted = item.text(2)
    
    def getItem(self):
        return self.item_accepted


class showDialog(QDialog):
    def __init__(self, dtype, lcontent, parent):
        super().__init__(parent)
        self.setWindowTitle("Info")
        #
        if dtype == 1:
            QBtn = QDialogButtonBox.Ok
        elif dtype == 2:
            QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        #
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        #
        # buttons style
        hpalette = self.palette().mid().color().name()
        csaa = ("QPushButton::hover:!pressed { border: none;")
        csab = ("background-color: {};".format(hpalette))
        csac = ("border-radius: 3px;")
        csad = ("text-align: center; }")
        csae = ("QPushButton { text-align: center;  padding: 5px; border: 1px solid #7F7F7F;")
        csae1 = ("background-color: '{}';".format(self.palette().midlight().color().name()))
        csae2 = (" }")
        csaf = ("QPushButton::checked { text-align: center; ")
        if button_menu_selected_color == "":
            csag = ("background-color: {};".format(self.palette().midlight().color().name()))
        else:
            csag = ("background-color: {};".format(button_menu_selected_color))
        csah = ("padding: 5px; border-radius: 3px;}")
        self.btn_csa = csaa+csab+csac+csad+csae+csae1+csae2+csaf+csag+csah
        for _w in self.buttonBox.children():
            if isinstance(_w, QPushButton):
                _w.setStyleSheet(self.btn_csa)
        #
        self.layout = QVBoxLayout()
        lay2 = QHBoxLayout()
        self.layout.addLayout(lay2)
        licon = QLabel()
        licon.setPixmap(QPixmap("icons/user.png"))
        lay2.addWidget(licon)
        message = QLabel(lcontent)
        lay2.addWidget(message, Qt.AlignCenter)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
        #
        self.adjustSize()
        self.updateGeometry()
        self.resize(self.sizeHint())
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

# notifications
class menuNotification(QWidget):
    def __init__(self, parent=None):
        super(menuNotification, self).__init__(parent)
        self.window = parent
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        ####### 
        self.mainBox = QHBoxLayout()
        self.mainBox.setContentsMargins(2,2,2,2)
        self.setLayout(self.mainBox)
        #
        parent_geom = self.window.geometry()
        win_height = parent_geom.height()
        #
        self.hbox = QHBoxLayout()
        self.mainBox.addLayout(self.hbox)
        #
        #### single notification box
        self.item_box = QVBoxLayout()
        self.item_box.setContentsMargins(0,0,0,0)
        self.hbox.addLayout(self.item_box)
        ## 
        if HYPER_CLICK == 0:
            self.item_textedit = QTextEdit()
            self.item_textedit.setReadOnly(True)
            self.item_textedit.setAcceptRichText(True)
            self.item_textedit.setTextInteractionFlags(Qt.TextBrowserInteraction)
        else:
            self.item_textedit = QTextBrowser()
            self.item_textedit.setOpenExternalLinks(True)
            self.item_textedit.highlighted.connect(self.on_link)
        #
        self.item_textedit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.item_box.addWidget(self.item_textedit)
        ##### list notification box
        self.lbox = QVBoxLayout()
        self.lbox.setContentsMargins(0,0,0,0)
        self.hbox.addLayout(self.lbox)
        #
        self.listWidget = QListWidget(self)
        self.listWidget.itemClicked.connect(self.listwidgetclicked)
        self.listWidget.setFixedSize(QSize(not_width,not_height))
        self.listWidget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
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
        self.listWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listWidget.verticalScrollBar().setStyleSheet(css)
        self.listWidget.setFocus(False)
        self.listWidget.setIconSize(QSize(not_icon_size, not_icon_size))
        #
        self.item_textedit.verticalScrollBar().setStyleSheet(css)
        #
        if LOST_FOCUS_CLOSE == 1:
            self.installEventFilter(self)
        #
        hpalette = self.palette().mid().color().name()
        csaa = ("QPushButton::hover:!pressed { border: none;")
        csab = ("background-color: {};".format(hpalette))
        csac = ("border-radius: 3px;")
        csad = ("text-align: center; }")
        csae = ("QPushButton { text-align: center;  padding: 5px; border: 1px solid #7F7F7F;}")
        csaf = ("QPushButton::checked { text-align: center; ")
        if button_menu_selected_color == "":
            csag = ("background-color: {};".format(self.palette().midlight().color().name()))
        else:
            csag = ("background-color: {};".format(button_menu_selected_color))
        csah = ("padding: 5px; border-radius: 3px;}")
        self.btn_csa = csaa+csab+csac+csad+csae+csaf+csag+csah
        #
        self.listDelete = QPushButton("Remove all")
        self.listDelete.clicked.connect(self.on_listdelete)
        self.lbox.addWidget(self.listDelete)
        #
        self.listDelete.setFlat(True)
        self.listDelete.setStyleSheet(self.btn_csa)
        #
        if DO_NOT_DISTURB:
            if os.path.exists(DO_NOT_DISTURB):
                _btn_text = "Disable"
                self.btn_donotdisturb = QPushButton(_btn_text)
                self.btn_donotdisturb.setCheckable(True)
                self.btn_donotdisturb.setFlat(True)
                self.lbox.addWidget(self.btn_donotdisturb)
                #
                self.btn_donotdisturb.setStyleSheet(self.btn_csa)
                #
                _nfile = "notificationdonotuse_"+str(DO_NOT_DISTURB_TYPE)
                if os.path.exists(os.path.join(DO_NOT_DISTURB, _nfile)):
                    self.btn_donotdisturb.setText("Disabled")
                    self.btn_donotdisturb.setChecked(True)
                #
                self.btn_donotdisturb.clicked.connect(self.on_not_disturb)
        ###########
        #
        self.populate_menu()
        #
        self.updateGeometry()
        # center
        NW = self.width()
        NH = self.height()
        if CENTRALIZE_EL == 1:
            sx = int((WINW - not_width)/2)
        # right
        elif CENTRALIZE_EL == 0 or CENTRALIZE_EL == 2:
            if use_menu == 2:
                sx = not_padx
            else:
                sx = WINW - not_width - not_win_content - not_padx
        #
        if dock_position == 0:
            sy = dock_height + not_pady
        elif dock_position == 1:
            sy = WINH - dock_height - not_height - not_pady
        #
        self.setGeometry(sx,sy,not_width+not_win_content,not_height)
        #
        self.hide()
        self.show()
        #
        _this_size = self.size()
        if dock_position == 0:
            sx = WINW - _this_size.width() - not_padx
            sy = dock_height + not_pady
        elif dock_position == 1:
            sx = WINW - _this_size.width() - not_padx
            sy = WINH - dock_height - _this_size.height() - not_pady
        if use_menu == 2:
            sx = not_padx
        self.move(sx,sy)
        
    def on_link(self, _url):
        self.item_textedit.setToolTip(_url.toString())
        self.item_textedit.setToolTipDuration(2000)
        
    def on_not_disturb(self):
        btn = self.sender()
        _nfile = "notificationdonotuse_"+str(DO_NOT_DISTURB_TYPE)
        if btn.isChecked():
            try:
                ff = open(os.path.join(DO_NOT_DISTURB, _nfile), "w")
                ff.write("")
                ff.close()
                btn.setText("Disabled")
                #
                self.window.btn_not.setIcon(QIcon("icons/notifications_disabled.svg"))
            except Exception as E:
                MyDialog("Error", "{}.".format(str(E)), self)
        else:
            try:
                os.remove(os.path.join(DO_NOT_DISTURB, _nfile))
                btn.setText("Disable")
                #
                if len(os.listdir(USE_NOTIFICATION)) > 0:
                   self.window.btn_not.setIcon(QIcon("icons/notifications_on.svg"))
                else:
                    self.window.btn_not.setIcon(QIcon("icons/notifications_off.svg"))
            except Exception as E:
                MyDialog("Error", "{}.".format(str(E)), self)
                
    
    def populate_menu(self):
        not_list = os.listdir(USE_NOTIFICATION)
        not_list.sort(reverse=True)
        for el in not_list:
            icon_name = os.path.join(USE_NOTIFICATION,el,"icon")
            text_name = os.path.join(USE_NOTIFICATION,el,"notification")
            #
            not_text = ""
            try:
                with open(text_name, "r") as ff:
                    not_text = ff.read()
            except:
                continue
            #
            _sep = "\n\n\n@\n\n\n"
            appname,summary,body = not_text.split(_sep)
            #
            icon = QPixmap(icon_name)
            icon = icon.scaled(QSize(not_icon_size,not_icon_size), aspectRatioMode=Qt.KeepAspectRatio)
            ilabel = QLabel()
            ilabel.setPixmap(icon)
            nitem = QListWidgetItem()
            # folder name - unix time
            nitem.el = el
            #
            # _user_time = datetime.datetime.fromtimestamp(int(el)).strftime('%Y-%m-%d %H:%M')
            _user_time = datetime.datetime.fromtimestamp(int(el)).strftime('%Y-%b-%d %H:%M')
            # keeps the aspect ration
            _i_w = icon.size().width()
            _i_h = icon.size().height()
            if _i_h > _i_w:
                nitem_text = "<html><body>{}<br><br><img src='{}' width={} ><br><br><b>{}</b><br><br>{}</body></html>".format(_user_time,icon_name, NOTIFICATION_ICON_SIZE, summary,body)
            else:
                nitem_text = "<html><body>{}<br><br><img src='{}' height={} ><br><br><b>{}</b><br><br>{}</body></html>".format(_user_time,icon_name, NOTIFICATION_ICON_SIZE, summary,body)
            #
            nitem.setToolTip(nitem_text)
            #
            self.item_widget = QWidget()
            item_layout = QHBoxLayout()
            item_layout.setContentsMargins(4,4,4,4)
            #
            item_lbl = QLabel(_user_time+"\n"+appname)
            #
            item_btn = QPushButton()
            item_btn.nitem = nitem
            item_btn.el = el
            item_btn.clicked.connect(self.on_item_btn)
            #
            btn_icon = QIcon("icons/list-remove.png")
            item_btn.setIcon(btn_icon)
            item_btn.setFixedSize(QSize(not_icon_size-4, not_icon_size-4))
            #
            item_btn.setSizePolicy(QSizePolicy.Maximum,QSizePolicy.Minimum)
            item_layout.addWidget(item_btn, Qt.AlignLeft)
            ilabel.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
            item_layout.addWidget(ilabel, Qt.AlignLeft)
            ilabel.setSizePolicy(QSizePolicy.Maximum,QSizePolicy.Minimum)
            item_layout.addWidget(item_lbl, Qt.AlignLeft)
            #
            self.item_widget.setLayout(item_layout)
            self.listWidget.addItem(nitem)
            nitem.setSizeHint(self.item_widget.sizeHint())
            self.listWidget.setItemWidget(nitem, self.item_widget)
    
    def _on_remove_item(self, nitem, el):
        not_path = os.path.join(USE_NOTIFICATION, el)
        try:
            shutil.rmtree(not_path)
        except Exception as E:
            MyDialog("Error", "{}.".format(str(E)), self)
    
    def on_item_btn(self):
        nitem = self.sender().nitem
        el = self.sender().el
        self._on_remove_item(nitem, el)
        self.listWidget.takeItem(self.listWidget.row(nitem))
        self.item_textedit.clear()
    
    
    def listwidgetclicked(self, item):
        self.item_textedit.clear()
        self.item_textedit.setText(item.toolTip())
    
    
    def on_listdelete(self):
        num_items = self.listWidget.count()
        if num_items:
            for i in range(num_items):
                nitem = self.listWidget.item(i)
                el = nitem.el
                self._on_remove_item(nitem, el)
        #
        self.listWidget.clear()
        self.item_textedit.clear()
    
    def eventFilter(self, object, event):
        if event.type() == QEvent.WindowDeactivate:
            if self.window.mn_is_shown:
                self.window.mn_is_shown.close()
                self.window.mn_is_shown = None
                return True
        return False


# menu
class menuWin(QWidget):
    def __init__(self, parent=None):
        super(menuWin, self).__init__(parent)
        self.window = parent
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        ####### 
        self.mainBox = QHBoxLayout()
        self.setLayout(self.mainBox)
        #
        sw = menu_width
        sh = 200
        sx = 0
        sy = 0
        #
        parent_geom = self.window.geometry()
        win_height = parent_geom.height()
        #
        self.hbox = QHBoxLayout()
        # 
        self.mainBox.setContentsMargins(2,2,2,2)
        self.mainBox.addLayout(self.hbox)
        #
        ##### left box
        self.lbox = QVBoxLayout()
        self.lbox.setContentsMargins(0,0,0,0)
        self.hbox.addLayout(self.lbox)
        #
        self.listWidget = QListWidget(self)
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
        self.listWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listWidget.verticalScrollBar().setStyleSheet(css)
        ###########
        self.line_edit = QLineEdit("")
        self.line_edit.setFrame(True)
        if search_field_bg:
            self.line_edit.setStyleSheet("background-color: {}".format(search_field_bg))
        #
        self.line_edit.textChanged.connect(self.on_line_edit)
        self.line_edit.setClearButtonEnabled(True)
        self.lbox.addWidget(self.line_edit)
        # self.line_edit.setFocus(True)
        self.listWidget.setFocus(True)
        self.listWidget.setIconSize(QSize(menu_app_icon_size, menu_app_icon_size))
        ##### right box
        self.rbox = QVBoxLayout()
        self.rbox.setContentsMargins(0,0,0,0)
        self.hbox.addLayout(self.rbox)
        #############
        self.fake_btn = QPushButton()
        self.fake_btn.setCheckable(True)
        self.fake_btn.setAutoExclusive(True)
        self.rbox.addWidget(self.fake_btn)
        self.fake_btn.hide()
        #
        self.pref = QPushButton("Bookmarks")
        self.pref.setIcon(QIcon("icons/bookmark.svg"))
        self.pref.setIconSize(QSize(menu_icon_size, menu_icon_size))
        self.pref.setFlat(True)
        #
        hpalette = self.palette().mid().color().name()
        csaa = ("QPushButton::hover:!pressed { border: none;")
        csab = ("background-color: {};".format(hpalette))
        csac = ("border-radius: 3px;")
        csad = ("text-align: left; }")
        csae = ("QPushButton { text-align: left;  padding: 5px;}")
        csaf = ("QPushButton::checked { text-align: left; ")
        if button_menu_selected_color == "":
            csag = ("background-color: {};".format(self.palette().midlight().color().name()))
        else:
            csag = ("background-color: {};".format(button_menu_selected_color))
        csah = ("padding: 5px; border-radius: 3px;}")
        self.btn_csa = csaa+csab+csac+csad+csae+csaf+csag+csah
        # self.pref.setStyleSheet(csa)
        self.pref.setStyleSheet(self.btn_csa)
        #
        self.pref.setCheckable(True)
        self.pref.setAutoExclusive(True)
        self.pref.clicked.connect(self.on_pref_clicked)
        self.rbox.addWidget(self.pref)
        #############
        sepLine = QFrame()
        sepLine.setFrameShape(QFrame.HLine)
        sepLine.setFrameShadow(QFrame.Plain)
        self.rbox.addWidget(sepLine)
        #
        self.rboxBtn = QVBoxLayout()
        self.rboxBtn.setContentsMargins(0,0,0,0)
        self.rbox.addLayout(self.rboxBtn)
        #
        self.populate_menu()
        #
        self.rbox.addStretch(1)
        #
        sepLine2 = QFrame()
        sepLine2.setFrameShape(QFrame.HLine)
        sepLine2.setFrameShadow(QFrame.Plain)
        sepLine2.setContentsMargins(0,0,0,0)
        self.rbox.addWidget(sepLine2)
        ##### buttons
        self.btn_box = QHBoxLayout()
        self.rbox.addLayout(self.btn_box)
        ## custom commands
        self.commBtn = QPushButton(QIcon("icons/list-commands.svg"), "")
        self.commBtn.setFlat(True)
        self.commBtn.setStyleSheet("border: none;")
        self.commBtn.setIconSize(QSize(service_icon_size, service_icon_size))
        self.commMenu = QMenu()
        self.commMenu.setToolTipsVisible(True)
        self.commBtn.setMenu(self.commMenu)
        #
        if COMM1_COMMAND or COMM2_COMMAND or COMM3_COMMAND:
            if COMM1_COMMAND:
                if COMM1_ICON:
                    icon = QIcon(COMM1_ICON)
                    if icon.isNull():
                        icon = QIcon("icons/none.svg")
                else:
                    icon = QIcon("icons/none.svg")
                baction = self.commMenu.addAction(icon, COMM1_NAME, lambda:self._on_change(COMM1_COMMAND))
                if COMM1_TOOLTIP:
                    baction.setToolTip(COMM1_TOOLTIP)
            if COMM2_COMMAND:
                if COMM2_ICON:
                    icon = QIcon(COMM2_ICON)
                    if icon.isNull():
                        icon = QIcon("icons/none.svg")
                else:
                    icon = QIcon("icons/none.svg")
                baction = self.commMenu.addAction(icon, COMM2_NAME, lambda:self._on_change(COMM2_COMMAND))
                if COMM2_TOOLTIP:
                    baction.setToolTip(COMM2_TOOLTIP)
            if COMM3_COMMAND:
                if COMM3_ICON:
                    icon = QIcon(COMM3_ICON)
                    if icon.isNull():
                        icon = QIcon("icons/none.svg")
                else:
                    icon = QIcon("icons/none.svg")
                baction = self.commMenu.addAction(icon, COMM3_NAME, lambda:self._on_change(COMM3_COMMAND))
                if COMM3_TOOLTIP:
                    baction.setToolTip(COMM3_TOOLTIP)
        #
        ## add custom applications
        if app_prog:
            self.menu_btn = QPushButton()
            self.menu_btn.setFlat(True)
            self.menu_btn.setStyleSheet("border: none;")
            self.menu_btn.setToolTip("Modify the menu")
            self.menu_btn.setIcon(QIcon("icons/menu.png"))
            self.menu_btn.setIconSize(QSize(service_icon_size, service_icon_size))
            self.menu_btn.setFlat(False)
            #
            self.menu_btn.clicked.connect(self.f_appWin)
            self.btn_box.addWidget(self.menu_btn)
        # menu
        if COMM1_COMMAND or COMM2_COMMAND or COMM3_COMMAND:
            self.btn_box.addWidget(self.commBtn)
        # logout button
        if logout_command:
            self.lo_cmd_btn = QPushButton()
            self.lo_cmd_btn.setFlat(True)
            self.lo_cmd_btn.setStyleSheet("border: none;")
            self.lo_cmd_btn.setToolTip("Logout")
            self.lo_cmd_btn.setIcon(QIcon("icons/system-logout.svg"))
            self.lo_cmd_btn.setIconSize(QSize(service_icon_size, service_icon_size))
            self.lo_cmd_btn.setFlat(False)
            #
            self.lo_cmd_btn.clicked.connect(lambda x: self._on_cmd_service("Logout?", logout_command))
            self.btn_box.addWidget(self.lo_cmd_btn)
        # restart button
        if restart_command:
            self.rs_cmd_btn = QPushButton()
            self.rs_cmd_btn.setFlat(True)
            self.rs_cmd_btn.setStyleSheet("border: none;")
            self.rs_cmd_btn.setToolTip("Restart")
            self.rs_cmd_btn.setIcon(QIcon("icons/system-restart.svg"))
            self.rs_cmd_btn.setIconSize(QSize(service_icon_size, service_icon_size))
            self.rs_cmd_btn.setFlat(False)
            #
            self.rs_cmd_btn.clicked.connect(lambda x: self._on_cmd_service("Restart?", restart_command))
            self.btn_box.addWidget(self.rs_cmd_btn)
        # shutdown button
        if shutdown_command:
            self.st_cmd_btn = QPushButton()
            self.st_cmd_btn.setFlat(True)
            self.st_cmd_btn.setStyleSheet("border: none;")
            self.st_cmd_btn.setToolTip("Shutdown")
            self.st_cmd_btn.setIcon(QIcon("icons/system-shutdown.svg"))
            self.st_cmd_btn.setIconSize(QSize(service_icon_size, service_icon_size))
            self.st_cmd_btn.setFlat(False)
            #
            self.st_cmd_btn.clicked.connect(lambda x: self._on_cmd_service("Shutdown?", shutdown_command))
            self.btn_box.addWidget(self.st_cmd_btn)
        #
        sepLine2 = QFrame()
        sepLine2.setFrameShape(QFrame.VLine)
        sepLine2.setFrameShadow(QFrame.Plain)
        sepLine2.setContentsMargins(0,0,0,0)
        sepLine2.setStyleSheet("QFrame{border: None; background-color: transparent;}")
        self.rbox.addWidget(sepLine2)
        #
        self.hide()
        self.show()
        self.updateGeometry()
        #
        # left
        if use_menu == 1:
            if CENTRALIZE_EL == 1 or CENTRALIZE_EL == 2:
                sx = int((WINW - menu_width)/2)
            elif CENTRALIZE_EL == 0:
                sx = parent_geom.x() + menu_padx
        # right
        elif use_menu == 2:
            sx = WINW - menu_width - menu_padx
        #
        if dock_position == 1:
            sy = WINH - dock_height - self.geometry().height() - menu_pady
        elif dock_position == 0:
            sy = dock_height + menu_pady
        # self.move(sx,sy)
        self.setGeometry(sx,sy,sw,sh)
        #
        self.emulate_clicked(self.pref, 100)
        self.pref.setChecked(True)
        #
        if item_highlight_color:
            ics = "QListWidget:item::hover:!pressed { "+"background-color: {}".format(item_highlight_color)+";}"
            self.listWidget.setStyleSheet(ics)
        #
        self.listWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidget.customContextMenuRequested.connect(self.itemClicked)
        # the bookmark button has been pressed
        self.itemBookmark = 1
        # while an item is been searching
        self.itemSearching = 0
        if LOST_FOCUS_CLOSE == 1:
            self.installEventFilter(self)
    
    #
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
            if result == QDialog.Accepted:
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
        if result == QDialog.Accepted:
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
            if result == QDialog.Accepted:
                dlg.close()
            else:
                dlg.close()

    
    def eventFilter(self, object, event):
        if event.type() == QEvent.WindowDeactivate:
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
        QTimer.singleShot(ms, button.clicked.emit)
    
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
                        # search for the icon by executable
                        icon = QIcon.fromTheme(el[1])
                        if icon.isNull() or icon.name() == "":
                            # set the icon by desktop file - not full path
                            icon = QIcon.fromTheme(el[2])
                            if icon.isNull() or icon.name() == "":
                                # set the icon by desktop file - full path
                                if os.path.exists(el[2]):
                                    icon = QIcon(el[2])
                                    if icon.isNull():
                                        # set a generic icon
                                        icon = QIcon("icons/none.svg")
                                        litem = QListWidgetItem(icon, el[0])
                                        litem.picon = "none"
                                    else:
                                        litem = QListWidgetItem(icon, el[0])
                                        litem.picon = el[2]
                                else:
                                    # set a generic icon
                                    icon = QIcon("icons/none.svg")
                                    litem = QListWidgetItem(icon, el[0])
                                    litem.picon = "none"
                            else:
                                litem = QListWidgetItem(icon, el[0])
                                litem.picon = icon.name()
                        else:
                            litem = QListWidgetItem(icon, el[0])
                            litem.picon = el[1]
                        #
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
            btn = QPushButton(el)
            btn.setIcon(QIcon("icons/{}".format(el+".svg")))
            btn.setIconSize(QSize(menu_icon_size, menu_icon_size))
            btn.setFlat(True)
            btn.setStyleSheet("text-align: left;")
            ##########
            # hpalette = self.palette().mid().color().name()
            # csaa = ("QPushButton::hover:!pressed { border: none;")
            # csab = ("background-color: {};".format(hpalette))
            # csac = ("border-radius: 3px;")
            # csad = ("text-align: left; }")
            # csae = ("QPushButton { text-align: left;  padding: 5px;}")
            # csaf = ("QPushButton::checked { text-align: left; ")
            # # csag = ("background-color: {};".format(self.palette().midlight().color().name()))
            # csag = ("background-color: #7F7F7F;")
            # csah = ("padding: 5px; border-radius: 3px;}")
            # csa = csaa+csab+csac+csad+csae+csaf+csag+csah
            btn.setStyleSheet(self.btn_csa)
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
            # search for the icon by executable
            icon = QIcon.fromTheme(el[1])
            if icon.isNull() or icon.name() == "":
                # set the icon by desktop file - not full path
                icon = QIcon.fromTheme(el[2])
                if icon.isNull() or icon.name() == "":
                    # set the icon by desktop file - full path
                    if os.path.exists(el[2]):
                        icon = QIcon(el[2])
                        if icon.isNull():
                            # set a generic icon
                            icon = QIcon("icons/none.svg")
                            litem = QListWidgetItem(icon, el[0])
                            litem.picon = "none"
                        else:
                            litem = QListWidgetItem(icon, el[0])
                            litem.picon = el[2]
                    else:
                        # set a generic icon
                        icon = QIcon("icons/none.svg")
                        litem = QListWidgetItem(icon, el[0])
                        litem.picon = "none"
                else:
                    litem = QListWidgetItem(icon, el[0])
                    litem.picon = icon.name()
            else:
                litem = QListWidgetItem(icon, el[0])
                litem.picon = el[1]
            #
            # executable
            litem.exec_n = el[1]
            # working directory
            litem.ppath = el[4]
            # comment
            litem.setToolTip(el[3])
            # use terminal
            litem.tterm = el[5]
            # file desktop full path
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
        self.listMenu= QMenu()
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
        # PIN
        item_idx = self.listWidget.indexAt(QPos)
        _item = self.listWidget.itemFromIndex(item_idx)
        item_fpath = _item.fpath
        fret = self.on_check_pin(item_fpath)
        if fret:
            item_p = self.listMenu.addAction("Pin")
        #
        action = self.listMenu.exec_(self.listWidget.mapToGlobal(QPos))
        #
        if fret == 1 and action == item_p:
            self.on_add_item_pin(_item)
        #
        elif pret == 1 and action == item_b:
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
    
    
    def on_check_pin(self, _fpath):
        list_apps = os.listdir("applications")
        if os.path.basename(_fpath) in list_apps:
            return 0
        else:
            return 1
    
    # pin the application
    def on_add_item_pin(self, _item):
        # file desktop full path
        item_fpath = _item.fpath
        # application name
        item_name = _item.text()
        # icon name
        item_icon = _item.picon
        # executable
        item_exec = _item.exec_n
        # use terminal
        item_term = _item.tterm
        # working directory
        item_ppath = _item.ppath
        #
        try:
            shutil.copy(item_fpath, "applications"+"/"+os.path.basename(item_fpath))
        except Exception as E:
            dlg = showDialog(1, str(E), self)
            result = dlg.exec_()
            dlg.close()
            return
        # add the button
        pbtn = QPushButton()
        pbtn.setFlat(True)
        #
        picon = None
        if os.path.exists(item_icon):
            picon = QIcon(item_icon)
        #
        if picon is None or picon.isNull():
            picon = QIcon.fromTheme(os.path.basename(item_icon).split(".")[0])
        if picon is None or picon.isNull():
            picon = QIcon("icons/unknown.svg")
        pbtn.setFixedSize(QSize(pbutton_size, pbutton_size))
        pbtn.setIcon(picon)
        pbtn.setIconSize(pbtn.size())
        pbtn.setToolTip(item_name or item_exec)
        #
        pbtn.pexec = item_exec
        pbtn.tterm = item_term
        pbtn.pdesktop = os.path.basename(item_fpath)
        #
        pbtn.ppath = item_ppath
        #
        self.window.prog_box.insertWidget(len(os.listdir("applications")), pbtn)
        if len(os.listdir("applications")) == 1:
            self.window.sepLine2.show()
        pbtn.clicked.connect(self.window.on_pbtn)
        pbtn.setContextMenuPolicy(Qt.CustomContextMenu)
        # unpin action
        pbtn.customContextMenuRequested.connect(self.window.pbtnClicked)
    
    
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
            if not tterminal or not shutil.which(tterminal):
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
        # ICON - NAME - EXEC - TOOLTIP - PATH - TERMINAL - FILENAME
        for el in prog_list:
            ICON = el[0].strip("\n")
            NAME = el[1].strip("\n")
            EXEC = el[2].strip("\n")
            TOOLTIP = el[3].strip("\n")
            PATH = el[4].strip("\n")
            TTERM = el[5].strip("\n")
            FILENAME = el[6].strip("\n")
            #
            icon = QIcon.fromTheme(ICON)
            if icon.isNull():
                icon = QIcon(icon)
            if icon.isNull():
                icon = QIcon("icons/none.svg")
            litem = QListWidgetItem(icon, NAME)
            litem.lbookmark = FILENAME
            litem.exec_n = EXEC
            litem.ppath = PATH
            litem.setToolTip(TOOLTIP)
            if TTERM == "True":
                litem.tterm = True
            else:
                litem.tterm = False
            #
            self.listWidget.addItem(litem)
            #
        self.listWidget.sortItems(Qt.AscendingOrder)
        self.listWidget.scrollToTop()
        if self.listWidget.count():
            self.listWidget.item(0).setSelected(False)
            self.listWidget.setFocus(True)
        
    #
    def listItemRightClickedToRemove(self, QPos):
        self.listMenuR= QMenu()
        item_b = self.listMenuR.addAction("Remove from bookmark")
        action = self.listMenuR.exec_(self.listWidget.mapToGlobal(QPos))
        if action == item_b:
            item_idx = self.listWidget.indexAt(QPos)
            item_row = item_idx.row()
            _item = self.listWidget.item(item_row)
            #
            try:
                os.remove(os.path.join("bookmarks",str(_item.lbookmark)))
                item_removed = self.listWidget.takeItem(item_row)
            except:
                pass

# popup per calendar
class calendarWin(QWidget):
    def __init__(self, parent=None):
        super(calendarWin, self).__init__(parent)
        self.window = parent
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        ####### main box 
        mainBox = QHBoxLayout()
        mainBox.setContentsMargins(0,0,0,0)
        self.setLayout(mainBox)
        ## basic box
        self.hbox = QHBoxLayout()
        self.hbox.setContentsMargins(2,2,2,2)
        mainBox.addLayout(self.hbox)
        #### 
        self.vbox_1 = QVBoxLayout()
        self.vbox_1.setContentsMargins(0,0,0,0)
        self.hbox.addLayout(self.vbox_1)
        # calendar event box
        self.scroll = QScrollArea()
        self.widget = QWidget()
        self.vbox = QVBoxLayout()
        self.widget.setLayout(self.vbox)
        # calendar event box navigator buttons
        self.ldatebox = QHBoxLayout()
        self.ldatebox.setContentsMargins(0,0,0,0)
        self.vbox_1.addLayout(self.ldatebox)
        #
        tomonth = datetime.datetime.now().strftime("%B")
        toyear = str(datetime.datetime.now().year)
        #
        self.mlabel = QLabel(tomonth+" "+toyear)
        self.mlabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.mlabel.setAlignment(Qt.AlignCenter)
        self.mlabel.mousePressEvent = self.go_today 
        #
        self.pmonth = QPushButton()
        self.pmonth.setIcon(QIcon("icons/go-prev.png"))
        self.pmonth.setFlat(True)
        #
        self.nmonth = QPushButton()
        self.nmonth.setIcon(QIcon("icons/go-next.png"))
        self.nmonth.setFlat(True)
        #
        self.pmonth.clicked.connect(self.on_prev_month)
        self.nmonth.clicked.connect(self.on_next_month)
        #
        self.ldatebox.addWidget(self.pmonth)
        self.ldatebox.addWidget(self.mlabel)
        self.ldatebox.addWidget(self.nmonth)
        #
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedWidth(appointment_window_size)
        self.widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
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
        #
        ################ the calendar
        thisMonth = QDate().currentDate().month()
        thisYear = QDate().currentDate().year()
        l_e = []
        # 
        for ev in list_events_all:
            tdata = ev.DTSTART
            ttime = ("{}:{}".format(tdata[9:11], tdata[11:13]))
            tdate = QDate.fromString(ev.DTSTART[0:8], 'yyyyMMdd')
            l_e.append((tdate, ttime+" "+ev.SUMMARY, ev.DESCRIPTION))
        #
        l_e.sort()
        ###
        self.calendar = Calendar(self, l_e, self.vbox)
        self.calendar.setContentsMargins(0,0,0,0)
        self.calendar.setNavigationBarVisible(False)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendar.currentPageChanged.connect(self.calendar_month_changed)
        self.calendar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        self.hbox.addWidget(self.calendar)
        self.show()
        #
        if self.window.mw_is_shown:
            self.window.mw_is_shown.close()
            self.window.mw_is_shown = None
        #
        cwX = 0
        cwY = 0
        NW = self.width()
        NH = self.height()
        if CENTRALIZE_EL == 0 or CENTRALIZE_EL == 2:
            this_geom = self.geometry()
            if dock_position == 0:
                sy = dock_height+clock_gapy
                if use_clock == 2:
                    sx = WINW-this_geom.width()-clock_gapx
                elif use_clock == 1:
                    sx = clock_gapx
            elif dock_position == 1:
                sy = WINH - dock_height - self.geometry().height() - clock_gapy
                if use_clock == 2:
                    sx = WINW-this_geom.width()-clock_gapx
                elif use_clock == 1:
                    sx = clock_gapx
            self.setGeometry(sx, sy, -1,-1)
        elif CENTRALIZE_EL == 1:
            this_geom = self.geometry()
            sx = int((NW - this_geom.width())/2)
            if dock_position == 0:
                sy = (dock_height+clock_gapy)
            elif dock_position == 1:
                sy = (NH-dock_height-this_geom.height()-clock_gapy)
            self.setGeometry(sx, sy, -1,-1)
        #
        if LOST_FOCUS_CLOSE == 1:
            self.installEventFilter(self)
    
    def eventFilter(self, object, event):
        if event.type() == QEvent.WindowDeactivate:
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
        to_day = QDate().currentDate()
        self.calendar.setSelectedDate(to_day)
        tomonth = datetime.datetime.now().strftime("%B")
        toyear = str(datetime.datetime.now().year)
        self.mlabel.setText(tomonth+" "+toyear)
        
    #
    def on_prev_month(self):
        thisMonth = QDate().currentDate().month()
        thisYear = QDate().currentDate().year()
        selectedDate = self.calendar.selectedDate()
        selectedMonth = selectedDate.month()
        selectedYear = selectedDate.year()
        thisDay = 1
        if selectedMonth == 1:
            selectedYear -= 1
            selectedMonth = 13
        if (thisMonth == selectedMonth - 1) and (thisYear == selectedYear):
            thisDay = QDate().currentDate().day()
        #
        self.calendar.setSelectedDate(QDate(selectedYear, selectedMonth-1, thisDay))
        #
        nmonth2 = datetime.datetime.strptime(str(selectedMonth-1), '%m')
        nmonth = nmonth2.strftime('%B')
        self.mlabel.setText(str(nmonth)+" "+str(selectedYear))
    # 
    def on_next_month(self):
        thisMonth = QDate().currentDate().month()
        thisYear = QDate().currentDate().year()
        selectedDate = self.calendar.selectedDate()
        selectedMonth = selectedDate.month()
        selectedYear = selectedDate.year()
        thisDay = 1
        if selectedMonth == 12:
            selectedYear += 1
            selectedMonth = 0
        if (thisMonth == selectedMonth+1) and (thisYear == selectedYear):
            thisDay = QDate().currentDate().day()
        #
        self.calendar.setSelectedDate(QDate(selectedYear, selectedMonth+1, thisDay))
        #
        nmonth2 = datetime.datetime.strptime(str(selectedMonth+1), '%m')
        nmonth = nmonth2.strftime('%B')
        self.mlabel.setText(str(nmonth)+" "+str(selectedYear))
        

class ClickLabel(QLabel):
    
    def mouseDoubleClickEvent(self, event):
        if event_command:
            try:
                # output format: 20220301
                cdate = self.cdate.toString('yyyyMMdd')
                subprocess.Popen([event_command, cdate])
            except:
                pass
        #
        QLabel.mousePressEvent(self, event)      



class Calendar(QCalendarWidget):
    
    def __init__(self, parent=None, c_dict=None, vbox=None):
        super(Calendar, self).__init__(parent)
        font = QFont()
        if calendar_cal_font:
            font.setFamily(calendar_cal_font)
        else:
            font.setFamily(font.defaultFamily())
        if calendar_cal_font_size:
            font.setPointSize(calendar_cal_font_size)
        if calendar_cal_font or calendar_cal_font_size:
            self.setFont(font)
        self.parent = parent
        self.events = c_dict
        self.cvbox = vbox
        self.color3 = QColor(calendar_appointment_day_color)
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
        self.vw = self.findChild(QTableView)
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
    
    def pageChanded(self, year, month):
        date = self.selectedDate()
        self.popCalEv(date)
    
    def paintCell(self, painter, rect, date):
        super().paintCell(painter, rect, date)
        if date in self.events_date:
            psize = 20
            startPoint = QPoint(rect.x()+rect.width(), rect.y()+rect.height()-psize)
            controlPoint1 = QPoint(rect.x()+rect.width(), rect.y()+rect.height())
            controlPoint2 = QPoint(rect.x()+rect.width()-psize, rect.y()+rect.height())
            endPoint = QPoint(rect.x(), rect.y())
            #
            path = QPainterPath(startPoint)
            path.lineTo(controlPoint1)
            path.lineTo(controlPoint2)
            painter.fillPath(path, self.color3)

# class profileDialog(QDialog):
    # def __init__(self,w,_list):
        # super().__init__()
        # self.w = w
        # self._list = _list
        # self.setWindowTitle("Choose one...")
        # layout = QVBoxLayout()
        # self.label = QLabel("Choose one:")
        # layout.addWidget(self.label)
        # #
        # self.combo = QComboBox()
        # # self.combo.currentIndexChanged.connect(self.on_combo_changed)
        # layout.addWidget(self.combo)
        # #
        # self.setLayout(layout)
        # #
        # if self._list:
            # self.combo.addItems(self._list)
        # #
        # self._value = None
        
    # # def on_combo_changed(self, _idx):
        # # pass
        
    # def getValue(self):
        # return self._value
    
    # def closeEvent(self,event):
        # self._value = self.combo.currentText()
        # self.accept()


class TimerWindow(QWidget):
    def __init__(self,w):
        super().__init__()
        self.w = w
        self.setWindowTitle("Set the timer")
        layout = QVBoxLayout()
        self.setLayout(layout)
        #
        self.label = QLabel("Add a timer:")
        layout.addWidget(self.label)
        #
        self.date_time = QDateTimeEdit()
        # setted to time only
        self.date_time.setDisplayFormat("HH:mm")
        dt = QDateTime()
        dt.setDate(QDate.currentDate())
        dt.setTime(QTime.currentTime())
        self.date_time.setDateTime(dt)
        self.date_time.dateTimeChanged.connect(self.on_date_time)
        layout.addWidget(self.date_time)
        #
        self.chkb1 = QCheckBox("Sound")
        layout.addWidget(self.chkb1)
        self.chkb2 = QCheckBox("Notification")
        # layout.addWidget(self.chkb2)
        self.chkb3 = QCheckBox("Dialog")
        layout.addWidget(self.chkb3)
        #
        self.btn_box = QHBoxLayout()
        layout.addLayout(self.btn_box)
        #
        self.btn_cancel = QPushButton("Cancel")
        self.btn_box.addWidget(self.btn_cancel)
        self.btn_cancel_pressed = None
        self.btn_cancel.clicked.connect(self.on_btn_cancel)
        #
        self.btn_accept = QPushButton("Accept")
        self.btn_box.addWidget(self.btn_accept)
        self.btn_accept_pressed = None
        self.btn_accept.clicked.connect(self.on_btn_accept)
        #
        self._value = None
    
    def on_date_time(self):
        self._value = self.date_time.dateTime()
    
    def on_btn_cancel(self):
        self.btn_cancel_pressed = 1
        self.close()
    
    def on_btn_accept(self):
        # if not self.chkb1.isChecked() and not self.chkb2.isChecked() and not self.chkb3.isChecked():
        if not self.chkb1.isChecked() and not self.chkb3.isChecked():
            return
        self.btn_accept_pressed = 1
        self.close()
    
    def closeEvent(self,event):
        if self._value and self.btn_cancel_pressed == None and self.btn_accept_pressed == 1:
            _date = self._value.date().toString("yyyy.MM.dd")
            _time = self._value.time().toString()
            with open(os.path.join(curr_path,"mytimer"), "w") as _f:
                _f.write(_date+"\n"+_time+"\n"+str(int(self.chkb1.isChecked()))+"\n"+str(int(self.chkb2.isChecked()))+"\n"+str(int(self.chkb3.isChecked())))
            #
            self.w._set_timer([_date, _time, self.chkb1.isChecked(), self.chkb2.isChecked(), self.chkb3.isChecked()])

    
# type - message - parent
class MyDialog(QMessageBox):
    def __init__(self, *args):
        super(MyDialog, self).__init__(args[-1])
        if args[0] == "Info":
            self.setIcon(QMessageBox.Information)
            self.setStandardButtons(QMessageBox.Ok)
        elif args[0] == "Error":
            self.setIcon(QMessageBox.Critical)
            self.setStandardButtons(QMessageBox.Ok)
        elif args[0] == "Question":
            self.setIcon(QMessageBox.Question)
            self.setStandardButtons(QMessageBox.Yes|QMessageBox.Cancel)
        self.setWindowIcon(QIcon("icons/clipman.svg"))
        self.setWindowTitle(args[0])
        self.resize(dialWidth,100)
        self.setText(args[1])
        self.retval = self.exec_()
    
    def event(self, e):
        result = QMessageBox.event(self, e)
        #
        self.setMinimumHeight(0)
        self.setMaximumHeight(16777215)
        self.setMinimumWidth(0)
        self.setMaximumWidth(16777215)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # 
        return result


###################

if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    size = screen.size()
    WINW = size.width()
    WINH = size.height()
    _dock = SecondaryWin(1, app, None, None)
    if dock_position == 0:
        _dock.setGeometry(0,0,WINW,dock_height)
    elif dock_position == 1:
        _dock.setGeometry(-1,WINH-dock_height,WINW,dock_height)
    #
    _dock.show()
    ret = app.exec_()
