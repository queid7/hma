
import hmath.mm_math as mm
import motion.motion as mot


def get_contact_states(motion: mot.JointMotion, index, h_ref, v_ref, h_index = 2):
    """

    :param motion:
    :param index:
    :param h_ref:
    :param v_ref:
    :param h_index: index of height direction. if z-up, h_index is 2. if y-up h_index is 1
    :return:
    """
    contact_states = list()
    for f in range(len(motion)):
        pos = motion.get_position(index, f)
        vel = motion.get_velocity(index, f)
        if pos[h_index] < h_ref and mm.length(vel) < v_ref:
            contact_states.append(True)
        else:
            contact_states.append(False)

    return contact_states


def get_contact_timings(contact_states):
    """

    :param contact_states:
    :return: contact start timings, contact end timings
    """
    start_frames = []
    end_frames = []

    if contact_states[0] is True:
        start_frames.append(0)

    for i in range(1, len(contact_states)):
        if contact_states[i] != contact_states[i-1]:
            if contact_states[i] is True:
                start_frames.append(i)
            else:
                end_frames.append(i)

    if contact_states[len(contact_states)-1] is True:
        end_frames.append(len(contact_states)-1)

    return start_frames, end_frames


