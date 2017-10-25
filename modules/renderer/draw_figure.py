from OpenGL import GL, GLU


def make_cube(size_x, size_y, size_z):
    genList = GL.glGenLists(1)
    GL.glNewList(genList, GL.GL_COMPILE)
    draw_cube(size_x, size_y, size_z)
    GL.glEndList()

    return genList


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


def make_line(x0, y0, z0, x1, y1, z1):
    genList = GL.glGenLists(1)
    GL.glNewList(genList, GL.GL_COMPILE)
    draw_line(x0, y0, z0, x1, y1, z1)
    GL.glEndList()

    return genList


def draw_line(x0, y0, z0, x1, y1, z1):
    vertices = [x0, y0, z0,
                x1, y1, z1]
    indices = [0, 1]
    GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
    GL.glVertexPointer(3, GL.GL_FLOAT, 0, vertices)
    GL.glDrawElements(GL.GL_LINES, len(indices), GL.GL_UNSIGNED_BYTE, indices)