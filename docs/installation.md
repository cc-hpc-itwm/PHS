## Installation
Since [Dask][1] is the productive parallelization library you need a [Dask][1] worker pool on your system. For stand-alone use, you must take care of your own [Dask] [1] setup, which is not covered here but can be found in their documentation. On the [Carme][3] cluster the worker pool is automatically defined with one GPU per worker.

### Standalone Usage
In order to use phs just clone this git repository to a local folder. Installation consists of executing the ```install.sh``` script, which appends the absolute path of your git repo permanently to the module search paths by creating a path configuration file (.pth). Thereafter importing the modules of phs should work by using:

```python
import phs.parameter_definition
import phs.experiment_definition
import phs.compute_definition
```

### Usage on the Carme-Cluster
Since this project is a built-in package of [Carme][3] it is usable with
 ```python
import CarmeModules.HyperParameterSearch.phs.parameter_definition
import CarmeModules.HyperParameterSearch.phs.experiment_definition
import CarmeModules.HyperParameterSearch.phs.compute_definition
```


[1]: http://docs.dask.org/en/latest/index.html "DASK"
[3]: http://www.open-carme.org "Carme"
