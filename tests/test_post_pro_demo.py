import random as rd
import os
from pathlib import Path
import filecmp
import tempfile
import phs.parameter_definition
import phs.parallel_hyperparameter_search
import phs.post_processing
import phs.utils


def test_post_pro_demo():
    with tempfile.TemporaryDirectory(dir=os.path.dirname(__file__) + '/tmp') as tmpdir:

        rd.seed(435)

        pardef = phs.parameter_definition.ParameterDefinition()

        pardef.set_data_types_and_order([('x', float), ('y', float)])

        pardef.add_individual_parameter_set(
            number_of_sets=20,
            set={'x': {'type': 'random', 'bounds': [-5, 5], 'distribution': 'uniform', 'round_digits': 3},
                 'y': {'type': 'random', 'bounds': [-5, 5], 'distribution': 'uniform', 'round_digits': 3}},
            prevent_duplicate=True)

        pardef.add_individual_parameter_set(
            number_of_sets=20,
            set={'x': {'type': 'bayesian', 'bounds': [-5, 5], 'round_digits': 2},
                 'y': {'type': 'bayesian', 'bounds': [-5, 5], 'round_digits': 2}})

        pardef.export_parameter_definitions(
            export_path=tmpdir + '/par')

        hs = phs.parallel_hyperparameter_search.ParallelHyperparameterSearch(
            **{'experiment_dir': tmpdir,
               'experiment_name': 'exper',
               'target_module_root_dir': str(Path(os.path.dirname(__file__)).parent) + '/examples/func_def',
               'target_module_name': 'basic_test_functions',
               'target_function_name': 'test_griewank',
               'parameter_definitions_root_dir_in': tmpdir + '/par',
               'parallelization': 'local_processes',
               'local_processes_num_workers': 1,
               'bayesian_wait_for_all': True})

        hs.start_execution()

        post_pro = phs.post_processing.PostProcessing(
            experiment_dir=tmpdir + '/exper')

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

        dcmp = filecmp.dircmp(
            os.path.dirname(__file__) + '/fixtures/fix_post_pro_demo',
            tmpdir,
            ignore=['additional_information_frame.csv', 'basic_test_functions.py',
                    'worker_timeline_post.png', 'worker_timeline_post.pdf',
                    'evo_post.pdf', 'parameter_combination_post.pdf'])

        # cmp.report_full_closure()
        print(phs.utils.comp_files_and_dirs(dcmp))
        # compared directories should be identical what means empty cmp.diff_files
        rd.seed()   # reseed with current system time
        assert not phs.utils.comp_files_and_dirs(dcmp)


'''fixture paths
    export_path = '/home/habelitz/parallel_hyperparameter_search/tests/fixtures/fix_post_pro_demo/par'

    'experiment_dir':
    '/home/habelitz/parallel_hyperparameter_search/tests/fixtures/fix_post_pro_demo'
    'target_module_root_dir':
    '/home/habelitz/parallel_hyperparameter_search/examples/func_def'
    'parameter_definitions_root_dir_in':
    '/home/habelitz/parallel_hyperparameter_search/tests/fixtures/fix_post_pro_demo/par'

    post_pro=phs.post_processing.PostProcessing(
        experiment_dir = '/home/habelitz/parallel_hyperparameter_search/tests/fixtures/fix_post_pro_demo' + '/exper')
    '''
