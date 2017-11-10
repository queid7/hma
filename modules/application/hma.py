import sys
import os
import typing
from PyQt5 import QtCore, QtGui, QtWidgets

import application.hma_ui as hu
import gui.motion_view as mv
import hmath.mm_math as mm
import renderer.renderer as renderer
import resource.bvh_loader as bl
import resource.htr_loader as hl
import motion


class Hma:
    def __init__(self):
        self.motion_container = []

    def add_motion(self, motion_):
        self.motion_container.append(motion_)


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
        print("file dialog")
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dlg.setNameFilters(["motion files (*.htr)", "motion files (*.bvh)", "all files (*.*)"])
        dlg.setDirectory("C:/Users/mrl/Research/Motions")
        if dlg.exec_():
            file_path = dlg.selectedFiles()
            ext = os.path.splitext(file_path[0])[1]
            print("action_import")
            if ext == ".bvh":
                joint_motion = bl.read_bvh_file(file_path[0])
            elif ext == ".htr":
                #joint_motion = hl.read_htr_file(file_path[0])
                htr_motion = hl.read_htr_file_as_htr(file_path[0])
                htr_motion.add_end_effector("L.Foot", mm.seq_to_vec3([100, 0, 0]))
                joint_motion = htr_motion.to_joint_motion()

            else:
                print("invalid file extension")
                return
            self.hma.add_motion(joint_motion)
            self.findChild(mv.MotionView, "motion_view").add_renderer(renderer.JointMotionRender(joint_motion))

        mot = self.hma.motion_container[0]
        ske = mot.get_skeleton()
        print([n.label for n in ske.get_nodes()])

#        foot_index = ske.get_index_by_label("L.Foot")
#        print(mot.get_position(foot_index, 0))
#        print(mot.get_positions(0))
#        print(mot.get_velocity(foot_index, 0, 120))
#        print(mot.get_velocities(0, 120))
#        print(mot.get_acceleration(foot_index, 0, 120))
#        print(mot.get_accelerations(0, 120))


#        joint_motion = bl.read_bvh_file("../../../../Research/Motions/cmuconvert-daz-01-09/01/01_02.bvh")
#        joint_motion = bl.read_bvh_file("../../../../Research/Motions/MotionData/Trial001.bvh")
#        joint_motion = bl.read_bvh_file("../../../../Research/Motions/cmuconvert-max-01-09/01/01_02.bvh", scale = 3)
#        joint_motion = hl.read_htr_file("../../../../Research/Motions/snuh/디딤자료-서울대(조동철선생님)/디딤LT/D-1/16115/trimmed_walk01.htr", 1)

#        self.hma.add_motion(joint_motion)
#        self.findChild(mv.MotionView, "motion_view").add_renderer(renderer.JointMotionRender(joint_motion))
        print("import success")
        """
        posture_list = []
        for i in range(len(joint_motion)-1):
            for j in range(10):
                posture_list.append(joint_motion[(i + 0.1 * j)])
#            posture_list.append(joint_motion[i].blend(joint_motion[i+1], 0.5))
        blended_joint_motion = motion.JointMotion(posture_list)
        self.hma.add_motion(blended_joint_motion)
        self.findChild(mv.MotionView, "motion_view").add_renderer(renderer.JointMotionRender(blended_joint_motion))
        print("blending success")
        """

    def action_export_event(self, checked):
        import analytic_ik as ai
        import mm_math as mm
        motion_ = self.hma.motion_container[0]
        print(motion_.get_skeleton())
        joint_index = motion_.get_skeleton().get_index_by_label("R.Foot")
        for posture in motion_:
            ai.ik_analytic(posture, joint_index, posture.get_global_p(joint_index) + mm.seq_to_vec3([300, 0, 200]),
                           mm.seq_to_vec3([0, 1, 0]))
#        ai.ik_analytic(self.hma.motion_container[0]: motion.JointPosture, joint_name_or_index, new_position, parent_joint_axis = None):
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

