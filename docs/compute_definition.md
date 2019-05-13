# Compute Definition

To start your experiment a single module which comes as the class ```ComputeDefinition``` is missing. To define a compute you need to have an experiment already set up (see [Experiment Definition](./docs/experiment_definition.md)). Your compute definition then builds upon that experiment by providing the ```experiment_dir``` which is the only mandatory setting. All further settings are optional and described down below.

In the following a minimal example is shown.

```python
import phs.compute_definition  # standalone import

compdef = phs.compute_definition.ComputeDefinition(
    experiment_dir='/absolute/path/to/folder/with/existing/experiment')

compdef.start_execution()
```

## Optional Settings
There are some optional settings hidden with an default value.

### ```parallelization```
As ```parallelization``` you can choose between ```'local_processes'``` (default) and ```'dask'``` (see [Parallelization Technique](parallelization_technique.md)).

### ```local_processes_num_workers```
If ```'local_processes'``` is chosen as ```parallelization``` the maximum number of parallel workers can be set with ```local_processes_num_workers```.

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
def main():
    import phs.parameter_definition  # standalone import
    import phs.experiment_definition  # standalone import
    import phs.compute_definition  # standalone import

    pardef = phs.parameter_definition.ParameterDefinition()

    pardef.set_data_types_and_order([('x', float), ('y', float), ('size', float)])

    pardef.add_individual_parameter_set(
        number_of_sets=20,
        set={'x': {'type': 'random', 'bounds': [0, 5], 'distribution': 'uniform', 'round_digits': 3},
             'y': {'type': 'random', 'bounds': [0, 5], 'distribution': 'uniform', 'round_digits': 3},
             'size': {'type': 'random', 'bounds': [10, 100], 'distribution': 'uniform', 'round_digits': 2}},
        prevent_duplicate=True)

    expdef = phs.experiment_definition.ExperimentDefinition(
        experiment_dir='/absolute/path/to/not/yet/existing/folder/your/experiments/should/be/saved',
        target_module_root_dir='/absolute/path/to/root/dir/in/which/your/test_function/resides',
        target_module_name='file_name_with_test_function_definition_(without_extension)',
        target_function_name='worker_out_demo_func',
        parameter_definitions=pardef.get_parameter_definitions())

    compdef = phs.compute_definition.ComputeDefinition(
        experiment_dir='/absolute/path/to/folder/with/existing/experiment',
        parallelization='local_processes',
        local_processes_num_workers=1,
        provide_worker_path=True,
        redirect_stdout=True)

    compdef.start_execution()


if __name__ == "__main__":
    main()
```

### ```bayesian_wait_for_all```
This option affects all function evaluations which have at least one parameter preceded by a bayesian optimization. If set to ```True``` the worker assigned with such a task sleeps until all previous tasks (in terms of the index of the parameter sets) are finished. Be aware that this will partially enforce a serialization causing massive decrease in parallel efficiency.


## Starting the experiment
To start the experiment just call the member method ```start_execution()```. The returned values of the target function together with the respective parameter set can be found in your specified experiment: ```'experiment_dir'/results/result_frame.csv```. Each result is appended in real time as it is completed. One monitoring suggestion is:

``` shell
watch -n 1 "(head -n 1; tail -n 10) < 'experiment_dir'/'experiment_name'/results/result_frame.csv"
```
