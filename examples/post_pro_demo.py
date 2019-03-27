import phs.parameter_definition  # standalone import
import phs.parallel_hyperparameter_search  # standalone import
import phs.post_processing  # standalone import


def main():
    pardef = phs.parameter_definition.ParameterDefinition()

    pardef.set_data_types_and_order([('x', float), ('y', float)])

    pardef.add_individual_parameter_set(
        number_of_sets=20,
        set={'x': {'type': 'random', 'bounds': [-5, 5], 'distribution': 'uniform', 'round_digits': 3},
             'y': {'type': 'random', 'bounds': [-5, 5], 'distribution': 'uniform', 'round_digits': 3}},
        prevent_duplicate=True)

    pardef.add_individual_parameter_set(
        number_of_sets=20,
        set={'x': {'type': 'bayesian', 'bounds': [-5, 5], 'round_digits': 3},
             'y': {'type': 'bayesian', 'bounds': [-5, 5], 'round_digits': 3}})

    pardef.export_parameter_definitions(export_path='absolute/path/to/parent/folder/for/export')

    hs = phs.parallel_hyperparameter_search.ParallelHyperparameterSearch(
        **{'experiment_dir': '/absolute/path/to/parent/folder/your/experiments/should/be/saved',
           'experiment_name': 'post_pro_demo',
           'target_module_root_dir': '/absolute/path/to/root/dir/in/which/your/test_function/resides',
           'target_module_name': 'file_name_with_test_function_definition_(without_extension)',
           'target_function_name': 'test_griewank',
           'parameter_definitions_root_dir_in': 'absolute/path/to/parent/folder/for/import',
           'parallelization': 'local_processes',
           'local_processes_num_workers': 3,
           'bayesian_wait_for_all': True})

    hs.start_execution()

    post_pro = phs.post_processing.PostProcessing(
        experiment_dir='/absolute/path/to/an/experiment')

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


if __name__ == "__main__":
    main()
