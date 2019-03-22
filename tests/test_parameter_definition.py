import phs.parameter_definition
import filecmp
import random as rd


def test_parameter_definition(tmpdir):
    rd.seed(5)
    subdir = 'subdir'
    tmpdir.mkdir(subdir)

    pardef = phs.parameter_definition.ParameterDefinition()

    pardef.set_data_types_and_order([('x', float), ('f', 'expr'), ('iterations', int), ('s', str)])

    pardef.add_individual_parameter_set(
        number_of_sets=3,
        set={'x': {'type': 'random', 'bounds': [-5, 5], 'distribution': 'uniform', 'round_digits': 3},
             'f': {'type': 'random_from_list', 'lst': ['math.sin(x)', 'math.cos(x)', 'math.tan(x)']},
             'iterations': {'type': 'random', 'bounds': [1, 7], 'distribution': 'uniform', 'round_digits': 0},
             's': {'type': 'random_from_list', 'lst': ['string1', 'string2', 'string3']}},
        prevent_duplicate=True)

    pardef.export_parameter_definitions(
        export_path=tmpdir+subdir)

    cmp = filecmp.dircmp(
        '/home/habelitz/parallel_hyperparameter_search/tests/fixtures/fix_parameter_def',
        tmpdir+subdir)

    # cmp.report()
    assert not cmp.diff_files   # compared directories should be identical what means empty cmp.diff_files
    print(cmp.diff_files)
