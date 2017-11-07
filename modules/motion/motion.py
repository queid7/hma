import numpy as np
import operator as op

import hmath.mm_math as mm

DEFAULT_FPS = 30


# ==================================
# Motion
# ==================================
class Motion(list):
    def __init__(self, ls=list()):
        super(Motion, self).__init__(ls)
        self._frame = 0
        self.fps = DEFAULT_FPS
        self.motion_name = 'no name'

    def __getitem__(self, key):
        if isinstance(key, slice):
            motion = self.__class__(super(Motion, self).__getitem__(key))
            motion.__dict__.update(self.__dict__)
            motion._frame = 0
            return motion
        if isinstance(key, float):
            floor = int(key)
            t = key - floor
            if t == 0.0:
                return self[floor]
            else:
                return self[floor].blend(self[floor + 1], t)
        return super(Motion, self).__getitem__(key)

    def __add__(self, next_motion):
        motion = self.__class__(super(Motion, self).__add__(next_motion))
        motion.__dict__.update(self.__dict__)
        return motion

    def copy(self):
        motion = self.__class__(super(Motion, self).copy())
        motion.__dict__.update(self.__dict__)
        return motion

    def get_frame(self):
        return self._frame

    def go_to_frame(self, frame):
        if frame < 0 or frame >= len(self):
            raise IndexError("frame out of range")
        self._frame = frame

    def move_frame(self, offset):
        frame = self._frame + offset
        if frame < 0 or frame >= len(self):
            raise IndexError("frame out of range")
        self._frame = frame

    def get_current_posture(self):
        return self[self._frame]

    def get_position(self, index, frame):
        return self[frame].get_position(index)

    def get_positions(self, frame):
        return self[frame].get_positions()

    def get_velocity(self, index, frame0, frame1=None):
        return self._get_derivative(index, frame0, frame1, self.get_position, op.sub)

    def get_velocities(self, frame0, frame1=None):
        return self._get_derivatives(frame0, frame1, self.get_positions, op.sub)

    def get_acceleration(self, index, frame0, frame1=None):
        return self._get_derivative(index, frame0, frame1, self.get_velocity, op.sub)

    def get_accelerations(self, frame0, frame1=None):
        return self._get_derivatives(frame0, frame1, self.get_velocities, op.sub)

    def _get_finite_difference_frames(self, frame):
        prev_frame = frame - 1 if frame > 0 else frame
        next_frame = frame + 1 if frame < len(self) - 1 else frame
        return prev_frame, next_frame

    def _get_derivative(self, index, frame0, frame1, position_func, sub_func):
        if frame0 == frame1 or len(self) == 1:
            return mm.o_vec3()

        if frame1 is None:
            frame0, frame1 = self._get_finite_difference_frames(frame0)
        p0 = position_func(index, frame0)
        p1 = position_func(index, frame1)
        return (self.fps / (frame1 - frame0)) * sub_func(p1, p0)

    def _get_derivatives(self, frame0, frame1, positions_func, sub_func):
        if frame0 == frame1 or len(self) == 1:
            return [mm.o_vec3()] * len(positions_func(frame0))

        if frame1 is None:
            frame0, frame1 = self._get_finite_difference_frames(frame0)
        positions0 = positions_func(frame0)
        positions1 = positions_func(frame1)
        return list(map(lambda p0, p1: (self.fps / (frame1 - frame0)) * sub_func(p1, p0), positions0, positions1))


class JointMotion(Motion):
    def __init__(self, ls=list()):
        super(JointMotion, self).__init__(ls)

    def set_skeleton(self, skeleton):
        for posture in self:
            posture.set_skeleton(skeleton)

    def get_skeleton(self):
        return self[0].get_skeleton() if len(self) > 0 else None


class PointMotion(Motion):
    pass


# ==================================
# Posture
# ==================================
class Posture:
    def __init__(self):
        pass

    def blend(self, posture, t):
        raise NotImplementedError

    def get_position(self, index):
        raise NotImplementedError

    def get_positions(self):
        raise NotImplementedError


class JointPosture(Posture):
    def __init__(self, skeleton=None):
        super(JointPosture, self).__init__()
        self._skeleton = skeleton
        self._root_position = None  # root position : vec3
        self._local_rs = []  # local rotation matrices : SE3
        self._global_ts = []  # global transformation matrices : SE3
        self._updated = []  # boolean list for _global_ts. if false, related _global_t must be updated
        self.initialize()

    def initialize(self):
        self._root_position = mm.o_vec3()
        self.set_local_rs([mm.i_se3() for _ in range(self._skeleton.get_len_nodes())])

    def get_root_position(self):
        return self._root_position

    def set_root_position(self, root_position):
        self._root_position = root_position
        for index in range(len(self._global_ts)):
            self._global_ts[index] = np.dot(mm.vec3_to_se3(self._root_position), self._global_ts[index])

    def get_local_rs(self):
        return self._local_rs

    def set_local_rs(self, local_rs):
        if len(local_rs) != self._skeleton.get_len_nodes():
            raise IndexError("length of local_rs must be same to length of skeleton's nodes")
        self._local_rs = local_rs
        self._updated = [False for _ in self._local_rs]
        self._global_ts = [None for _ in self._local_rs]
        self._update_global_ts()

    def get_local_r(self, index):
        return self._local_rs[index]

    def set_local_r(self, index, local_r):
        self._local_rs[index] = local_r
        for i in self._skeleton.get_descendant_indices_at(index):
            self._updated[i] = False
        self._update_global_ts()

    def set_local_r_without_update(self, index, local_r):
        """
        set local rotation SE3 and don't update global transformation matrices
        must call update_global_ts method after this function
        :param index:
        :param local_r:
        :return:
        """
        self._local_rs[index] = local_r

    def get_local_p(self, index):
        return self._skeleton.get_parent_node_at(index).get_translation()

    def get_global_ts(self):
        return self._global_ts

    def get_global_t(self, index):
        return self._global_ts[index]

    def get_global_r(self, index):
        return mm.t_to_r(self._global_ts[index])

    def set_global_r(self, index, global_r):
        """
        :param index:
        :param global_r: gin
        :return:
        # Gp : global rotation of parent of joint i
        # Gi : global rotation of joint i
        # Gin : new global rotation of joint i
        # Li : local rotation of joint i
        # Lin : new local rotation of joint i
        # Gi = Gp * Li
        # Gin = Gp * Lin
        # Lin = Gp.transpose() * Gin
        """
        parent = self._skeleton.get_parent_node_at(index)
        if parent is None:
            gp = mm.i_se3()
        else:
            gp = mm.p_to_rt(self._global_ts[self._skeleton.get_index(parent)])
        self.set_local_r(index, np.dot(gp.transpose(), global_r))

    def get_global_p(self, index):
        return mm.t_to_p(self._global_ts[index])

    def _update_global_ts(self):
        for i in range(len(self._updated)):
            if self._updated[i] is False:
                parent = self._skeleton.get_parent_node_at(i)
                global_t = mm.vec3_to_se3(self._root_position) if parent is None \
                    else self._global_ts[self._skeleton.get_parent_index_at(i)]
                local_p = mm.vec3_to_se3(self._skeleton.get_node_at(i).get_translation())
                self._global_ts[i] = np.dot(np.dot(global_t, local_p), self._local_rs[i])
                self._updated[i] = True

    def update_global_ts(self):
        for i in range(len(self._updated)):
            self._updated[i] = False
        self._update_global_ts()

    def get_tpose(self, initial_rs=None):
        tpose = JointPosture(self._skeleton)
        tpose.set_root_position(self._root_position.copy())
        if initial_rs is not None:
            tpose.set_local_rs(initial_rs)
        return tpose

    def get_skeleton(self):
        return self._skeleton

    def set_skeleton(self, skeleton):
        self._skeleton = skeleton
        self.initialize()

    def blend(self, posture, t):
        blended_posture = JointPosture(self._skeleton)
        blended_posture.set_root_position(mm.linearInterpol(self._root_position, posture.get_root_position(), t))
        blended_local_rs = list()
        for i in range(len(self._local_rs)):
            blended_local_rs.append(mm.so3_to_se3(mm.slerp(mm.se3_to_so3(self._local_rs[i]),
                                                           mm.se3_to_so3(posture.get_local_r(i)), t)))
        blended_posture.set_local_rs(blended_local_rs)
        return blended_posture

    def get_position(self, index):
        return mm.t_to_p(self._global_ts[index])

    def get_positions(self):
        return [mm.t_to_p(t) for t in self._global_ts]


class PointPosture(Posture):
    def blend(self, posture, t):
        raise NotImplementedError


# ==================================
# Tree
# ==================================
class Node:
    def __init__(self, label="no name"):
        self._parent = None
        self._children = list()
        self.label = label

    def __str__(self):
        return self.label

    def get_parent(self):
        return self._parent

    def has_parent(self):
        return self._parent is not None

    def get_children(self):
        return self._children

    def get_child(self, index):
        return self._children[index]

    def has_child(self):
        return len(self._children) > 0

    def add_child(self, child):
        child._parent = self
        self._children.append(child)

    def remove_child(self, child):
        self._children.remove(child)


class Tree:
    def __init__(self, root=None):
        self._nodes = list([root])

    def __str__(self):
        if self.is_empty():
            return '< no module available >'

        def _str_node_hierarchy(_node):
            _s = _node.__str__() + "\n"
            for child in _node.get_children():
                _s_child = "\t" + _str_node_hierarchy(child).replace("\n", "\n\t")
                _s += _s_child
            return _s
        return '< hierarchy >\n' + _str_node_hierarchy(self.get_root())

    def is_empty(self):
        return self._nodes[0] is None

    def get_root(self):
        return self._nodes[0]

    def set_root(self, root):
        self._nodes = list([root])

    def get_len_nodes(self):
        return len(self._nodes)

    def get_nodes(self):
        return self._nodes

    def get_node_at(self, index):
        return self._nodes[index]

    def get_node_by_label(self, label):
        for node in self._nodes:
            if node.label == label:
                return node
        raise ValueError("no node has this label.")

    def get_index(self, node):
        return self._nodes.index(node)

    def get_index_by_label(self, label):
        return self._nodes.index(self.get_node_by_label(label))

    def get_label_by_index(self, index):
        return self._nodes[index].label

    def get_parent_node_at(self, index):
        return self._nodes[index].get_parent()

    def get_parent_index_at(self, index):
        return self._nodes.index(self.get_parent_node_at(index))

    def get_descendant_indices_at(self, index):
        """
        :param index:
        :return: descendant's indices including self index
        """
        result = list([index])
        for node in self._nodes[index].get_children():
            result.extend(self.get_descendant_indices_at(self.get_index(node)))
        return result

    def get_ancestor_indices_at(self, index):
        """
        :param index:
        :return: ancestor's indices including self index
        """
        return [0] if index == 0 else self.get_ancestor_indices_at(self.get_parent_index_at(index)).append(index)

    def add_node(self, node, parent):
        parent.add_child(node)
        self._nodes.append(node)

    def remove_node(self, node):
        def _remove_node(_node):
            for child in _node.get_children():
                _remove_node(child)
            self._nodes.remove(_node)
        if node is self.get_root():
            raise ValueError("can't remove. this node is root of tree.")
        _remove_node(node)
        node.get_parent().remove_child(node)

    def remove_node_at(self, index):
        self.remove_node(self._nodes[index])


# ==================================
# Skeleton
# ==================================
class Skeleton(Tree):
    pass


class JointNode(Node):
    def __init__(self, label="no name", translation=mm.o_vec3()):
        super(JointNode, self).__init__(label)
        self._translation = translation

    def get_translation(self):
        return self._translation

    def set_translation(self, translation):
        self._translation = translation


class PointNode(Node):
    pass
