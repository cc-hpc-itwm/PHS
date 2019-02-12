import math


def test_quadratic(parameter):
    exec(parameter['hyperpar'], globals(), globals())
    y = x*x
    return y


def test_rosenbrock(parameter):
    # x1 [-5,10]
    # x2 [-5,10]
    # min 0 at (1,1)
    exec(parameter['hyperpar'], globals(), globals())
    z = (1-x1)**2 + 100 * ((x2-x1**2))**2
    return z


def test_griewank(parameter):
    # x [-6,6]
    # y [-6,6]
    # min 0 at (0,0)
    exec(parameter['hyperpar'], globals(), globals())
    z = (x*x+y*y)/4000 - math.cos(x)*math.cos(y/math.sqrt(2)) + 1
    return z
