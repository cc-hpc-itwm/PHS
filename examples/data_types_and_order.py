import phs.parameter_definition  # standalone import
import phs.parallel_hyperparameter_search  # standalone import

pardef = phs.parameter_definition.ParameterDefinition()

pardef.set_data_types_and_order([('x', float), ('f', 'expr'), ('iterations', int), ('s', str)])

pardef.add_individual_parameter_set(
    number_of_sets=3,
    set={'x': {'type': 'random', 'bounds': [-5, 5], 'distribution': 'uniform', 'round_digits': 3},
         'f': {'type': 'random_from_list', 'lst': ['math.sin(x)', 'math.cos(x)', 'math.tan(x)']},
         'iterations': {'type': 'random', 'bounds': [1, 7], 'distribution': 'uniform', 'round_digits': 0},
         's': {'type': 'random_from_list', 'lst': ['string1', 'string2', 'string3']}},
    prevent_duplicate=True)

pardef.export_parameter_definitions(export_path='absolute/path/to/parent/folder/for/export')

hs = phs.parallel_hyperparameter_search.ParallelHyperparameterSearch(
    **{'experiment_dir': '/absolute/path/to/parent/folder/your/experiments/should/be/saved',
       'experiment_name': 'data_types_and_order',
       'target_module_root_dir': '/absolute/path/to/root/dir/in/which/your/test_function/resides',
       'target_module_name': 'file_name_with_test_function_definition_(without_extension)',
       'target_function_name': 'data_types_and_order_func',
       'parameter_definitions_root_dir_in': 'absolute/path/to/parent/folder/for/import',
       'parallelization': 'local_processes',
       'redirect_stdout': True})

hs.start_execution()
