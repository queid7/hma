import sys
from PyQt5 import QtCore, QtGui, QtWidgets

import motion_player as mp


class HmaUi(object):
    DEFAULT_WIDTH = 1600
    DEFAULT_HEIGHT = 1200
    """
    this class makes ui for main window and connect ui signals to event handlers of main window
    custom event handlers in main window must be implemented
    """
    def setupUi(self, MainWindow: QtWidgets.QMainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(HmaUi.DEFAULT_WIDTH, HmaUi.DEFAULT_HEIGHT)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # centralwidget
        MainWindow.setCentralWidget(self.centralwidget)
        self.central_layout = QtWidgets.QHBoxLayout()
        self.centralwidget.setLayout(self.central_layout)

        # motion_player
        self.motion_player = mp.MotionPlayer()
#        self.motion_player.setGeometry(QtCore.QRect(0, 0, 960, 720))
        print(self.motion_player.size())
        print(self.motion_player.sizeHint())
        print(self.motion_player.minimumSizeHint())
        self.motion_player.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        self.motion_player.setMouseTracking(False)
        self.motion_player.setObjectName("motion_player")
        self.central_layout.addWidget(self.motion_player)

        # menubar
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1280, 47))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuAnalysis = QtWidgets.QMenu(self.menubar)
        self.menuAnalysis.setObjectName("menuAnalysis")
        MainWindow.setMenuBar(self.menubar)
        self.actionNew = QtWidgets.QAction(MainWindow)
        self.actionNew.setObjectName("actionNew")
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionImport = QtWidgets.QAction(MainWindow)
        self.actionImport.setObjectName("actionImport")
        self.actionExport = QtWidgets.QAction(MainWindow)
        self.actionExport.setObjectName("actionExport")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionImport)
        self.menuFile.addAction(self.actionExport)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())

        # status bar
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        # tool bar
        self.toolbar = QtWidgets.QToolBar(MainWindow)
        self.toolbar.setObjectName("toolbar")
        MainWindow.addToolBar(self.toolbar)
        self.toolBtn0 = QtWidgets.QAction("toolBtn0", MainWindow)
        self.toolBtn1 = QtWidgets.QAction("toolBtn1", MainWindow)
        self.toolBtn2 = QtWidgets.QAction("toolBtn2", MainWindow)
        self.toolbar.addAction(self.toolBtn0)
        self.toolbar.addAction(self.toolBtn1)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.toolBtn2)
        #MainWindow.addToolBar("toolbar")
        self.toolbar2 = QtWidgets.QToolBar(MainWindow)
        self.toolbar.setObjectName("toolbar2")
        MainWindow.addToolBar(self.toolbar2)
        self.toolbar2.addAction(self.toolBtn2)

        # dock widgets
        self.dock0 = QtWidgets.QDockWidget("dock0", MainWindow)
        self.dock0.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.dock1 = QtWidgets.QDockWidget("dock1", MainWindow)
        self.dock1.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        MainWindow.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dock0)
        MainWindow.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock1)
        self.toolbar3 = QtWidgets.QToolBar("toolbar3", MainWindow)
        MainWindow.addToolBar(self.toolbar3)
        self.toolbar3.addAction(self.dock0.toggleViewAction())
        self.toolbar3.addAction(self.dock1.toggleViewAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.connectUi(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionNew.setText(_translate("MainWindow", "New"))
        self.actionOpen.setText(_translate("MainWindow", "Open"))
        self.actionImport.setText(_translate("MainWindow", "Import"))
        self.actionExport.setText(_translate("MainWindow", "Export"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))

    def connectUi(self, MainWindow):
        self.actionNew.triggered.connect(MainWindow.action_new_event)
        self.actionOpen.triggered.connect(MainWindow.action_open_event)
        self.actionImport.triggered.connect(MainWindow.action_import_event)
        self.actionExport.triggered.connect(MainWindow.action_export_event)
        self.actionExit.triggered.connect(MainWindow.action_exit_event)

#        self.horizontalSlider.valueChanged.connect(self.main_view.go_to_frame)
#        self.playMotionButton.pressed.connect(self.main_view.start_timer)
