## Installation
Since [Dask][1] is the productive parallelization library you need a [Dask][1] worker pool on your system. For stand-alone use, you must take care of your own [Dask] [1] setup, which is not covered here but can be found in their documentation. Because it helps to understand the parallelization scheme, the most basic setup for a multinode cluster will be explained:

Connect to the node from which you start your experiments later on and launch the dask scheduler which will directly print the IP and port.

```bash
$ dask-scheduler
Scheduler at:   tcp://192.0.0.100:8786
```
Thereafter connect to the nodes you want to become workers and start dask workers providing the ip adress and port of the node that hosts dask scheduler.

```bash
$ dask-worker tcp://192.0.0.100:8786
Start worker at:  tcp://192.0.0.1:12345
Registered to:    tcp://192.0.0.100:8786

$ dask-worker tcp://192.0.0.100:8786
Start worker at:  tcp://192.0.0.2:40483
Registered to:    tcp://192.0.0.100:8786

$ dask-worker tcp://192.0.0.100:8786
Start worker at:  tcp://192.0.0.3:27372
Registered to:    tcp://192.0.0.100:8786
```

One very important fact which is not required by dask itself but comes with the implementation in this framework is the necessity to define two environment variables. These have to be known by the node from which you start your experiments.

```bash
DASK_MASTER_IP=192.0.0.100
DASK_MASTER_PORT=8786
```

On the [Carme][3] cluster the worker pool is automatically defined with one GPU per worker.

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


### Note
Please take notice that the cluster do share a common file system among its nodes. In practice this means that the absolute path you provide as ```experiment_dir``` (see [Experiment Definition](experiment_definition.md)) is accessible from all workers (nodes).

[1]: http://docs.dask.org/en/latest/index.html "DASK"
[3]: http://www.open-carme.org "Carme"
