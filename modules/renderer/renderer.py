import sys
import numpy as np
from PyQt5.QtGui import QColor
from OpenGL import GL, GLU

import mm_math as mm
import motion
import draw_figure as df

DEFAULT_COLOR = (0., 0., 1., 1.)
DEFAULT_LINK_WIDTH = 5

LINE_MODE = True


class Renderer:
    def __init__(self):
        self._visible = True

    def make_visible(self):
        self._visible = True

    def make_invisible(self):
        self._visible = False

    def is_visible(self):
        return self._visible

    def render(self):
        raise NotImplementedError

    def go_to_frame(self):
        pass


class JointMotionRender(Renderer):
    def __init__(self, joint_motion=motion.JointMotion()):
        super(JointMotionRender, self).__init__()
        self._joint_motion = joint_motion
        self._link_color = DEFAULT_COLOR
        # c = QColor.fromCmykF(0.40, 0.0, 1.0, 0.0)
        # (c.redF(), c.greenF(), c.blueF(), c.alphaF())

        self.gl_objects = None
        self.make_gl_objects()

    def render(self):
        """
        render joint_motion at frame using gl_objects
        :return:
        """
#        posture = self._joint_motion.get_current_posture()
        global_ts = self._joint_motion.get_current_posture().get_global_ts()
        for i in range(len(self.gl_objects)):
            if len(self.gl_objects[i]) > 0:
                GL.glPushMatrix()
                GL.glMultTransposeMatrixd(global_ts[i].tolist())
                for obj in self.gl_objects[i]:
                    if obj[1] is not None:
                        GL.glTranslated(*obj[1])
                    GL.glCallList(obj[0])
                GL.glPopMatrix()

    def go_to_frame(self, frame):
        self._joint_motion.go_to_frame(frame)

    def move_frame(self, offset):
        self._joint_motion.move_frame(offset)

    def get_joint_motion(self):
        return self._joint_motion

    def set_joint_motion(self, joint_motion):
        self._joint_motion = joint_motion
        self.make_gl_objects()

    def make_gl_objects(self):
        """
        makes gl objects to draw from skeleton of _joint_motion
        if _joint_motion is empty list, skeleton is None, then return None
        else makes gl objects and return
        :return:
        """
        if self._joint_motion.get_skeleton() is None:
            self.gl_objects = None
            return None
        self.gl_objects = list()
        skeleton = self._joint_motion.get_skeleton()
        for node in skeleton.get_nodes():
            gl_object = list()
            for child in node.get_children():
                translation = child.get_translation()
                cube_size = [DEFAULT_LINK_WIDTH] * 3
                for i in range(len(translation)):
                    if translation[i] != 0:
                        cube_size[i] = abs(translation[i])
                if LINE_MODE:
                    obj = (df.make_line(0, 0, 0, translation[0], translation[1], translation[2]), [0, 0, 0])
                else:
                    obj = (df.make_cube(cube_size[0], cube_size[1], cube_size[2]), translation / 2)
                gl_object.append(obj)
            self.gl_objects.append(gl_object)
