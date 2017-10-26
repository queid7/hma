

import motion


class Constraint:
    def __init__(self):
        pass


class IK:
    def __init__(self):
        self._motion = None
        self.constraints = list()

    def set_motion(self, motion):
        self._motion = motion

    def set_constraints(self, constraints):
        self.constraints = constraints

    def solve(self):
        raise NotImplementedError