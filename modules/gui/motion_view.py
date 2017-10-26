import numpy as np
import typing
from PyQt5 import QtCore, QtGui, QtWidgets
from OpenGL import GL, GLU

import mm_math as mm
import draw_figure as df
import renderer
import motion
import bvh_loader as bl


class MotionView(QtWidgets.QOpenGLWidget):
    """
    MotionView is a QOpenGLWidget which has a camera and renderers for motions
    """
    zRotationChanged = QtCore.pyqtSignal(int)
    DEFAULT_FPS = 120

    def __init__(self, parent=None, flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = QtCore.Qt.
                 WindowFlags()):
        super(MotionView, self).__init__(parent, flags)
        self._renderers = list()
        self.base_plane_renderer = None

        # initialize camera
        self.camera = Camera()
#        self.camera.set_center(mm.seq_to_vec3([0., 200., 2000.]))
        self.camera.set_center(mm.seq_to_vec3([2000., 0., 200.]))
        self.camera.set_direction(mm.seq_to_vec3([-1., 0., 0.]))
        self.camera.set_up(mm.seq_to_vec3([0., 0., 1.]))
        self.camera.z_near = 10
        self.camera.z_far = 5000

        # information for frame
        self._max_frame = 0
        self._fps = MotionView.DEFAULT_FPS
        self._spf = int(1000. / self._fps)

        # initialize timer
        self._timer = QtCore.QTimer()
        self._timer.timeout.connect(self._timer_event)

        # temporary data for mouse
        self.last_pos = QtCore.QPoint(0, 0)

    def initializeGL(self):
        print("initializeGL")
        GL.glClearColor(0., 0., 0., 1.)

#        GL.glShadeModel(GL.GL_SMOOTH)
        GL.glShadeModel(GL.GL_FLAT)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)

        self.base_plane_renderer = renderer.PlaneRenderer(mm.seq_to_vec3([1, 0, 0]), mm.seq_to_vec3([0, 1, 0]),
                                                          1000, 1000, mm.o_vec3())
        self.base_plane_renderer.color = (0., 0., 1., .7)
        self.base_plane_renderer.set_mode(renderer.PlaneRenderer.GRID_MODE)

    def paintGL(self):
        print("paintGL")
        self.camera.gluPerspective()
        self.camera.gluLookAt()
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glMatrixMode(GL.GL_MODELVIEW)

        self.base_plane_renderer.render()
        for _renderer in self._renderers:
            _renderer.render()

    def resizeGL(self, width, height):
        print("resizeGL")
        side = min(width, height)
        if side < 0:
            return
        GL.glViewport((width - side) // 2, (height - side) // 2, side, side)

    def mousePressEvent(self, a0: QtGui.QMouseEvent):
        self.last_pos = a0.pos()

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent):
        dx = a0.x() - self.last_pos.x()
        dy = a0.y() - self.last_pos.y()

        if a0.buttons() == QtCore.Qt.RightButton:
            print("right button")
            self.camera.set_center(self.camera.get_center() + self.camera.get_up() * dy * 0.005 +
                                   self.camera.get_right() * -dx * 0.002)
            self.update()
        elif a0.buttons() == QtCore.Qt.LeftButton:
            print("left button")
            self.camera.rotate_up += dx
            self.camera.rotate_right += dy
            self.update()
        elif a0.buttons() == QtCore.Qt.MiddleButton:
            print("middle button")
            self.camera.add_fovy(dx * 0.5)
            self.camera.add_fovy(-dy * 0.5)
            self.update()

        self.last_pos = a0.pos()

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent):
        self.last_pos = mm.o_vec3()

    def keyPressEvent(self, a0: QtGui.QKeyEvent):
        print("key pressed")
        print(a0)
        print(a0.key())

    def keyReleaseEvent(self, a0: QtGui.QKeyEvent):
        print("key released")
        print(a0)
        print(a0.key())

    """
    def set_projection_matrix(self):
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(-5, +5, -5, +5, -5, 15.0)
        GL.glMatrixMode(GL.GL_MODELVIEW)
    """

    def add_renderer(self, renderer_):
        if renderer_ is not None:
            self._renderers.append(renderer_)
        self._update_max_frame()

    def remove_renderer(self, renderer_):
        self._renderers.remove(renderer_)
        self._update_max_frame()

    def get_renderer_at(self, index):
        return self._renderers[index]

    def get_renderer_by_name(self, name):
        for r in self._renderers:
            if r.name == name:
                return r
        raise ValueError("there is no renderer with that name")

    def _update_max_frame(self):
        try:
            self._max_frame = min([r.get_max_frame() for r in self._renderers
                                   if r.get_max_frame() is not None])
        except ValueError:
            self._max_frame = 0

    def go_to_frame(self, frame):
        """
        if frame < self._max_frame:
            for r in self._renderers:
                r.go_to_frame(frame)
            self.update()
        """
        # for test
        for r in self._renderers:
            if r.get_max_frame() is not None and frame < r.get_max_frame():
                r.go_to_frame(frame)
        self.update()
        print(frame)

    def set_fps(self, fps):
        self._fps = fps
        self._spf = int(1000. / self._fps)

    def start_timer(self, interval=None):
        if self._timer.isActive():
            self._timer.stop()
        else:
            if interval is None:
                self._timer.start(self._spf)
            else:
                self._timer.start(interval)

    def _timer_event(self):
        print("a motion_view's timer emmit a timeout signal")
        for r in self._renderers:
            r.move_frame(1)


# =====================================================
class Camera:
    DEFAULT_MIN_FOVY = 10
    DEFAULT_MAX_FOVY = 170

    def __init__(self, center=np.array([0., 0., 10.]), direction=np.array([0., 0., -10.]), up=np.array([0., 10., 0.]),
                 fovy=60, aspect=1.0, z_near=0.5, z_far=15.):
        self.view_matrix = mm.i_se3()

        self._center = center
        self._direction = direction
        self._up = up
        self._right = np.cross(self._direction, self._up)

        self.rotate_up = 0.
        self.rotate_right = 0.

        self.fovy = fovy
        self.aspect = aspect
        self.z_near = z_near
        self.z_far = z_far

    def _update_right(self):
        self._right = np.cross(self._direction, self._up)

    def update_view_matrix(self):
        rotation_matrix = mm.i_se3()
        translation_matrix = mm.p_to_t(-self._center)

        rotation_matrix[0, 0] = self._right[0]
        rotation_matrix[0, 1] = self._right[1]
        rotation_matrix[0, 2] = self._right[2]
        rotation_matrix[1, 0] = self._up[0]
        rotation_matrix[1, 1] = self._up[1]
        rotation_matrix[1, 2] = self._up[2]
        rotation_matrix[2, 0] = -self._direction[0]
        rotation_matrix[2, 1] = -self._direction[1]
        rotation_matrix[2, 2] = -self._direction[2]

        self.view_matrix = np.dot(rotation_matrix, translation_matrix)

    def set_center(self, position_vec3):
        self._center = position_vec3.copy()

    def get_center(self):
        return self._center

    def set_direction(self, direction_vec3):
        self._direction = mm.normalize(direction_vec3)
        self._update_right()

    def get_direction(self):
        return self._direction

    def set_up(self, up_vec3):
        self._up = mm.normalize(up_vec3)
        self._update_right()

    def get_up(self):
        return self._up

    def get_right(self):
        return self._right

    def add_fovy(self, fovy):
        self.fovy += fovy
        if self.fovy > Camera.DEFAULT_MAX_FOVY:
            self.fovy = Camera.DEFAULT_MAX_FOVY
        elif self.fovy < Camera.DEFAULT_MIN_FOVY:
            self.fovy = Camera.DEFAULT_MIN_FOVY

    def gluLookAt(self):
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GLU.gluLookAt(*self.get_center().tolist(),
                      *(self.get_center() + self.get_direction()).tolist(),
                      *self.get_up().tolist())
        GL.glRotated(self.rotate_up, self._up[0], self._up[1], self._up[2])
        GL.glRotated(self.rotate_right, self._right[0], self._right[1], self._right[2])

    def gluPerspective(self):
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GLU.gluPerspective(self.fovy, self.aspect, self.z_near, self.z_far)
        GL.glMatrixMode(GL.GL_MODELVIEW)
