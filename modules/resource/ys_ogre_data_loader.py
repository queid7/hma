import xml.sax
import xml.sax.handler
import xml.dom.minidom
import numpy, os

import sys

if '..' not in sys.path:
    sys.path.append('..')
import mesh.ys_mesh as yms
import motion.ys_motion as ym
import hmath.mm_math as mm_math

'''
Maya(8.5) Ogre Exporter(1.2.6) Setting (supported in this module)
Mesh
  v Export mesh
  v Use shared geometry
  v Include vertex bone assignements
    Include diffuse vertex colours
    Include texture coordinates
    Build edges list(for shadows)
    Build tanget vectors(for normal maps)
Materials
    Export materials to Ogre .material file
Skeleton
  v Export skeleton
Skeleton Animations
  v Export animations (requires export of skeleton)
Blend Shapes
    Export blend shapes (to mesh file)
Blend Shape Animations
    Export animations (to mesh file)
Vertex Animations
    Export animations (to mesh file)
Cameras
    Export cameras to Ogre .camera file
Particles
    Export particles to Ogre .particles file
'''


def read_ogre_data_files(mesh_file_path, scale=1.0, skeleton_file_path=None):
    parser = xml.sax.make_parser()
    handler = OgreSkinMeshSaxHandler(scale)
    parser.set_content_handler(handler)
    parser.parse(open(mesh_file_path))

    if skeleton_file_path is None:
        if handler.skeletonlink != None:
            dirname = os.path.dirname(mesh_file_path)
            skeleton_file_path = dirname + '/' + handler.skeletonlink + '.xml'

    joint_motions = []
    if skeleton_file_path != None:
        joint_skeleton, initial_rs, joint_motions = read_ogre_skeleton_file(skeleton_file_path, scale)
        initial_posture = ym.JointPosture(joint_skeleton)
        #        initial_posture.init_local_r_map(initial_r_map)
        initial_posture.init_local_rs(initial_rs)
        handler.mesh.initialize(initial_posture)

    return handler.mesh, joint_motions


def read_ogre_mesh_file_as_mesh(mesh_file_path, scale=1.0):
    parser = xml.sax.make_parser()
    handler = OgreMeshSaxHandler(scale)
    parser.set_content_handler(handler)
    parser.parse(open(mesh_file_path))
    return handler.mesh


class OgreMeshSaxHandler(xml.sax.handler.ContentHandler):
    def __init__(self, scale):
        self.mesh = None
        self.scale = scale
        self.current_submesh_name = None

    def start_document(self):
        self.mesh = yms.Mesh()

    def start_element(self, name, attrs):
        if name == 'submesh':
            self.current_submesh_name = attrs.get('material').encode()
            self.mesh.submesh_map[self.current_submesh_name] = []
        elif name == 'face':
            face = yms.Face()
            face.vertex_index[0] = int(attrs.get('v1', ""))
            face.vertex_index[1] = int(attrs.get('v2', ""))
            face.vertex_index[2] = int(attrs.get('v3', ""))
            self.mesh.faces.append(face)
            self.mesh.submesh_map[self.current_submesh_name].append(len(self.mesh.faces) - 1)
        elif name == 'position':
            vertex = yms.Vertex()
            vertex.pos[0] = float(attrs.get('x', "")) * self.scale
            vertex.pos[1] = float(attrs.get('y', "")) * self.scale
            vertex.pos[2] = float(attrs.get('z', "")) * self.scale
            self.mesh.vertices.append(vertex)


def read_ogre_mesh_file_as_skin_mesh(mesh_file_path, joint_skeleton, initial_rs, scale=1.0):
    parser = xml.sax.make_parser()
    handler = OgreSkinMeshSaxHandler(scale)
    parser.set_content_handler(handler)
    parser.parse(open(mesh_file_path))

    initial_posture = ym.JointPosture(joint_skeleton)
    initial_posture.init_local_rs(initial_rs)
    handler.mesh.initialize(initial_posture)

    return handler.mesh


class OgreSkinMeshSaxHandler(OgreMeshSaxHandler):
    def __init__(self, scale):
        OgreMeshSaxHandler.__init__(self, scale)
        self.skeletonlink = None

    def start_document(self):
        self.mesh = yms.SkinMesh()

    def start_element(self, name, attrs):
        OgreMeshSaxHandler.start_element(self, name, attrs)
        if name == 'sharedgeometry':
            self.mesh.vertex_bone_weights = [None] * int(attrs.get('vertexcount'))
            for i in range(int(attrs.get('vertexcount'))):
                self.mesh.vertex_bone_weights[i] = []
        if name == 'skeletonlink':
            self.skeletonlink = attrs.get('name')
        if name == 'vertexboneassignment':
            vertex_index = int(attrs.get('vertexindex'))
            bone_index = int(attrs.get('boneindex'))
            weight = float(attrs.get('weight'))
            self.mesh.vertex_bone_weights[vertex_index].append((bone_index, weight))


def read_ogre_skeleton_file(skeleton_file_path, scale=1.0):
    dom = xml.dom.minidom.parse(skeleton_file_path)
    joint_skeleton, initial_rs = _readOgreSkeleton(dom, scale)
    joint_motions = _readOgreSkeletonAnimations(dom, joint_skeleton, initial_rs, scale)
    return joint_skeleton, initial_rs, joint_motions


def read_ogre_skeleton_file__skeleton(skeleton_file_path, scale=1.0):
    dom = xml.dom.minidom.parse(skeleton_file_path)
    joint_skeleton, initial_rs = _readOgreSkeleton(dom, scale)
    return joint_skeleton, initial_rs


def read_ogre_skeleton_file__skeleton_animations(skeleton_file_path, scale=1.0):
    dom = xml.dom.minidom.parse(skeleton_file_path)
    joint_skeleton, initial_rs = _readOgreSkeleton(dom, scale)
    joint_motions = _readOgreSkeletonAnimations(dom, joint_skeleton, initial_rs, scale)
    return joint_motions


def _readOgreSkeleton(dom, scale=1.0):
    bones = dom.get_elements_by_tag_name('bone')
    joint_map = {}
    #    initial_r_map = {}
    initial_rs = []
    for bone in bones:
        joint = ym.Joint(bone.get_attribute('name').encode(), None)
        joint_map[joint.name] = joint

        pos_ele = bone.get_elements_by_tag_name('position')[0]
        joint.offset[0] = float(pos_ele.get_attribute('x')) * scale
        joint.offset[1] = float(pos_ele.get_attribute('y')) * scale
        joint.offset[2] = float(pos_ele.get_attribute('z')) * scale

        rot_ele = bone.get_elements_by_tag_name('rotation')[0]
        angle = float(rot_ele.get_attribute('angle'))
        axis_ele = rot_ele.get_elements_by_tag_name('axis')[0]
        axis = mm_math.s2v((float(axis_ele.get_attribute('x')), float(axis_ele.get_attribute('y')),
                            float(axis_ele.get_attribute('z'))))
        R = mm_math.exp(axis, angle)
        #        initial_r_map[joint.name] = R
        initial_rs.append(R)

    root_joint = joint_map[bones[0].get_attribute('name').encode()]

    bone_parents = dom.get_elements_by_tag_name('boneparent')
    for bp in bone_parents:
        joint = joint_map[bp.get_attribute('bone').encode()]
        parent_joint = joint_map[bp.get_attribute('parent').encode()]
        joint.parent = parent_joint
        parent_joint.add_child(joint)

    joint_skeleton = ym.JointSkeleton(root_joint)
    for bone in bones:
        #        joint_skeleton.joints_ar.append(joint_map[bone.get_attribute('name')])
        bone_name = bone.get_attribute('name').encode()
        joint_skeleton.add_element(joint_map[bone_name], bone_name)
    # return joint_skeleton, initial_r_map
    return joint_skeleton, initial_rs


def _readOgreSkeletonAnimations(dom, joint_skeleton, initial_rs, scale=1.0):
    joint_motions = []
    animation_eles = dom.get_elements_by_tag_name('animation')

    for animation_ele in animation_eles:
        joint_motion = ym.Motion()
        #        joint_motion.resource_name = animation_ele.get_attribute('name').encode()
        track_eles = animation_ele.get_elements_by_tag_name('track')
        first_keyframes = track_eles[0].get_elements_by_tag_name('keyframe')
        len_keyframes = len(first_keyframes)
        time2frameMap = {}
        for i in range(len_keyframes):
            joint_posture = ym.JointPosture(joint_skeleton)
            #            joint_posture.init_local_r_map(initial_r_map)
            joint_posture.init_local_rs(initial_rs)
            joint_motion.append(joint_posture)

            # because each bone may not have same number of keyframes
            time2frameMap[first_keyframes[i].get_attribute('time')] = i

        for track_ele in track_eles:
            #            print i, track_ele.get_attribute('bone'), len(track_ele.get_elements_by_tag_name('keyframe'))
            keyframe_eles = track_ele.get_elements_by_tag_name('keyframe')

            for keyframe_ele in keyframe_eles:
                keyframe_time = keyframe_ele.get_attribute('time')

                # because each bone may not have same number of keyframes
                frame = time2frameMap[keyframe_time]
                joint_posture = joint_motion[frame]

                bone_name = track_ele.get_attribute('bone').encode()
                if bone_name == joint_skeleton.root.name:
                    trans_ele = keyframe_ele.get_elements_by_tag_name('translate')[0]
                    joint_posture.root_pos[0] = float(trans_ele.get_attribute('x')) * scale
                    joint_posture.root_pos[1] = float(trans_ele.get_attribute('y')) * scale
                    joint_posture.root_pos[2] = float(trans_ele.get_attribute('z')) * scale

                rot_ele = keyframe_ele.get_elements_by_tag_name('rotate')[0]
                angle = float(rot_ele.get_attribute('angle'))
                axis_ele = rot_ele.get_elements_by_tag_name('axis')[0]
                axis = mm_math.v3(float(axis_ele.get_attribute('x')), float(axis_ele.get_attribute('y')),
                                  float(axis_ele.get_attribute('z')))
                R = mm_math.exp(axis, angle)

                #                joint_posture.mul_local_r(bone_name, R)
                joint_posture.mul_local_r(joint_skeleton.get_element_index(bone_name), R)
                joint_posture.update_global_t()

        joint_motions.append(joint_motion)
    return joint_motions


if __name__ == '__main__':
    import psyco;

    psyco.full()
    from fltk import *
    import profile
    import copy
    from datetime import datetime
    import GUI.ys_simple_viewer as ysv
    import Renderer.ys_renderer as yr
    import Mesh.ys_mesh_util as ysu
    import Util.ys_gl_helper as ygh
    import Resource.ys_motion_loader as yf


    def test_dom():
        node_types = ['ELEMENT_NODE', 'ATTRIBUTE_NODE', 'TEXT_NODE', 'CDATA_SECTION_NODE', 'ENTITY_NODE',
                      'PROCESSING_INSTRUCTION_NODE', 'COMMENT_NODE', 'DOCUMENT_NODE', 'DOCUMENT_TYPE_NODE',
                      'NOTATION_NODE']

        def _print(ele, depth=0):
            s = ' ' * depth
            s += 'name: ' + ele.node_name + ', '
            s += 'type: ' + node_types[ele.node_type] + ', '
            s += 'value: ' + repr(ele.node_value) + ', '
            s += 'attrs: ['
            if ele.attributes:
                for i in range(ele.attributes.length):
                    s += ele.attributes.item(i).name + ', '
            s += ']'
            print(s)

            for child in ele.child_nodes:
                _print(child, depth + 2)

        xml_file_path = '../samples/test.xml'
        dom = xml.dom.minidom.parse(xml_file_path)
        _print(dom)


    def test_sax():
        class TestSaxHandler(xml.sax.handler.ContentHandler):
            def start_document(self):
                print('startDocument: ')

            def start_element(self, name, attrs):
                print('startElement: ', name)

            def end_element(self, name):
                print('endElement: ', name)

        xml_file_path = '../samples/test.xml'
        parser = xml.sax.make_parser()
        handler = TestSaxHandler()
        parser.set_content_handler(handler)
        parser.parse(open(xml_file_path))


    def test_readOgreMeshFileAsMesh():
        mesh_file_path = '../samples/woody2_15.mesh.xml'
        mesh = read_ogre_mesh_file_as_mesh(mesh_file_path, .01)

        viewer = ysv.SimpleViewer()
        viewer.doc.add_renderer('mesh', yr.MeshRenderer(mesh))
        viewer.doc.add_object('mesh', mesh)

        viewer.start_timer(1 / 30.)
        viewer.show()
        Fl.run()


    def test_readOgreSkeletonFile_Skeleton():
        #        mesh_file_path = '../samples/woody2_15.mesh.xml'
        mesh_file_path = '../samples/physics2_woody_binding1.mesh.xml'
        mesh = read_ogre_mesh_file_as_mesh(mesh_file_path, .01)

        #        skeleton_file_path = '../samples/woody2_15.skeleton.xml'
        skeleton_file_path = '../samples/physics2_woody_binding1.skeleton.xml'
        joint_skeleton, initial_rs = read_ogre_skeleton_file__skeleton(skeleton_file_path, .01)

        skeleton_posture = ym.JointPosture(joint_skeleton)
        skeleton_posture.init_local_rs(initial_rs)
        #        skeleton_posture.init_local_rs()
        skeleton_motion = ym.Motion([skeleton_posture])

        viewer = ysv.SimpleViewer()
        viewer.doc.add_motion(skeleton_motion)
        viewer.doc.add_renderer('skeleton', yr.JointMotionRenderer(skeleton_motion, (0, 0, 255), yr.LINK_LINE))
        viewer.doc.add_renderer('mesh', yr.MeshRenderer(mesh))

        viewer.start_timer(1 / 30.)
        viewer.show()
        Fl.run()


    def test_readOgreSkeletonFile_SkeletonAnimation():
        mesh_file_path = '../samples/physics2_woody_binding1.mesh.xml'
        mesh = read_ogre_mesh_file_as_mesh(mesh_file_path, .01)

        #        skeleton_file_path = '../samples/woody2_15.skeleton.xml'
        skeleton_file_path = '../samples/physics2_woody_binding1.skeleton.xml'
        joint_motions = read_ogre_skeleton_file__skeleton_animations(skeleton_file_path, .01)

        viewer = ysv.SimpleViewer()
        for i in range(len(joint_motions)):
            viewer.doc.add_motion(joint_motions[i])
            viewer.doc.add_renderer(joint_motions[i].resource_name,
                                    yr.JointMotionRenderer(joint_motions[i], (0, 0, 255), yr.LINK_LINE))
        viewer.doc.add_renderer('mesh', yr.MeshRenderer(mesh))

        def extra_draw_callback():
            frame = viewer.get_current_frame()
            for i in range(joint_motions[0][0].skeleton.get_element_num()):
                ygh.draw_point(joint_motions[0][frame].get_position(i))

        viewer.set_extra_draw_callback(extra_draw_callback)

        viewer.start_timer(1 / 30.)
        viewer.show()
        Fl.run()


    def test_readOgreMeshFileAsSkinMesh():
        skeleton_file_path = '../samples/woody2_15.skeleton.xml'

        #        joint_skeleton, initial_r_map = read_ogre_skeleton_file__skeleton(skeleton_file_path, .1)
        #        joint_motions = read_ogre_skeleton_file__skeleton_animations(skeleton_file_path, .1)
        joint_skeleton, initial_rs, joint_motions = read_ogre_skeleton_file(skeleton_file_path, .01)

        mesh_file_path = '../samples/woody2_15.mesh.xml'
        skin_mesh = read_ogre_mesh_file_as_skin_mesh(mesh_file_path, joint_skeleton, initial_rs, .01)

        joint_motion = yf.read_bvh_file('../samples/wd2_WalkSameSame00.bvh', .01)

        viewer = ysv.SimpleViewer()
        #        for i in range(len(joint_motions)):
        #            viewer.doc.add_motion(joint_motions[i])
        #            viewer.doc.add_renderer(joint_motions[i].resource_name, yr.JointMotionRenderer(joint_motions[i], (0, 0, 255), yr.LINK_LINE))
        viewer.doc.add_renderer('jointMotion', yr.JointMotionRenderer(joint_motion, (0, 0, 255), yr.LINK_BONE))
        viewer.doc.add_object('jointMotion', joint_motion)
        viewer.doc.add_renderer('skinMesh', yr.MeshRenderer(skin_mesh))

        def pre_frame_callback(frame):
            skin_mesh.update(joint_motion[frame])

        viewer.set_pre_frame_callback(pre_frame_callback)

        viewer.start_timer(1 / 30.)
        viewer.show()
        Fl.run()


    def test_readOgreDataFiles():
        mesh_file_path = '../samples/physics2_woody_binding1.mesh.xml'
        skeleton_file_path = '../samples/physics2_woody_binding1.skeleton.xml'
        skin_mesh, joint_motions = read_ogre_data_files(mesh_file_path, .01, skeleton_file_path)

        for joint_posture in joint_motions[0]:
            joint_posture.update_global_t()

        viewer = ysv.SimpleViewer()
        for i in range(len(joint_motions)):
            viewer.doc.add_object('ys_motion%d' % i, joint_motions[i])
            viewer.doc.add_renderer('ys_motion%d' % i,
                                    yr.JointMotionRenderer(joint_motions[i], (0, 0, 255), yr.LINK_LINE))
        viewer.doc.add_renderer('skinMesh', yr.MeshRenderer(skin_mesh))

        def pre_frame_callback(frame):
            skin_mesh.update(joint_motions[0][frame])

        viewer.set_pre_frame_callback(pre_frame_callback)

        viewer.start_timer(1 / 30.)
        viewer.show()
        Fl.run()


    def test_compare_skeletonanimation_vs_bvhmotion():
        mesh_file_path = '../samples/physics2_woody_binding1.mesh.xml'
        skeleton_file_path = '../samples/physics2_woody_binding1.skeleton.xml'
        skeleton_mesh, skeleton_motions = read_ogre_data_files(mesh_file_path, .01, skeleton_file_path)
        skeleton_motion = skeleton_motions[0]
        ysu.merge_points(skeleton_mesh)

        bvh_motion = yf.read_bvh_file('../samples/wd2_WalkSameSame00.bvh', .01)
        bvh_mesh = copy.deepcopy(skeleton_mesh)
        #        bvh_mesh.initialize(bvh_motion[0])

        viewer = ysv.SimpleViewer()
        viewer.doc.add_renderer('skeletonMotion', yr.JointMotionRenderer(skeleton_motion, (0, 0, 255), yr.LINK_LINE))
        viewer.doc.add_motion2('skeletonMotion', skeleton_motion)
        viewer.doc.add_renderer('skeletonMesh', yr.MeshRenderer(skeleton_mesh, (255 * .5, 255 * .5, 255)))

        viewer.doc.add_renderer('bvhMotion', yr.JointMotionRenderer(bvh_motion, (0, 255, 0), yr.LINK_LINE))
        viewer.doc.add_motion2('bvhMotion', bvh_motion)
        viewer.doc.add_renderer('bvhMesh', yr.MeshRenderer(bvh_mesh, (255 * .5, 255, 255 * .5)))

        def pre_frame_callback(frame):
            if frame < len(skeleton_motion):
                skeleton_mesh.update(skeleton_motion[frame])
            if frame < len(bvh_motion):
                bvh_mesh.update(bvh_motion[frame])

        viewer.set_pre_frame_callback(pre_frame_callback)

        viewer.start_timer(1 / 30.)
        viewer.show()

        Fl.run()


    #    test_sax()
    #    test_dom()

    #    test_readOgreMeshFileAsMesh()
    #    test_readOgreSkeletonFile_Skeleton()
    #    test_readOgreSkeletonFile_SkeletonAnimation()
    test_readOgreMeshFileAsSkinMesh()
# test_readOgreDataFiles()
#    test_compare_skeletonanimation_vs_bvhmotion()
