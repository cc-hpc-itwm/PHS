# proxy

## proxy_function
```python
proxy_function(parallelization, fun, arg, index, data_types_ordered_list, expression_data_type_flag, auxiliary_information, with_bayesian=False, paths={}, result_col_name=None, bayesian_wait_for_all=False, bayesian_register_dict={}, bayesian_options_bounds_low_dict={}, bayesian_options_bounds_high_dict={}, bayesian_options_round_digits_dict={})
```

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

