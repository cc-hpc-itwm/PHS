import random as rd
import os
import filecmp
import tempfile
import phs.parameter_definition
import phs.utils


def test_parameter_definition():
    rd.seed(8856)
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

        dcmp = filecmp.dircmp(
            os.path.dirname(__file__) + '/fixtures/fix_parameter_def/par',
            tmpdir + '/par')

        # cmp.report_full_closure()
        print(phs.utils.comp_files_and_dirs(dcmp))
        # compared directories should be identical what means empty cmp.diff_files
        rd.seed()   # reseed with current system time
        assert not phs.utils.comp_files_and_dirs(dcmp)


'''fixture paths
    export_path='/home/habelitz/parallel_hyperparameter_search/tests/fixtures/fix_parameter_def/par'
    '''
