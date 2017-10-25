import numpy, math

import sys

if '..' not in sys.path:
    sys.path.append('..')
import Math.mm_math as mm
import Math.cs_math as cm
import Motion.ys_motion as ym

ROOT_NAME = "root"


# ===============================================================================
# .mm file
# ===============================================================================
def read_m_m_file(mm_file_path):
    names = {}
    names[0] = 'root'
    names[2] = 'lKnee'
    names[4] = 'neck'
    names[6] = 'rKnee'
    names[8] = 'rFoot'
    names[10] = 'rToe'
    names[12] = 'head'
    names[14] = 'rArm'
    names[16] = 'lArm'
    names[18] = 'lHand'
    names[20] = 'rHand'
    #    names[14] = 'lArm'
    #    names[16] = 'rArm'
    #    names[18] = 'rHand'
    #    names[20] = 'lHand'
    names[22] = 'lFoot'
    names[24] = 'lToe'

    skeleton = ym.MMSkeleton()
    skeleton.add_link("head", "neck")
    skeleton.add_link("neck", "lArm")
    skeleton.add_link("lArm", "lHand")
    skeleton.add_link("neck", "rArm")
    skeleton.add_link("rArm", "rHand")
    skeleton.add_link("neck", "root")
    skeleton.add_link("root", "lKnee")
    skeleton.add_link("lKnee", "lFoot")
    skeleton.add_link("lFoot", "lToe")
    skeleton.add_link("root", "rKnee")
    skeleton.add_link("rKnee", "rFoot")
    skeleton.add_link("rFoot", "rToe")

    #    # lowest foot height finding code
    #    lowest = 100
    #    for mm_file_path in paths:
    #        point_motion = yf.read_m_m_file(mm_file_path)
    #        i = 0
    #        for name, point in point_motion[i].point_map.items():
    #            if name == 'rFoot' or name == 'lFoot' or name == 'rToe' or name == 'lToe':
    #                if point[1] < lowest:
    #                    print mm_file_path, i
    #                    print name
    #                    print point[1]
    #                    lowest = point[1]
    lowest = .15

    f = open(mm_file_path)
    file_lines = f.readlines()
    point_motion = ym.Motion()
    i = 0
    while i != len(file_lines):
        if file_lines[i].isspace() == False:
            splited = file_lines[i].split()
            point_posture = ym.MMPosture(skeleton)
            for j in range(0, len(splited), 2):
                point = numpy.array([float(splited[j]), float(splited[j + 1]), 0.])
                point[1] -= lowest
                point_posture.add_point(names[j], point)
            point_motion.append(point_posture)
        i += 1

    f.close()
    point_motion.fps = 30.
    return point_motion


# ===============================================================================
# .trc file
# ===============================================================================
def read_trc_file(trc_file_path, scale=1.0):
    f = open(trc_file_path)
    file_lines = f.readlines()
    point_motion = ym.Motion()
    i = 0
    while i != len(file_lines):
        splited = file_lines[i].split()
        bone_names = []
        if i == 2:
            data_rate = float(splited[0])
            num_frames = int(splited[2])
            num_markers = int(splited[3])
        # print num_frames, num_markers
        elif i == 3:
            marker_names = [name.split(':')[1] for name in splited[2:]]
            skeleton = ym.PointSkeleton()
            for name in marker_names:
                skeleton.add_element(None, name)
                #            print marker_names
        elif i > 5:
            marker_positions = splited[2:]
            #            print marker_positions
            #            print 'i', i
            point_posture = ym.PointPosture(skeleton)
            for m in range(num_markers):
                point = numpy.array([float(marker_positions[m * 3]), float(marker_positions[m * 3 + 1]),
                                     float(marker_positions[m * 3 + 2])])
                point = numpy.dot(mm.exp(numpy.array([1, 0, 0]), -math.pi / 2.), point) * scale
                #                point_posture.add_point(marker_names[m], point)
                point_posture.set_position(m, point)
            # print 'm', m
            #                print marker_names[m], (marker_positions[m*3],markerPositions[m*3+1],markerPositions[m*3+2])
            point_motion.append(point_posture)
        i += 1
    f.close()
    point_motion.fps = data_rate
    return point_motion


pass


# ===============================================================================
# .bvh file
# ===============================================================================
def read_bvh_file(bvh_file_path, scale=1.0, apply_root_offset=False):
    bvh = Bvh()
    bvh.parse_bvh_file(bvh_file_path)
    joint_motion = bvh.to_joint_motion(scale, apply_root_offset)
    return joint_motion


def read_bvh_file_as_bvh(bvh_file_path):
    bvh = Bvh()
    bvh.parse_bvh_file(bvh_file_path)
    return bvh


def write_bvh_file(bvh_file_path, joint_motion):
    bvh = Bvh()
    bvh.from_joint_motion(joint_motion)
    bvh.write_bvh_file(bvh_file_path)


class Bvh:
    channel_types6dof = ['XPOSITION', 'YPOSITION', 'ZPOSITION', 'ZROTATION', 'XROTATION', 'YROTATION']
    channel_types3dof = ['ZROTATION', 'XROTATION', 'YROTATION']

    class Joint:
        def __init__(self, name):
            self.name = name
            self.offset = None
            self.channels = []
            self.children = []

        def __strHierarchy__(self, depth=0):
            s = ''
            tab1 = '  ' * depth
            tab2 = '  ' * (depth + 1)
            s += '%sJOINT %s\n' % (tab1, self.name)
            s += '%s{\n' % tab1
            s += '%sOFFSET %s\n' % (tab2, self.offset)

            channel_string = ''
            for channel in self.channels:
                channel_string += channel.__str__() + ' '
            s += '%sCHANNELS %s\n' % (tab2, channel_string)

            for child in self.children:
                s += child.__strHierarchy__(depth + 1)
            s += '%s}\n' % tab1
            return s

    class Channel:
        def __init__(self, channel_type, channel_index):
            self.channel_type = channel_type
            self.channel_index = channel_index

        def __str__(self):
            return self.channel_type

    def __init__(self):
        self.joints = []
        self.frame_num = 0
        self.frame_time = 0
        self.motion_list = []

        self.total_channel_count = 0

    def __str__(self):
        s = 'HIERARCHY\n'
        s += self.joints[0].__strHierarchy__()
        s += 'MOTION\n'
        s += 'Frame: %d\n' % self.frame_num
        s += 'Frame Time: %f\n' % self.frame_time
        #        for i in range(len(self.motion_list)):
        #            s += self.motion_list[i].__str__() + '\n'
        return s

    # ===========================================================================
    # read functions
    # ===========================================================================
    def parse_bvh_file(self, filepath_or_fileobject):
        if isinstance(filepath_or_fileobject, str):
            file = open(filepath_or_fileobject)
        else:
            file = filepath_or_fileobject

        tokens = file.read().split()
        tokens.reverse()

        self.total_channel_count = 0
        self.parse_bvh_hierachy(tokens)
        self.parse_bvh_motion(tokens)

        if isinstance(filepath_or_fileobject, str): file.close()

    def parse_bvh_hierachy(self, tokens):
        if tokens.pop().upper() != "HIERARCHY":
            print("HIERARCHY missing")
            return
        if tokens.pop().upper() != "ROOT":
            print("ROOT missing")
            return
        self.parse_bvh_joint(tokens.pop(), tokens)

    def parse_bvh_joint(self, name, tokens):
        bvh_joint = Bvh.Joint(name)
        self.joints.append(bvh_joint)

        if tokens.pop() != "{":
            print("'{' missing")
            return None

        end_detected = False
        while not end_detected:
            t = tokens.pop().upper()
            if t == '}':
                end_detected = True
            elif t == 'OFFSET':
                x = float(tokens.pop())
                y = float(tokens.pop())
                z = float(tokens.pop())
                bvh_joint.offset = numpy.array([x, y, z], float)
            elif t == 'CHANNELS':
                channel_count = int(tokens.pop())
                for i in range(channel_count):
                    channel_type = tokens.pop().upper()
                    bvh_joint.channels.append(Bvh.Channel(channel_type, self.total_channel_count))
                    self.total_channel_count += 1
            elif t == 'JOINT':
                bvh_joint.children.append(self.parse_bvh_joint(tokens.pop(), tokens))
            elif t == 'END':
                next = tokens.pop().upper()
                if next != 'SITE':
                    print('END', next, 'is unknown keyword')
                bvh_joint.children.append(self.parse_bvh_joint("%s_Effector" % name, tokens))
            else:
                print("invalid bvh_joint definition")
                return None
        return bvh_joint

    def parse_bvh_motion(self, tokens):
        if tokens.pop().upper() != 'MOTION':
            print("MOTION missing")
            return None
        if tokens.pop().upper() != 'FRAMES:':
            print("FRAMES: missing")
            return None
        self.frame_num = int(tokens.pop())
        if tokens.pop().upper() != 'FRAME TIME:':
            if tokens.pop().upper() != 'TIME:':
                print("FRAME TIME: missing")
                return None
        self.frame_time = float(tokens.pop())

        self.motion_list = [None] * self.frame_num
        for i in range(self.frame_num):
            self.motion_list[i] = [None] * self.total_channel_count

        for i in range(self.frame_num):
            for j in range(self.total_channel_count):
                self.motion_list[i][j] = float(tokens.pop())

    # ===========================================================================
    # write functions
    # ===========================================================================
    def write_bvh_file(self, filepath_or_fileobject):
        if isinstance(filepath_or_fileobject, str):
            file = open(filepath_or_fileobject, 'w')
        else:
            file = filepath_or_fileobject

        self.write_bvh_hierarchy(file)
        self.write_bvh_motion(file)

        if isinstance(filepath_or_fileobject, str): file.close()

    def write_bvh_hierarchy(self, file):
        file.write('HIERARCHY\n')
        self.write_bvh_joint(file, self.joints[0], 0)

    def write_bvh_joint(self, file, joint, depth):
        indent_joint = '  ' * depth
        indent_offset = '  ' * (depth + 1)

        if len(joint.children) > 0:
            endsite = False
        else:
            endsite = True

        # JOINT
        if not endsite:
            if depth == 0:
                joint_label = 'ROOT'
            else:
                joint_label = 'JOINT'
            file.write('%s%s %s\n' % (indent_joint, joint_label, joint.name))
        else:
            file.write('%sEnd Site\n' % indent_joint)
        file.write('%s{\n' % indent_joint)

        # OFFSET
        file.write('%sOFFSET %s %s %s\n' % (indent_offset, joint.offset[0], joint.offset[1], joint.offset[2]))

        if not endsite:
            # CHANNELS
            channel_string = ''
            for channel in joint.channels:
                channel_string += channel.__str__() + ' '
            file.write('%sCHANNELS %d %s\n' % (indent_offset, len(joint.channels), channel_string))

            # children
            for child in joint.children:
                self.write_bvh_joint(file, child, depth + 1)

        # end JOINT
        file.write('%s}\n' % indent_joint)

    def write_bvh_motion(self, file):
        file.write('MOTION\n')
        file.write('Frames: %d\n' % self.frame_num)
        file.write('Frame Time: %f\n' % self.frame_time)

        for i in range(self.frame_num):
            for j in range(self.total_channel_count):
                file.write('%s ' % self.motion_list[i][j])
            file.write('\n')

    # ===========================================================================
    # Bvh -> JointMotion
    # ===========================================================================
    def to_joint_motion(self, scale, apply_root_offset):
        skeleton = self.to_joint_skeleton(scale, apply_root_offset)

        joint_motion = ym.JointMotion()
        for i in range(len(self.motion_list)):
            joint_posture = ym.JointPosture(skeleton)
            self.add_joint_s_o3_from_bvh_joint(joint_posture, self.joints[0], self.motion_list[i], scale)
            joint_posture.update_global_t()
            joint_motion.append(joint_posture)

        joint_motion.fps = 1. / self.frame_time
        return joint_motion

    def to_joint_skeleton(self, scale, apply_root_offset):
        # build joint hierarchy
        joint_map = {}
        root = self.add_joint_from_bvh_joint(joint_map, self.joints[0].name, self.joints[0], None, scale,
                                             apply_root_offset)

        # build joint array
        skeleton = ym.JointSkeleton(root)
        for bvh_joint in self.joints:
            skeleton.add_element(joint_map[bvh_joint.name], bvh_joint.name)
        skeleton.root_index = skeleton.get_element_index(root.name)

        # initialize
        skeleton.initialize()

        return skeleton

    def add_joint_from_bvh_joint(self, joint_map, joint_name, bvh_joint, parent_joint, scale, apply_offset):
        joint = ym.Joint(joint_name, parent_joint)
        if apply_offset:
            joint.offset = bvh_joint.offset * scale
        joint_map[joint_name] = joint

        for i in range(len(bvh_joint.children)):
            child = self.add_joint_from_bvh_joint(joint_map, bvh_joint.children[i].name, bvh_joint.children[i], joint,
                                                  scale, True)
            joint.children.append(child)

        return joint

    def add_joint_s_o3_from_bvh_joint(self, joint_posture, bvh_joint, channel_values, scale=1.0):
        local_r = mm.i_so3()
        for channel in bvh_joint.channels:
            if channel.channel_type == 'XPOSITION':
                joint_posture.root_pos[0] = channel_values[channel.channel_index] * scale
            elif channel.channel_type == 'YPOSITION':
                joint_posture.root_pos[1] = channel_values[channel.channel_index] * scale
            elif channel.channel_type == 'ZPOSITION':
                joint_posture.root_pos[2] = channel_values[channel.channel_index] * scale
            elif channel.channel_type == 'XROTATION':
                local_r = numpy.dot(local_r, mm.rot_x(mm.RAD * channel_values[channel.channel_index]))
            elif channel.channel_type == 'YROTATION':
                local_r = numpy.dot(local_r, mm.rot_y(mm.RAD * channel_values[channel.channel_index]))
            elif channel.channel_type == 'ZROTATION':
                local_r = numpy.dot(local_r, mm.rot_z(mm.RAD * channel_values[channel.channel_index]))
        joint_posture.set_local_r(joint_posture.skeleton.get_element_index(bvh_joint.name), local_r)

        for i in range(len(bvh_joint.children)):
            self.add_joint_s_o3_from_bvh_joint(joint_posture, bvh_joint.children[i], channel_values)

    # ===========================================================================
    # JointMotion -> Bvh
    # ===========================================================================
    def from_joint_motion(self, joint_motion):
        skeleton = joint_motion[0].skeleton
        self.from_joint_skeleton(skeleton)

        self.frame_num = len(joint_motion)
        self.motion_list = [[None] * self.total_channel_count for i in range(self.frame_num)]
        for i in range(self.frame_num):
            self._jointValue2channelValues(joint_motion[i], self.motion_list[i], skeleton, self.joints[0])

        self.frame_time = 1. / joint_motion.fps

    def from_joint_skeleton(self, joint_skeleton):
        # build bvh joint hierarchy
        bvh_joint_dict = {}
        self.total_channel_count = 0
        bvh_root = self._Joint2BvhJoint(joint_skeleton.get_element(0), bvh_joint_dict)

        # build bvh joint array
        self.joints = [None] * joint_skeleton.get_element_num()
        for i in range(joint_skeleton.get_element_num()):
            self.joints[i] = bvh_joint_dict[joint_skeleton.get_element_name(i)]

    def _Joint2BvhJoint(self, joint, bvh_joint_dict):
        bvh_joint = Bvh.Joint(joint.name)  # name
        bvh_joint_dict[joint.name] = bvh_joint

        bvh_joint.offset = joint.offset  # offset

        # channels
        if joint.parent is None:
            channel_types = Bvh.channel_types6dof
        elif len(joint.children) == 0:
            channel_types = []
        else:
            channel_types = Bvh.channel_types3dof
        for channel_type in channel_types:
            bvh_joint.channels.append(Bvh.Channel(channel_type, self.total_channel_count))
            self.total_channel_count += 1

        # children
        for child in joint.children:
            bvh_joint.children.append(self._Joint2BvhJoint(child, bvh_joint_dict))

        return bvh_joint

    # joint_posture : input
    # channel_values : output
    def _jointValue2channelValues(self, joint_posture, channel_values, joint_skeleton, bvh_joint):
        joint_index = joint_skeleton.get_element_index(bvh_joint.name)
        zrot, xrot, yrot = cm.R2zxy_r(joint_posture.get_local_r(joint_index))

        for channel in bvh_joint.channels:
            if channel.channel_type == 'XPOSITION':
                channel_values[channel.channel_index] = joint_posture.root_pos[0]
            elif channel.channel_type == 'YPOSITION':
                channel_values[channel.channel_index] = joint_posture.root_pos[1]
            elif channel.channel_type == 'ZPOSITION':
                channel_values[channel.channel_index] = joint_posture.root_pos[2]
            elif channel.channel_type == 'XROTATION':
                channel_values[channel.channel_index] = xrot * mm.DEG
            elif channel.channel_type == 'YROTATION':
                channel_values[channel.channel_index] = yrot * mm.DEG
            elif channel.channel_type == 'ZROTATION':
                channel_values[channel.channel_index] = zrot * mm.DEG

        for child in bvh_joint.children:
            self._jointValue2channelValues(joint_posture, channel_values, joint_skeleton, child)


if __name__ == "__main__":
    #    import psyco; psyco.full()
    import time
    import c_profile, os
    from datetime import datetime
    from fltk import *
    import GUI.ys_simple_viewer as ysv
    import Renderer.ys_renderer as yr


    def test_readTrcFile():
        trc_motion = read_trc_file('../samples/Day7_Session2_Take01_-_walk.trc', .01)
        print(trc_motion[0].skeleton)

        viewer = ysv.SimpleViewer()
        viewer.record(False)
        viewer.doc.add_renderer('trcMotion', yr.PointMotionRenderer(trc_motion, (0, 255, 0)))
        viewer.doc.add_object('trcMotion', trc_motion)

        viewer.start_timer(1 / trc_motion.fps)
        viewer.show()

        Fl.run()


    def test_parseBvhFile():
        bvh_file_path = '../samples/wd2_WalkSameSame00.bvh'
        bvh = Bvh()
        bvh.parse_bvh_file(bvh_file_path)
        print(bvh)


    def test_readBvhFile():
        #        bvh_file_path = '../samples/wd2_WalkSameSame00.bvh'
        #        ys_motion = read_bvh_file(bvh_file_path, .01)
        #        motion2 = read_bvh_file(bvh_file_path, .01, True)
        bvh_file_path = '../../../Walking/ppmotion/wd2_WalkForwardNormal00.bvh'
        bvh_file_path2 = '../../../Walking/adun/adun.bvh'
        motion = read_bvh_file(bvh_file_path, 1)
        motion2 = read_bvh_file(bvh_file_path2, 1)
        print(motion[0].skeleton)
        print(motion2[0].skeleton)

        viewer = ysv.SimpleViewer()
        viewer.record(False)
        viewer.doc.add_renderer('ys_motion', yr.JointMotionRenderer(motion, (0, 255, 0)))
        viewer.doc.add_object('ys_motion', motion)
        viewer.doc.add_renderer('motion2', yr.JointMotionRenderer(motion2, (255, 0, 0)))
        viewer.doc.add_object('motion2', motion2)

        viewer.start_timer(1 / motion.fps)
        viewer.show()

        Fl.run()


    def test_writeBvhFile():
        #        # bvh
        #        bvh_file_path = '../samples/wd2_WalkSameSame00.bvh'
        #        bvh = read_bvh_file_as_bvh(bvh_file_path)
        #
        #        temp_file_path = '../samples/bvh_wd2_WalkSameSame00.bvh.temp'
        #        bvh.write_bvh_file(temp_file_path)

        # ys_motion
        bvh_file_path = '../samples/wd2_WalkSameSame00.bvh'
        motion = read_bvh_file(bvh_file_path, .01)
        #        ys_motion[0] = ys_motion[0].get_t_pose()

        temp_file_path = '../samples/motion_temp_wd2_WalkSameSame00.bvh.temp'
        write_bvh_file(temp_file_path, motion)
        motion2 = read_bvh_file(temp_file_path)
        #        motion2[0] = motion2[0].get_t_pose()

        viewer = ysv.SimpleViewer()
        viewer.record(False)
        viewer.doc.add_renderer('ys_motion', yr.JointMotionRenderer(motion, (0, 255, 0)))
        viewer.doc.add_object('ys_motion', motion)
        viewer.doc.add_renderer('motion2', yr.JointMotionRenderer(motion2, (255, 0, 0)))
        viewer.doc.add_object('motion2', motion2)

        viewer.start_timer(1 / motion.fps)
        viewer.show()

        Fl.run()


    def profile_readBvhFile():
        bvh_file_path = '../samples/wd2_WalkSameSame00.bvh'

        profile_data_file = '../samples/cProfile_%s.profile' % datetime.today().strftime('%y%m%d_%H%M%S')
        c_profile.runctx('ys_motion = read_bvh_file(bvh_file_path)', globals(), locals(), profile_data_file)
        os.system('python ../../Tools/pprofui.py %s' % profile_data_file)


    pass

    #    test_readTrcFile()
    #    test_parseBvhFile()
    test_readBvhFile()
# test_writeBvhFile()
#    profile_readBvhFile()
