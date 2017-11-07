import numpy as np

import hmath.mm_math as mm
import motion.motion as motion


# if parent_joint_axis is None: assume 3dof parent joint
# if not: use parent_joint_axis as rotV
# parent_joint_axis is a local direction
def ik_analytic(posture: motion.JointPosture, joint_name_or_index, new_position, parent_joint_axis=None):
    skeleton = posture.get_skeleton()
    if isinstance(joint_name_or_index, int):
        joint_index = joint_name_or_index
    else:
        joint_index = skeleton.get_index_by_label(joint_name_or_index)

    joint_parent_index = skeleton.get_parent_index_at(joint_index)
    joint_grand_parent_index = skeleton.get_parent_index_at(joint_parent_index)

    B = posture.get_global_p(joint_index)
    C = posture.get_global_p(joint_parent_index)
    A = posture.get_global_p(joint_grand_parent_index)

    L = B - A
    N = B - C
    M = C - A

    l = mm.length(L)
    n = mm.length(N)
    m = mm.length(M)

    a = mm.acos((l*l + n*n - m*m) / (2*l*n))
    b = mm.acos((l*l + m*m - n*n) / (2*l*m))

    B_new = new_position
    L_new = B_new - A

    l_ = mm.length(L_new)

    a_ = mm.acos((l_*l_ + n*n - m*m) / (2*l_*n))
    b_ = mm.acos((l_*l_ + m*m - n*n) / (2*l_*m))

    # rotate joint in plane
    if parent_joint_axis is not None:
        rotV = np.dot(posture.get_global_r(joint_parent_index), mm.normalize(parent_joint_axis))
    else:
        rotV = mm.normalize(np.cross(M, L))
    if mm.length(rotV) <= 1e-9:
        z_axis = np.array([0, 0, 1], float)
        rotV = np.dot(posture.get_global_r(joint_parent_index), z_axis)
        print("mm_analytic_ik.py: ik_analytic: length of rotV is 0. check the orientations of results of ik")
    rotb = b - b_
    rota = a_ - a - rotb
#    posture.mulJointOrientationGlobal(joint_parent_parent, mm.exp(rotV, rotb))
#    posture.mulJointOrientationGlobal(joint_parent, mm.exp(rotV * rota))
    posture.set_local_r(joint_grand_parent_index,
                        np.dot(posture.get_local_r(joint_grand_parent_index), mm.so3_to_se3(mm.exp(rotV, rotb))))
    posture.set_local_r(joint_parent_index,
                        np.dot(posture.get_local_r(joint_parent_index), mm.so3_to_se3(mm.exp(rotV * rota))))


    # rotate plane
    rotV2 = mm.normalize(np.cross(L, L_new))
    l_new = mm.length(L_new)
    l_diff = mm.length(L_new - L)
    rot2 = mm.acos((l_new * l_new + l * l - l_diff * l_diff) / (2 * l_new * l))
#    posture.mulJointOrientationGlobal(joint_parent_parent, mm.exp(rotV2, rot2))
    posture.set_local_r(joint_grand_parent_index,
                        np.dot(posture.get_local_r(joint_grand_parent_index), mm.so3_to_se3(mm.exp(rotV2, rot2))))

    return posture
