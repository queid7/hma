import numpy, math
import pickle

import sys

if '..' not in sys.path:
    sys.path.append('..')

import resource.ys_motion_loader as yml


class Wrl:
    child_types = ['JOINT', 'SEGMENT', 'TRANSFORM', 'SHAPE']

    class Child:
        def __init__(self):
            self.child_type = None

        def get_type(self):
            return self.child_type

    class Joint(Child):
        def __init__(self, name):
            self.child_type = 'JOINT'
            self.name = name
            self.joint_type = None
            self.translation = None
            self.joint_axes = []
            self.children = []

        def __strHierarchy__(self, depth=0):
            s = ''
            tab1 = '  ' * depth
            tab2 = '  ' * (depth + 1)
            s += '%sJOINT %s\n' % (tab1, self.name)
            s += '%s{\n' % tab1
            s += '%sTRANSLATION %s\n' % (tab2, self.translation)

            joint_axes_string = ''
            for axis in self.joint_axes:
                joint_axes_string += axis + ' '
            s += '%sJOINTAXES %s\n' % (tab2, joint_axes_string)

            for child in self.children:
                s += child.__strHierarchy__(depth + 1)
            s += '%s}\n' % tab1

            return s

        def get_child_segment(self):
            child_segment = None
            for child in self.children:
                if child.get_type() == 'SEGMENT':
                    if child_segment is None:
                        child_segment = child
                    else:
                        print("two childsegment exist")

            if child_segment is None:
                print("no childsegment exists")

            return child_segment

    class Segment(Child):
        def __init__(self):
            self.child_type = 'SEGMENT'
            self.center_of_mass = None
            self.mass = None
            self.moments_of_inertia = None
            self.children = []

        def __strHierarchy__(self, depth=0):
            s = ''
            tab1 = '  ' * depth
            tab2 = '  ' * (depth + 1)
            s += '%sSEGMENT\n' % tab1
            s += '%s{\n' % tab1
            s += '%sCENTEROFMASS %s\n' % (tab2, self.center_of_mass)

            s += '%s{\n' % tab1
            s += '%sMASS %s\n' % (tab2, self.mass)

            s += '%s{\n' % tab1
            s += '%sMOMENTSOFINETIA %s\n' % (tab2, self.moments_of_inertia)

            for child in self.children:
                s += child.__strHierarchy__(depth + 1)
            s += '%s}\n' % tab1

            return s

    class Shape(Child):
        def __init__(self):
            self.child_type = 'SHAPE'
            self.obj_path = None

        def __strHierarchy__(self, depth=0):
            s = ''
            tab1 = '  ' * depth
            tab2 = '  ' * (depth + 1)
            s = '%sSHAPE\n' % tab1
            s += '%s{\n' % tab1
            s += '%sGEOMETRY OBJ %s\n' % (tab2, self.obj_path)

            return s

    class Transform(Child):
        def __init__(self):
            self.child_type = 'TRANSFORM'
            self.rotation = None
            self.translation = None
            self.scale = None
            self.children = []

        def __strHierarchy__(self, depth=0):
            s = ''
            tab1 = '  ' * depth
            tab2 = '  ' * (depth + 1)

            for child in self.children:
                s += child.__strHierarchy__(depth + 1)
            s += '%s}\n' % tab1

            return s

    def __init__(self):
        self.name = None
        self.joints = []

    def __str__(self):
        s = 'NAME\n'
        s += self.name
        s += 'HIERARCHY\n'
        s += self.joints[0].__strHierarchy__()

        return s

    # ===========================================================================
    # read
    # ===========================================================================
    def parse_wrl(self, filepath_or_fileobject):
        if isinstance(filepath_or_fileobject, str):
            file = open(filepath_or_fileobject)
        else:
            file = filepath_or_fileobject

        tokens = file.read().split()
        if not isinstance(filepath_or_fileobject, str): file.close()

        tokens.reverse()
        #        print tokens

        if tokens.pop().upper() != "DEF":
            print("'DEF' is missing")
            return None
        tokens.pop()
        if tokens.pop().upper() != "HUMANOID":
            print("'Humanoid' is missing")
            return None
        self.parse_wrl_humanoid(tokens)

    def parse_wrl_humanoid(self, tokens):
        if tokens.pop() != "{":
            print("'{' missing")
            return None
        t = tokens.pop().upper()
        if t == "NAME":
            self.name = tokens.pop()
            t = tokens.pop().upper()
        if t != "HUMANOIDBODY":
            print("'humanoidbody' is missing")
            return None
        if tokens.pop() != "[":
            print("'[' is missing")
            return None
        if tokens.pop().upper() != "DEF":
            print("'DEF' is missing")
            return None
        root_joint_name = tokens.pop()
        if tokens.pop().upper() != "JOINT":
            print("'Joint' is missing")
            return None
        self.parse_wrl_joint(root_joint_name, tokens)

    def parse_wrl_joint(self, name, tokens):
        wrl_joint = Wrl.Joint(name)
        self.joints.append(wrl_joint)

        if tokens.pop() != "{":
            print("'{' is missing")
            return None

        end_detected = False
        while not end_detected:
            t = tokens.pop().upper()
            if t == '}':
                end_detected = True
            elif t == 'JOINTTYPE':
                jt = tokens.pop()
                if jt[0] == '"' and jt[-1] == '"':
                    wrl_joint.joint_type = jt[1:-1]
                else:
                    wrl_joint.joint_type = jt
            elif t == 'TRANSLATION':
                x = float(tokens.pop())
                y = float(tokens.pop())
                z = float(tokens.pop())
                wrl_joint.translation = numpy.array([x, y, z], float)
            elif t == 'JOINTAXIS':
                jt = tokens.pop().upper()
                for c in jt:
                    if c.upper() == 'Z':
                        wrl_joint.joint_axes.append('ZROTATION')
                    elif c.upper() == 'X':
                        wrl_joint.joint_axes.append('XROTATION')
                    elif c.upper() == 'Y':
                        wrl_joint.joint_axes.append('YROTATION')
            elif t == 'CHILDREN':
                wrl_joint.children = wrl_joint.children + self.parse_wrl_children(tokens)

        return wrl_joint

    def parse_wrl_children(self, tokens):
        children = []

        if tokens.pop() != '[':
            print("'[' is missing")
            return None

        end_detected = False
        while not end_detected:
            t = tokens.pop().upper()
            if t == ']':
                end_detected = True
            elif t == 'DEF':
                name = tokens.pop()
                t = tokens.pop().upper()
                if t == 'JOINT':
                    children.append(self.parse_wrl_joint(name, tokens))
                else:
                    print("'DEF' is incorrect")
                    return None
            elif t == 'SEGMENT':
                children.append(self.parse_wrl_segment(tokens))
            elif t == 'TRANSFORM':
                children.append(self.parse_wrl_transform(tokens))
            elif t == 'SHAPE':
                children.append(self.parse_wrl_shape(tokens))

        return children

    def parse_wrl_segment(self, tokens):
        wrl_segment = Wrl.Segment()

        if tokens.pop() != '{':
            print("'{' is missing")
            return None

        end_detected = False
        while not end_detected:
            t = tokens.pop().upper()
            if t == '}':
                end_detected = True
            elif t == 'CENTEROFMASS':
                x = float(tokens.pop())
                y = float(tokens.pop())
                z = float(tokens.pop())
                wrl_segment.center_of_mass = numpy.array([x, y, z], float)
            elif t == 'MASS':
                wrl_segment.mass = float(tokens.pop())
            elif t == 'MOMENTSOFINERTIA':
                mat = []
                for i in range(3):
                    row = []
                    for j in range(3):
                        t = tokens.pop()
                        if t[0] == '[':
                            t = t[1:]
                        elif t[-1] == ']':
                            t = t[:-1]
                        row.append(float(t))
                    mat.append(row)
                wrl_segment.moments_of_inertia = numpy.matrix(mat)
            elif t == 'CHILDREN':
                wrl_segment.children = wrl_segment.children + self.parse_wrl_children(tokens)

        return wrl_segment

    def parse_wrl_shape(self, tokens):
        wrl_shape = Wrl.Shape()
        if tokens.pop() != '{':
            print("'{' is missing")
            return None
        if tokens.pop().upper() != "GEOMETRY":
            print("'GEOMETRY' is missing")
            return None
        if tokens.pop().upper() != "OBJ":
            print("'OBJ' is missing")
            return None
        t = tokens.pop()
        if t[-1] == '}':
            t = t[:-1]
        wrl_shape.obj_path = t
        return wrl_shape

    def parse_wrl_transform(self, tokens):
        wrl_transform = Wrl.Transform()

        if tokens.pop() != '{':
            print("'{' is missing")
            return None

        end_detected = False
        while not end_detected:
            t = tokens.pop().upper()
            if t == '}':
                end_detected = True
            elif t == 'ROTATION':
                w = float(tokens.pop())
                x = float(tokens.pop())
                y = float(tokens.pop())
                z = float(tokens.pop())
                wrl_transform.rotation = numpy.array([w, x, y, z], float)
            elif t == 'TRANSLATION':
                x = float(tokens.pop())
                y = float(tokens.pop())
                z = float(tokens.pop())
                wrl_transform.translation = numpy.array([x, y, z], float)
            elif t == 'SCALE':
                x = float(tokens.pop())
                y = float(tokens.pop())
                z = float(tokens.pop())
                wrl_transform.scale = numpy.array([x, y, z], float)
            elif t == 'CHILDREN':
                wrl_transform.children = wrl_transform.children + self.parse_wrl_children(tokens)

        return wrl_transform

    # =============================================
    # =============================================

    def to_bvh(self):
        bvh = yml.Bvh()
        self.wrl_joint_to_bvh_joint(bvh, self.joints[0])
        bvh.frame_num = 1
        bvh.frame_time = 1. / 30.

        # =============================
        # make default bvh ys_motion
        # =============================
        bvh.motion_list = []
        bvh.motion_list.append([None] * bvh.total_channel_count)
        for i in range(bvh.total_channel_count):
            bvh.motion_list[0][i] = 0.

        return bvh

    def wrl_joint_to_bvh_joint(self, bvh, wrl_joint):
        bvh_joint = yml.Bvh.Joint(wrl_joint.name)
        bvh.joints.append(bvh_joint)
        bvh_joint.offset = wrl_joint.translation
        if wrl_joint.joint_type.upper() == 'FREE':
            for idof in range(len(yml.Bvh.channel_types6dof)):
                bvh_joint.channels.append(
                    yml.Bvh.Channel(yml.Bvh.channel_types6dof[idof], bvh.total_channel_count + idof))
        else:
            for idof in range(len(wrl_joint.joint_axes)):
                bvh_joint.channels.append(yml.Bvh.Channel(wrl_joint.joint_axes[idof], bvh.total_channel_count + idof))
        bvh.total_channel_count += len(bvh_joint.channels)
        has_joint_child = False
        for child in wrl_joint.children:
            if child.get_type() == 'JOINT':
                bvh_joint.children.append(self.wrl_joint_to_bvh_joint(bvh, child))
                has_joint_child = True

        if not has_joint_child:
            end_site = yml.Bvh.Joint("%s_Effector" % bvh_joint.name)
            end_site.offset = None
            for child in wrl_joint.children:
                if child.get_type() == 'SEGMENT':
                    if end_site.offset is None:
                        end_site.offset = child.center_of_mass.copy() * 2
                    else:
                        print("an end site joint has segments more than two")
            bvh.joints.append(end_site)
            bvh_joint.children.append(end_site)

        return bvh_joint

    # ============================================================
    # member function
    # ============================================================
    def get_wrl_joint(self, name):
        for joint in self.joints:
            if joint.name == name:
                return joint
        return None


# ===========================================================================
# write
# ===========================================================================


# =========================================
# function
# =========================================
def read_wrl_fileas_wrl(wrl_file_path_or_wrl_file):
    wrl = Wrl()
    wrl.parse_wrl(wrl_file_path_or_wrl_file)
    return wrl


# =========================================
# test
# =========================================

def test_parse():
    wrl = Wrl()
    wrl.parse_wrl("/home/jo/Research/yslee/Resource/ys_motion/opensim/FullBody2_lee.wrl")
    print(wrl)


def test_to_bvh():
    wrl = Wrl()
    wrl.parse_wrl("/home/jo/Research/yslee/Resource/ys_motion/opensim/FullBody2_lee.wrl")
    bvh = wrl.to_bvh()
    print(bvh)
    print("Total Channel Count: %d\n" % bvh.total_channel_count)
    # bvh = yml.read_bvh_file_as_bvh("/home/jo/ys2010/Walking/adun/adun.bvh")
    # aa = bvh.to_joint_motion(100, False)
    # bvh.from_joint_motion(bvh.to_joint_motion(100, False))
    bvh.write_bvh_file("/home/jo/ys2010/Walking/adun/adun.bvh")

# ======
# test
# ======
# if __name__=='__main__':
# test_parse()
# test_to_bvh()
