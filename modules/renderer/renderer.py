import sys
import numpy as np
from PyQt5.QtGui import QColor
from OpenGL import GL, GLU

import hmath.mm_math as mm
import motion.motion as motion
import renderer.draw_figure as df

DEFAULT_COLOR = (0., 1., 1., 1.)
DEFAULT_LINK_WIDTH = 5

LINE_MODE = True


class Renderer:
    def __init__(self):
        self._visible = True
        self.color = DEFAULT_COLOR
        self.mode = None
        self.gl_objects = None

    def make_visible(self):
        self._visible = True

    def make_invisible(self):
        self._visible = False

    def set_color(self, color):
        self.color = color

    def get_color(self):
        return self.color

    def is_visible(self):
        return self._visible

    def render(self):
        raise NotImplementedError

    def go_to_frame(self):
        pass

    def move_frame(self):
        pass

    def get_max_frame(self):
        return None

    def set_mode(self, mode):
        self.mode = mode
        self.make_gl_objects()

    def make_gl_objects(self):
        raise NotImplementedError


class JointMotionRender(Renderer):
    LINE_MODE = 0
    CUBE_MODE = 1

    def __init__(self, joint_motion=motion.JointMotion()):
        super(JointMotionRender, self).__init__()
        self.mode = JointMotionRender.LINE_MODE

        self._joint_motion = joint_motion
        self.make_gl_objects()

    def render(self):
        """
        render joint_motion at frame using gl_objects
        :return:
        """
        if self._visible is not True:
            return

        # c = QColor.fromCmykF(0.40, 0.0, 1.0, 0.0)
        # (c.redF(), c.greenF(), c.blueF(), c.alphaF())
        GL.glColor4d(*self.color)
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

    def go_to_frame(self, frame=0):
        self._joint_motion.go_to_frame(frame)

    def move_frame(self, offset=1):
        self._joint_motion.move_frame(offset)

    def get_joint_motion(self):
        return self._joint_motion

    def set_joint_motion(self, joint_motion):
        self._joint_motion = joint_motion
        self.make_gl_objects()

    def get_max_frame(self):
        return len(self._joint_motion)

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
        # gl_objects[i] : i-th joint's objects to draw
        # gl_objects[i][j] : j-th object of i-th joint : (genList, translation vec3 : numpy.ndarray)
        self.gl_objects = list()
        skeleton = self._joint_motion.get_skeleton()
        for node in skeleton.get_nodes():
            gl_object_at_joint = list()
            for child in node.get_children():
                translation = child.get_translation()
                cube_size = [DEFAULT_LINK_WIDTH] * 3
                for i in range(len(translation)):
                    if translation[i] != 0:
                        cube_size[i] = abs(translation[i])
                if self.mode == JointMotionRender.LINE_MODE:
                    obj = (df.make_line(0, 0, 0, translation[0], translation[1], translation[2]), [0, 0, 0])
                elif self.mode == JointMotionRender.CUBE_MODE:
                    obj = (df.make_cube(cube_size[0], cube_size[1], cube_size[2]), translation / 2)
                else:
                    raise ValueError("invalid mode : ", self.mode)
                gl_object_at_joint.append(obj)
            self.gl_objects.append(gl_object_at_joint)


class PlaneRenderer(Renderer):
    FILL_MODE = 0
    GRID_MODE = 1

    def __init__(self, x_axis, y_axis, half_size_x, half_size_y, center=mm.o_vec3()):
        super(PlaneRenderer, self).__init__()

        self.x_axis = x_axis
        self.y_axis = y_axis
        self.half_size_x = half_size_x
        self.half_size_y = half_size_y
        self.center = center

        self.grid_num_x = 10
        self.grid_num_y = 10

        self.mode = PlaneRenderer.FILL_MODE

        self.make_gl_objects()

    def render(self):
        if self._visible is not True:
            return
        GL.glColor4d(*self.color)
        for obj in self.gl_objects:
            GL.glCallList(obj)

    def set_mode(self, mode):
        self.mode = mode
        self.make_gl_objects()

    def make_gl_objects(self):
        self.gl_objects = list()
        if self.mode == PlaneRenderer.FILL_MODE:
            self.gl_objects.append(df.make_plane(self.x_axis, self.y_axis, self.half_size_x, self.half_size_y,
                                                 self.center))
        elif self.mode == PlaneRenderer.GRID_MODE:
            self.gl_objects.append(df.make_grid_plane(self.x_axis, self.y_axis, self.half_size_x, self.half_size_y,
                                                      self.grid_num_x, self.grid_num_y, self.center))
        else:
            raise ValueError("invalid mode : ", self.mode)
