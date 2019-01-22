import phs.parallel_hyperparameter_search as phs  # standalone import
# Make sure that python can import 'phs'.
# One way is to run the 'install.sh' script provided within this project.
# import CarmeModules.HyperParameterSearch as phs  # import on Carme


hs = phs.ParallelHyperparameterSearch(
    experiment_name='experiment_griewank_1',
    working_dir='/absolute/path/to/a/folder/your/experiments/should/be/saved',
    custom_module_root_dir='/absolute/path/to/root/dir/in/which/your/test_function/resides',
    custom_module_name='file_name_with_test_function_definition_(without_extension)',
    custom_function_name='test_griewank',
    parallelization='processes',
    parameter_data_types={'x': float, 'y': float})

for i in range(20):
    hs.add_random_numeric_parameter(parameter_name='x', bounds=[-5, 5], distribution='uniform', round_digits=3)
    hs.add_random_numeric_parameter(parameter_name='y', bounds=[-5, 5], distribution='uniform', round_digits=3)
    hs.register_parameter_set()

for i in range(10):
    hs.add_bayesian_parameter(parameter_name='x', bounds=[-5, 5], round_digits=3)
    hs.add_bayesian_parameter(parameter_name='y', bounds=[-5, 5], round_digits=3)
    hs.register_parameter_set(ignore_duplicates=False)

hs.show_parameter_set()

hs.start_execution()
