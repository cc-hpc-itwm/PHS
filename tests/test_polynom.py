import random as rd
import pandas as pd
import os
import sys
from pathlib import Path
import tempfile
import phs.parameter_definition  # standalone import
import phs.experiment_definition  # standalone import
import phs.compute_definition  # standalone import


def test_polynom():
    with tempfile.TemporaryDirectory(
            dir=os.path.dirname(__file__) + '/tmp', suffix=sys._getframe().f_code.co_name) as tmpdir:

        print(tmpdir)
        tmpdir_ex = tmpdir + '/exper'

        pardef = phs.parameter_definition.ParameterDefinition()

        pardef.set_data_types_and_order([('x', float), ('y', float)])

        pardef.add_individual_parameter_set(
            number_of_sets=2,
            set={'x': {'type': 'random', 'bounds': [-3, 3], 'distribution': 'uniform', 'round_digits': 3},
                 'y': {'type': 'random', 'bounds': [-3, 3], 'distribution': 'uniform', 'round_digits': 3}},
            prevent_duplicate=True)

        pardef.add_individual_parameter_set(
            number_of_sets=25,
            set={'x': {'type': 'bayesian', 'bounds': [-3, 3]},
                 'y': {'type': 'bayesian', 'bounds': [-3, 3]}})

        expdef = phs.experiment_definition.ExperimentDefinition(
            experiment_dir=tmpdir_ex,
            target_module_root_dir=str(
                Path(os.path.dirname(__file__)).parent) + '/examples/func_def',
            target_module_name='basic_test_functions',
            target_function_name='test_polynom',
            parameter_definitions=pardef.get_parameter_definitions())

        compdef = phs.compute_definition.ComputeDefinition(
            experiment_dir=tmpdir_ex,
            parallelization='local_processes',
            local_processes_num_workers=1)

        compdef.start_execution()

        with open(tmpdir_ex + "/results/result_frame.csv") as f:
            result_frame = pd.read_csv(f, index_col=0)
        print(result_frame)
        print(result_frame['result'].min())

        # assert result_frame['result'].min() < -0.99

        rd.seed()   # reseed with current system time
