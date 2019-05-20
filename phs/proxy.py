import time
import os
import json as js
import numpy as np
import pandas as pd
from dask.distributed import get_worker

import phs.bayes
import phs.utils


def proxy_function(parallelization,
                   fun,
                   arg,
                   index,
                   data_types_ordered_list,
                   expression_data_type_flag,
                   auxiliary_information,
                   with_bayesian=False,
                   paths={},
                   result_col_name=None,
                   bayesian_wait_for_all=False,
                   bayesian_register_dict={},
                   bayesian_options_bounds_low_dict={},
                   bayesian_options_bounds_high_dict={}):
    """
    This function is directly submitted to the scheduler, which means it is spawned on the parallel workers. It serves
    as a precursor to build the needed structure of the single string which is transfered to the target function.
    Bayesian optimization is called from inside in case it is set, whereby it is performed on the worker itself.
    Thereafter the target function is called.

    Parameters
    ----------
    - **parallelization** (str): type of parallelization used, one of {'local_processes', 'dask'}
    - **fun** (callable): target function
    - **arg** (dict): arguments for 'fun' temporary encapsulated in a dict
    - **index** (int): index of the parameter set which is evaluated
    - **data_types_ordered_list** (list): list of tuples holding information about order and data types of parameters
    in the current set
    - **expression_data_type_flag** (str): custom name of the data type 'expression'
    - **auxiliary_information** (dict): additional information
    - **with_bayesian** (bool, Default value = False): indicates whether any parameter in the set has to be calculated
    with bayesian optimization
    - **paths** (dict, Default value = {}): path information
    - **result_col_name** (str, Default value = None): column name of the result frame holding the return value of the
    target function

    Returns
    -------
    **tuple**: (index, result, start_time, end_time, worker, bayesian_replacement_dict)
    - **index** (int): index of the parameter set which has been evaluated
    - **result** (float): returned value of the target function
    - **start_time** (datetime.datetime): start time of the 'proxy_function' what is the start of the worker job
    - **end_time** (datetime.datetime): end time of the 'proxy_function' what is the end of the worker job
    - **worker** (str): nam eof the current worker
    - **bayesian_replacement_dict** (dict): parameter names with values suggested by bayesian optimization
    """

    start_time = pd.datetime.now()
    np.random.seed(1)  # needed to make all bayesian optimization reproducible
    time.sleep(0.01)
    if auxiliary_information['provide_worker_path'] or auxiliary_information['redirect_stdout']:
        zero_fill = auxiliary_information['zero_fill']
        worker_save_path = auxiliary_information['worker_save_path_root'] + \
            '/' + str(index).zfill(zero_fill) + '/'
        os.mkdir(worker_save_path)
    else:
        worker_save_path = False

    data_types_unordered_dict = {}
    for tuple_i in data_types_ordered_list:
        data_types_unordered_dict[tuple_i[0]] = tuple_i[1]

    bayesian_replacement_dict = None
    if with_bayesian:
        bayesian_replacement_dict = phs.bayes.compute_bayesian_suggestion(index,
                                                                          paths,
                                                                          data_types_unordered_dict,
                                                                          result_col_name,
                                                                          bayesian_wait_for_all,
                                                                          bayesian_register_dict,
                                                                          bayesian_options_bounds_low_dict,
                                                                          bayesian_options_bounds_high_dict)
        for col in bayesian_replacement_dict:
            arg[col] = bayesian_replacement_dict[col]

    for key in arg:
        if isinstance(arg[key], np.integer):  # json can not serialize numpy.integer
            arg[key] = int(arg[key])
    string = js.dumps(arg, separators=['\n', '='])
    string = string[1:-1]  # strips {}
    for key in arg:
        if data_types_unordered_dict[key] != expression_data_type_flag:
            string = string.replace("\"" + key + "\"", key)
        else:
            string = string.replace("\"" + key + "\"" + "=\"" +
                                    arg[key] + "\"", key + "=" + arg[key])
    parameter = {'hyperpar': string, 'worker_save_path': worker_save_path}
    if auxiliary_information['redirect_stdout']:
        with phs.utils.RedirectStdoutStream(worker_save_path + auxiliary_information['std_out_name']):
            result = fun(parameter)
    else:
        result = fun(parameter)
    end_time = pd.datetime.now()
    worker = None
    if parallelization == 'local_processes':
        worker = os.getpid()
    elif parallelization == 'mpi':
        worker = os.uname()[1]
    elif parallelization == 'dask':
        worker = get_worker().name  # The worker on which this task is running

    return (index, result, start_time, end_time, worker, bayesian_replacement_dict)
