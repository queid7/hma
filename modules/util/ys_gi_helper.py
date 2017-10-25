import numpy
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import sys

if '..' not in sys.path:
    sys.path.append('..')

import hmath.mm_math as mm_math


class DrawingSet:
    def __init__(self, default_color=(0, 255, 0)):
        self.point_map = {}
        self.vector_map = {}
        self.vector_origin_map = {}
        self.SO3Map = {}
        self.SO3OriginMap = {}
        self.color_map = {}

        self.coordinate = mm_math.i_se3()

        self.point_size = 3.0
        self.line_width = 1.0
        self.default_color = default_color

    def add_point(self, name, point, color=None):
        self.point_map[name] = point
        if not color:
            color = self.default_color
        self.color_map[name] = color

    def add_vector(self, name, vector, origin=(0, 0, 0), color=None):
        self.vector_map[name] = vector
        self.vector_origin_map[name] = origin
        if not color:
            color = self.default_color
        self.color_map[name] = color

    def add_s_o3(self, name, so3, origin=(0, 0, 0), color=None):
        self.SO3Map[name] = so3
        self.SO3OriginMap[name] = origin
        if not color:
            color = self.default_color
        self.color_map[name] = color

    def begin_draw(self):
        begin_draw()
        glMultMatrixf(self.coordinate.transpose())

    def draw_all(self):
        self.draw_points()
        self.draw_vectors()
        self.draw_s_o3s()
        self.draw_coordinate()

    def draw_points(self):
        for name in list(self.point_map.keys()):
            self.draw_point(name)

    def draw_vectors(self):
        for name in list(self.vector_map.keys()):
            self.draw_vector(name)

    def draw_s_o3s(self):
        for name in list(self.SO3Map.keys()):
            self.draw_s_o3(name)

    def draw_point(self, name):
        draw_point(self.point_map[name], self.color_map.get(name, self.default_color), self.point_size, name)

    def draw_vector(self, name):
        draw_vector(self.vector_map[name], self.vector_origin_map.get(name, (0, 0, 0)),
                    self.color_map.get(name, self.default_color), self.line_width, name)

    def draw_s_o3(self, name):
        draw_s_o3(self.SO3Map[name], self.SO3OriginMap.get(name, (0, 0, 0)),
                  self.color_map.get(name, self.default_color), self.line_width, name)

    def draw_coordinate(self):
        draw_coordinate(self.default_color, .5, 1.0)

    def end_draw(self):
        end_draw()

    def __str__(self):
        string = ''
        string += '# point_map\n'
        for name, point in list(self.point_map.items()):
            string += name + str(point) + '\n'
        string += '# vector_map\n'
        for name, vector in list(self.vector_map.items()):
            string += name + str(vector) + 'origin -' + str(self.vector_origin_map.get(name, (0, 0, 0))) + '\n'
        string += '# SO3Map\n'
        for name, SO3 in list(self.SO3Map.items()):
            print(name, SO3)
        string += '# coordinate\n' + str(self.coordinate)
        return string


def begin_draw():
    glPushMatrix()
    glPushAttrib(GL_CURRENT_BIT | GL_POINT_BIT | GL_LINE_BIT | GL_LIGHTING_BIT | GL_ENABLE_BIT)
    glShadeModel(GL_SMOOTH)


def draw_polygon(vertices, color=(0, 255, 0), name=''):
    glColor3ubv(color)
    glDisable(GL_CULL_FACE)
    glPolygonMode(GL_FRONT, GL_FILL)
    glPolygonMode(GL_BACK, GL_LINE)
    glBegin(GL_TRIANGLES)
    for v in vertices:
        glVertex3fv(v)
    glEnd()


def draw_point(point, color=(0, 255, 0), size=3.0, name=''):
    glColor3ubv(color)
    glPointSize(size)
    glBegin(GL_POINTS)
    glVertex3fv(point)
    glEnd()


def draw_vector(vector, origin=numpy.array([0, 0, 0]), color=(0, 255, 0), line_width=1.0, name=''):
    glLineWidth(line_width)
    glBegin(GL_LINES)
    glColor3ubv((255, 255, 255))
    glVertex3fv(origin)
    glColor3ubv(color)
    glVertex3fv((origin[0] + vector[0], origin[1] + vector[1], origin[2] + vector[2]))
    glEnd()


def draw_line(start_pos, end_pos, color=(0, 255, 0), line_width=1.0, name=''):
    glLineWidth(line_width)
    glBegin(GL_LINES)
    glColor3ubv(color)
    glVertex3fv(start_pos)
    glVertex3fv(end_pos)
    glEnd()


def draw_s_o3(SO3, origin=numpy.array([0, 0, 0]), color=(0, 255, 0), line_width=1.0, name=''):
    glEnable(GL_LINE_STIPPLE)
    glLineStipple(2, 0xFAFA)
    draw_vector(mm_math.log_s_o3(SO3), origin, color, line_width)
    glDisable(GL_LINE_STIPPLE)


def draw_coordinate(color=(0, 255, 0), axis_length=.5, line_width=1.0):
    glLineWidth(line_width)
    glColor3ubv(color)
    glBegin(GL_LINES)
    font_size = axis_length / 20
    glVertex3f(axis_length, 0, 0)  # x
    glVertex3f(0, 0, 0)
    glVertex3f(axis_length - font_size, font_size, 0)
    glVertex3f(axis_length + font_size, -font_size, 0)
    glVertex3f(axis_length + font_size, +font_size, 0)
    glVertex3f(axis_length - font_size, -font_size, 0)
    glVertex3f(0, axis_length, 0)  # y
    glVertex3f(0, 0, 0)
    glVertex3f(font_size, axis_length + font_size, 0)
    glVertex3f(0, axis_length, 0)
    glVertex3f(-font_size, axis_length + font_size, 0)
    glVertex3f(0, axis_length, 0)
    glVertex3f(0, 0, axis_length)  # z
    glVertex3f(0, 0, 0)
    glEnd()


def draw_cross(point, color=(0, 255, 0), cross_length=.1, line_width=1.0, name=''):
    glLineWidth(line_width)
    glColor3ubv(color)
    glPushMatrix()
    glTranslatef(point[0], point[1], point[2])
    glBegin(GL_LINES)
    glVertex3f(cross_length / 2., 0, 0)  # x
    glVertex3f(-cross_length / 2., 0, 0)
    glVertex3f(0, cross_length / 2., 0)  # y
    glVertex3f(0, -cross_length / 2., 0)
    glVertex3f(0, 0, cross_length / 2.)  # z
    glVertex3f(0, 0, -cross_length / 2.)
    glEnd()
    glPopMatrix()


def end_draw():
    glPopAttrib()
    glPopMatrix()    