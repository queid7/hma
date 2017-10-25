import sys
import os
import re


def camel_to_sletter(filename):

    """ transform function names of camel case to that of small letters """

    o_filename = os.path.splitext(filename)[0] + "_converted.py"
    print("input : ", os.path.splitext(filename))
    print("output : ", o_filename)

    # _regex_camel = re.compile(r'[.\s()+=\-#][a-z]+[A-Z][a-zA-Z_]*')
    _regex_camel = re.compile(r'[.\s()+=\-#](?!gl)[a-z]+[A-Z][0-9a-zA-Z_]*')
    _regex_upper = re.compile(r'[A-Z][a-z]*')

    with open(filename, 'r') as i_file, open(o_filename, 'w') as o_file:
        for line in i_file:
            _camels = _regex_camel.findall(line)
            for _c in _camels:
                _camel = _c[1:]
                _uppers = _regex_upper.findall(_camel)
                print("origin : {0}".format(_camel))
                for _upper in _uppers:
                    _camel = _camel.replace(_upper, '_' + _upper.lower())
                    print("replaced : {0}".format(_camel))

                line = line.replace(_c, _c[0] + _camel)

            print("replaced line : {0}".format(line))
            o_file.write(line)


camel_to_sletter("../resource/ys_motion_loader.py")
camel_to_sletter("../resource/ys_ogre_data_loader.py")
