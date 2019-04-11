def def_quick_start(experiment_dir, target_module_root_dir):
    import random as rd
    rd.seed(8877)
    import phs.parameter_definition  # standalone import
    import phs.experiment_definition  # standalone import
    import phs.compute_definition  # standalone import
    # Make sure that python can import 'phs'.
    # One way is to run the 'install.sh' script provided within this project.

    # import CarmeModules.HyperParameterSearch.phs.parallel_hyperparameter_search as phs  # import on Carme

    pardef = phs.parameter_definition.ParameterDefinition()

    pardef.set_data_types_and_order([('x', float), ('y', float)])

    pardef.add_individual_parameter_set(
        number_of_sets=2,
        set={'x': {'type': 'random', 'bounds': [-5, 5], 'distribution': 'uniform', 'round_digits': 3},
             'y': {'type': 'random_from_list', 'lst': [1.2, 3.4, 5.4, 6.3]}},
        prevent_duplicate=True)

    pardef.add_individual_parameter_set(
        number_of_sets=1,
        set={'x': {'type': 'bayesian', 'bounds': [-5, 5]},
             'y': {'type': 'bayesian', 'bounds': [-5, 5]}})

    expdef = phs.experiment_definition.ExperimentDefinition(
        experiment_dir=experiment_dir,
        target_module_root_dir=target_module_root_dir,
        target_module_name='basic_test_functions',
        target_function_name='test_griewank',
        parameter_definitions=pardef.get_parameter_definitions())

    compdef = phs.compute_definition.ComputeDefinition(
        experiment_dir=experiment_dir,
        parallelization='local_processes',
        local_processes_num_workers=1)

    compdef.start_execution()

    rd.seed()
