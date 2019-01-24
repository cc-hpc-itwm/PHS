import time
import datetime as dt
import os
import json as js
import numpy as np

import sys
import inspect

from . import bayes


def proxy_function(parallelization, fun, arg, auxiliary_information, with_bayesian=False, at_index=None, bayesian_placeholder_phrase=None, paths={}, data_types={}):
    start_time = dt.datetime.now()
    # np.random.seed(int(dt.datetime.now().strftime('%f')))
    # t = float(np.random.rand(1))
    time.sleep(0.01)
    if auxiliary_information['save_path'] is not False:
        zero_fill = 5
        my_save_path = auxiliary_information['save_path'] + '/' + \
            str(auxiliary_information['parameter_index']).zfill(zero_fill)
        os.mkdir(my_save_path)
    else:
        my_save_path = False
    bayesian_replacement_dict = None
    if with_bayesian:
        bayesian_replacement_dict = bayes.compute_bayesian_suggestion(
            at_index, bayesian_placeholder_phrase, paths, data_types)
        for col in bayesian_replacement_dict:
            arg[col] = bayesian_replacement_dict[col]
    string = js.dumps(arg, separators=['\n', '='])
    # string = string.strip('{}')
    string = string[1:-1]
    for key in arg:
        string = string.replace("\"" + key + "\"", key)
    parameter = {'hyperpar': string, 'my_save_path': my_save_path}
    result = fun(parameter)
    end_time = dt.datetime.now()
    worker = None
    if parallelization == 'processes':
        worker = os.getpid()
        return (result, start_time, end_time, worker, bayesian_replacement_dict)
    elif parallelization == 'mpi':
        worker = os.uname()[1]
        return (result, start_time, end_time, worker, bayesian_replacement_dict)
    elif parallelization == 'dask':
        worker = os.uname()[1]
        return (result, start_time, end_time, worker, bayesian_replacement_dict)
