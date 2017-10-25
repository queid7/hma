from datetime import datetime
import operator as op


def frange(start, end=None, inc=None):
    """A range function, that does accept float increments..."""

    if end is None:
        end = start + 0.0
        start = 0.0

    if inc is None:
        inc = 1.0

    L = []
    while 1:
        next_ = start + len(L) * inc
        if inc > 0 and next_ >= end:
            break
        elif inc < 0 and next_ <= end:
            break
        L.append(next_)

    return L


def mrange(minvec, maxvec=None):
    if maxvec is None:
        maxvec = minvec
        minvec = [0] * len(maxvec)
    vec = list(minvec)
    unit_pos = len(vec) - 1
    max_unit = maxvec[unit_pos]
    _tuple = tuple
    while 1:
        if vec[unit_pos] == max_unit:
            i = unit_pos
            while vec[i] == maxvec[i]:
                vec[i] = minvec[i]
                i -= 1
                if i == -1:
                    return
                vec[i] += 1
        yield _tuple(vec)
        vec[unit_pos] += 1


def map_dict(func, dic1, dic2):
    dic = {}
    for key in dic1:
        dic[key] = func(dic1[key], dic2[key])
    return dic


def format_seq(seq, single_line=False):
    s = ''
    if single_line:
        s += '['
        for i in range(len(seq)):
            s += seq[i]
        s += ']\n'
    else:
        for i in range(len(seq)):
            s += '[%d]' % i + seq[i].__repr__() + '\n'
    return s


def print_seq(seq, single_line=False):
    if single_line:
        print('[', end=' ')
        for i in range(len(seq)):
            print(seq[i], end=' ')
        print(']')
    else:
        for i in range(len(seq)):
            print('[%d]' % i, seq[i])


def print_dict(dic, single_line=False):
    if single_line:
        print('{', end=' ')
        for key, value in list(dic.items()):
            print('%s' % repr(key), ':', value, ',', end=' ')
        print('}')
    else:
        for key, value in list(dic.items()):
            print('[%s]' % repr(key), value)


def update_object(object_, other_object_):
    # update_object
    object_.__dict__ = other_object_.__dict__


def get_log_time_string():
    return datetime.today().strftime('%y%m%d_%H%M%S')


def get_reverse_dict(dic):
    r_dic = {}
    for key, value in list(dic.items()):
        r_dic[value] = key
    return r_dic


# input :
# in_list == [10,20,30]
# out_list == [None,None,None,None,None,None]
# repeat_nums = [3,2,1]
# output :
# out_list == [10,10,10,20,20,30]
def repeat_list_elements(in_list, out_list, repeat_nums):
    index = 0
    for i in range(len(in_list)):
        for j in range(repeat_nums[i]):
            out_list[index] = in_list[i]
            index += 1


# input:
# in_list == [1,2,3,4,5,6]
# out_list == [None, None]
# sum_nums == [3,3]
# output:
# out_list == [6, 15]
def sum_list_elements(in_list, out_list, sum_nums, add_operation=op.iadd, additive_identity=0):
    index = 0
    for i in range(len(sum_nums)):
        _sum = additive_identity
        for j in range(sum_nums[i]):
            _sum = add_operation(_sum, in_list[index])
            index += 1
        out_list[i] = _sum


def make_flat_list(total_dof):
    return [None] * total_dof


def make_nested_list(dof_list):
    ls = [None] * len(dof_list)
    for i in range(len(dof_list)):
        ls[i] = [None] * dof_list[i]
    return ls


def flatten(nested_list, flat_list):
    i = 0
    for a in range(len(nested_list)):
        for b in range(len(nested_list[a])):
            flat_list[i] = nested_list[a][b]
            i += 1


def nested(flat_list, nested_list):
    i = 0
    for a in range(len(nested_list)):
        for b in range(len(nested_list[a])):
            nested_list[a][b] = flat_list[i]
            i += 1


if __name__ == "__main__":
    import operator as op


    def test_getLogTimeString():
        print(get_log_time_string())


    def test_frange():
        for i in frange(1.2, 5, 1.):
            print(i)


    def test_mrange():
        for i in mrange([2, 2, 1, 2]):
            print(i)

        # so the rather horrid
        for i in range(1):
            for j in range(2):
                for k in range(3):
                    for l in range(4):
                        print(i, j, k, l)
        # reduces to
        for i, j, k, l in mrange([1, 2, 3, 4]):
            print(i, j, k, l)


    class A:
        def __init__(self, name):
            self.name = name

        def __str__(self):
            return self.name


    def test_print_seq():
        ls = []
        for i in range(10):
            ls.append(A('name_%s' % str(i)))
        print(ls)
        print_seq(ls)


    def test_print_dict():
        dic = {}
        for i in range(10):
            dic[str(i)] = A('name_%s' % str(i))
        # dic[i] = A('name_%s'%str(i))
        print(dic)
        print_dict(dic)


    def test_updateObject():
        a = A('a')
        b = A('b')
        print(a, b)
        update_object(a, b)
        print(a, b)


    def test_map():
        def and_list(ls1, ls2):
            if len(ls1) != len(ls2):
                raise ValueError
            ls = [None] * len(ls1)
            for i in range(len(ls1)):
                ls[i] = ls1[i] and ls2[i]
            return ls

        ls0 = [1, 0, 1]
        ls1 = [1, 1, 0]

        print('list')
        print(list(map(lambda x, y: x and y, ls0, ls1)))
        print(list(map(op.and_, ls0, ls1)))
        print(and_list(ls0, ls1))
        print()

        dic1 = {0: 0, 1: 1, 2: 2}
        dic2 = {1: 1, 2: 2, 0: 0}
        dic3 = {2: 2, 0: 0, 'a': 4, 1: 1}
        del dic3['a']

        print('dict')
        print('dic1', dic1)
        print('dic2', dic2)
        print('dic3', dic3)
        print(list(map(lambda x, y: x + y, list(dic1.values()), list(dic2.values()))))
        print(list(map(lambda x, y: x + y, list(dic1.values()), list(dic3.values()))))
        print(map_dict(lambda x, y: x + y, dic1, dic3))


    def test_enum():
        class Event:
            EV_addRenderer = 0
            EV_setRendererVisible = 1
            EV_addObject = 2
            EV_selectObjectElement = 3
            EV_selectObject = 4

            text = get_reverse_dict(locals())

        print(Event.text)


    pass
    #    test_getLogTimeString()
    #    test_map()
    #    test_frange()
    #    test_updateObject()
    #    test_print_dict()
    #    test_print_seq()
    test_mrange()
    test_enum()
