#!/usr/bin/env python3
# V 0.9.0.2
from PyQt5 import QtCore, QtGui, QtWidgets
import sys, os, time
import shutil
from Xlib.display import Display
from Xlib import X, Xatom, Xutil, error
import Xlib.protocol.event as pe
import subprocess
from xdg import DesktopEntry
from xdg import IconTheme
from ewmh import EWMH
ewmh = EWMH()
from cfg_dock import *

# width and height of the program
WINW = 0
WINH = 0

this_window = None
this_windowID = None

### TRAY
P_HEIGHT        = dock_height   # Panel height
TRAY_I_HEIGHT   = min(tbutton_size, button_size)   # System tray icon height (usually 16 or 24)
TRAY_I_WIDTH    = min(tbutton_size, button_size)   # System tray icon width  (usually 16 or 24)
TRAY            = 1             # System tray section

#############
stopCD = 0
data_run = 1
# 
class winThread(QtCore.QThread):
    
    sig = QtCore.pyqtSignal(list)
    
    def __init__(self, display, parent=None):
        super(winThread, self).__init__(parent)
        self.display = display
        self.root = self.display.screen().root
        #
        self.win_l = []
        self.root.change_attributes(event_mask=X.PropertyChangeMask)
    
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
            
            # properties
            if (event.type == X.PropertyNotify):
                if event.atom == self.display.intern_atom('_NET_NUMBER_OF_DESKTOPS'):
                    vd_v = self.root.get_full_property(self.display.intern_atom('_NET_NUMBER_OF_DESKTOPS'), X.AnyPropertyType).value
                    number_of_virtual_desktops = vd_v.tolist()[0]
                    self.sig.emit(["DESKTOP_NUMBER", number_of_virtual_desktops])
                # change the current desktop
                if event.atom == self.display.intern_atom("_NET_CURRENT_DESKTOP"):
                    cvd_v = self.root.get_full_property(self.display.intern_atom("_NET_CURRENT_DESKTOP"), X.AnyPropertyType).value
                    active_virtual_desktop = cvd_v.tolist()[0]
                    self.sig.emit(["ACTIVE_VIRTUAL_DESKTOP", active_virtual_desktop])
                
                # active window changed
                if event.atom == self.display.intern_atom('_NET_ACTIVE_WINDOW'):
                    self.sig.emit(["ACTIVE_WINDOW_CHANGED", ""])
                
                #
                if event.atom == self.display.intern_atom('_NET_CLIENT_LIST'):
                    self.sig.emit(["NETLIST"])
                    
            if stopCD:
                break
        if stopCD:
            return


######################

# label1
class label1Thread(QtCore.QThread):
    
    label1sig = QtCore.pyqtSignal(list)
    
    def __init__(self, label1_data):
        super(label1Thread, self).__init__()
        # script - loop
        self.label1_data = label1_data
    
    def run(self):
        while data_run:
            data = subprocess.check_output([self.label1_data[0]], shell=True, encoding='utf-8').strip("\n")
            self.label1sig.emit([data])
            time.sleep(self.label1_data[1])
            if not data_run:
                break
        
# label2
class label2Thread(QtCore.QThread):
    
    label2sig = QtCore.pyqtSignal(list)
    
    def __init__(self, label2_data):
        super(label2Thread, self).__init__()
        # script - loop
        self.label2_data = label2_data
    
    def run(self):
        while data_run:
            data = subprocess.check_output([self.label2_data[0]], shell=True, encoding='utf-8').strip("\n")
            self.label2sig.emit([data])
            time.sleep(self.label2_data[1])
            if not data_run:
                break


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
        ## the number of virtual desktops
        atom_vs = self.display.intern_atom('_NET_NUMBER_OF_DESKTOPS')
        vd_v = self.root.get_full_property(atom_vs, X.AnyPropertyType).value
        self.num_virtual_desktops = vd_v.tolist()[0]
        ## the active virtual desktop - 0 is 1 etc.
        atom_cvd = self.display.intern_atom("_NET_CURRENT_DESKTOP")
        vd_cv = self.root.get_full_property(atom_cvd, X.AnyPropertyType).value
        self.active_virtual_desktop = vd_cv.tolist()[0]
        # actual virtual desktop
        self.actual_virtual_desktop = self.active_virtual_desktop
        #######
        screen = app.primaryScreen()
        self.screen_size = screen.size()
        #
        if self.position in [0,1]:
            self.abox = QtWidgets.QVBoxLayout()
            self.abox.setContentsMargins(0,0,0,0)
            self.setLayout(self.abox)
            ## virtual desktop box
            self.virtbox = QtWidgets.QHBoxLayout()
            self.virtbox.setContentsMargins(0,0,0,0)
            self.abox.addLayout(self.virtbox)
            ## main program box
            self.ibox = QtWidgets.QVBoxLayout()
            self.ibox.setContentsMargins(0,0,0,0)
            self.abox.addLayout(self.ibox)
        # 3 top - 4 bottom
        elif self.position in [2,3]:
            if with_compositor:
                self.mainBox = QtWidgets.QHBoxLayout()
                self.setLayout(self.mainBox)
                #
                self.abox = QtWidgets.QHBoxLayout()
                self.abox.setContentsMargins(0,0,0,0)
                self.abox.setDirection(QtWidgets.QBoxLayout.LeftToRight)
                self.abox.setSpacing(0)
                #
                self.frame=QtWidgets.QFrame(self)
                self.frame.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
                self.frame.setLayout(self.abox)
                self.mainBox.addWidget(self.frame)
                if with_transparency:
                    self.frame.setStyleSheet("background-color:rgba(255,255,255,0.5); border-top-left-radius:{0}px; border-top-right-radius:{0}px".format(border_radius))
                else:
                    self.frame.setStyleSheet("background: palette(window); border-top-left-radius:{0}px; border-top-right-radius:{0}px".format(border_radius))
                self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
                #
                self.mainBox.setContentsMargins(10,10,10,10)
                shadow_effect = QtWidgets.QGraphicsDropShadowEffect(
                        blurRadius=blur_radius,
                        offset=QtCore.QPointF(5, 5)
                    )
                self.setGraphicsEffect(shadow_effect)
                #
            else:
                self.abox = QtWidgets.QHBoxLayout()
                self.abox.setContentsMargins(0,0,0,0)
                self.abox.setDirection(QtWidgets.QBoxLayout.LeftToRight)
                self.abox.setSpacing(0)
                if with_transparency:
                    self.aaabox = QtWidgets.QHBoxLayout()
                    self.aaabox.setContentsMargins(0,0,0,0)
                    self.aaabox.setSpacing(0)
                    self.setLayout(self.aaabox)
                    self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
                    bwidget = QtWidgets.QWidget()
                    bwidget.setObjectName('bwidget')
                    bwidget.setStyleSheet('QWidget#bwidget{background-color: rgba(255,255,255,0.5)}')
                    self.aaabox.addWidget(bwidget)
                    bwidget.setLayout(self.abox)
                else:
                    self.setLayout(self.abox)
            #
            ## virtual desktop box
            self.virtbox = QtWidgets.QHBoxLayout()
            self.virtbox.setContentsMargins(0,0,0,0)
            self.virtbox.setSpacing(4)
            self.virtbox.desk = "v"
            self.abox.insertLayout(0, self.virtbox)
            #
            vbtn = QtWidgets.QPushButton()
            vbtn.setFlat(True)
            # vbtn.setAutoExclusive(True)
            vbtn.setCheckable(True)
            vbtn.setFixedSize(QtCore.QSize(int(dock_height*1.3), dock_height))
            if with_transparency:
                csaa = ("QPushButton::checked { border: none;")
                csab = ("background-color: {};".format("rgba(255,255,255,0.1)"))
                csac = ("border-radius: 9px; border-style: outset; padding: 5px;")
                csad = ("text-align: center; }")
                csae = ("QPushButton { text-align: center; padding: 5px; background-color:rgba(255,255,255,0.0)}")
                csa = csaa+csab+csac+csad+csae
                vbtn.setStyleSheet(csa)
            elif with_compositor:
                hpalette = self.palette().dark().color().name()
                csaa = ("QPushButton::checked { border: none;")
                csab = ("background-color: {};".format(hpalette))
                csac = ("}")
                csa = csaa+csab+csac
                vbtn.setStyleSheet(csa)
            if virtual_desktops:
                self.virtbox.addWidget(vbtn)
            else:
                self.abox.addSpacing(8)
                self.abox.insertSpacing(100, 8)
            vbtn.desk = 0
            vbtn.clicked.connect(self.on_vbtn_clicked)
            self.on_virt_desk(self.num_virtual_desktops)
            #
            ## program box
            self.prog_box = QtWidgets.QHBoxLayout()
            self.prog_box.setContentsMargins(4,0,4,0)
            self.prog_box.setSpacing(4)
            self.prog_box.desk = "p"
            self.abox.insertLayout(2, self.prog_box)
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
                    pbtn = QtWidgets.QPushButton()
                    pbtn.setFlat(True)
                    if with_compositor and with_transparency:
                        csae = ("QPushButton { text-align: center; padding: 5px; background-color:rgba(255,255,255,0.0)}")
                        pbtn.setStyleSheet(csae)
                    elif with_transparency:
                        csae = ("QPushButton { text-align: center; padding: 5px; background-color:rgba(255,255,255,0.0)}")
                        pbtn.setStyleSheet(csae)
                    picon = QtGui.QIcon.fromTheme(icon)
                    if picon.isNull():
                        image = QtGui.QImage(icon)
                        if image.isNull():
                            image = QtGui.QImage("icons/unknown.svg")
                        pixmap = QtGui.QPixmap(image)
                        picon = QtGui.QIcon(pixmap)
                    pbtn.setFixedSize(QtCore.QSize(button_size, button_size))
                    pbtn.setIcon(picon)
                    pbtn.setIconSize(pbtn.size())
                    pbtn.setToolTip(fname or pexec)
                    pbtn.setIcon(picon)
                    pbtn.pexec = pexec_temp
                    pbtn.pdesktop = ffile
                    pbtn.ppath = fpath
                    self.prog_box.addWidget(pbtn)
                    pbtn.clicked.connect(self.on_pbtn)
                    pbtn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
                    pbtn.customContextMenuRequested.connect(self.pbtnClicked)
            #
            ## application icons box
            self.ibox = QtWidgets.QHBoxLayout()
            self.ibox.setContentsMargins(0,0,0,0)
            self.ibox.setSpacing(4)
            if tasklist_position == 0:
                self.ibox.setAlignment(QtCore.Qt.AlignLeft)
                # #
                # pframe = QtWidgets.QFrame()
                # pframe.setFrameShape(QtWidgets.QFrame.VLine)
                # self.ibox.addWidget(pframe)
            elif tasklist_position == 1:
                self.ibox.setAlignment(QtCore.Qt.AlignCenter)
            elif tasklist_position == 2:
                self.ibox.setAlignment(QtCore.Qt.AlignRight)
                self.ibox.setDirection(QtWidgets.QBoxLayout.RightToLeft)
            # the first virtual desktop
            self.ibox.desk = 0
            # fake button
            self.fake_btn = QtWidgets.QPushButton()
            self.fake_btn.setAutoExclusive(True)
            self.fake_btn.setCheckable(True)
            self.fake_btn.setFixedSize(QtCore.QSize(1,1))
            self.fake_btn.setFlat(True)
            self.fake_btn.winid = 1
            self.fake_btn.desktop = 0
            self.fake_btn.setVisible(False)
            self.ibox.addWidget(self.fake_btn)
            self.abox.insertLayout(3, self.ibox)
            if dock_width == 0:
                self.abox.setStretchFactor(self.ibox,1)
        ################################
        # winid - desktop
        self.list_prog = []
        # desktop in which the program appared
        on_desktop = 0
        winid_list = self.root.get_full_property(self.display.intern_atom('_NET_CLIENT_LIST'), X.AnyPropertyType).value
        for winid in winid_list:
            window = self.display.create_resource_object('window', winid)
            #
            prop = window.get_full_property(self.display.intern_atom('_NET_WM_WINDOW_TYPE'), X.AnyPropertyType)
            #
            if prop:
                if self.display.intern_atom('_NET_WM_WINDOW_TYPE_DOCK') in prop.value.tolist():
                    continue
                elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_DESKTOP') in prop.value.tolist():
                    continue
                # elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_DIALOG') in prop.value.tolist():
                    # continue
                # elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_UTILITY') in prop.value.tolist():
                    # continue
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
                #
                if self.display.intern_atom('_NET_WM_WINDOW_TYPE_NORMAL') in prop.value.tolist():
                    ppp = self.getProp(self.display,window,'DESKTOP')
                    on_desktop = ppp[0]
                    # the exec name
                    win_name_t = window.get_wm_class()
                    if win_name_t is not None:
                        win_exec = str(win_name_t[0])
                    else:
                        win_exec == "Unknown"
                    #
                    self.list_prog.append([winid, on_desktop, win_exec])
        #
        # current window active - window id
        self.curr_win_active = None
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
        ########
        self.mythread = winThread(Display())
        self.mythread.sig.connect(self.threadslot)
        self.mythread.start()
        # 
        if label1_script:
            self.labelw1 = QtWidgets.QLabel()
            self.labelw1.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
            self.abox.addWidget(self.labelw1)
            if label1_use_richtext:
                self.labelw1.setTextFormat(QtCore.Qt.RichText)
                if with_transparency:
                    self.labelw1.setStyleSheet("background-color:rgba(255,255,255,0.0)")
            else:
                if label1_color:
                    if with_transparency:
                        self.labelw1.setStyleSheet("color: {}; background-color:rgba(255,255,255,0.0)".format(label1_color))
                    else:
                        self.labelw1.setStyleSheet("color: {}".format(label1_color))
                else:
                    if with_transparency:
                        self.labelw1.setStyleSheet("background-color:rgba(255,255,255,0.0)")
                tfont = QtGui.QFont()
                if label1_font:
                    tfont.setFamily(label1_font)
                tfont.setPointSize(label1_font_size)
                tfont.setWeight(label1_font_weight)
                tfont.setItalic(label1_font_italic)
                self.labelw1.setFont(tfont)
            # 
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
            self.abox.addWidget(self.labelw2)
            if label2_use_richtext:
                self.labelw2.setTextFormat(QtCore.Qt.RichText)
                if with_transparency:
                    self.labelw2.setStyleSheet("background-color:rgba(255,255,255,0.0)")
            else:
                if label2_color:
                    if with_transparency:
                        self.labelw2.setStyleSheet("color: {}; background-color:rgba(255,255,255,0.0)".format(label2_color))
                    else:
                        self.labelw2.setStyleSheet("color: {}".format(label2_color))
                else:
                    if with_transparency:
                        self.labelw2.setStyleSheet("background-color:rgba(255,255,255,0.0)")
                tfont = QtGui.QFont()
                if label2_font:
                    tfont.setFamily(label2_font)
                tfont.setPointSize(label2_font_size)
                tfont.setWeight(label2_font_weight)
                tfont.setItalic(label2_font_italic)
                self.labelw2.setFont(tfont)
            ###
            # self.l2p = QtCore.QProcess()
            # self.l2p.readyReadStandardOutput.connect(self.p2ready)
            # self.l2p.finished.connect(self.p2finished)
            # self.l2p.start("scripts/./label2.sh")
            #
            self.label2thread = label2Thread(["scripts/./label2.sh", label2_interval])
            self.label2thread.label2sig.connect(self.on_label2)
            self.label2thread.start()
        #
        #### tray section
        if use_tray:
            self.tframe = QtWidgets.QFrame()
            self.tframe.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
            # self.tframe.setStyleSheet("background: palette(window); border-top-left-radius:{0}px; border-top-right-radius:{0}px".format(border_radius))
            #
            self.frame_box = QtWidgets.QHBoxLayout()
            self.frame_box.setContentsMargins(0,0,0,0)
            self.frame_box.setSpacing(0)
            self.tframe.setLayout(self.frame_box)
            #
            self.abox.addWidget(self.tframe)
            # frame widget counter
            self.frame_counter = 0
            # widget background color
            bcolor = self.palette().color(QtGui.QPalette.Background).name()
            #
            self.tthread = trayThread(self.tframe.winId(), bcolor)
            self.tthread.sig.connect(self.tthreadslot)
            self.tthread.start()
        #
        if not fixed_position:
            QtCore.QTimer.singleShot(1500, self.on_leave_event)
        #
        if dock_width:
            self.on_move_win()
    
    
    def tthreadslot(self, aa):
        # if aa[0] == "a":
            # self.frame_counter += 1
            # #
            # lbl = QtWidgets.QLabel("")
            # lbl.setContentsMargins(0, 0, 0, 0)
            # lbl.setStyleSheet("background-color: palette(window)")
            # lbl.setMinimumSize(tbutton_size, tbutton_size)
            # self.frame_box.addWidget(lbl)
        # elif aa[0] == "b":
            # self.frame_counter -= 1
            # self.frame_counter = max(0, self.frame_counter)
            # if self.frame_box.count():
                # self.frame_box.takeAt(0).widget().deleteLater()
        if isinstance(aa[0], int):
            num_lbl = self.frame_box.count()
            if aa[0] > num_lbl:
                while aa[0] > num_lbl:
                    lbl = QtWidgets.QLabel("")
                    lbl.setContentsMargins(0, 0, 0, 0)
                    lbl.setStyleSheet("background-color: palette(window)")
                    lbl.setMinimumSize(tbutton_size, tbutton_size)
                    self.frame_box.addWidget(lbl)
                    num_lbl += 1
            elif aa[0] < num_lbl:
                while num_lbl > aa[0]:
                    if self.frame_box.count():
                        self.frame_box.takeAt(0).widget().deleteLater()
                        num_lbl -= 1
        #
        self.tframe.adjustSize()
        self.tframe.updateGeometry()
        self.tframe.resize(self.tframe.sizeHint())
        #
        self.adjustSize()
        self.updateGeometry()
        self.resize(self.sizeHint())
    
    
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
        time.sleep(1)
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
                self.virtual_desktops_changed(data[1])
            # current virtual desktop changed
            elif data[0] == "ACTIVE_VIRTUAL_DESKTOP":
                self.active_virtual_desktop_changed(data[1])
                self.active_virtual_desktop = data[1]
            # net list
            elif data[0] == "NETLIST":
                self.net_list()
    
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
        self.get_active_window()
            
    # a new window has apparead
    def on_new_window(self, window_list):
        for w in window_list:
            #
            if this_windowID not in self.wid_l:
                self.wid_l.append(this_windowID)
            if w not in self.wid_l:
                window = self.display.create_resource_object('window', w)
                ########### skip unmanaged windows
                prop = window.get_full_property(self.display.intern_atom('_NET_WM_WINDOW_TYPE'), X.AnyPropertyType)
                #
                if prop:
                    if self.display.intern_atom('_NET_WM_WINDOW_TYPE_DOCK') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_DESKTOP') in prop.value.tolist():
                        continue
                    # elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_DIALOG') in prop.value.tolist():
                        # continue
                    # elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_UTILITY') in prop.value.tolist():
                        # continue
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
                #
                ###########
                #
                try:
                    if not self.display.intern_atom("_NET_WM_STATE_SKIP_TASKBAR") in window.get_full_property(self.display.intern_atom("_NET_WM_STATE"), Xatom.ATOM).value:
                        ppp = self.getProp(self.display, window,'DESKTOP')
                        on_desktop = ppp[0]
                         # the exec name
                        win_name_t = window.get_wm_class()
                        if win_name_t is not None:
                            win_exec = str(win_name_t[0])
                        else:
                            win_exec == "Unknown"
                        #
                        self.on_dock_items([w, on_desktop, win_exec])
                except:
                    pass
        # 
        if dock_width:
            self.on_move_win()

    
    # a window has been destroyed
    def delete_window_destroyed(self, window_list):
        for w in self.wid_l:
            if w not in window_list:
                self.wid_l.remove(w)
                self.on_remove_win(w)
        # 
        if dock_width:
            self.on_move_win()

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
                if with_transparency:
                    csaa = ("QPushButton::checked { border: none;")
                    csab = ("background-color: {};".format("rgba(255,255,255,0.1)"))
                    csac = ("border-radius: 9px; border-style: outset; padding: 5px;")
                    csad = ("text-align: center; }")
                    csae = ("QPushButton { text-align: center; padding: 5px; background-color:rgba(255,255,255,0.0)}")
                    csa = csaa+csab+csac+csad+csae
                    vbtn.setStyleSheet(csa)
                elif with_compositor:
                    hpalette = self.palette().dark().color().name()
                    csaa = ("QPushButton::checked { border: none;")
                    csab = ("background-color: {};".format(hpalette))
                    csac = ("}")
                    csa = csaa+csab+csac
                    vbtn.setStyleSheet(csa)
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
    
    # 2
    # add a button
    def on_dock_items(self, pitem):
        if pitem[2] in SKIP_APP:
            return
        winid = pitem[0]
        self.wid_l.append(winid)
        window = self.display.create_resource_object('window', winid)
        win_name_class = window.get_wm_class()[0]
        if win_name_class and QtGui.QIcon.hasThemeIcon(win_name_class):
            licon = QtGui.QIcon.fromTheme(win_name_class)
        else:
            icon_icon = window.get_full_property(self.display.intern_atom('_NET_WM_ICON'), 0)
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
        #
        hpalette = self.palette().dark().color().name()
        csaa = ("QPushButton::checked { border: none;")
        csab = ("background-color: {};".format(hpalette))
        csac = ("border-radius: 9px; border-style: outset; padding: 5px;")
        csad = ("text-align: center; }")
        if with_compositor and with_transparency:
            csae = ("QPushButton { text-align: center; padding: 5px; background-color:rgba(255,255,255,0.0)}")
        elif with_transparency:
            csae = ("QPushButton { text-align: center; padding: 5px; background-color:rgba(255,255,255,0.0)}")
        else:
            csae = ("QPushButton { text-align: center; padding: 5px;}")
        csaf1 = ("QPushButton::hover:!pressed {")
        csaf2 = ("background-color: {};".format("#DF5E0B"))
        csaf3 = ("border-radius: 9px;"
        "border-style: outset;"
        "padding: 5px;"
        "text-align: center;"
        "padding: 5px;"
        "}")
        csaf = csaf1+csaf2+csaf3
        csa = csaa+csab+csac+csad+csae+csaf
        btn.setStyleSheet(csa)
        #
        btn.setAutoExclusive(True)
        btn.clicked.connect(self.on_btn_clicked)
        # btn.setFixedSize(QtCore.QSize(dock_height, dock_height))
        btn.setFixedSize(QtCore.QSize(button_size, button_size))
        btn.setIcon(licon)
        # btn.setIconSize(QtCore.QSize(dock_height-8, dock_height-8))
        btn.setIconSize(QtCore.QSize(button_size-button_padding, button_size-button_padding))
        btn.setMinimumSize(QtCore.QSize(button_size, button_size))
        btn.winid = pitem[0]
        btn.desktop = pitem[1]
        btn.pexec = pitem[2]
        btn.installEventFilter(self)
        if pitem[1] == 0:
            self.ibox.addWidget(btn)
        else:
            self.ibox.insertWidget(pitem[1] * 100, btn)
        btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        btn.customContextMenuRequested.connect(self.btnClicked)
    
    # 3
    # get the active window when the program starts
    def get_active_window_first(self):
        window_id_temp = self.root.get_full_property(self.display.intern_atom('_NET_ACTIVE_WINDOW'), X.AnyPropertyType)
        if window_id_temp:
            window_id = window_id_temp.value[0]
            for i in range(self.ibox.count()):
                item = self.ibox.itemAt(i).widget()
                if not item:
                    continue
                if isinstance(item, QtWidgets.QPushButton):
                    if item.winid == window_id:
                        item.setChecked(True)
                        break
    
    # 4
    def on_btn_clicked(self):
        btn = self.sender()
        # same virtual desktop
        if btn.desktop == self.active_virtual_desktop:
            window = self.display.create_resource_object('window', btn.winid)
            active_window_id = self.root.get_full_property(self.display.intern_atom('_NET_ACTIVE_WINDOW'), X.AnyPropertyType).value[0]
            ## its the actual active window
            if btn.winid == active_window_id:
                # minimize
                if alternate_wm:
                    prog = "xdotool windowminimize {}".format(hex(btn.winid))
                    subprocess.run([prog], shell=True)
                    self.get_active_window()
                    return
                window = self.display.create_resource_object('window', btn.winid)
                ewmh.setWmState(window, 1, '_NET_WM_STATE_HIDDEN')
                ewmh.display.flush()
                ewmh.display.sync()
                self.get_active_window()
            # raise and or bring to top
            else:
                if alternate_wm:
                    prog = "xdotool windowactivate {}".format(hex(btn.winid))
                    subprocess.run([prog], shell=True)
                    self.get_active_window()
                    return
                window = self.display.create_resource_object('window', btn.winid)
                ewmh.setActiveWindow(window)
                ewmh.display.flush()
                # needed
                ewmh.display.sync()
                self.get_active_window()
            return
        # different virtual desktop
        else:
            if alternate_wm:
                ewmh.setCurrentDesktop(btn.desktop)
                ewmh.display.flush()
                # needed
                ewmh.display.sync()
                prog = "xdotool windowactivate {}".format(hex(btn.winid))
                subprocess.run([prog], shell=True)
                self.get_active_window()
                return
            # change the virtual desktop
            ewmh.setCurrentDesktop(btn.desktop)
            ewmh.display.flush()
            # needed
            ewmh.display.sync()
            self.get_active_window()
    
    # 5    
    # get the active window
    def get_active_window(self):
        window_id_temp = self.root.get_full_property(self.display.intern_atom('_NET_ACTIVE_WINDOW'), X.AnyPropertyType)
        if window_id_temp:
            window_id = window_id_temp.value[0]
            # no active window
            if window_id == 0:
                self.fake_btn.setChecked(True)
            #
            else:
                window = self.display.create_resource_object('window', window_id)
                is_found = 0
                for i in range(self.ibox.count()):
                    btn = self.ibox.itemAt(i).widget()
                    if isinstance(btn, QtWidgets.QPushButton):
                        if btn.winid == window_id:
                            btn.setChecked(True)
                            is_found = 1
                            break
                if not is_found:
                    # in case no window has been activated
                    self.fake_btn.setChecked(True)
        
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
        app_dirs = ["/usr/share/applications", "/usr/local/share/applications", os.path.expanduser("~")+"/.local/share/applications"]
        # full desktop file path - exec - name - icon
        app_found = []
        # args to remove from the exec entry
        execArgs = [" %f", " %F", " %u", " %U", " %d", " %D", " %n", " %N", " %k", " %v"]
        for ddir in app_dirs:
            if os.path.exists(ddir):
                ffiles = os.listdir(ddir)
                for ffile in ffiles:
                    if ffile.split(".")[1] != "desktop":
                        continue
                    #
                    try:
                        entry = DesktopEntry.DesktopEntry(os.path.join(ddir, ffile))
                        pgexec_temp = ""
                        try:
                            pgexec_temp = entry.getTryExec()
                        except Exception as E:
                            pass
                        # if pgexec_temp:
                            # pgexec_temp = os.path.basename(pgexec_temp)
                        # else:
                        try:
                            pgexeca = entry.getExec()
                            if pgexeca:
                                for aargs in execArgs:
                                    if aargs in pgexeca:
                                        pgexeca = pgexeca.strip(aargs)
                                pgexec = pgexeca.split()[0]
                        except:
                            pass
                        # 
                        if pgexec_temp or pgexec:
                            # if pgexec == pexec:
                            if os.path.basename(pgexec_temp) == pexec or os.path.basename(pgexec) == pexec:
                                fname = entry.getName()
                                ficon = entry.getIcon()
                                fpath = entry.getPath()
                                # desktop file - exec - name - icon - program path
                                app_found.append([os.path.join(ddir, ffile), pgexeca, fname, ficon or "unknown", fpath or ""])
                    except Exception as E:
                        dlg = showDialog(1, str(E), self)
                        result = dlg.exec_()
                        dlg.close()
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
            picon = QtGui.QIcon.fromTheme(icon, QtGui.QIcon("icons/unknown.svg"))
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
                picon = QtGui.QIcon.fromTheme(icon, QtGui.QIcon("icons/unknown.svg"))
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
            dlg = showDialog(1, "No file desktop found.", self)
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
        self.btnMenu.exec_(self.sender().mapToGlobal(QPos)) 
        
    def on_close_prog(self, btn):
        window = self.display.create_resource_object('window', btn.winid)
        winPid = self.getProp(self.display, window, 'PID')[0]
        # 9 signal.SIGKILL - 15 signal.SIGTERM
        os.kill(winPid, 15)
        self.right_button_pressed = 0
    
    
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
        ewmh.setCurrentDesktop(vdesk)
        ewmh.display.flush()
    
    # move the window when a button is added or removed
    def on_move_win(self):
        self.adjustSize()
        self.updateGeometry()
        self.resize(self.sizeHint())
        #
        if self.position in [0, 1]:
            pass
        elif self.position in [2,3]:
            if dock_width:
                sx = int((self.screen_size.width() - self.size().width())/2)
            else:
                sx = int((self.screen_size.width() - WINW)/2)
            if sec_position == 2:
                sy = 0
            elif sec_position == 3:
                sy = self.screen_size.height() - WINH
            # 
            if with_compositor:
                self.move(sx, sy - 10)
            else:
                self.move(sx, sy)

    
    def enterEvent(self, event):
        if not fixed_position:
            if self.on_leave:
                self.on_leave.stop()
                self.on_leave.deleteLater()
                self.on_leave = None
            #
            ewmh.setWmState(this_window, 0, '_NET_WM_STATE_BELOW')
            ewmh.setWmState(this_window, 1, '_NET_WM_STATE_ABOVE')
            ewmh.display.flush()
            ewmh.display.sync()
        return super(SecondaryWin, self).enterEvent(event)

    def leaveEvent(self, event):
        if not fixed_position:
            self.on_leave = QtCore.QTimer()
            self.on_leave.timeout.connect(self.on_leave_event)
            self.on_leave.start(2000)
        return super(SecondaryWin, self).enterEvent(event)
    
    def on_leave_event(self):
        ewmh.setWmState(this_window, 0, '_NET_WM_STATE_ABOVE')
        ewmh.setWmState(this_window, 1, '_NET_WM_STATE_BELOW')
        ewmh.display.flush()
        ewmh.display.sync()
        self.on_leave = None
    
############## TRAY

class trayThread(QtCore.QThread):
    sig = QtCore.pyqtSignal(list)
    
    def __init__(self, frame_id, bcolor, parent=None):
        super(trayThread, self).__init__(parent)
        self.frame_id = frame_id
        self.bcolor = bcolor
        
    def run(self):
        while 1:
            try:
                self.PyPanel(int(self.frame_id), self, self.bcolor)
            except Exception as E:
                print("Some problems with the systray:", str(E))
    
    ####
    class Obj(object):
        """ Multi-purpose class """
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)


    class PyPanel(object):
        
        def __init__(self, parent_id, par, bcolor):
            """ Initialize and display the panel """
            self.display = Display()                 # Display obj
            self.screen  = self.display.screen()     # Screen obj
            self.root    = self.screen.root          # Display root
            self.parent_id = parent_id               # 
            self.error   = error.CatchError()        # Error Handler/Suppressor
            self.panel   = {"sections":[]}           # Panel data and layout
            self.par = par
            self.bcolor = bcolor                     # tray icon background color
            #
            global P_HEIGHT
            #
            # tray icon background color
            colormap = self.screen.default_colormap
            self.background = colormap.alloc_named_color(self.bcolor).pixel
            #
            self.panel["sections"].append(TRAY)
            self.panel[TRAY] = self.par.Obj(id="tray", tasks={}, order=[])
            self.createTray(self.display, self.screen)
            
        """ Create the System Tray Selection Owner Window """
        def createTray(self, dsp, scr):
            self._OPCODE = dsp.intern_atom("_NET_SYSTEM_TRAY_OPCODE")
            manager      = dsp.intern_atom("MANAGER")
            selection    = dsp.intern_atom("_NET_SYSTEM_TRAY_S%d" % dsp.get_default_screen())
            ## Selection owner window
            # self.selowin = scr.root.create_window(-1, -1, 50, 50, 0, self.screen.root_depth)
            self.selowin = scr.root.create_window(0, 0, tbutton_size, tbutton_size, 0, self.screen.root_depth)
            self.selowin.set_selection_owner(selection, X.CurrentTime)
            self.sendEvent(self.root, manager,[X.CurrentTime, selection, self.selowin.id], (X.StructureNotifyMask))
            #
            self.loop(self.display, self.root, self.selowin, self.panel)
            
        """ Send a ClientMessage event to the root """
        def sendEvent(self, win, ctype, data, mask=None):
            data = (data+[0]*(5-len(data)))[:5]
            ev = pe.ClientMessage(window=win, client_type=ctype, data=(32,(data)))
            #
            if not mask:
                mask = (X.SubstructureRedirectMask|X.SubstructureNotifyMask)
            self.root.send_event(ev, event_mask=mask)
        
        
        """ Redraw the panel """
        def updatePanel(self, root, win, panel):
            curr_x   = 0
            tray     = None
            #
            # curr_x += 2
            curr_x += 0
            tray = panel[TRAY]
            #
            if tray:
                tti = 0
                for tid in tray.order:
                    t = tid
                    tx = curr_x
                    twidth = tbutton_size
                    theight = tbutton_size
                    ty = int((P_HEIGHT-theight)/2)
                    tobj = self.display.create_resource_object("window", t)
                    tobj.configure(onerror=self.error, x=tx, y=ty, width=twidth, height=theight)
                    # tray icon background color
                    tobj.change_attributes(background_pixel = self.background)
                    #
                    tobj.map(onerror=self.error)
                    curr_x += twidth
                    tti += 1
                #
                self.par.sig.emit([tti])

        """ Event loop - handle events as they occur until we're killed """ 
        def loop(self, dsp, root, win, panel):
            tray = panel[TRAY]
            while 1:
                e = dsp.next_event()
                if e.type == X.ConfigureNotify and TRAY:
                    if e.window.id in tray.tasks:
                        task = tray.tasks[e.window.id]
                        task.obj.configure(onerror=self.error, width=task.width, height=task.height)                                            
                elif e.type == X.ClientMessage and TRAY:
                    if e.window == self.selowin:
                        data = e.data[1][1] # opcode
                        task = e.data[1][2] # taskid
                        if e.client_type == self._OPCODE and data == 0:
                            obj = dsp.create_resource_object("window", task)
                            obj.reparent(int(self.parent_id), 0, 0)
                            obj.change_attributes(event_mask=(X.ExposureMask|X.StructureNotifyMask))
                            # tray icon background color
                            obj.change_attributes(background_pixel = self.background)
                            #
                            tray.tasks[task] = self.par.Obj(obj=obj, x=0, y=0, width=TRAY_I_WIDTH, height=TRAY_I_HEIGHT)
                            tray.order.append(task)
                            # added
                            self.par.sig.emit(["a"])
                            #
                            self.updatePanel(root, win, panel)
                ## an applet is been removed from the systray
                elif e.type == X.DestroyNotify:
                    # delete the object from the list if it is a member
                    if e.window.id in tray.order:
                        tray.order.remove(e.window.id)
                        # removed
                        self.par.sig.emit(["b"])
                        #
                        # update
                        self.updatePanel(root, win, panel)
                #

############## 

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
        message = QtWidgets.QLabel(lcontent)
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
        
        self.adjustSize()
        self.updateGeometry()
        self.resize(self.sizeHint())
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        
################
if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    ########### sec_window
    sec_position = 3
    sec_window = SecondaryWin(sec_position)
    sec_window.setWindowFlags(sec_window.windowFlags() | QtCore.Qt.WindowDoesNotAcceptFocus)
    sec_window.setAttribute(QtCore.Qt.WA_AlwaysShowToolTips, True)
    sec_window.setAttribute(QtCore.Qt.WA_X11NetWmWindowTypeDock)
    screen = app.primaryScreen()
    size = screen.size()
    if dock_width:
        WINW = dock_width
    else:
        WINW = size.width()
    WINH = dock_height
    this_windowID = int(sec_window.winId())
    _display = Display()
    this_window = _display.create_resource_object('window', this_windowID)
    L = 0
    R = 0
    T = 0
    B = 0
    if sec_position == 2:
        if not fixed_position:
            T = reserved_space
        else:
            T = WINH
    elif sec_position == 3:
        if not fixed_position:
            B = reserved_space
        else:
            if with_compositor:
                B = WINH + 10
            else:
                B = WINH
    # 
    this_window.change_property(_display.intern_atom('_NET_WM_STRUT'),
                                _display.intern_atom('CARDINAL'),
                                32, [L, R, T, B])
    x = 0
    y = x+WINW-1
    this_window.change_property(_display.intern_atom('_NET_WM_STRUT_PARTIAL'),
                           _display.intern_atom('CARDINAL'), 32,
                           [L, R, T, B, 0, 0, 0, 0, x, y, T, B],
                           X.PropModeReplace)
    _display.sync()
    #
    sec_window.show()
    #############
    # move and center the window
    if sec_position in [0, 1]:
        pass
    elif sec_position in [2,3]:
        sx = int((size.width() - WINW)/2)
        if sec_position == 2:
            sy = 0
        elif sec_position == 3:
            if with_compositor:
                sy = size.height() - WINH - 10
            else:
                sy = size.height() - WINH
        # 
        sec_window.move(sx, sy)
        sec_window.resize(WINW, WINH)
        sec_window.setMaximumWidth(size.width())
    ############
    # set new style globally
    if theme_style:
        s = QtWidgets.QStyleFactory.create(theme_style)
        app.setStyle(s)
    # set the icon style globally
    if icon_theme:
        QtGui.QIcon.setThemeName(icon_theme)
    ################
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
