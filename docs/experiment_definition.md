# Experiment Definition
The second class ```ParallelHyperparameterSearch``` of this framework, after defining the parameters, manages the setup of an experiment. It is done by a single dictionary providing settings for the class instantiation. A minimal example with all mandatory options follows

...


A new folder with name ```experiment_name``` will be created in the directory ```experiment_dir``` which must already exist. ```target_module_root_dir``` is the absolute path to the directory where your python module ```target_module_name``` with your custom function ```target_function_name``` can be found (see [Preparation of the Target Function](preparation_of_the_target_function.md)).

```parameter_definitions_root_dir_in``` specifies the folder with the parameter definitions (see [Search Strategies](search_strategies.md)).

As ```parallelization``` you can choose between ```'local_processes'``` and ```'dask'``` (see [Parallelization Technique](parallelization_technique.md)).

## Optional Settings
There are some optional settings hidden with an default value.

### ```provide_worker_path```
To deal with possible output of the function to hard disc, an individual path for each function evaluation (parameter set) is provided by ```parameter['worker_save_path']```. To activate this feature just set the flag ```provide_worker_path``` in the experiment definition to ```True```. Now a folder named 'worker_out' in your experiment directory will be created. Therein each function evaluation makes a folder with the respective index of the evaluated parameter set (padded with zeros). An example experiment with affiliated function demonstrates the usage and can be found in examples.

.. literalinclude:: ../../examples/worker_out_demo_func.py
   :caption: examples/worker_out_demo_func.py

.. literalinclude:: ../../examples/worker_out_demo.py
   :caption: examples/worker_out_demo.py

### ```redirect_stdout```
In case the target function uses print statements you want to have access to, set ```redirect_stdout``` to ```True```. This way the standard out is redirected to a text file located in the same folder as explained above.

### ```save_parameter_definitions```
The parameter definitions specified with  ```parameter_definitions_root_dir_in```

### ```bayesian_wait_for_all```
This option affects all function evaluations which have at least one parameter preceded by a bayesian optimization. If set to ```True``` the worker assigned with such a task sleeps until all previous tasks (in terms of the index of the parameter sets) are finished. Be aware that this will partially enforce a serialization causing massive decrease in parallel efficiency.

### ```l```
If ```parallelization``` is ```'local_processes'``` the maximum number of workers can be set with ```l```
