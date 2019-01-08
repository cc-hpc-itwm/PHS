import math as ma

def test_quadratic(parameter):
    exec(parameter['hyperpar'],globals(),globals())
    y = x*x
    return y

def test_rosenbrock(parameter):
    # x [-5,10]
    # y [-5,10]
    # min 0 at (1,1)
    exec(parameter['hyperpar'],globals(),globals())
    z = (1-x)**2 + 100* ((y-x**2))**2
    return z

def test_griewank(parameter):
    # x [-6,6]
    # y [-6,6]
    # min 0 at (0,0)
    exec(parameter['hyperpar'],globals(),globals())
    z = (x*x+y*y)/4000 - ma.cos(x)*ma.cos(y/ma.sqrt(2)) + 1
    return z