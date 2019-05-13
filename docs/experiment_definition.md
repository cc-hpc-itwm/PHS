# Experiment Definition
The class ```ExperimentDefinition``` is the second module of the framework. It manages the setup of an experiment which is done by a single class instantiation. An example with all settings follows

```python
import phs.experiment_definition  # standalone import

expdef = phs.experiment_definition.ExperimentDefinition(
    experiment_dir='/absolute/path/to/not/yet/existing/folder/your/experiments/should/be/saved',
    target_module_root_dir='/absolute/path/to/root/dir/in/which/your/test_function/resides',
    target_module_name='file_name_with_test_function_definition_(without_extension)',
    target_function_name='name_of_function_inside_target_module',
    parameter_definitions_root_dir_in='absolute/path/to/parent/folder/of/parameterdefinitions')
```

A new folder with name ```experiment_dir``` will be created. ```target_module_root_dir``` is the absolute path to the directory where your python module ```target_module_name``` with your custom function ```target_function_name``` can be found (see [Preparation of the Target Function](preparation_of_the_target_function.md)).

```parameter_definitions_root_dir_in``` specifies the folder with the parameter definitions exported beforehand (see [Search Strategies](search_strategies.md)).
