from OpenGL import GL, GLU

import mm_math as mm


def make_figure(make_function):
    def wrapping_function(*args, **kargs):
        genList = GL.glGenLists(1)
        GL.glNewList(genList, GL.GL_COMPILE)
        make_function(*args, **kargs)
        GL.glEndList()

        return genList
    return wrapping_function


@make_figure
def make_cube(size_x, size_y, size_z):
    draw_cube(size_x, size_y, size_z)


def draw_cube(size_x, size_y, size_z):
    x = size_x / 2.
    y = size_y / 2.
    z = size_z / 2.
    vertices = [-x, y, z,
                -x, -y, z,
                x, -y, z,
                x, y, z,
                -x, y, -z,
                -x, -y, -z,
                x, -y, -z,
                x, y, -z]
    indices = [0, 1, 2, 3,
               3, 2, 6, 7,
               7, 6, 5, 4,
               4, 5, 1, 0,
               0, 3, 7, 4,
               5, 6, 2, 1]

    GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
    GL.glVertexPointer(3, GL.GL_FLOAT, 0, vertices)
    GL.glDrawElements(GL.GL_QUADS, len(indices), GL.GL_UNSIGNED_BYTE, indices)


@make_figure
def make_line(x0, y0, z0, x1, y1, z1):
    draw_line(x0, y0, z0, x1, y1, z1)


def draw_line(x0, y0, z0, x1, y1, z1):
    vertices = [x0, y0, z0,
                x1, y1, z1]
    indices = [0, 1]
    GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
    GL.glVertexPointer(3, GL.GL_FLOAT, 0, vertices)
    GL.glDrawElements(GL.GL_LINES, len(indices), GL.GL_UNSIGNED_BYTE, indices)


@make_figure
def make_plane(x_axis, y_axis, half_size_x, half_size_y, center=mm.o_vec3()):
    draw_plane(x_axis, y_axis, half_size_x, half_size_y, center)


def draw_plane(x_axis, y_axis, half_size_x, half_size_y, center=mm.o_vec3()):
    #       ^  y axis
    #       |
    #
    # ------y_p----
    # |           |
    # |     c     x_p     ---> x axis
    # |           |
    # -------------
    #
    #   length(x_p - c) : half_size_x, length(y_p - c) : half_size_y
    vertices = [*(center - half_size_x * x_axis + half_size_y * y_axis),
                *(center - half_size_x * x_axis - half_size_y * y_axis),
                *(center + half_size_x * x_axis - half_size_y * y_axis),
                *(center + half_size_x * x_axis + half_size_y * y_axis)
                ]
    indices = [0, 1, 2, 3]
    GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
    GL.glVertexPointer(3, GL.GL_FLOAT, 0, vertices)
    GL.glDrawElements(GL.GL_QUADS, len(indices), GL.GL_UNSIGNED_BYTE, indices)


@make_figure
def make_grid_plane(x_axis, y_axis, half_size_x, half_size_y, grid_num_x, gird_num_y, center=mm.o_vec3()):
    draw_grid_plane(x_axis, y_axis, half_size_x, half_size_y, grid_num_x, gird_num_y, center=mm.o_vec3())


def draw_grid_plane(x_axis, y_axis, half_size_x, half_size_y, grid_num_x, grid_num_y, center=mm.o_vec3()):
    corner = [(center - half_size_x * x_axis + half_size_y * y_axis),
              (center - half_size_x * x_axis - half_size_y * y_axis),
              (center + half_size_x * x_axis - half_size_y * y_axis),
              (center + half_size_x * x_axis + half_size_y * y_axis)]
    step_x = (corner[3] - corner[0]) / (grid_num_x + 1)
    step_y = (corner[1] - corner[0]) / (grid_num_y + 1)

    vertices = [*corner[0], *corner[1], *corner[2], *corner[3]]
    indices = [0, 1, 3, 2, 0, 3, 1, 2]

    vertex_i = 3
    for i in range(grid_num_x):
        vertices.extend([*(corner[0] + step_x * (i+1))])
        vertices.extend([*(corner[1] + step_x * (i+1))])
        indices.extend([vertex_i + 1, vertex_i + 2])
        vertex_i += 2
    for i in range(grid_num_y):
        vertices.extend([*(corner[0] + step_y * (i+1))])
        vertices.extend([*(corner[3] + step_y * (i+1))])
        indices.extend([vertex_i + 1, vertex_i + 2])
        vertex_i += 2

    GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
    GL.glVertexPointer(3, GL.GL_FLOAT, 0, vertices)
    GL.glDrawElements(GL.GL_LINES, len(indices), GL.GL_UNSIGNED_BYTE, indices)
