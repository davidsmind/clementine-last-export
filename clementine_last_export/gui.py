#!/usr/bin/env python
#-*- coding: utf-8 -*-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""Module containing the GUI of the clementine_last_export tool"""

from PyQt5 import QtCore, QtGui, QtWidgets

import sys, os
import platform
import pickle

from optparse import OptionParser
import logging
from logging import info, warning, error, debug
from update_playcount import Update_playcount
from import_loved_tracks import Import_loved_tracks

SERVER_LIST = ["last.fm", "libre.fm"]

# Import icons resource to have the icon image
import icons_rc

class Ui_MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        """Init function of the class, called at each creation"""
        super(Ui_MainWindow, self).__init__()
        
                
        self.cache_path = self.get_cachepath()
        self.configfile = os.path.expanduser("%sconfig.pkl" %self.cache_path)
        if os.path.exists(self.configfile):
            self.load_config()
        else:
            self.config = {}
            self.config["username"] = ""
            self.config["server"] = "last.fm"
            self.config["backup_database"] = True
            self.config["force_update"] = False
            self.config["use_cache"] = True
            self.config["target"] = Update_playcount
        #self.setupUi()
                
        
    def setupUi(self, MainWindow):
        """Initialisation of the UI, called during the creation of an instance of the 
        class, to create the main window and its elements
        """   
        #MenuBar
        ##Exit menu
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(402, 359)
        
        #FIXME LOAD Window ICON not working
        self.setWindowIcon(QtGui.QIcon(':/myresources/clementine_last_export.png'))
        
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        
        self.progressbar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressbar.setProperty("value", 24)
        self.progressbar.setObjectName("progressbar")
        self.gridLayout.addWidget(self.progressbar, 17, 0, 1, 1)
        
              
        ####Run button
        self.update_button = QtWidgets.QPushButton(self.centralwidget)
        self.update_button.setFocusPolicy(QtCore.Qt.WheelFocus)
        self.update_button.setObjectName("update_button")
        self.update_button.setToolTip('Run the script')
        self.update_button.clicked.connect(self.run_script)
        ##Run button can be triggered by pressing the return key
        self.update_button.setShortcut(self.update_button.tr("Return"))    
        self.gridLayout.addWidget(self.update_button, 17, 4, 1, 1)
        
        ###Part target
        # Definition of the two radio buttons
        self.playcount_radio_button = QtWidgets.QRadioButton('Import playcount', self.centralwidget)
        #self.playcount_radio_button.setObjectName("playcount_radio_button")
        self.gridLayout.addWidget(self.playcount_radio_button, 3, 0, 1, 1)
        self.lovedtracks_radio_button = QtWidgets.QRadioButton('Import loved tracks', self.centralwidget)
        #self.lovedtracks_radio_button.setObjectName("lovedtracks_radio_button")
        self.gridLayout.addWidget(self.lovedtracks_radio_button, 2, 0, 1, 1)

        #Creation of the group of radio buttons
        self.radio_group = QtWidgets.QButtonGroup(self.centralwidget)
        self.radio_group.addButton(self.playcount_radio_button)
        self.radio_group.addButton(self.lovedtracks_radio_button)
        #Only one radio button can be selected at once
        self.radio_group.setExclusive(True)
        self.radio_group.buttonClicked.connect(self.targetChanged)

        self.use_cache_checkbox = QtWidgets.QCheckBox(self.centralwidget)
        self.use_cache_checkbox.setObjectName("use_cache_checkbox")
        self.use_cache_checkbox.stateChanged.connect(self.useCacheChanged)
        self.use_cache_checkbox.setToolTip('Check this box if you want to use the cache file from a previous import')        
        self.gridLayout.addWidget(self.use_cache_checkbox, 10, 0, 1, 1)
        
        ##Checkbox to activate or not the backup of the database
        self.backup_checkbox = QtWidgets.QCheckBox(self.centralwidget)
        self.backup_checkbox.setObjectName("backup_checkbox")
        self.backup_checkbox.stateChanged.connect(self.backupChanged)
        self.gridLayout.addWidget(self.backup_checkbox, 8, 0, 1, 1)
        
        self.frame = QtWidgets.QFrame(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QtCore.QSize(300, 100))
        self.frame.setMaximumSize(QtCore.QSize(300, 100))
        self.frame.setFrameShape(QtWidgets.QFrame.Box)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.serverDetailsLabelRO = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.serverDetailsLabelRO.sizePolicy().hasHeightForWidth())
        
        self.serverDetailsLabelRO.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.serverDetailsLabelRO.setFont(font)
        self.serverDetailsLabelRO.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.serverDetailsLabelRO.setObjectName("serverDetailsLabelRO")
        self.gridLayout_2.addWidget(self.serverDetailsLabelRO, 0, 0, 1, 1, QtCore.Qt.AlignLeft)
        self.username_LabelRO = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.username_LabelRO.sizePolicy().hasHeightForWidth())
        self.username_LabelRO.setSizePolicy(sizePolicy)
        self.username_LabelRO.setMinimumSize(QtCore.QSize(100, 10))
        self.username_LabelRO.setObjectName("username_LabelRO")
        self.gridLayout_2.addWidget(self.username_LabelRO, 1, 0, 1, 1)
        self.field_username = QtWidgets.QLineEdit(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.field_username.sizePolicy().hasHeightForWidth())
        self.field_username.setSizePolicy(sizePolicy)
        self.field_username.setMinimumSize(QtCore.QSize(100, 20))
        self.field_username.setObjectName("field_username")
        self.field_username.textChanged[str].connect(self.usernameChanged)
        self.gridLayout_2.addWidget(self.field_username, 1, 1, 1, 1)
        self.selectServerLabelRO = QtWidgets.QLabel(self.frame)
        self.selectServerLabelRO.setObjectName("selectServerLabelRO")
        self.gridLayout_2.addWidget(self.selectServerLabelRO, 2, 0, 1, 1)
        
        self.server_combo = QtWidgets.QComboBox(self.frame)
        self.server_combo.setMinimumSize(QtCore.QSize(0, 20))
        self.server_combo.setObjectName("server_combo")
        for server in SERVER_LIST:
            self.server_combo.addItem(server)
        self.server_combo.activated[str].connect(self.serverChanged)
        
        
        self.gridLayout_2.addWidget(self.server_combo, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.frame, 1, 0, 1, 2)
        
        self.force_update_checkbox = QtWidgets.QCheckBox(self.centralwidget)
        self.force_update_checkbox.setObjectName("force_update_checkbox")
        self.force_update_checkbox.stateChanged.connect(self.forceUpdateChanged)
        self.force_update_checkbox.setToolTip('Check this box if you want to force the update\n - of loved tracks already rated at 4.5 stars\n - of playcounts higher locally than the one on the music server')
        self.gridLayout.addWidget(self.force_update_checkbox, 9, 0, 1, 1)
        
        self.optionsLabelRO = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        
        self.optionsLabelRO.setFont(font)
        self.optionsLabelRO.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.optionsLabelRO.setObjectName("optionsLabelRO")
        self.gridLayout.addWidget(self.optionsLabelRO, 4, 0, 1, 2, QtCore.Qt.AlignLeft|QtCore.Qt.AlignBottom)
        
        self.statusLabel = QtWidgets.QLabel(self.centralwidget)
        self.statusLabel.setMaximumSize(QtCore.QSize(16777215, 10))
        self.statusLabel.setObjectName("statusLabel")
        self.gridLayout.addWidget(self.statusLabel, 18, 4, 1, 1)
        
        ###Menubar getting all the previously defined menus
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 402, 26))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuImport = QtWidgets.QMenu(self.menubar)
        self.menuImport.setObjectName("menuImport")
        self.menuAbout = QtWidgets.QMenu(self.menubar)
        self.menuAbout.setObjectName("menuAbout")
        MainWindow.setMenuBar(self.menubar)
        
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionExit.setShortcut('Ctrl+Q')
        self.actionExit.setStatusTip('Exit application')
        self.actionExit.triggered.connect(QtWidgets.QApplication.quit)
        
        ###About menu
        self.actionAbout_Clementine_Last_Export = QtWidgets.QAction(MainWindow)
        self.actionAbout_Clementine_Last_Export.setObjectName("actionAbout_Clementine_Last_Export")
        self.actionAbout_QT = QtWidgets.QAction(MainWindow)
        self.actionAbout_QT.setObjectName("actionAbout_QT")
        self.actionAbout_QT.triggered.connect(self.open_aboutQt)
        self.actionAbout_Clementine_Last_Export.triggered.connect(self.open_about)
        
        ###Import menu
        self.importAction = QtWidgets.QAction(MainWindow)
        self.importAction.setObjectName("importAction")
        self.importAction.setStatusTip('Run Import')
        self.importAction.triggered.connect(self.run_script)
        self.menuFile.addAction(self.actionExit)
        self.menuImport.addAction(self.importAction)
        self.menuAbout.addAction(self.actionAbout_Clementine_Last_Export)
        self.menuAbout.addAction(self.actionAbout_QT)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuImport.menuAction())
        self.menubar.addAction(self.menuAbout.menuAction())

        self.progressbar.reset()
        
        ##Status bar 
        self.statusBar().showMessage('Ready') 
        
        self.restore_config()
        
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
       
       
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Clementine Last Export"))
        self.update_button.setText(_translate("MainWindow", "Run"))
        self.lovedtracks_radio_button.setText(_translate("MainWindow", "Import loved"))
        self.playcount_radio_button.setText(_translate("MainWindow", "Import playcount"))
        self.use_cache_checkbox.setText(_translate("MainWindow", "Use Cache File (If Available)"))
        self.backup_checkbox.setText(_translate("MainWindow", "Backup Database"))
        self.serverDetailsLabelRO.setText(_translate("MainWindow", "Server Details"))
        self.username_LabelRO.setText(_translate("MainWindow", "Username"))
        self.field_username.setText(_translate("MainWindow", self.config["username"]))
        self.selectServerLabelRO.setText(_translate("MainWindow", "Select The Server"))
        self.force_update_checkbox.setText(_translate("MainWindow", "Force Update"))
        self.optionsLabelRO.setText(_translate("MainWindow", "Options"))
        self.statusLabel.setText(_translate("MainWindow", "Ready"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuImport.setTitle(_translate("MainWindow", "Import"))
        self.menuAbout.setTitle(_translate("MainWindow", "About"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionAbout_Clementine_Last_Export.setText(_translate("MainWindow", "About Clementine Last Export"))
        self.actionAbout_QT.setText(_translate("MainWindow", "About QT"))
        self.importAction.setText(_translate("MainWindow", "Run"))
        
        
    def restore_config(self):
        """Function called to update the UI according to the configuration dictionary
        """
        self.server_combo.setCurrentIndex(SERVER_LIST.index(self.config["server"]))
        self.field_username.setText(self.config["username"])
        if self.config["target"] == Update_playcount:
            self.playcount_radio_button.toggle()
        else:
            self.lovedtracks_radio_button.toggle()
        if self.config["backup_database"]:
            self.backup_checkbox.toggle()
        if self.config["use_cache"]:        
            self.use_cache_checkbox.toggle()
        if self.config["force_update"]:
            self.force_update_checkbox.toggle()
            
        
    def center(self):
        """Function called to center the main window to the display screen"""         
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
        
    def run_script(self):
        """Function called when pressing the "Run" button on the UI"""
        if self.config["username"] == '':
            self.statusLabel.setText('Username needed')
        else: 
            cache_file = os.path.expanduser("%scache_%s.txt" %(self.cache_path, self.config["target"].__name__))
            self.statusLabel.setText('Running')          
            debug("Running the process %s with the info: server = %s, username = %s, backup = %s, force update = %s, use cache = %s\n"
                    %(self.config["target"], self.config["server"], self.config["username"], self.config["backup_database"], self.config["force_update"], self.config["use_cache"]))
            
            thread1 = self.config["target"](self.config["username"], False, self.config["server"],
                cache_file, 1, self.config["backup_database"], self.config["force_update"], self.config["use_cache"])
            
            #Connect the partDone signal of the thread to the progress bar    
            thread1.partDone.connect(self.updatePBar)
            #Run the thread
            thread1.run()
            
    
    def updatePBar(self, val):
        """Function called when the thread progress
        
        :param val: Value of the thread progress
        :type val: float
        """
        self.progressbar.setValue(val)   
        
    def usernameChanged(self, text):
        """Function called when the username text field is changed
        
        :param text: Text written in the text field by the user, representing his username
        :type text: string
        """
        self.config["username"] = text
        self.store_config()
        
    def serverChanged(self, text):
        """Function called when the server combobox is changed
        
        :param text: Value of the selected element in the combobox
        :type text: string
        """
        self.config["server"] = text
        self.store_config()
                
    def backupChanged(self, state):
        """Function called when the "backup database" checkbox changes its state
        
        :param state: State of the "backup database" checkbox, True if the database shall be backed up
        :type state: boolean
        """
        if state == QtCore.Qt.Checked:
            self.config["backup_database"] = True
        else:
            self.config["backup_database"] = False
        self.store_config()        
        
    def forceUpdateChanged(self, state):
        """Function called when the "force update" checkbox changes its state
        
        :param state: State of the "force update" checkbox, True if the update is forced
        :type state: boolean
        """
        if state == QtCore.Qt.Checked:
            self.config["force_update"] = True
        else:
            self.config["force_update"] = False
        self.store_config()        
        
    def useCacheChanged(self, state):
        """Function called when the "use cache" checkbox changes its state
        
        :param state: State of the "use cahce" checkbox, True if the cache shall be used
        :type state: boolean
        """
        if state == QtCore.Qt.Checked:
            self.config["use_cache"] = True
        else:
            self.config["use_cache"] = False
        self.store_config()    
    
    def targetChanged(self, button):
        """Function called when clicked on one of the radiobuttons to select which information shall be imported
        
        :param button: Radiobutton clicked (as they are exclusive, it means that the other one is no longer clicked)
        :type button: QtGui.QRadioButton
        """
        if button.text() == 'Import playcount':
            self.config["target"] = Update_playcount
        else:
            self.config["target"] = Import_loved_tracks
        self.store_config()
        
    def import_completed(self, msg):
        """Function called when the thread is finished (normally or not)
        
        :param message: Message sent from the thread
        :type message: string
        """
        QtWidgets.QMessageBox.information(self, u"Operation finished", msg)        
        self.statusLabel.setText('Import completed')
        
    def open_about(self):
        """Function called when the about dialog is requested"""
        about_text="""<b>Clementine Last Export</b>
        <br/><br/>
        Developed by David Adrian Mattatall<br/><br/>
        <a href="https://github.com/davidsmind/clementine-last-export/">https://github.com/davidsmind/clementine-last-export/</a>"""
        QtWidgets.QMessageBox.about(self,"About Clementine Last Export", about_text)
        
    def open_aboutQt(self):
        """Function called when the aboutQt dialog is requested"""
        QtWidgets.QMessageBox.aboutQt(self)
        
    def get_cachepath(self):
        """Function called to create the cache repository next to the Clementine data
        
        :return: Path to the cache directory in which the file will be stored
        :rtype: string
        """
        operating_system = platform.system()
        if operating_system == 'Linux':
            cache_path = '~/.clementine_last_export/'
        if operating_system == 'Darwin':
            cache_path = '~/Library/Application Support/clementine_last_export/'
        if operating_system == 'Windows':
            cache_path = '%USERPROFILE%\\.clementine_last_export\\'''
        
        if not os.path.exists(os.path.expanduser(cache_path)):
            os.makedirs(os.path.expanduser(cache_path))
            
        return cache_path

    def store_config(self):
        """Function called to stored the configuration of the UI for the next use in a 
        configuration file"""
        pickle.dump(self.config, open(self.configfile, 'w'))
        
    def load_config(self):
        """Function called to load the configuration of the UI from a configuration file
        """
        self.config = pickle.load(open(self.configfile))
       
def main():
    """Main method of the script, called when the script is run"""
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_()) 

if __name__ == "__main__":

    parser = OptionParser()
    parser.usage = """Usage: %prog [options]
    
    Run the GUI which will use the scripts of the package
    """
    parser.add_option("-d", "--debug", dest="debug", default=False, action="store_true", help="debug mode")
    parser.add_option("-v", "--verbose", dest="verbose", default=False, action="store_true", help="activate verbose mode")
    
    options, args = parser.parse_args()
    if options.verbose:
        logging.basicConfig(level="INFO")
    if options.debug:
        logging.basicConfig(level="DEBUG")
        
    main()
