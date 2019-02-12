Quick Start
===========

The easiest way to become familiar with the tool is to go through the following example of finding minima of the second order `Griewank function <https://en.wikipedia.org/wiki/Griewank_function>`_ which is a common test scenario for optimization algorithms. Code with respective output can be found in the examples folder.

Preparation of a target function
--------------------------------

- Declare your phyton script as a function with a single argument named ``parameter``
- Delete (or comment out) all hard coded parameter definitions you want to control with phs tool
- add ``exec(parameter['hyperpar'],globals(),globals())``
- return a meaningful parameter

.. literalinclude:: ../../examples/test_functions.py
   :caption: examples/test_functions.py

Definition of a phs experiment
------------------------------

- create a new script to define a phs experiment (customize the arguments ```working_dir, custom_module_root_dir, custom_module_name``` of the class instantiation):

.. literalinclude:: ../../examples/quick_start.py
   :caption: examples/quick_start.py
