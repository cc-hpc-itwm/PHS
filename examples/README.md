# Examples

Here you find a collection of examples addressing different aspects of the framework. The python scripts inside this directory contains the parameter and experiment definitions fitting the affiliated target function, which is predefined in the experiment. The utilized target functions are located in *func_def*.

To start the experiments you need to customize the arguments ```experiment_dir```, ```target_module_root_dir```, ```target_module_name```, ```target_function_name``` and ```parameter_definitions_root_dir_in``` of the experiment settings and the ```export_path``` of the parameters.

### quick_start.py
Simple example to get started with blackbox optimization using random and bayesian search strategy tackling the griewank test function.
+ [Quick Start](./docs/quick_start.md)

### par_def_simple.py
Basic explanation of the parameter definition.
+ [Search Strategies](./docs/search_strategies.md)

### par_def_simple_bayesian.py
Example definition of bayesian optimization search strategy.
+ [Search Strategies](./docs/search_strategies.md)

### data_types_and_order.py
Usage of different parameter data types including the special expression type ```'expr'``` is demonstrated. Here also the right order of the parameters plays a role. The transferred parameter set is printed and redirected.
+ [Data Types, Order and Transfer of Parameters](./docs/data_types_order_transfer.md)

### worker_out_demo.py
Demonstration of redirecting the standard output via ```print()``` and of providing a valid path for saving any data from inside the target function.
+ [Experiment Definition](./docs/experiment_definition.md)

### post_pro_demo.py
The post processing capabilities are shown with previous parameter and experiment setup.
+ [Post Processing](./docs/post_processing.md)
