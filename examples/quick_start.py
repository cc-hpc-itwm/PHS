import phs.parallel_hyperparameter_search  # standalone import
# Make sure that python can import 'phs'.
# One way is to run the 'install.sh' script provided within this project.

# import CarmeModules.HyperParameterSearch.phs.parallel_hyperparameter_search as phs  # import on Carme
import phs.parameter_definition  # standalone import

inst = phs.parameter_definition.ParameterDefinition()

inst.set_data_types_and_order([('x', float), ('y', float)])

inst.add_individual_parameter_set(
    number_of_sets=20,
    set={'x': {'type': 'random', 'bounds': [-5, 5], 'distribution': 'uniform', 'round_digits': 3},
         'y': {'type': 'random_from_list', 'lst': [1.2, 3.4, 5.4, 6.3]}},
    prevent_duplicate=True)

inst.add_individual_parameter_set(
    number_of_sets=10,
    set={'x': {'type': 'bayesian', 'bounds': [-5, 5], 'round_digits': 3},
         'y': {'type': 'bayesian', 'bounds': [-5, 5], 'round_digits': 3}})

inst.export_parameter_definitions(export_path='absolute/path/to/folder/with/parameter_definitions')


hs = phs.parallel_hyperparameter_search.ParallelHyperparameterSearch(
    experiment_name='experiment_griewank_1',
    working_dir='/absolute/path/to/a/folder/your/experiments/should/be/saved',
    custom_module_root_dir='/absolute/path/to/root/dir/in/which/your/test_function/resides',
    custom_module_name='file_name_with_test_function_definition_(without_extension)',
    custom_function_name='test_griewank',
    parameter_definitions_root_dir_in='absolute/path/to/folder/with/parameter_definitions',
    parallelization='processes')

hs.start_execution()
