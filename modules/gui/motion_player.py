import numpy as np
import typing
from PyQt5 import QtCore, QtGui, QtWidgets

import gui.motion_view as mv


class MotionPlayer(QtWidgets.QWidget):
    DEFAULT_FPS = 120

    def __init__(self, parent=None, flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.
                 WindowFlags()):
        super(MotionPlayer, self).__init__(parent, flags)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.motion_view = mv.MotionView()
#        self.motion_view.setGeometry(QtCore.QRect(0, 0, 960, 720))
        self.motion_view.setObjectName("motion_view")
        self.main_layout.addWidget(self.motion_view, 1)

        self.player = QtWidgets.QWidget()
        self.player.setObjectName("player")
        self.main_layout.addWidget(self.player, 0, QtCore.Qt.AlignTop)

        self.player_layout = QtWidgets.QHBoxLayout()
        self.player.setLayout(self.player_layout)

        self.play_button = QtWidgets.QPushButton()
        self.play_button.setObjectName("play_button")
        self.player_layout.addWidget(self.play_button)

        self.play_slider = QtWidgets.QSlider()
        self.play_slider.setOrientation(QtCore.Qt.Horizontal)
        self.play_slider.setMaximum(2000)
        self.play_slider.setObjectName("play_slider")
        self.player_layout.addWidget(self.play_slider)

        self.timer = QtCore.QTimer()
        self._fps = MotionPlayer.DEFAULT_FPS
        self._spf = int(1000 / self._fps)

        self.connectUi()
        self.connectTimer()

    def connectUi(self):
        self.play_button.pressed.connect(self.start_timer)
        self.play_slider.valueChanged.connect(self.motion_view.go_to_frame)

    def connectTimer(self):
        self.timer.timeout.connect(self.timer_event)

    def start_timer(self, interval: int=None):
        if self.timer.isActive():
            self.timer.stop()
        else:
            if interval is None:
                self.timer.start(self._spf)
            else:
                self.timer.start(interval)

    def timer_event(self):
        self.play_slider.setValue(self.play_slider.value() + 1)

    def set_fps(self, fps):
        self._fps = fps
        self._spf = int(1000 / self._fps)
