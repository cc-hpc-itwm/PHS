def def_post_pro_demo(experiment_dir, target_module_root_dir):
    import random as rd
    rd.seed(435)
    import phs.parameter_definition  # standalone import
    import phs.experiment_definition  # standalone import
    import phs.compute_definition  # standalone import
    import phs.post_processing  # standalone import
    # Make sure that python can import 'phs'.
    # One way is to run the 'install.sh' script provided within this project.

    # import CarmeModules.HyperParameterSearch.phs.parallel_hyperparameter_search as phs  # import on Carme

    pardef = phs.parameter_definition.ParameterDefinition()

    pardef.set_data_types_and_order([('x', float), ('y', float)])

    pardef.add_individual_parameter_set(
        number_of_sets=2,
        set={'x': {'type': 'random', 'bounds': [-5, 5], 'distribution': 'uniform', 'round_digits': 3},
             'y': {'type': 'random', 'bounds': [-5, 5], 'distribution': 'uniform', 'round_digits': 3}},
        prevent_duplicate=True)

    pardef.add_individual_parameter_set(
        number_of_sets=2,
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
        local_processes_num_workers=1,
        redirect_stdout=False,
        provide_worker_path=False,
        bayesian_wait_for_all=True)

    compdef.start_execution()

    post_pro = phs.post_processing.PostProcessing(experiment_dir=experiment_dir)

    post_pro.plot_3d(name='plot_xyr_post',
                     first='x',
                     second='y',
                     third='result',
                     contour=True,
                     animated=True,
                     animated_step_size=1,
                     animated_fps=1)

    post_pro.result_evolution(name='evo_post')
    post_pro.create_worker_timeline(name='worker_timeline_post')
    post_pro.create_parameter_combination(name='parameter_combination_post')

    rd.seed()
