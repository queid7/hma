import sys
import resource.bvh_loader as bl


class HumanMotionAnalyzer:
    def __init__(self):
        self.motions = list()

    def set_motions(self, motions):
        self.motions.extend(motions)

