import numpy as np

import hmath.mm_math as mm
import motion.motion as motion


def read_htr_file(htr_file_path, scale=1.0):
    htr = Htr()
    htr.parse_htr_file(htr_file_path)
    joint_motion = htr.to_joint_motion(scale)
    return joint_motion


def read_htr_file_as_htr(htr_file_path):
    htr = Htr()
    htr.parse_htr_file(htr_file_path)
    return htr


def write_htr_file(htr_file_path, joint_motion):
    htr = Htr()
    htr.from_joint_motion(joint_motion)
    htr.write_htr_file(htr_file_path)


class Htr:
    KEYWORDS = ["[Head]", "[SegmentNames&Hierarchy]", "[BasePosition]", "#Beginning of Data.", "#Beginning of Data"]

    class Joint:
        def __init__(self, name="no name"):
            self.name = name
            # the base data of the joint
            self.base_translation = mm.o_vec3()
            self.base_euler_rotation = mm.o_vec3()
            self.base_bone_length = None
            # the data per frame of the joint
            self.translations = []
            self.euler_rotations = []
            self.sfs = []
            # the data name order of the data per frame
            self.data_names = []

    def __init__(self):
        # header information
        self.property_dict = {}
        # key: name, value: Joint instance
        self.joint_dict = {}
        # childs : child list
        # parents : parents list related to childs list
        self.parents = []
        self.children = []
        # the data order of base_position
        self.base_position_names = []

        self.root = None

    def get_num_frame(self):
        return 0 if self.root is None else len(self.root.translations)

    def parse_htr_file(self, filepath_or_fileobject):
        if isinstance(filepath_or_fileobject, str):
            file = open(filepath_or_fileobject)
        else:
            file = filepath_or_fileobject

        lines = file.read().split("\n")
        lines.reverse()

        while len(lines) > 0:
            line = lines.pop()
            if line == "[Header]":
                while len(lines) > 0:
                    line = lines.pop()
                    if Htr._is_htr_keyword(line):
                        lines.append(line)
                        break
                    tokens = line.split()
                    if len(tokens) > 1:
                        self.property_dict[tokens[0]] = tokens[1]
                    elif len(tokens) == 1:
                        self.property_dict[tokens[0]] = None
            elif line == "[SegmentNames&Hierarchy]":
                lines.pop()
                while len(lines) > 0:
                    line = lines.pop()
                    if Htr._is_htr_keyword(line):
                        lines.append(line)
                        break
                    tokens = line.split()
                    if len(tokens) > 1:
                        if tokens[0][0] == "#":
                            continue
                        try:
                            parent_joint = self.joint_dict[tokens[1]]
                        except KeyError:
                            parent_joint = Htr.Joint(tokens[1]) if tokens[1].upper() != "GLOBAL" else None
                            self.joint_dict[tokens[1]] = parent_joint
                        try:
                            child_joint = self.joint_dict[tokens[0]]
                        except KeyError:
                            child_joint = Htr.Joint(tokens[0])
                            self.joint_dict[tokens[0]] = child_joint
                        self.parents.append(parent_joint)
                        self.children.append(child_joint)
                        if self.root is None and parent_joint is None:
                            self.root = child_joint
            elif line == "[BasePosition]":
                while len(lines) > 0:
                    line = lines.pop()
                    if Htr._is_htr_keyword(line):
                        lines.append(line)
                        break
                    tokens = line.split()
                    if line[0] == "#":
                        self.base_position_names = line[1:].split()
                    elif len(tokens) > 0:
                        if len(self.base_position_names) < 1:
                            raise ValueError("the order of base position is not defined")
                        joint = self.joint_dict[tokens[self.base_position_names.index("SegmentName")]]
                        for i in range(len(self.base_position_names)):
                            if self.base_position_names[i] == "Tx":
                                joint.base_translation[0] = tokens[i]
                            elif self.base_position_names[i] == "Ty":
                                joint.base_translation[1] = tokens[i]
                            elif self.base_position_names[i] == "Tz":
                                joint.base_translation[2] = tokens[i]
                            elif self.base_position_names[i] == "Rx":
                                joint.base_euler_rotation[0] = tokens[i]
                            elif self.base_position_names[i] == "Ry":
                                joint.base_euler_rotation[1] = tokens[i]
                            elif self.base_position_names[i] == "Rz":
                                joint.base_euler_rotation[2] = tokens[i]
                            elif self.base_position_names[i] == "BoneLength":
                                joint.base_bone_length = tokens[i]
            elif line == "#Beginning of Data." or line == "#Beginning of Data":
                joint = None
                while len(lines) > 0:
                    line = lines.pop()
                    if Htr._is_htr_keyword(line):
                        lines.append(line)
                        break
                    tokens = line.split()
                    if len(tokens) < 1:
                        continue
                    elif tokens[0][0] == "[" and tokens[0][-1] == "]":
                        try:
                            joint = self.joint_dict[tokens[0][1:-1]]
                        except KeyError:
                            raise KeyError("undefined joint data")
                    elif joint is not None:
                        if line[0] == "#":
                            joint.data_names = line[1:].split()
                        else:
                            translation = mm.o_vec3()
                            euler_rotation = mm.o_vec3()
                            sf = 1.0
                            for i in range(len(joint.data_names)):
                                if joint.data_names[i] == "Tx":
                                    translation[0] = tokens[i]
                                elif joint.data_names[i] == "Ty":
                                    translation[1] = tokens[i]
                                elif joint.data_names[i] == "Tz":
                                    translation[2] = tokens[i]
                                elif joint.data_names[i] == "Rx":
                                    euler_rotation[0] = tokens[i]
                                elif joint.data_names[i] == "Ry":
                                    euler_rotation[1] = tokens[i]
                                elif joint.data_names[i] == "Rz":
                                    euler_rotation[2] = tokens[i]
                                elif joint.data_names[i] == "SF":
                                    sf = float(tokens[i])
                            joint.translations.append(translation)
                            joint.euler_rotations.append(euler_rotation)
                            joint.sfs.append(sf)

        if isinstance(filepath_or_fileobject, str):
            file.close()

    @staticmethod
    def _is_htr_keyword(keyword):
        for htr_keyword in Htr.KEYWORDS:
            if keyword == htr_keyword:
                return True
        return False

    def find_children(self, parent):
        children = list()
        for i in range(len(self.parents)):
            if self.parents[i] is parent:
                children.append(self.children[i])
        return children

    def find_parent(self, child):
        for i in range(len(self.children)):
            if self.children[i] is child:
                return self.parents[i]

    def add_end_effector(self, joint_name, translation):
        joint = self.joint_dict[joint_name]
        child_joint = Htr.Joint(joint_name + "_end_effector")
        self.joint_dict[joint_name + "_end_effector"] = child_joint
        self.parents.append(joint)
        self.children.append(child_joint)

        child_joint.base_bone_length = 1.0

        total_frames = self.get_num_frame()
        child_joint.translations = [translation] * total_frames
        child_joint.euler_rotations = [mm.o_vec3()] * total_frames
        child_joint.sfs = [1.0] * total_frames

        child_joint.data_names = joint.data_names.copy()

    # ===========================================================================
    # Htr -> JointMotion
    # ===========================================================================
    def to_joint_motion(self, scale=1.0):
        skeleton = self.to_joint_skeleton(scale)

        joint_motion = motion.JointMotion()
        base_ts = self._make_base_transformations(skeleton)
        for frame in range(int(self.property_dict["NumFrames"])):
            joint_posture = motion.JointPosture(skeleton)
            self._set_local_rs_from_htr(frame, joint_posture, base_ts)
            joint_posture.update_global_ts()
            joint_motion.append(joint_posture)

        # print(range(len(self.property_dict["NumFrames"])))

        joint_motion.fps = float(self.property_dict["DataFrameRate"])
        return joint_motion

    def to_joint_skeleton(self, scale=1.0):
        def _rec_make_skeleton_joint(skeleton_: motion.Skeleton, htr_joint: Htr.Joint, parent=None):
            skeleton_joint = motion.JointNode(htr_joint.name)
            # (base_translation) (base_rotation) (local_translation) = (transformation)
            # translation is translation part of (transformation)

            if parent is None:
                # root node
                skeleton_joint.set_translation(mm.o_vec3())
                skeleton_.set_root(skeleton_joint)
            else:
                if self.property_dict["EulerRotationOrder"] != "XYZ":
                    raise ValueError("undefined euler rotation order")
                # XYZ order
                # base_local_r : se3 = (base_rotation)
                base_local_r = mm.so3_to_se3(np.dot(np.dot(mm.rot_x(self.root.base_euler_rotation[0] * mm.RAD),
                                                           mm.rot_y(self.root.base_euler_rotation[1] * mm.RAD)),
                                                    mm.rot_z(self.root.base_euler_rotation[2] * mm.RAD)))
                base_local_p = htr_joint.base_translation
                # choose average of local_translation as fixed local translation of skeleton
                local_p = np.average(htr_joint.translations, 0)
                fixed_translation = base_local_p + mm.se3_to_vec3(np.dot(base_local_r, mm.vec3_to_se3(local_p)))
                skeleton_joint.set_translation(fixed_translation * scale)
                skeleton_.add_node(skeleton_joint, parent)

            for child in self.find_children(htr_joint):
                _rec_make_skeleton_joint(skeleton_, child, skeleton_joint)

        if self.root is None:
            raise ValueError("the root joint of Htr is not defined")
        # root
        skeleton = motion.Skeleton()
        _rec_make_skeleton_joint(skeleton, self.root, parent=None)
        return skeleton

    def _make_base_transformations(self, skeleton: motion.Skeleton):
        # base_transformations are used for calculating local_rs from htr
        # base_transformations are same order as motion.Skeleton.get_nodes()
        base_ts = list()
        for node in skeleton.get_nodes():
            htr_joint = self.joint_dict[node.label]
            if self.property_dict["EulerRotationOrder"] != "XYZ":
                raise ValueError("undefined euler rotation order")
            # XYZ order
            # base_local_r : se3 = (base_rotation)
            base_local_r = mm.so3_to_se3(
                np.dot(np.dot(mm.rot_x(self.root.base_euler_rotation[0] * mm.RAD),
                              mm.rot_y(self.root.base_euler_rotation[1] * mm.RAD)),
                       mm.rot_z(self.root.base_euler_rotation[2] * mm.RAD)))
            base_local_p = htr_joint.base_translation
            base_ts.append(np.dot(mm.vec3_to_se3(base_local_p), base_local_r))
        return base_ts

    def _set_local_rs_from_htr(self, frame: int, joint_posture: motion.JointPosture, base_ts: list):
        skeleton = joint_posture.get_skeleton()
        for i in range(len(skeleton.get_nodes())):
            skeleton_joint = skeleton.get_node_at(i)
            htr_joint = self.joint_dict[skeleton_joint.label]
            if htr_joint is self.root:
                print("root!!!")
                root_position = mm.se3_to_vec3(np.dot(base_ts[i], mm.vec3_to_se3(htr_joint.translations[frame])))
                joint_posture.set_root_position(root_position)
            # (base_transformation) (local_transformation) = (transformation)
            # XYZ order
            local_r_so3 = np.dot(np.dot(mm.rot_x(htr_joint.euler_rotations[frame][0] * mm.RAD),
                                        mm.rot_y(htr_joint.euler_rotations[frame][1] * mm.RAD)),
                                 mm.rot_z(htr_joint.euler_rotations[frame][2] * mm.RAD))
            base_local_r_so3 = mm.se3_to_so3(base_ts[i])
            r_so3 = np.dot(base_local_r_so3, local_r_so3)
            joint_posture.set_local_r_without_update(i, mm.so3_to_se3(r_so3, mm.o_vec3()))


if __name__ == '__main__':
    read_htr_file("../../../../Research/Motions/snuh/디딤자료-서울대(조동철선생님)/디딤LT/D-1/16115/trimmed_walk01.htr")
