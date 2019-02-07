import time
import datetime as dt
import os
import json as js
import numpy as np

import sys
import inspect

from . import bayes


def proxy_function(parallelization,
                   fun,
                   arg,
                   index,
                   data_types_ordered,
                   expression_data_type_flag,
                   auxiliary_information,
                   with_bayesian=False,
                   paths={},
                   result_col_name=None,
                   bayesian_wait_for_all=False,
                   bayesian_register_dict={},
                   bayesian_options_bounds_low_dict={},
                   bayesian_options_bounds_high_dict={},
                   bayesian_options_round_digits_dict={}):
    start_time = dt.datetime.now()
    np.random.seed(int(dt.datetime.now().strftime('%f')))
    t = float(np.random.rand(1))
    time.sleep(t/100 + 0.01)
    if auxiliary_information['save_path'] is not False:
        zero_fill = 5
        my_save_path = auxiliary_information['save_path'] + '/' + \
            str(auxiliary_information['parameter_index']).zfill(zero_fill)
        os.mkdir(my_save_path)
    else:
        my_save_path = False
    bayesian_replacement_dict = None
    if with_bayesian:
        bayesian_replacement_dict = bayes.compute_bayesian_suggestion(index,
                                                                      paths,
                                                                      data_types_ordered,
                                                                      result_col_name,
                                                                      bayesian_wait_for_all,
                                                                      bayesian_register_dict,
                                                                      bayesian_options_bounds_low_dict,
                                                                      bayesian_options_bounds_high_dict,
                                                                      bayesian_options_round_digits_dict)
        for col in bayesian_replacement_dict:
            arg[col] = bayesian_replacement_dict[col]
    string = js.dumps(arg, separators=['\n', '='])
    string = string[1:-1]  # strips {}
    for key in arg:
        if data_types_ordered[key] != expression_data_type_flag:
            string = string.replace("\"" + key + "\"", key)
        else:
            string = string.replace("\"" + key + "\"" + "=\"" +
                                    arg[key] + "\"", key + "=" + arg[key])
    parameter = {'hyperpar': string, 'my_save_path': my_save_path}
    result = fun(parameter)
    end_time = dt.datetime.now()
    worker = None
    if parallelization == 'processes':
        worker = os.getpid()
        return (index, result, start_time, end_time, worker, bayesian_replacement_dict)
    elif parallelization == 'mpi':
        worker = os.uname()[1]
        return (index, result, start_time, end_time, worker, bayesian_replacement_dict)
    elif parallelization == 'dask':
        worker = os.uname()[1]
        return (index, result, start_time, end_time, worker, bayesian_replacement_dict)
