import random as rd
import os
import sys
from pathlib import Path
import filecmp
import tempfile
import phs.parameter_definition
import phs.parallel_hyperparameter_search
import phs.utils


def test_quick_start():
    rd.seed(8876)
    with tempfile.TemporaryDirectory(
            dir=os.path.dirname(__file__) + '/tmp', suffix=sys._getframe().f_code.co_name) as tmpdir:

        print(tmpdir)
        pardef = phs.parameter_definition.ParameterDefinition()

        pardef.set_data_types_and_order([('x', float), ('y', float)])

        pardef.add_individual_parameter_set(
            number_of_sets=20,
            set={'x': {'type': 'random', 'bounds': [-5, 5], 'distribution': 'uniform', 'round_digits': 3},
                 'y': {'type': 'random_from_list', 'lst': [1.2, 3.4, 5.4, 6.3]}},
            prevent_duplicate=True)

        pardef.add_individual_parameter_set(
            number_of_sets=10,
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
               'local_processes_num_workers': 1,
               'parallelization': 'local_processes'})

        hs.start_execution()

        with open(tmpdir + "/exper/results/result_frame.csv") as f:
            data = f.read()
            print(data)

        with open(str(Path(os.path.dirname(__file__))) + "/fixtures/fix_quick_start/exper/results/result_frame.csv") as f:
            data = f.read()
            print(data)

        print(os.path.dirname(__file__), 'fix_quick_start')
        dcmp = filecmp.dircmp(
            os.path.dirname(__file__) + '/fixtures/fix_quick_start',
            tmpdir,
            ignore=['additional_information_frame.csv', 'basic_test_functions.py'])

        # cmp.report_full_closure()
        print(phs.utils.comp_files_and_dirs(dcmp).join("\n"))
        # compared directories should be identical what means empty cmp.diff_files
        rd.seed()   # reseed with current system time
        assert not phs.utils.comp_files_and_dirs(dcmp)

        '''fixture paths
                    export_path='/home/habelitz/parallel_hyperparameter_search/tests/fixtures/fix_quick_start/par'

                    'experiment_dir':
                    '/home/habelitz/parallel_hyperparameter_search/tests/fixtures/fix_quick_start'
                    'target_module_root_dir':
                    '/home/habelitz/parallel_hyperparameter_search/examples/func_def'
                    'parameter_definitions_root_dir_in':
                    '/home/habelitz/parallel_hyperparameter_search/tests/fixtures/fix_quick_start/par'
                    '''
