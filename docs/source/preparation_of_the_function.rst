Preparation of the function
===========================

One key feature of the phs framework is its ergonomic handling. Care was taken to ensure that the entry barrier for use is as low as possible. So the extent of necessary modifications is kept to a minimum. Besides there is also the possibility to manage all kind of possible output by your function.

Necessaray Modifications
------------------------

As briefly described in :ref:`Quick Start` there are a few modifications needed to get your python script ready for use in the phs framework:

- Declare your phyton script as a function with a single argument named ``parameter``
- Delete (or comment out) all hard coded parameter definitions you want to control with phs tool
- add ``exec(parameter['hyperpar'],globals(),globals())``
- return a meaningful parameter

Let's assume you want to use the following pseudo code within phs to vary parameter ``x`` and ``size``::

   x = 5.6
   y = 500
   size = 103.56

   # some calculations

   print result

The function has to be::

   def my_function(parameter):
       exec(parameter['hyperpar'], globals(), globals())
       y = 500

       # some calculations

       return result

That's all.

Management of Output
--------------------

To deal with possible output of the function an individual path for each function evaluation (parameter set) is provided by ``parameter['worker_save_path']``. To activate this feature just set the flag ``provide_worker_path=True`` in the experiment definition. Now a folder named 'worker_out' in your experiment directory will be created. Therein each function evaluation makes a folder with the respective index of the evaluated parameter set (padded with zeros). An example experiment with affiliated function demonstrates the usage and can be found in examples.

.. literalinclude:: ../../examples/worker_out_demo_func.py
   :caption: examples/worker_out_demo_func.py

.. literalinclude:: ../../examples/worker_out_demo.py
   :caption: examples/worker_out_demo.py
