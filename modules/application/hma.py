import sys
import typing
from PyQt5 import QtCore, QtGui, QtWidgets

import hma_ui as hu
import motion_view as mv
import renderer
import bvh_loader as bl
import htr_loader as hl
import motion


class Hma:
    def __init__(self):
        self.motion_container = []

    def add_motion(self, motion):
        self.motion_container.append(motion)


class HmaWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None, flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.
                 WindowFlags()):
        super(HmaWindow, self).__init__(parent, flags)
        self.hma = Hma()

    def action_new_event(self, checked):
        print("action_new")

    def action_open_event(self, checked):
        print("action_open")

    def action_import_event(self, checked):
        print("action_import")
#        joint_motion = bl.read_bvh_file("../../../../Research/Motions/cmuconvert-daz-01-09/01/01_02.bvh")
#        joint_motion = bl.read_bvh_file("../../../../Research/Motions/MotionData/Trial001.bvh")
#        joint_motion = bl.read_bvh_file("../../../../Research/Motions/cmuconvert-max-01-09/01/01_02.bvh", scale = 3)
        joint_motion = hl.read_htr_file("../../../../Research/Motions/snuh/디딤자료-서울대(조동철선생님)/디딤LT/D-1/16115/trimmed_walk01.htr", 1)

        self.hma.add_motion(joint_motion)
        self.findChild(mv.MotionView, "motion_view").add_renderer(renderer.JointMotionRender(joint_motion))
        print("import success")

    def action_export_event(self, checked):
        print("action_export")

    def action_exit_event(self, checked):
        print("action_exit")
        self.close()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    hma_window = HmaWindow(None, QtCore.Qt.FramelessWindowHint)
#    hma_window = HmaWindow()
    ui = hu.HmaUi()
    ui.setupUi(hma_window)
    hma_window.show()
    sys.exit(app.exec_())

