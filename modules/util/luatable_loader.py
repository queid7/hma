import pickle

import sys
if '..' not in sys.path:
    sys.path.append('..')
# =======================================================================
# need lupa
# https://pypi.python.org/pypi/lupa
# =======================================================================

import lupa
from lupa import LuaRuntime

lua = LuaRuntime(unpack_returned_tuples=True)


def lua_table_to_dict(lua_table):
    result = dict()
    for i in lua_table:
        result[i] = lua_table[i]
        if lupa.lua_type(result[i]) is 'table':
            result[i] = lua_table_to_dict(result[i])
    return result


def read_lua_table_file(lua_table_file_path):
    lua_table = lua.eval('dofile("'+lua_table_file_path+'")')
    result = lua_table_to_dict(lua_table)
    return result


def save_dict(dict_file_path, dict_data):
    dictfile = open(dict_file_path, 'wb')
    pickle.dump(dict_data, dictfile)
    dictfile.close()


def save_dict_from_lua_table_file(dict_file_path, lua_table_file_path):
    save_dict(dict_file_path, read_lua_table_file(lua_table_file_path))


# ======================================================================
# test
# ======================================================================


def test_read_lua_table():
    path = "/home/jo/Research/yslee/Resource/ys_motion/opensim/FullBody2_lee.luamscl"
    result = read_lua_table_file(path)
    for i in result:
        print(i, result[i])
    for i in result[1]:
        print(i, result[1][i])


def test_read_and_write():
    lua_path = "/home/jo/Research/yslee/Resource/ys_motion/opensim/FullBody2_lee.luamscl"
    dict_path = "dictResult"
    save_dict_from_lua_table_file(dict_path, lua_path)


def test_written_file():
    dict_path = "dictResult"
    dictfile = open(dict_path, 'rb')
    result = pickle.load(dictfile)
    dictfile.close()
    for i in result:
        print(i, result[i])
    for i in result[1]:
        print(i, result[1][i])


if __name__ == '__main__':
    test_read_lua_table()
    test_read_and_write()
    test_written_file()
