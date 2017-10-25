import math
import numpy as np

from scipy import linalg

_I_SO3 = np.array([[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]], float)
_I_SE3 = np.array([[1., 0., 0., 0.], [0., 1., 0., 0.], [0., 0., 1., 0.], [0., 0., 0., 1.]], float)

_O_VEC3 = np.array([0., 0., 0.], float)
_O_SO3 = np.zeros((3, 3))

RAD = 0.0174532925199432957692  # = pi / 180
DEG = 57.2957795130823208768  # = 180 / pi


def acos(x):
    if x > 1.0:
        return 0.0
    elif x < -1.0:
        return math.pi
    else:
        return math.acos(x)


def i_so3():
    return _I_SO3.copy()


def i_se3():
    return _I_SE3.copy()


def o_vec3():
    return _O_VEC3.copy()


def linearInterpol(v0, v1, t):
    return v0 + (v1 - v0) * t


def slerp(r1, r2, t):
    return np.dot(r1, exp(t * log_so3(np.dot(r1.transpose(), r2))))
    #   return np.dot(R1, cm.exp(t * cm.log(np.dot(R1.T, R2))))


def scaleSO3(r, t):
    return exp(t * log_so3(r))
    #   return cm.exp(t * cm.log(R))


def deg2Rad(deg):
    return float(deg) / 180.0 * math.pi


def rad2Deg(rad):
    return float(rad) / math.pi * 180.0


def length(vec3):
    if isinstance(vec3, np.ndarray):
        return math.sqrt(np.dot(vec3, vec3))
    else:
        return math.sqrt(vec3[0] * vec3[0] + vec3[1] * vec3[1] + vec3[2] * vec3[2])


# return math.sqrt(transV[0]*transV[0] + transV[1]*transV[1] + transV[2]*transV[2])

def normalize_tuple(vec3):
    """

    :param vec3:
    :return tuple(normalized transV):
    """
    _len = length(vec3)
    if _len > 0.:
        return vec3[0] / _len, vec3[1] / _len, vec3[2] / _len
    else:
        raise ValueError("the length of vector is lower than 0")
        #       return None
        #       return transV


def normalize(vec3):
    """

    :param vec3:
    :return v3(normalized transV):
    """
    _len = length(vec3)
    if _len > 0.:
        return seq_to_vec3([vec3[0] / _len, vec3[1] / _len, vec3[2] / _len])
    else:
        raise ValueError("the length of vector is lower than 0")
        #       return None
        #       return transV


def se3_to_vec3(se3):
    return np.array([se3[0][3], se3[1][3], se3[2][3]])


def se3_to_ode_vec3(se3):
    return se3[0][3], se3[1][3], se3[2][3]


def vec3_to_se3(vec3):
    se3 = np.array([[1, 0, 0, vec3[0]], [0, 1, 0, vec3[1]], [0, 0, 1, vec3[2]], [0, 0, 0, 1]], float)
    return se3


def get_so3_by_euler(euler_angles):
    alpha = euler_angles[0]
    beta = euler_angles[1]
    gamma = euler_angles[2]

    cosA = math.cos(alpha)
    cosB = math.cos(beta)
    cosG = math.cos(gamma)

    sinA = math.sin(alpha)
    sinB = math.sin(beta)
    sinG = math.sin(gamma)

    so3 = np.array([[cosB * cosG, cosG * sinA * sinB - cosA * sinG, cosA * cosG * sinB + sinA * sinG],
                    [cosB * sinG, cosA * cosG + sinA * sinB * sinG, cosA * sinB * sinG - cosG * sinA],
                    [-sinB, cosB * sinA, cosA * cosB]], float)

    return so3


def ode_so3_to_so3(ose_so3):
    so3 = np.array(
        [[ose_so3[0], ose_so3[1], ose_so3[2]], [ose_so3[3], ose_so3[4], ose_so3[5]], [ose_so3[6], ose_so3[7],
                                                                                      ose_so3[8]]],
        float)
    return so3


def so3_to_ode_so3(so3):
    return [so3[0, 0], so3[0, 1], so3[0, 2], so3[1, 0], so3[1, 1], so3[1, 2], so3[2, 0], so3[2, 1], so3[2, 2]]


def ose_vec3_to_vec3(ode_vec3):
    _vec3 = np.array([ode_vec3[0], ode_vec3[1], ode_vec3[2]], float)
    return _vec3


def so3_to_se3(so3, vec3=list([0., 0., 0.])):
    se3 = np.array([[so3[0, 0], so3[0, 1], so3[0, 2], vec3[0]], [so3[1, 0], so3[1, 1], so3[1, 2], vec3[1]],
                    [so3[2, 0], so3[2, 1], so3[2, 2], vec3[2]], [0., 0., 0., 1.]], float)
    return se3


def se3_to_so3(se3):
    so3 = np.array(
        [[se3[0, 0], se3[0, 1], se3[0, 2]], [se3[1, 0], se3[1, 1], se3[1, 2]], [se3[2, 0], se3[2, 1], se3[2, 2]]],
        float)
    return so3


def invert_se3(se3):
    r = np.array(
        [[se3[0, 0], se3[0, 1], se3[0, 2]], [se3[1, 0], se3[1, 1], se3[1, 2]], [se3[2, 0], se3[2, 1], se3[2, 2]]],
        float)
    p = np.array([se3[0, 3], se3[1, 3], se3[2, 3]])
    r_t = r.transpose()
    r_tp = np.dot(r_t, p)

    se3_inv = np.array(
        [[r_t[0, 0], r_t[0, 1], r_t[0, 2], 0.], [r_t[1, 0], r_t[1, 1], r_t[1, 2], 0.], [r_t[2, 0], r_t[2, 1],
                                                                                        r_t[2, 2], 0.],
         [0., 0., 0., 1.]], float)
    se3_inv[0, 3] = -r_tp[0]
    se3_inv[1, 3] = -r_tp[1]
    se3_inv[2, 3] = -r_tp[2]

    return se3_inv


LIE_EPS = 1E-6


def log_so3_old(so3):
    cosTheta = 0.5 * (so3[0, 0] + so3[1, 1] + so3[2, 2] - 1.0)
    if math.fabs(cosTheta) > 1.0 - LIE_EPS:
        #        print 'log_so3 return zero array'
        return np.array([0., 0., 0.])
    theta = math.acos(cosTheta)

    cof = theta / (2.0 * math.sin(theta))
    return np.array([cof * (so3[2][1] - so3[1][2]), cof * (so3[0][2] - so3[2][0]), cof * (so3[1][0] - so3[0][1])],
                    float)


M_PI_SQRT2 = 2.22144146907918312351  # = pi / sqrt(2)


def log_so3(so3):
    cosTheta = 0.5 * (so3[0, 0] + so3[1, 1] + so3[2, 2] - 1.0)
    if cosTheta < LIE_EPS - 1.0:
        if so3[0, 0] > 1.0 - LIE_EPS:
            return np.array([math.pi, 0., 0.], float)
        elif so3[1, 1] > 1.0 - LIE_EPS:
            return np.array([0., math.pi, 0.], float)
        elif so3[2, 2] > 1.0 - LIE_EPS:
            return np.array([0., 0., math.pi], float)
        else:
            return np.array(
                [M_PI_SQRT2 * math.sqrt((so3[1, 0] * so3[1, 0] + so3[2, 0] * so3[2, 0]) / (1.0 - so3[0, 0])),
                 M_PI_SQRT2 * math.sqrt((so3[0, 1] * so3[0, 1] + so3[2, 1] * so3[2, 1]) / (1.0 - so3[1, 1])),
                 M_PI_SQRT2 * math.sqrt((so3[0, 2] * so3[0, 2] + so3[1, 2] * so3[1, 2]) / (1.0 - so3[2, 2]))], float)
    else:
        if cosTheta > 1.0:
            cosTheta = 1.0
        theta = math.acos(cosTheta)

        if theta < LIE_EPS:
            cof = 3.0 / (6.0 - theta * theta)
        else:
            cof = theta / (2.0 * math.sin(theta))

        return np.array([cof * (so3[2][1] - so3[1][2]), cof * (so3[0][2] - so3[2][0]), cof * (so3[1][0] - so3[0][1])],
                        float)


def log_so3_tuple(so3):
    cosTheta = 0.5 * (so3[0, 0] + so3[1, 1] + so3[2, 2] - 1.0)
    if math.fabs(cosTheta) > 1.0 - LIE_EPS:
        return np.array([0., 0., 0.])
    theta = math.acos(cosTheta)

    cof = theta / (2.0 * math.sin(theta))
    return cof * (so3[2][1] - so3[1][2]), cof * (so3[0][2] - so3[2][0]), cof * (so3[1][0] - so3[0][1])


def exp(axis, theta=None):
    """

    :param axis: vec3 axis
    :param theta: radian
    :return: rotation matrix
    """
    if theta is None:
        theta = length(axis)
    axis = normalize(axis)

    [x, y, z] = axis
    c = math.cos(theta)
    s = math.sin(theta)
    #    seq_to_so3 = np.array( [[c + (1.0-c)*x*x,    (1.0-c)*x*y - s*z,    (1-c)*x*z + s*y],
    #                       [(1.0-c)*x*y + s*z,    c + (1.0-c)*y*y,    (1.0-c)*y*z - s*x],
    #                       [(1.0-c)*z*x - s*y,    (1.0-c)*z*y + s*x,    c + (1.0-c)*z*z]])
    #    return seq_to_so3
    r = _I_SO3.copy()
    r[0, 0] = c + (1.0 - c) * x * x
    r[0, 1] = (1.0 - c) * x * y - s * z
    r[0, 2] = (1 - c) * x * z + s * y
    r[1, 0] = (1.0 - c) * x * y + s * z
    r[1, 1] = c + (1.0 - c) * y * y
    r[1, 2] = (1.0 - c) * y * z - s * x
    r[2, 0] = (1.0 - c) * z * x - s * y
    r[2, 1] = (1.0 - c) * z * y + s * x
    r[2, 2] = c + (1.0 - c) * z * z
    return r


# returns X that X dot vec1 = vec2
def get_so3_from_vectors(vec1, vec2):
    vec1 = normalize(vec1)
    vec2 = normalize(vec2)

    rot_axis = normalize(np.cross(vec1, vec2))
    inner = np.inner(vec1, vec2)
    theta = math.acos(inner)
    #    if np.inner(vec1, vec2) < 0:
    #        theta = math.pi * 2 - theta
    #        rot_axis = - rot_axis
    if rot_axis[0] == 0 and rot_axis[1] == 0 and rot_axis[2] == 0:
        rot_axis = [0, 1, 0]

    x, y, z = rot_axis
    c = inner
    s = math.sin(theta)
    so3 = np.array([[c + (1.0 - c) * x * x, (1.0 - c) * x * y - s * z, (1 - c) * x * z + s * y],
                    [(1.0 - c) * x * y + s * z, c + (1.0 - c) * y * y, (1.0 - c) * y * z - s * x],
                    [(1.0 - c) * z * x - s * y, (1.0 - c) * z * y + s * x, c + (1.0 - c) * z * z]])
    return so3


def get_se3_by_vec3(vec3):
    se3 = np.array([[1, 0, 0, vec3[0]], [0, 1, 0, vec3[1]], [0, 0, 1, vec3[2]], [0, 0, 0, 1]], float)
    return se3


def get_se3_by_rot_x(angle):
    c = math.cos(angle)
    s = math.sin(angle)
    se3 = np.array([[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]], float)
    return se3


def get_se3_by_rot_y(angle):
    c = math.cos(angle)
    s = math.sin(angle)
    se3 = np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]], float)
    return se3


def se3_to_se2(se3):
    rotV = log_so3(se3_to_so3(se3))
    cosT = math.cos(rotV[1])
    sinT = math.sin(rotV[1])
    se2 = np.array([[cosT, -sinT, se3[2, 3]], [sinT, cosT, se3[0, 3]], [0, 0, 1]], float)

    return se2


def diff_angle(x, y):
    arrayX = [math.cos(x), -math.sin(x), math.sin(x), math.cos(x)]
    arrayY = [math.cos(y), -math.sin(y), math.sin(y), math.cos(y)]
    invArrayY = [arrayY[3], -arrayY[1], -arrayY[2], arrayY[0]]
    a = arrayX
    b = invArrayY
    Z = [a[0] * b[0] + a[1] * b[2], a[0] * b[1] + a[1] * b[3], a[2] * b[0] + a[3] * b[2], a[2] * b[1] + a[3] * b[3]]

    if Z[0] > 1:
        Z[0] = 1
    elif Z[0] < -1:
        Z[0] = -1

    if Z[2] >= 0:
        theta = math.acos(Z[0])
    else:
        theta = -math.acos(Z[0])

    return theta


# A = (a11, a12, a13, a21, a22, a23, a31, a32, a33)
def dot_tuple_so3(a, b):
    return (a[0] * b[0] + a[1] * b[3] + a[2] * b[6], a[0] * b[1] + a[1] * b[4] + a[2] * b[7],
            a[0] * b[2] + a[1] * b[5] + a[2] * b[8], a[3] * b[0] + a[4] * b[3] + a[5] * b[6],
            a[3] * b[1] + a[4] * b[4] + a[5] * b[7], a[3] * b[2] + a[4] * b[5] + a[5] * b[8],
            a[6] * b[0] + a[7] * b[3] + a[8] * b[6], a[6] * b[1] + a[7] * b[4] + a[8] * b[7],
            a[6] * b[2] + a[7] * b[5] + a[8] * b[8])


def subtract_tuple_vec(a, b):
    return a[0] - b[0], a[1] - b[1], a[2] - b[2]


def transpose_tuple_so3(a):
    return a[0], a[3], a[6], a[1], a[4], a[7], a[2], a[5], a[8]


def log_so3_tuple_so3(a):
    cos_theta = 0.5 * (a[0] + a[4] + a[8] - 1.0)
    if math.fabs(cos_theta) > 1.0 - LIE_EPS:
        return 0, 0, 0
    theta = math.acos(cos_theta)

    cof = theta / (2.0 * math.sin(theta))
    return cof * (a[7] - a[5]), cof * (a[2] - a[6]), cof * (a[3] - a[1])


def numpy_so3_to_tuple_so3(so3):
    return so3[0, 0], so3[0, 1], so3[0, 2], so3[1, 0], so3[1, 1], so3[1, 2], so3[2, 0], so3[2, 1], so3[2, 2]


# ===============================================================================
# vector projection
# ===============================================================================

# projection of inputVector on directionVector
# vi = input vector
# vd = direction vector

# (vd<inner>vi)/|vd|
# ( vd<inner>vi = |vd||vi|cos(th) )
def component_on_vector(input_vector, direction_vector):
    return np.inner(direction_vector, input_vector) / length(direction_vector) ** 2


# component_on_vector() * vd
def projection_on_vector(input_vector, direction_vector):
    return component_on_vector(input_vector, direction_vector) * direction_vector


def projection_on_plane(input_vector, plane_vector1, plane_vector2):
    h = np.cross(plane_vector1, plane_vector2)
    projectionOn_h = projection_on_vector(input_vector, h)
    return input_vector - projectionOn_h


# return projected vector, residual vector
def projection_on_vector2(input_vector, direction_vector):
    projectedVector = projection_on_vector(input_vector, direction_vector) if not np.array_equal(input_vector,
                                                                                                 o_vec3()) else o_vec3()
    residualVector = input_vector - projectedVector
    return projectedVector, residualVector


# R = axisR * residualR
def project_rotation(axis, r):
    axisR = exp(projection_on_vector(log_so3(r), seq_to_vec3(axis)))
    # axisR = cm.exp(projection_on_vector(cm.log(R), s2v(axis)))
    residualR = np.dot(axisR.T, r)
    return axisR, residualR


# R = residualR * axisR
def projectRotation2(axis, r):
    axisR = exp(projection_on_vector(log_so3(r), seq_to_vec3(axis)))
    # axisR = cm.exp(projection_on_vector(cm.log(R), s2v(axis)))
    residualR = np.dot(r, axisR.T)
    return axisR, residualR


# ===============================================================================
# list vector manipulation functions
# ===============================================================================
def v3_scale(v, scale):
    return [v[0] * scale, v[1] * scale, v[2] * scale]


def v3_add(v1, v2):
    return [v1[0] + v2[0], v1[1] + v2[1], v1[2] + v2[2]]


# ===============================================================================
# conversion functions
# ===============================================================================
def r_to_t(r):
    t = _I_SE3.copy()
    # A[0,0] is 2 times faster than A[0][0]
    t[0, 0] = r[0, 0]
    t[0, 1] = r[0, 1]
    t[0, 2] = r[0, 2]
    t[1, 0] = r[1, 0]
    t[1, 1] = r[1, 1]
    t[1, 2] = r[1, 2]
    t[2, 0] = r[2, 0]
    t[2, 1] = r[2, 1]
    t[2, 2] = r[2, 2]
    return t


def p_to_t(p):
    t = _I_SE3.copy()
    t[0, 3] = p[0]
    t[1, 3] = p[1]
    t[2, 3] = p[2]
    return t


def r_p_to_t(r, p):
    t = _I_SE3.copy()
    t[0, 0] = r[0, 0]
    t[0, 1] = r[0, 1]
    t[0, 2] = r[0, 2]
    t[0, 3] = p[0]
    t[1, 0] = r[1, 0]
    t[1, 1] = r[1, 1]
    t[1, 2] = r[1, 2]
    t[1, 3] = p[1]
    t[2, 0] = r[2, 0]
    t[2, 1] = r[2, 1]
    t[2, 2] = r[2, 2]
    t[2, 3] = p[2]
    return t


def t_to_p(t):
    p = _O_VEC3.copy()
    p[0] = t[0, 3]
    p[1] = t[1, 3]
    p[2] = t[2, 3]
    return p


def t_to_r(t):
    r = _I_SO3.copy()
    r[0, 0] = t[0, 0]
    r[0, 1] = t[0, 1]
    r[0, 2] = t[0, 2]
    r[1, 0] = t[1, 0]
    r[1, 1] = t[1, 1]
    r[1, 2] = t[1, 2]
    r[2, 0] = t[2, 0]
    r[2, 1] = t[2, 1]
    r[2, 2] = t[2, 2]
    return r


def p_to_rt(t):
    """
    :param t:
    :return: rotation matrix in SE3
    """
    rt = t.copy()
    rt[0, 3] = 0.0
    rt[1, 3] = 0.0
    rt[2, 3] = 0.0
    return rt


def t_to_r_p(t):
    r = _I_SO3.copy()
    p = _O_VEC3.copy()
    r[0, 0] = t[0, 0]
    r[0, 1] = t[0, 1]
    r[0, 2] = t[0, 2]
    p[0] = t[0, 3]
    r[1, 0] = t[1, 0]
    r[1, 1] = t[1, 1]
    r[1, 2] = t[1, 2]
    p[1] = t[1, 3]
    r[2, 0] = t[2, 0]
    r[2, 1] = t[2, 1]
    r[2, 2] = t[2, 2]
    p[2] = t[2, 3]
    return r, p


def r_to_zxy(r):
    """
    rotation SO3 to rotation angle z, x, y
    :param r: SO3
    :return: rotation angle z, x, y
    """
    return math.atan2(-r[0, 1], r[1, 1]),\
           math.atan2(r[2, 1], math.sqrt(r[0, 1] * r[0, 1] + r[1, 1] * r[1, 1])),\
           math.atan2(-r[2, 0], r[2, 2])


def seq_to_vec3(sequence):
    vec = _O_VEC3.copy()
    vec[0] = sequence[0]
    vec[1] = sequence[1]
    vec[2] = sequence[2]
    return vec


def seq_to_so3(nine_scalar_sequence):
    r = _I_SO3.copy()
    r[0, 0] = nine_scalar_sequence[0]
    r[0, 1] = nine_scalar_sequence[1]
    r[0, 2] = nine_scalar_sequence[2]
    r[1, 0] = nine_scalar_sequence[3]
    r[1, 1] = nine_scalar_sequence[4]
    r[1, 2] = nine_scalar_sequence[5]
    r[2, 0] = nine_scalar_sequence[6]
    r[2, 1] = nine_scalar_sequence[7]
    r[2, 2] = nine_scalar_sequence[8]
    return r



#        | T[0]    T[3]    T[6]    T[ 9] |
#        | T[1]    T[4]    T[7]    T[10] |
#        | T[2]    T[5]    T[8]    T[11] |
#    return vec3(atan2(T[1], T[0]), atan2(-T[2], sqrt(T[0] * T[0] + T[1] * T[1])), atan2(T[5], T[8]));
#
# def R2ZYX(R):
#    return v3(math.atan2(R[1,0], R[0,0]),
#              math.atan2(-R[2,0], math.sqrt(R[0,0]*R[0,0] + R[1,0]*R[1,0]) ),
#              math.atan2(R[2,1], R[2,2]) )
#
# def ZYX2R(euler):
#    ca = math.cos(euler[0]); sa = math.sin(euler[0]); cb = math.cos(euler[1]); sb = math.sin(euler[1]);
#    cg = math.cos(euler[2]); sg = math.sin(euler[2]);
#    outSO3 = _I_SO3()
#    outSO3[0][0] = ca * cb;
#    outSO3[1][0] = sa * cb;
#    outSO3[2][0] = -sb;
#    outSO3[0][1] = ca * sb * sg - sa * cg;
#    outSO3[1][1] = sa * sb * sg + ca * cg;
#    outSO3[2][1] = cb * sg;
#    outSO3[0][2] = ca * sb * cg + sa * sg;
#    outSO3[1][2] = sa * sb * cg - ca * sg;
#    outSO3[2][2] = cb * cg;
#    return outSO3


def get_cross_matrix_form(w):
    W = _O_SO3.copy()
    W[0, 1] = -w[2]
    W[1, 0] = w[2]
    W[0, 2] = w[1]
    W[2, 0] = -w[1]
    W[1, 2] = -w[0]
    W[2, 1] = w[0]
    return W


def matrix_rank(mat):
    return linalg.matrix_rank(mat)


def rot_x(theta):
    R = _I_SO3.copy()
    c = math.cos(theta)
    s = math.sin(theta)
    R[1, 1] = c
    R[1, 2] = -s
    R[2, 1] = s
    R[2, 2] = c
    return R


def rot_y(theta):
    R = _I_SO3.copy()
    c = math.cos(theta)
    s = math.sin(theta)
    R[0, 0] = c
    R[0, 2] = s
    R[2, 0] = -s
    R[2, 2] = c
    return R


def rot_z(theta):
    R = _I_SO3.copy()
    c = math.cos(theta)
    s = math.sin(theta)
    R[0, 0] = c
    R[0, 1] = -s
    R[1, 0] = s
    R[1, 1] = c
    return R


'''
if __name__ == '__main__':
    import psyco;

    psyco.full()
    import profile
    import os, time, copy
    import operator as op

    from fltk import *
    import sys

    if '..' not in sys.path:
        sys.path.append('..')
    import GUI.ysSimpleViewer as ysv
    import Util.ysGlHelper as ygh
    import Renderer.ysRenderer as yr


    def test_array_copy():
        I = np.identity(4, float)
        print('I', I)
        Icopy = I.copy()
        print('Icopy', Icopy)
        Iview = I.view()
        print('Iview', Iview)

        Icopy[0, 0] = 0
        print('Icopy', Icopy)
        print('I', I)

        Iview[0, 0] = 0
        print('Iview', Iview)
        print('I', I)

        print()

        I = np.identity(4, float)
        print('I', I)
        Ipythondeepcopy = copy.deepcopy(I)
        print('Ipythondeepcopy', Ipythondeepcopy)
        Ipythoncopy = copy.copy(I)
        print('Ipythoncopy', Ipythoncopy)

        Ipythondeepcopy[0, 0] = 0
        print('Ipythondeepcopy', Ipythondeepcopy)
        print('I', I)

        Ipythoncopy[0, 0] = 0
        print('Ipythoncopy', Ipythoncopy)
        print('I', I)


    def test_tupleSO3_funcs():
        #        A_tuple = (12,3,434,5643,564,213,43,5,13)
        #        B_tuple = (65,87,6457,345,78,74,534,245,87)
        #        A_numpy = ode_so3_to_so3(A_tuple)
        #        B_numpy = ode_so3_to_so3(B_tuple)
        A_numpy = exp((1, 0, 0), math.pi / 2.)
        B_numpy = exp((1, 0, 1), -0.2)
        A_tuple = numpy_so3_to_tuple_so3(A_numpy)
        B_tuple = numpy_so3_to_tuple_so3(B_numpy)

        print(A_tuple)
        print(A_numpy)

        print(dot_tuple_so3(A_tuple, B_tuple))
        print(np.dot(A_numpy, B_numpy))

        print(transpose_tuple_so3(A_tuple))
        print(A_np.transpose())

        print(log_so3(A_numpy))
        print(log_so3_tuple_so3(A_tuple))


    def test_getSO3FromVectors():
        vec1 = np.array([0, 0, 1])
        #        vec1 = np.array([0.0000000001,0,1])
        vec2 = np.array([0, 0, -1])

        R = get_so3_from_vectors(vec1, vec2)
        print(R)


    def test_logSO3():
        A = i_so3()
        B = exp((0, 1, 0), math.pi)
        print(log_so3(A))
        print(log_so3(B))


    def test_slerp():
        R1 = exp(v3(1.0, 0.0, 0.0), math.pi / 2)
        R2 = exp(v3(0.0, 1.0, 0.0), math.pi / 2)
        print(log_so3(R1), log_so3(R2))

        R = slerp(R1, R2, 0.1)
        print(log_so3(R))


    def test_projectRotation():
        orig_pol = [(1, 0, 0), (0, 0, 0), (0, 0, 1)]
        num = len(orig_pol)

        R = exp(v3(1, 1, 0), math.pi / 2)
        R_pol = list(map(np.dot, [R] * num, orig_pol))

        # R = Rv * Rp
        v_axis = (0, 1, 0)
        Rv = exp(projection_on_vector(log_so3(R), s2v(v_axis)))
        Rv_pol = list(map(np.dot, [Rv] * num, orig_pol))
        Rp = np.dot(Rv.T, R)
        Rp_pol = list(map(np.dot, [Rp] * num, orig_pol))
        Rv_dot_Rp_pol = list(map(np.dot, [np.dot(Rv, Rp)] * num, orig_pol))

        # R = Rv * Rp
        Rv2, Rp2 = project_rotation(v_axis, R)
        Rv_pol2 = list(map(np.dot, [Rv2] * num, orig_pol))
        Rp_pol2 = list(map(np.dot, [Rp2] * num, orig_pol))
        Rv_dot_Rp_pol2 = list(map(np.dot, [np.dot(Rv2, Rp2)] * num, orig_pol))

        viewer = ysv.SimpleViewer()
        viewer.record(False)
        #        viewer.doc.addRenderer('orig_pol', yr.PolygonRenderer(orig_pol, (255,0,0)))
        viewer.doc.addRenderer('R_pol', yr.PolygonRenderer(R_pol, (0, 0, 255)))
        #        viewer.doc.addRenderer('Rv_pol', yr.PolygonRenderer(Rv_pol, (100,100,0)))
        #        viewer.doc.addRenderer('Rp_pol', yr.PolygonRenderer(Rp_pol, (0,100,100)))
        viewer.doc.addRenderer('Rv_dot_Rp_pol', yr.PolygonRenderer(Rv_dot_Rp_pol, (0, 255, 0)))
        #        viewer.doc.addRenderer('Rv_pol2', yr.PolygonRenderer(Rv_pol2, (100,100,0)))
        #        viewer.doc.addRenderer('Rp_pol2', yr.PolygonRenderer(Rp_pol2, (0,100,100)))
        viewer.doc.addRenderer('Rv_dot_Rp_pol2', yr.PolygonRenderer(Rv_dot_Rp_pol2, (255, 255, 255)))

        viewer.startTimer(1 / 30.)
        viewer.show()

        Fl.run()


    def test_diff_orientation():
        points = [(0, 0, -.1), (0, 0, .1), (2, 0, .1), (2, 0, -.1)]

        Ra = exp(v3(0, 1, 1), 1)
        Rb = exp(v3(1, 0, 0), 1)

        # Ra - Rb
        diffVec1 = log_so3(Ra) - log_so3(Rb)
        diffVec2_1 = log_so3(np.dot(Ra, np.transpose(Rb)))
        diffVec2_2 = log_so3(np.dot(np.transpose(Rb), Ra))
        diffVec2_3 = log_so3(np.dot(Rb, np.transpose(Ra)))
        diffVec2_4 = log_so3(np.dot(np.transpose(Ra), Rb))

        print(diffVec1)
        print(diffVec2_1)
        print(diffVec2_2)
        print(diffVec2_3)
        print(diffVec2_4)

        viewer = ysv.SimpleViewer()
        viewer.record(False)
        viewer.doc.addRenderer('I', yr.PolygonRenderer(points, (255, 255, 255)))
        viewer.doc.addRenderer('Ra', yr.PolygonRenderer(list(map(np.dot, [Ra] * len(points), points)), (255, 0, 0)))
        viewer.doc.addRenderer('Rb', yr.PolygonRenderer(list(map(np.dot, [Rb] * len(points), points)), (0, 0, 255)))

        viewer.startTimer(1 / 30.)
        viewer.show()

        Fl.run()


    def test_matrixrank():
        A = np.array([[0., 0., 1., 0., 0., 0.5],
                      [0., 0., 0., 0., 0., 0.],
                      [-1., 0., 0., -0.5, 0., 0.],
                      [1., 0., 0., 1., 0., 0.],
                      [0., 1., 0., 0., 1., 0.],
                      [0., 0., 1., 0., 0., 1.]])
        print(matrix_rank(A))


    pass
    #    test_array_copy()
    #    test_tupleSO3_funcs()
    #    test_getSO3FromVectors()
    #    test_logSO3()
    #    test_slerp()
    test_projectRotation()
# test_diff_orientation()
#    test_matrixrank()
'''
