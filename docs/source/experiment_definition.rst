Experiment Definition
=====================

To define a custom experiment you have to set some mandatory variables when instantiating the ``ParallelHyperparameterSearch`` class. An embedded minimal example with all non optional arguments can be found in :ref:`Quick Start`:

.. literalinclude:: ../../examples/quick_start.py
   :caption: examples/quick_start.py
   :lines: 8-15

Explanations
------------

A new folder with name ``experiment_name`` will be created in the directory ``working_dir`` which must already exist. ``custom_module_root_dir`` is the absolute path to the directory where your python module ``custom_module_name`` with your custom function ``custom_function_name`` can be found.

As ``parallelization`` you can choose between ``'processes'`` and ``'dask'`` (s. :ref:`Parallelization Technique`).

``parameter_data_types_and_order`` is a list of tuples which defines the data types of all your parameters and their order. For more information about data types and their order read :ref:`Parameter Definition`.
