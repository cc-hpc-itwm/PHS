Parameter Definition
====================

The parameter definition is all about creating a table where each column represents a different parameter and each row represents a parameter set. Each set forms a unit and defines the input of one function evaluation. First you have to name all your parameters. Be careful to use names according to your custom function. Referring to the test_functions in :ref:`Quick Start` you would need the parameter ``x`` for ``test_quadratic``, ``x1``, ``x2`` for ``test_rosenbrock`` and ``x``, ``y`` for ``test_griewank``.

.. .. literalinclude:: ../../examples/test_functions.py
   :caption: examples/test_functions.py

The general procedure for creating the parameter table is as follows:

Consider one parameter set (row) and add a value for each parameter (column). There are several methods like random choice, explicit or bayesian to set a parameter. This has to be done for each parameter seperately which ensures maximum flexibility. To finalize the parameter set the method ``register_parameter_set()`` is used. Then the next parameter set can be defined.

Methods Defining a Parameter Table
----------------------------------

All methods expect the argument ``parameter_name`` which describes the parameter name as a string.

Explicit
^^^^^^^^
::

   add_explicit_parameter(parameter_name, value)

- ``value`` is assigned to ``parameter_name``.

Random
^^^^^^
::

   add_random_numeric_parameter(parameter_name, bounds, round_digits=None)

- A value is drawn from an uniform distribution between the ``bounds=[low high]``. As an option you can round the value to ``round_digits`` digits. ::

   add_random_parameter_from_list(parameter_name, lst)

- Randomly draw one element from the list ``lst``.

Bayesian
^^^^^^^^
::

   add_bayesian_parameter(parameter_name, bounds, round_digits=None)

- No value won't be set yet. Instead a placeholder is assigned to mark it as a bayesian task. A parameter set containing any bayesian placeholder is scheduled as normal. When it comes to executing all previously finished evaluations (parameter sets + results) are loaded by the worker. With these information the bayesian optimization algorithm is started to suggest values for all the parameters having a bayesian placeholder.

How the parameters are unpacked
-------------------------------

In each function evaluation a parameter set (row of the parameter table) is unpacked inside your custom function using the python built-in ``exec()`` function. Consider the parameter set

===== =====
x     size
===== =====
4.8   350.6
===== =====

which will result in the string ``parameter['hyperpar'] = 'x=4.8\nsize=350.6'``. When this string is executed it is equal to the statement ::

   x=4.8
   size=350.6

So ``exec()`` enables to replace any hard coded statement with a single string.

Parameter Data Types
--------------------

The data type of each parameter is set in the :ref:`Experiment Definition`. All numpy dtypes and in addition the special flag ``'expr'`` can be used.

Python Expression
^^^^^^^^^^^^^^^^^

If a parameter should contain an expression which returns a value or object when evaluated such as ``math.sin(x)`` there is a problem. Such an expression will be executed immediately what is not intended. To prevent this you have to use quotes to mask such statements as a string. Furthermore the data type ``'expr'`` indicates that the respective parameter has to be interpreted as a python expression and not as a string. Therefor the quotes are internally removed before the parameter set is executed by ``exec()``.

String
^^^^^^

A parameter can also contain a real string. Just declare the respective parameter data type as a ``str`` and mask the values with quotes. This way the quotes will remain when the parameter set is executed by ``exec()``::

   add_explicit_parameter(parameter_name='algo_flag', value='\'option_1\'')
   add_random_parameter_from_list(parameter_name='algo_flag', lst=['\'option_1\'', '\'option_2\'', '\'option_3\''])

Order of Parameters
-------------------

The order in which the data types are defined in the :ref:`Experiment Definition` is used as order for the parameters themselves. This can come into play if a parameter value depends on another parameter value.

Examples
--------

This section shows exemplary parameter definitions addressing different aspects.


Summary of Methods
^^^^^^^^^^^^^^^^^^

::

	hs.add_explicit_parameter(parameter_name='x', value=2.5)
	hs.add_explicit_parameter(parameter_name='y', value=-3.12)
	hs.register_parameter_set()

	hs.add_explicit_parameter(parameter_name='x', value=10.45)
	hs.add_explicit_parameter(parameter_name='y', value=3)
	hs.register_parameter_set()

	hs.add_random_numeric_parameter(parameter_name='x', bounds=[-2, 2], round_digits=1)
	hs.add_random_numeric_parameter(parameter_name='y', bounds=[-1, 5], round_digits=1)
	hs.register_parameter_set()

	for i in range(5):
	    hs.add_random_numeric_parameter(parameter_name='x', bounds=[-5, 5], round_digits=3)
	    hs.add_random_numeric_parameter(parameter_name='y', bounds=[-5, 5], round_digits=3)
	    hs.register_parameter_set()

	hs.add_random_parameter_from_list(parameter_name='x', lst=[1.1, 2.2, 3.3, 4.4])
	hs.add_random_parameter_from_list(parameter_name='y', lst=[0.1, 0.2, 0.3, 0.4])
	hs.register_parameter_set()

	for i in range(2):
	    hs.add_bayesian_parameter(parameter_name='x', bounds=[-5, 5], round_digits=3)
	    hs.add_bayesian_parameter(parameter_name='y', bounds=[-5, 5], round_digits=3)
	    hs.register_parameter_set()


=== ====== ======
_    x      y
=== ====== ======
0    2.500 -3.120
1   10.450  3.000
2   -1.800  0.700
3    4.945 -0.401
4   -1.362 -3.929
5   -2.639  3.784
6    1.965 -1.413
7    4.604 -1.133
8   -4.836 -3.846
9    0.000  0.000
10   0.000  0.000
=== ====== ======

Data Type ``expr`` and Order
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Consider an application where you want to evaluate different mathematical functions ``f_x`` with random inputs ``x``. Because the input has to be defined before evaluation of ``f_x`` can happen the order of your parameters must be ::
 
	parameter_data_types_and_order=[('x', float), ('f_x', 'expr')]

A possible target function could be ::

	def data_type_expr_demo(parameter):
	    exec(parameter['hyperpar'], globals(), globals())
	    return f_x

The following parameter definitions ::

	for i in range(5):
	    hs.add_random_numeric_parameter(parameter_name='x', bounds=[-5, 5], round_digits=3)
	    hs.add_explicit_parameter(parameter_name='f_x', value='math.sin(x)')
	    hs.register_parameter_set()

	for i in range(5):
	    hs.add_explicit_parameter(parameter_name='f_x', value='math.cos(x)')
	    hs.add_random_numeric_parameter(parameter_name='x', bounds=[-5, 5], round_digits=3)
	    hs.register_parameter_set()

	for i in range(5):
	    hs.add_random_numeric_parameter(parameter_name='x', bounds=[-5, 5], round_digits=3)
	    hs.add_explicit_parameter(parameter_name='f_x', value='math.exp(x)')
	    hs.register_parameter_set()

yield

== ======  ===========
_  x       f_x
== ======  ===========
0   3.314  math.sin(x)
1  -4.573  math.sin(x)
2  -0.647  math.sin(x)
3   4.599  math.sin(x)
4   1.283  math.sin(x)
5   4.540  math.cos(x)
6   4.056  math.cos(x)
7  -1.276  math.cos(x)
8   0.031  math.cos(x)
9  -3.041  math.cos(x)
10 -0.405  math.exp(x)
11  2.370  math.exp(x)
12  4.580  math.exp(x)
13 -2.803  math.exp(x)
14  0.021  math.exp(x)
== ======  ===========

Evaluation of parameter set ``7`` is equal to ::

	x=-1.276
	f_x=math.cos(x)


