# Preparation of the function

One key feature of the framework is its ergonomic handling. Care was taken to ensure that the entry barrier for use is as low as possible. So the extent of necessary modifications is kept to a minimum. Besides there is also the possibility to manage all kind of possible output by your function.

## Necessary Modifications

As briefly described in [Quick Start](quick_start.md) there are a few modifications needed to get your python script ready for use in the phs framework:

- Declare your phyton script as a function with a single argument named ``parameter``
- Delete (or comment out) all hard coded parameter definitions you want to control with phs tool
- add ``exec(parameter['hyperpar'],globals(),globals())``
- return a meaningful parameter

## Example
Let's assume you want to optimize the [Griewank function][2] within the framework.

```python
import math

x = 3.4
y = 7.56
z = (x*x+y*y)/4000-math.cos(x)*math.cos(y/math.sqrt(2))+1
```

Therefor the following adaptations are needed.

```python
import math

def griewank_func(parameter):
    # x = 3.4
    # y = 7.56
    exec(parameter['hyperpar'], globals(), globals())
    z = (x*x+y*y)/4000-math.cos(x)*math.cos(y/math.sqrt(2))+1
    return z
```

That's all.

[2]: https://en.wikipedia.org/wiki/Griewank_function "Griewank"
