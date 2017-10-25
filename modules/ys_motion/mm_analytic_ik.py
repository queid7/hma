''' analytic ik module by mmkim'''
import numpy as np

import sys
if '..' not in sys.path:
    sys.path.append('..')

import hmath.mm_math as mm


# if parent_joint_axis is None: assume 3dof parent joint
# if not: use parent_joint_axis as rotV
# parent_joint_axis is a local direction
def ik_analytic(posture, joint_name_or_index, new_position, parent_joint_axis=None):
    if isinstance(joint_name_or_index, int):
        joint = joint_name_or_index
    else:
        joint = posture.skeleton.getJointIndex(joint_name_or_index)

    joint_parent = posture.skeleton.getParentJointIndex(joint)
    joint_parent_parent = posture.skeleton.getParentJointIndex(joint_parent)

    B = posture.getJointPositionGlobal(joint)
    C = posture.getJointPositionGlobal(joint_parent)
    A = posture.getJointPositionGlobal(joint_parent_parent)

    L = B - A
    N = B - C
    M = C - A

    l = mm.length(L)
    n = mm.length(N)
    m = mm.length(M)

    a = mm.ACOS((l*l + n*n - m*m) / (2*l*n))
    b = mm.ACOS((l*l + m*m - n*n) / (2*l*m))

    B_new = new_position
    L_new = B_new - A

    l_ = mm.length(L_new)

    a_ = mm.ACOS((l_*l_ + n*n - m*m) / (2*l_*n))
    b_ = mm.ACOS((l_*l_ + m*m - n*n) / (2*l_*m))

    # rotate joint in plane 
    rotV = mm.normalize2(np.cross(M, L))
    if parent_joint_axis is not None:
        rotV = np.dot(posture.getJointOrientationGlobal(joint_parent), mm.normalize(parent_joint_axis))
        print(mm.length(rotV))
    if mm.length(rotV) <= 1e-9:
        z_axis = np.array([0, 0, 1], float)
        rotV = np.dot(posture.getJointOrientationGlobal(joint_parent), z_axis)
        print("mm_analytic_ik.py: ik_analytic: length of rotV is 0. check the orientations of results of ik")
    rotb = b - b_
    rota = a_ - a - rotb
    posture.mulJointOrientationGlobal(joint_parent_parent, mm.exp(rotV, rotb))
    posture.mulJointOrientationGlobal(joint_parent, mm.exp(rotV * rota))

    # rotate plane
    rotV2 = mm.normalize2(np.cross(L, L_new))
    l_new = mm.length(L_new)
    l_diff = mm.length(L_new - L)
    rot2 = mm.ACOS((l_new * l_new + l * l - l_diff * l_diff) / (2 * l_new * l))
    posture.mulJointOrientationGlobal(joint_parent_parent, mm.exp(rotV2, rot2))

    return posture


if __name__ == '__main__':
    from fltk import *
    import copy
    import Resource.ysMotionLoader as yf
    import GUI.ysSimpleViewer as ysv
    import Renderer.ysRenderer as yr
    
    def test_ik_analytic():
        bvhFilePath = '../samples/wd2_WalkSameSame00.bvh'
        jointMotion = yf.readBvhFile(bvhFilePath, .01)

        ik_target = [(0, .3, -.3)]
        
        jointMotion2 = copy.deepcopy(jointMotion)
        for i in range(len(jointMotion2)):
            ik_analytic(jointMotion2[i], 'LeftFoot', ik_target[0])
        
        viewer = ysv.SimpleViewer()
        viewer.record(False)
        viewer.doc.addRenderer('jointMotion', yr.JointMotionRenderer(jointMotion, (0,150,255)))
        viewer.doc.addObject('jointMotion', jointMotion)
        viewer.doc.addRenderer('jointMotion2', yr.JointMotionRenderer(jointMotion2, (0,255,0)))
        viewer.doc.addObject('jointMotion2', jointMotion2)
        viewer.doc.addRenderer('ik_target', yr.PointsRenderer(ik_target, (255,0,0)))

        viewer.startTimer(1/30.)
        viewer.show()
        Fl.run()
        
        pass        

    test_ik_analytic()
