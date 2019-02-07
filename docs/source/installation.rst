Installation
============


Standalone Installation
-----------------------

In order to use phs just clone this git repository to a local folder. Installation consists of executing the install.sh script, which appends the absolute path of your git repo permanently to the module search paths by creating a path configuration file (.pth). After that the following import should work::

   import phs.parallel_hyperparameter_search as phs  # standalone import

Usage on the Carme-Cluster
--------------------------

Since this project is a built-in package of `Carme <http://www.open-carme.org/>`_ it is usable with::

   import CarmeModules.HyperParameterSearch.phs.parallel_hyperparameter_search as phs

.. toctree::
   :maxdepth: 3
   :caption: fgf
