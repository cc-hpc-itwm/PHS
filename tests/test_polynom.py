import random as rd
import pandas as pd
import os
import sys
from pathlib import Path
import tempfile
import phs.parameter_definition
import phs.parallel_hyperparameter_search
import phs.utils


def test_polynom():
    with tempfile.TemporaryDirectory(
            dir=os.path.dirname(__file__) + '/tmp', suffix=sys._getframe().f_code.co_name) as tmpdir:

        print(tmpdir)
        pardef = phs.parameter_definition.ParameterDefinition()

        pardef.set_data_types_and_order([('x', float), ('y', float)])

        pardef.add_individual_parameter_set(
            number_of_sets=2,
            set={'x': {'type': 'random', 'bounds': [-3, 3], 'distribution': 'uniform', 'round_digits': 3},
                 'y': {'type': 'random', 'bounds': [-3, 3], 'distribution': 'uniform', 'round_digits': 3}},
            prevent_duplicate=True)

        pardef.add_individual_parameter_set(
            number_of_sets=25,
            set={'x': {'type': 'bayesian', 'bounds': [-3, 3], 'round_digits': 3},
                 'y': {'type': 'bayesian', 'bounds': [-3, 3], 'round_digits': 3}})

        pardef.export_parameter_definitions(
            export_path=tmpdir + '/par')

        hs = phs.parallel_hyperparameter_search.ParallelHyperparameterSearch(
            **{'experiment_dir': tmpdir,
               'experiment_name': 'exper',
               'target_module_root_dir': str(Path(os.path.dirname(__file__)).parent) + '/examples/func_def',
               'target_module_name': 'basic_test_functions',
               'target_function_name': 'test_polynom',
               'parameter_definitions_root_dir_in': tmpdir + '/par',
               'local_processes_num_workers': 1,
               'parallelization': 'local_processes'})

        hs.start_execution()

        with open(tmpdir + "/exper/results/result_frame.csv") as f:
            result_frame = pd.read_csv(f, index_col=0)
        print(result_frame)
        print(result_frame['result'].min())

        rd.seed()   # reseed with current system time
        assert result_frame['result'].min() < -0.99
