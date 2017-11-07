import numpy

import hmath.mm_math as mm
import motion.motion as motion


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
    """
    A Bvh class stores a joint hierarchy and animation data read from a bvh file.

    A joint hierarchy is a kind of tree composed of joint nodes.
    Each joint node has a relative translation information to its parent node.

    Animation data comprise root translation data and joint rotation data per frame
    The rotation data of the joint determines the order of the global rotation transformation.
    ex) z, x, y in bvf file -> global coordinates = (parent's transformation) (z) (x) (y) local coordinates
    """
    CHANNEL_6DOF = ['XPOSITION', 'YPOSITION', 'ZPOSITION', 'ZROTATION', 'XROTATION', 'YROTATION']
    CHANNEL_3DOF = ['ZROTATION', 'XROTATION', 'YROTATION']

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
        self.parse_bvh_hierarchy(tokens)
        self.parse_bvh_motion(tokens)

        if isinstance(filepath_or_fileobject, str):
            file.close()

    def parse_bvh_hierarchy(self, tokens):
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
                next_ = tokens.pop().upper()
                if next_ != 'SITE':
                    print('END', next_, 'is unknown keyword')
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

        if isinstance(filepath_or_fileobject, str):
            file.close()

    def write_bvh_hierarchy(self, file):
        file.write('HIERARCHY\n')
        self.write_bvh_joint(file, self.joints[0], 0)

    def write_bvh_joint(self, file, joint, depth):
        indent_joint = '  ' * depth
        indent_offset = '  ' * (depth + 1)

        if len(joint.children) > 0:
            end_site = False
        else:
            end_site = True

        # JOINT
        if not end_site:
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

        if not end_site:
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
    def to_joint_motion(self, scale=1.0, apply_root_offset=False):
        skeleton = self.to_joint_skeleton(scale, apply_root_offset)

        joint_motion = motion.JointMotion()
        for i in range(len(self.motion_list)):
            joint_posture = motion.JointPosture(skeleton)
            self._set_local_r_from_bvh_joint(joint_posture, self.joints[0], self.motion_list[i], scale)
            joint_posture.update_global_ts()
            joint_motion.append(joint_posture)

        joint_motion.fps = 1. / self.frame_time
        return joint_motion

    def to_joint_skeleton(self, scale=1.0, apply_root_offset=False):
        skeleton = motion.Skeleton()
        self._add_joint_from_bvh_joint(skeleton, self.joints[0].name, self.joints[0], None, scale, apply_root_offset)

        return skeleton

    def _add_joint_from_bvh_joint(self, skeleton, joint_name, bvh_joint, parent_joint, scale, apply_offset):
        joint = motion.JointNode(joint_name)
        if apply_offset:
            joint.set_translation(bvh_joint.offset * scale)
        if parent_joint is None:
            skeleton.set_root(joint)
        else:
            skeleton.add_node(joint, parent_joint)

        for i in range(len(bvh_joint.children)):
            self._add_joint_from_bvh_joint(skeleton, bvh_joint.children[i].name, bvh_joint.children[i], joint, scale,
                                           True)

    def _set_local_r_from_bvh_joint(self, joint_posture, bvh_joint, channel_values, scale=1.0):
        local_r = mm.i_se3()
        for channel in bvh_joint.channels:
            if channel.channel_type == 'XPOSITION':
                joint_posture.get_root_position()[0] = channel_values[channel.channel_index] * scale
            elif channel.channel_type == 'YPOSITION':
                joint_posture.get_root_position()[1] = channel_values[channel.channel_index] * scale
            elif channel.channel_type == 'ZPOSITION':
                joint_posture.get_root_position()[2] = channel_values[channel.channel_index] * scale
            elif channel.channel_type == 'XROTATION':
                local_r = numpy.dot(local_r, mm.so3_to_se3(mm.rot_x(mm.RAD * channel_values[channel.channel_index]),
                                                           mm.o_vec3()))
            elif channel.channel_type == 'YROTATION':
                local_r = numpy.dot(local_r, mm.so3_to_se3(mm.rot_y(mm.RAD * channel_values[channel.channel_index]),
                                                           mm.o_vec3()))
            elif channel.channel_type == 'ZROTATION':
                local_r = numpy.dot(local_r, mm.so3_to_se3(mm.rot_z(mm.RAD * channel_values[channel.channel_index]),
                                                           mm.o_vec3()))

        joint_posture.set_local_r_without_update(joint_posture.get_skeleton().get_index_by_label(bvh_joint.name), local_r)

        for child in bvh_joint.children:
            self._set_local_r_from_bvh_joint(joint_posture, child, channel_values)


    # ===========================================================================
    # JointMotion -> Bvh
    # ===========================================================================
    def from_joint_motion(self, joint_motion):
        skeleton = joint_motion.get_skeleton()
        self._from_joint_skeleton(skeleton)

        self.frame_num = len(joint_motion)
        self.motion_list = [[None] * self.total_channel_count for _ in range(self.frame_num)]
        for i in range(self.frame_num):
            self._joint_value_to_channel_value(joint_motion[i], self.motion_list[i], skeleton, self.joints[0])

        self.frame_time = 1. / joint_motion.fps

    def _from_joint_skeleton(self, joint_skeleton):
        # build bvh joint hierarchy
        bvh_joint_dict = {}
        self.total_channel_count = 0
        self._joint_to_bvh_joint(joint_skeleton.get_root(), bvh_joint_dict)

        # build bvh joint array
        self.joints = list()
        for node in joint_skeleton.get_nodes():
            self.joints.append(bvh_joint_dict[node.label])

    def _joint_to_bvh_joint(self, joint, bvh_joint_dict):
        bvh_joint = Bvh.Joint(joint.label)
        bvh_joint_dict[joint.label] = bvh_joint

        bvh_joint.offset = joint.get_translation

        # channels
        if joint.get_parent is None:
            channel_types = Bvh.CHANNEL_6DOF
        elif len(joint.children) == 0:
            channel_types = []
        else:
            channel_types = Bvh.CHANNEL_3DOF
        for channel_type in channel_types:
            bvh_joint.channels.append(Bvh.Channel(channel_type, self.total_channel_count))
            self.total_channel_count += 1

        for child in joint.get_children():
            bvh_joint.children.append(self._joint_to_bvh_joint(child, bvh_joint_dict))

        return bvh_joint

    # joint_posture : input
    # channel_values : output
    def _joint_value_to_channel_value(self, joint_posture, channel_values, joint_skeleton, bvh_joint):
        z_angle, x_angle, y_angle = mm.r_to_zxy(joint_posture.get_local_r(joint_skeleton.get_index_by_label(bvh_joint.
                                                                                                            name)))

        for channel in bvh_joint.channels:
            if channel.channel_type == 'XPOSITION':
                channel_values[channel.channel_index] = joint_posture.root_pos[0]
            elif channel.channel_type == 'YPOSITION':
                channel_values[channel.channel_index] = joint_posture.root_pos[1]
            elif channel.channel_type == 'ZPOSITION':
                channel_values[channel.channel_index] = joint_posture.root_pos[2]
            elif channel.channel_type == 'XROTATION':
                channel_values[channel.channel_index] = z_angle * mm.DEG
            elif channel.channel_type == 'YROTATION':
                channel_values[channel.channel_index] = x_angle * mm.DEG
            elif channel.channel_type == 'ZROTATION':
                channel_values[channel.channel_index] = y_angle * mm.DEG

        for child in bvh_joint.children:
            self._joint_value_to_channel_value(joint_posture, channel_values, joint_skeleton, child)
