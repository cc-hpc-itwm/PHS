## Installation
Since [Dask][1] is the productive parallelization library you need a [Dask][1] worker pool on your system. For stand-alone use, you must take care of your own [Dask] [1] setup, which is not covered here but can be found in their documentation. On the [Carme][3] cluster the worker pool is automatically defined.

### Standalone Usage
In order to use phs just clone this git repository to a local folder. Installation consists of executing the ```install.sh``` script, which appends the absolute path of your git repo permanently to the module search paths by creating a path configuration file (.pth). After that the following import should work:

```import phs.parallel_hyperparameter_search as phs  # standalone import```

### Usage on the Carme-Cluster
Since this project is a built-in package of [Carme][3] it is usable with ```import CarmeModules.HyperParameterSearch.phs.parallel_hyperparameter_search as phs```.
