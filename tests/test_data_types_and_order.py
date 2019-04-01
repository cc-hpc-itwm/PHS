import random as rd
import os
from pathlib import Path
import filecmp
import tempfile
import phs.parameter_definition
import phs.parallel_hyperparameter_search
import phs.utils


def test_data_types_and_order():
    rd.seed(1109)
    with tempfile.TemporaryDirectory(dir=os.path.dirname(__file__) + '/tmp') as tmpdir:

        pardef = phs.parameter_definition.ParameterDefinition()

        pardef.set_data_types_and_order(
            [('x', float), ('f', 'expr'), ('iterations', int), ('s', str)])

        pardef.add_individual_parameter_set(
            number_of_sets=3,
            set={'x': {'type': 'random', 'bounds': [-5, 5], 'distribution': 'uniform', 'round_digits': 3},
                 'f': {'type': 'random_from_list', 'lst': ['math.sin(x)', 'math.cos(x)', 'math.tan(x)']},
                 'iterations': {'type': 'random', 'bounds': [1, 7], 'distribution': 'uniform', 'round_digits': 0},
                 's': {'type': 'random_from_list', 'lst': ['string1', 'string2', 'string3']}},
            prevent_duplicate=True)

        pardef.export_parameter_definitions(
            export_path=tmpdir + '/par')

        hs = phs.parallel_hyperparameter_search.ParallelHyperparameterSearch(
            **{'experiment_dir': tmpdir,
               'experiment_name': 'exper',
               'target_module_root_dir': str(Path(os.path.dirname(__file__)).parent) + '/examples/func_def',
               'target_module_name': 'data_types_and_order_func',
               'target_function_name': 'data_types_and_order_func',
               'parameter_definitions_root_dir_in': tmpdir + '/par',
               'parallelization': 'local_processes',
               'local_processes_num_workers': 1,
               'redirect_stdout': True})

        hs.start_execution()

        dcmp = filecmp.dircmp(
            os.path.dirname(__file__) + '/fixtures/fix_data_types_and_order',
            tmpdir,
            ignore=['additional_information_frame.csv', 'data_types_and_order_func.py'])

        # cmp.report_full_closure()
        print(phs.utils.comp_files_and_dirs(dcmp))
        # compared directories should be identical what means empty cmp.diff_files
        rd.seed()   # reseed with current system time
        assert not phs.utils.comp_files_and_dirs(dcmp)

        '''fixture paths
            export_path='/home/habelitz/parallel_hyperparameter_search/tests/fixtures/fix_data_types_and_order/par')

            'experiment_dir':
            '/home/habelitz/parallel_hyperparameter_search/tests/fixtures/fix_data_types_and_order'
            'target_module_root_dir':
            '/home/habelitz/parallel_hyperparameter_search/examples/func_def'
            'parameter_definitions_root_dir_in':
            '/home/habelitz/parallel_hyperparameter_search/tests/fixtures/fix_data_types_and_order/par'
            '''
