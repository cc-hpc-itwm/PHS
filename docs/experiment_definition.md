# Experiment Definition
The second class ```ParallelHyperparameterSearch``` of this framework, after defining the parameters, manages the setup of an experiment. It is done by a single dictionary providing settings for the class instantiation. A minimal example with all mandatory options follows

```python
import phs.parallel_hyperparameter_search  # standalone import

hs = phs.parallel_hyperparameter_search.ParallelHyperparameterSearch(
    **{'experiment_dir': '/absolute/path/to/parent/folder/your/experiments/should/be/saved',
       'experiment_name': 'experiment_griewank_1',
       'target_module_root_dir': '/absolute/path/to/root/dir/in/which/your/test_function/resides',
       'target_module_name': 'file_name_with_test_function_definition_(without_extension)',
       'target_function_name': 'name_of_function_inside_target_module',
       'parameter_definitions_root_dir_in': 'absolute/path/to/parent/folder/for/import',
       'parallelization': 'local_processes'})

hs.start_execution()
```

A new folder with name ```experiment_name``` will be created in the directory ```experiment_dir``` which must already exist. ```target_module_root_dir``` is the absolute path to the directory where your python module ```target_module_name``` with your custom function ```target_function_name``` can be found (see [Preparation of the Target Function](preparation_of_the_target_function.md)).

```parameter_definitions_root_dir_in``` specifies the folder with the parameter definitions (see [Search Strategies](search_strategies.md)).

As ```parallelization``` you can choose between ```'local_processes'``` and ```'dask'``` (see [Parallelization Technique](parallelization_technique.md)).

## Optional Settings
There are some optional settings hidden with an default value.

### ```provide_worker_path```
To deal with possible output of the function to hard disc, an individual path for each function evaluation (parameter set) is provided by ```parameter['worker_save_path']```. To activate this feature just set the flag ```provide_worker_path``` in the experiment definition to ```True```. Now a folder named 'worker_out' in your experiment directory will be created. Therein each function evaluation makes a folder with the respective index of the evaluated parameter set (padded with zeros).

### ```redirect_stdout```
In case the target function uses print statements you want to have access to, set ```redirect_stdout``` to ```True```. This way the standard out is redirected to a text file located in the same folder as explained above. An example experiment with affiliated target function demonstrates the usage and can be found in examples.

```python
import matplotlib.pyplot as plt


def worker_out_demo_func(parameter):
    exec(parameter['hyperpar'], globals(), globals())
    print('\'x\' is {0}, \'y\' is {1} and \'size\' is {2}' .format(x, y, size))
    plt.switch_backend('agg')
    plt.ioff()
    fig = plt.figure(figsize=(10, 2))
    ax = fig.add_subplot(1, 1, 1)
    ax.scatter(x, y, s=size)
    fig.savefig(parameter['worker_save_path'] + 'scatter_plot.pdf')
    plt.close(fig)

    return x * y + size
```

```python
import phs.parallel_hyperparameter_search  # standalone import
import phs.parameter_definition  # standalone import

pardef = phs.parameter_definition.ParameterDefinition()

pardef.set_data_types_and_order([('x', float), ('y', float), ('size', float)])

pardef.add_individual_parameter_set(
    number_of_sets=20,
    set={'x': {'type': 'random', 'bounds': [0, 5], 'distribution': 'uniform', 'round_digits': 3},
         'y': {'type': 'random', 'bounds': [0, 5], 'distribution': 'uniform', 'round_digits': 3},
         'size': {'type': 'random', 'bounds': [10, 100], 'distribution': 'uniform', 'round_digits': 2}},
    prevent_duplicate=True)

pardef.export_parameter_definitions(export_path='absolute/path/to/parent/folder/for/export')


hs = phs.parallel_hyperparameter_search.ParallelHyperparameterSearch(
    **{'experiment_dir': '/absolute/path/to/parent/folder/your/experiments/should/be/saved',
       'experiment_name': 'worker_out_demo',
       'target_module_root_dir': '/absolute/path/to/root/dir/in/which/your/test_function/resides',
       'target_module_name': 'file_name_with_test_function_definition_(without_extension)',
       'target_function_name': 'worker_out_demo_func',
       'parameter_definitions_root_dir_in': 'absolute/path/to/parent/folder/for/import',
       'parallelization': 'local_processes',
       'provide_worker_path': True,
       'redirect_stdout': True})

hs.start_execution()
```

### ```save_parameter_definitions```
The parameter definitions specified with  ```parameter_definitions_root_dir_in```

### ```bayesian_wait_for_all```
This option affects all function evaluations which have at least one parameter preceded by a bayesian optimization. If set to ```True``` the worker assigned with such a task sleeps until all previous tasks (in terms of the index of the parameter sets) are finished. Be aware that this will partially enforce a serialization causing massive decrease in parallel efficiency.

### ```local_processes_num_workers```
If ```parallelization``` is ```'local_processes'``` the maximum number of workers can be set with ```local_processes_num_workers```.

## Starting the experiment
To start the experiment just call the member method ```start_execution()```. The returned values of the target function together with the respective parameter set can be found in your specified experiment: ```'experiment_dir'/'experiment_name'/results/result_frame.csv```. Each result is appended in real time as it is completed. One monitoring suggestion is:

``` shell
watch -n 1 "(head -n 1; tail -n 10) < 'experiment_dir'/'experiment_name'/results/result_frame.csv"
```
