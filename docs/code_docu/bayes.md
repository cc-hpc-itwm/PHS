# bayes

## compute_bayesian_suggestion
```python
compute_bayesian_suggestion(at_index, paths, data_types_unordered_dict, result_col_name, bayesian_wait_for_all, bayesian_register_dict, bayesian_options_bounds_low_dict, bayesian_options_bounds_high_dict, bayesian_options_round_digits_dict)
```

Wrapper function executed on a certain worker to organize the bayesian optimization. This includes reading the
latest .csv file with all previous results in a thread save way, preparing the data, calling the bayesian
optimization algorithm and returning the suggested parameter values.

Parameters
----------
- **at_index** (int): index of the parameter frame at which bayesian optimization should be performed
- **paths** (dict): path information
- **data_types_unordered_dict** (dict): data type information of the parameters
- **result_col_name** (str): column name of the result frame holding the return value of the target function
- **bayesian_wait_for_all** (bool): sleep until all parameter sets with lower index are completed
- **bayesian_register_dict** (dict): information to decide which parameters in the current parameter set should be
suggested by bayesian optimization
- **bayesian_options_bounds_low_dict** (dict): lower bound for bayesian optimization for all involved parameters
- **bayesian_options_bounds_high_dict** (dict): upper bound for bayesian optimization for all involved parameters
- **bayesian_options_round_digits_dict** (dict): rounding information for suggested values


Returns
-------
**dict**: parameter names with values suggested by bayesian optimization

