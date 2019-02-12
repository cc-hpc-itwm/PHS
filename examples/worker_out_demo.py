import phs.parallel_hyperparameter_search  # standalone import
# Make sure that python can import 'phs'.
# One way is to run the 'install.sh' script provided within this project.

# import CarmeModules.HyperParameterSearch.phs.parallel_hyperparameter_search as phs  # import on Carme
import phs.parameter_definition  # standalone import

inst = phs.parameter_definition.ParameterDefinition()

inst.set_data_types_and_order([('x', float), ('y', float), ('size', float)])

for i in range(20):
    inst.add_individual_parameter_set(
        set={'x': {'type': 'random', 'bounds': [0, 5], 'distribution': 'uniform', 'round_digits': 3},
             'y': {'type': 'random', 'bounds': [0, 5], 'distribution': 'uniform', 'round_digits': 3},
             'size': {'type': 'random', 'bounds': [10, 100], 'distribution': 'uniform', 'round_digits': 2}},
        prevent_duplicate=True)


parameter_definitions = inst.return_parameter_definitions()

hs = phs.parallel_hyperparameter_search.ParallelHyperparameterSearch(
    experiment_name='experiment_worker_out_demo',
    working_dir='/absolute/path/to/a/folder/your/experiments/should/be/saved',
    custom_module_root_dir='/absolute/path/to/root/dir/in/which/your/test_function/resides',
    custom_module_name='file_name_with_test_function_definition_(without_extension)',
    custom_function_name='worker_out_demo_func',
    parallelization='processes',
    parameter_definitions=parameter_definitions,
    provide_worker_path=True)

hs.start_execution()
