import math

import sys

if '..' not in sys.path:
    sys.path.append('..')


# ===============================================================================
# manipulate functions
# ===============================================================================
# translate entire function graph
def translate(f, x_trans, y_trans):
    return lambda x: f(x - x_trans) + y_trans


# take function value at x=0 as if x=x_range[0], at x=1 as if x=x_range[1]
def domain(f, x_range):
    return lambda x: f((x * (x_range[1] - x_range[0])) + x_range[0])


# scale function graph; x: [0.,1.] -> x_range, y: [0.,1.] -> y_range
def scale(f, x_range, y_range=list([0., 1.])):
    return (
        lambda x: (y_range[1] - y_range[0]) * f(float(x - x_range[0]) / float(x_range[1] - x_range[0])) + y_range[0]) \
        if x_range[0] != x_range[1] else (lambda x: float(y_range[1] - y_range[0]) * .5)


# mirror function graph
def mirror(f, x_axis, y_axis):
    #    return lambda x: -function(x) + 2*y_axis
    #    return lambda x: function(-x + 2*x_axis)
    return lambda x: (-1 if y_axis is not None else 1) * f(-x + 2 * x_axis if x_axis is not None else x) + \
                     (2 * y_axis if y_axis is not None else 0)


# n functions, n-1 seperators
def concatenate(functions, seperators, x_range=list([0., 1.])):
    # build function domains
    # x_ranges = [None] * len(functions)
    x_ranges = []
    new_seperators = seperators[:]
    new_seperators.insert(0, x_range[0])
    new_seperators.append(x_range[1])
    for i in range(len(functions)):
        x_ranges.append([new_seperators[i], new_seperators[i + 1]])

    # build scaled functions
    # scaled_functions = [None] * len(functions)
    scaled_functions = []
    for i in range(len(functions)):
        scaled_functions.append(scale(functions[i], x_ranges[i]))

    def concatenated(x):
        # 0 < x < seperators[-1]
        for j in range(len(functions)):
            if x < x_ranges[j][1]:
                return scaled_functions[j](x)
        # seperators[-1] < x < 1
        return scaled_functions[-1](x)

    return concatenated


# ===============================================================================
# graph functions
# f:= X->Y, X = {x|x<is element of>R, 0<x<1}, Y = {y|y<is element of>R, 0<y<1}
# ===============================================================================
identity = lambda x: x
hermite2nd = lambda x: -2 * x * x * x + 3 * x * x
sine = lambda x: (math.sin(2. * x * math.pi - math.pi / 2) + 1) / 2.0
halfsine = scale(sine, (0., 2.))
zero = lambda x: 0.
one = lambda x: 1.
H1 = lambda t: -2 * t * t * t + 3 * t * t
H2 = lambda t: t * t * t - 2 * t * t + t
H3 = lambda t: t * t * t - t * t


if __name__ == '__main__':
    #   import operator as op
    import util.ysMatplotEx as ymp
    import util.ysPythonEx as pe


    def test_manipulate():
        x_draw_range = (-2, 2)
        y_draw_range = (-2, 2)

        plot = ymp.SmartPlot()
        plot.setXlimit(x_draw_range[0], x_draw_range[1])
        plot.setYlimit(y_draw_range[0], y_draw_range[1])
        X = pe.frange(x_draw_range[0], x_draw_range[1], .01)
        plot.setXdata('frames', X)

        #        x_range = (0,1); y_range = (0,1)
        #        plot.addYdata('translate', map(translate(sine, .1, .1), X))
        #        plot.addYdata('domain', map(domain(sine, [.2, .7]), X))
        #        plot.addYdata('translate * domain', map(translate(domain(sine, [.0, .5]), .1, .1), X))

        x_range = (0, 1)
        y_range = (0, 1)
        plot.addYdata('concatenate', list(map(concatenate([zero, hermite2nd, one], [1 / 3., 2 / 3.]), X)))

        #        x_range = (0,2); y_range = (0,.5)
        #        plot.addYdata('scale', map(scale(sine, x_range, y_range), X))
        #       plot.addYdata('domain', map(domain(sine, x_range), X))

        #        x_range = (0,1); y_range = (0,1)
        #        plot.addYdata('hermite2nd', map(hermite2nd, X))
        #        plot.addYdata('mirror', map(mirror(hermite2nd, .5, .0), X))
        #        plot.addYdata('mirror2', map(mirror(hermite2nd, None, .0), X))
        #        plot.addYdata('mirror3', map(mirror(hermite2nd, .5, None), X))

        plot.addXspans('x_range', [x_range])
        plot.addYspans('y_range', [y_range])
        plot.show()


    def test_graph_functions():
        x_draw_range = (0, 1)
        y_draw_range = (0, 1)

        plot = ymp.SmartPlot()
        plot.setXlimit(x_draw_range[0], x_draw_range[1])
        plot.setYlimit(y_draw_range[0], y_draw_range[1])

        X = pe.frange(x_draw_range[0], x_draw_range[1], .01)
        plot.setXdata('frames', X)

        plot.addYdata('identity', list(map(identity, X)))
        plot.addYdata('hermite2nd', list(map(hermite2nd, X)))
        plot.addYdata('halfsine', list(map(halfsine, X)))
        plot.addYdata('halfsineextended2', list(map(concatenate([zero, halfsine, one], [.25, .75]), X)))
        plot.addYdata('sine', list(map(sine, X)))
        plot.addYdata('zero', list(map(zero, X)))
        plot.addYdata('H1', list(map(H1, X)))
        plot.addYdata('H2', list(map(H2, X)))
        plot.addYdata('H3', list(map(H3, X)))

        plot.show()


    pass
    #    test_manipulate()
    test_graph_functions()
