import phs.parallel_hyperparameter_search  # standalone import
# Make sure that python can import 'phs'.
# One way is to run the 'install.sh' script provided within this project.

# import CarmeModules.HyperParameterSearch.phs.parallel_hyperparameter_search as phs  # import on Carme
import phs.parameter_definition  # standalone import

par_def = phs.parameter_definition.ParameterDefinition()

par_def.set_data_types_and_order([('x', float), ('y', float), ('size', float)])

for i in range(20):
    par_def.add_individual_parameter_set(
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
       'parallelization': 'local_processes'
       'provide_worker_path': True,
       'redirect_stdout': True})

hs.start_execution()
