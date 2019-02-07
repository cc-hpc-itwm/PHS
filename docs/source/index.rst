.. parallel_hyperparameter_search documentation master file, created by
   sphinx-quickstart on Wed Jan 23 14:53:52 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. highlight:: python


parallel_hyperparameter_search phs
==================================

*phs is an ergonomic tool for performing hyperparameter searches on numerous cumpute instances of any arbitrary python function. This is achieved with minimal modifications inside your custom function. Possible applications appear in numerical computations which strongly depend on hyperparameters such as machine learning.*

Functionality
-------------

- capable of all kinds of parameter types such as continuous or discrete numerical values, categorical values and even arbitrary python statements
- no binding to a particular python framework like TensorFlow or PyTorch
- possible search strategies are explicit specification, random search and Bayesian optimization
- no limitation to the number of hyperparameter
- parameter types and search strategies can be mixed for each parameter set as you like
- handy monitor and visualization functions for supervising the progress are already built-in
- (fault tolerance)

Parallelization Technique
-------------------------

At the moment two general types of parallelization are implemented, a third is under development. All of these share the same functionalities but differ in definition of workers and underlying technology of task scheduling. On the software side there is one lightweight master. It runs the parameter setup, manages the task scheduling to the workers and gathers the results immediately as they are completed. Some monitoring and visualization possibilities are already built-in. This way the user can observe and evaluate the progress. These functionalities can be customized, extended or performed only once after the last task.

Each function evaluation is done on a single worker. Even the Bayesian optimization for suggesting new parameter values is done on the workers themself. By this means the master is relieved and the prerequisites for a solid scaling behavior are ensured.

DASK
^^^^

`Dask <http://docs.dask.org/en/latest/index.html>`_ is a flexible library for parallel computing in Python. It provides dynamic task scheduling and 'Big Data' collections. Hereof futures are enough to schedule tasks to the workers. Dask is meant to be the parallelization backend for productive usage.

The definition and setup of one scheduler and multiple workers is done automatically in the background during the initialization routines of a multinode job on the Carme Cluster. Currently two workers are started on each node. Every worker sees one of the two GPUs of a node exclusively, while owning 4 CPU cores each. This static environment will be customizable to meet different use cases in the future.

Processes
^^^^^^^^^

Beside Dask native processes of the Python built-in concurrent.futures module is implemented as an alternative back end. It provides the same functionalities and user experience. Local processes serve as workers which means that the CPU cores of one machine can be utilized exclusively. The intention of this kind of computing resources is less on the computation heavy use in terms of production but rather on testing and debugging especially when no HPC system is available. But taking CPU only function evaluations into account the processes version can also be utilized in a meaningful manner.

.. toctree::

   installation
   quick_start

.. toctree::

   experiment_definition
   parameter_definition

.. toctree::

   preparation_of_the_function


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
