import os
import time
import numpy as np
import pandas as pd

import sklearn.gaussian_process as gp
from scipy.stats import norm
from scipy.optimize import minimize


def compute_bayesian_suggestion(at_index,
                                paths,
                                data_types_unordered_dict,
                                result_col_name,
                                bayesian_wait_for_all,
                                bayesian_register_dict,
                                bayesian_options_bounds_low_dict,
                                bayesian_options_bounds_high_dict):
    """
    Wrapper function executed on a certain worker to organize the bayesian optimization. This includes reading the
    latest .csv file with all previous results in a thread save way, preparing the data, calling the bayesian
    optimization algorithm and returning the suggested parameter values.

    Parameters
    ----------
    - **at_index** (int): index of the parameter set at which bayesian optimization should be performed
    - **paths** (dict): path information
    - **data_types_unordered_dict** (dict): data type information of the parameters
    - **result_col_name** (str): column name of the result frame holding the return value of the target function
    - **bayesian_wait_for_all** (bool): sleep until all parameter sets with lower index are completed
    - **bayesian_register_dict** (dict): information to decide which parameters in the current parameter set should be
    suggested by bayesian optimization
    - **bayesian_options_bounds_low_dict** (dict): lower bound for bayesian optimization for all involved parameters
    - **bayesian_options_bounds_high_dict** (dict): upper bound for bayesian optimization for all involved parameters


    Returns
    -------
    **dict**: parameter names with values suggested by bayesian optimization
    """

    bayesian_col_name_list = []
    for key in bayesian_register_dict:
        if bayesian_register_dict[key] == 1:
            bayesian_col_name_list.append(key)

    columns_to_read = ['index']
    columns_to_read.extend(bayesian_col_name_list)
    columns_to_read.append(result_col_name)

    lock_result_path = paths['lock_result_path']
    result_file_path = paths['result_file_path']

    while True:
        while True:
            try:
                os.mkdir(lock_result_path)
                break
            except OSError:
                # print('read locked')
                time.sleep(0.1)
                continue

        with open(result_file_path, 'r') as f:
            current_result_frame = pd.read_csv(
                f, index_col='index', usecols=columns_to_read)

        if os.path.exists(lock_result_path) and os.path.isdir(lock_result_path):
            os.rmdir(lock_result_path)

        number_current_results = len(current_result_frame.index)
        if number_current_results == 0: # check if not a single result is available
            time.sleep(5) # wait and read again
        else:
            if not bayesian_wait_for_all:
                break
            else:
                if at_index <= number_current_results:
                    break
                else:
                    time.sleep(0.1)

    # print('bayesian at index %d sees %d results.' % (at_index, number_current_results))
    # print(current_result_frame)

    # important: values in bounds must have the same order as in xp according to the parameter names (col_names) they
    # belong to:
    # bounds = [[x1_low, x1_high], [x2_low, x2_high], [x3_low, x3_high], ...]
    #           -----------------  -----------------  -----------------
    #           ↓                  ↓                  ↓
    #    xp = [[x1_par1,           x2_par1,           x3_par1, ...], [x1_par2, x2_par2, x3_par2, ...], ... parN]
    bounds = []
    for col_name in current_result_frame[bayesian_col_name_list].columns:
        bounds.append([bayesian_options_bounds_low_dict[col_name],
                       bayesian_options_bounds_high_dict[col_name]])
    bounds = np.asarray(bounds).reshape(-1, 2)

    xp = current_result_frame[bayesian_col_name_list].values
    yp = current_result_frame[result_col_name].values

    kernel = gp.kernels.Matern(nu=2.5)
    alpha = 1e-6
    model = gp.GaussianProcessRegressor(kernel=kernel,
                                        alpha=alpha,
                                        n_restarts_optimizer=25,
                                        normalize_y=True)
    model.fit(xp, yp)
    next_sample = get_next_sample(acquisition_function=expected_improvement,
                                             gaussian_process=model,
                                             evaluated_loss=yp,
                                             maximize=False,
                                             bounds=bounds,
                                             restarts=100)

    bayesian_replacement_dict = {}
    for i, col in enumerate(bayesian_col_name_list):

        '''epsilon = np.full(shape=bounds.shape[0], fill_value=1e-7)
        if np.any((np.all((np.abs(next_sample - xp) <= epsilon), axis=1))):
            next_sample = np.random.uniform(bounds[:, 0], bounds[:, 1], bounds.shape[0])
            print('\tWarning: Bayesian Optimization has suggested an already seen sample point.\
                  \n\tHence a random sample is drawn.')'''

        bayesian_replacement_dict[col] = next_sample[i]
    return bayesian_replacement_dict


def get_next_sample(acquisition_function,
                               gaussian_process,
                               evaluated_loss,
                               maximize,
                               bounds=(0, 10),
                               restarts=25):

    best_x = None
    best_acquisition_value = None
    number_parameters = bounds.shape[0]

    for starting_point in np.random.uniform(bounds[:, 0], bounds[:, 1], size=(restarts, number_parameters)):

        minimize_obj = minimize(fun=acquisition_function,
                                x0=starting_point.reshape(1, -1),
                                bounds=bounds,
                                method='L-BFGS-B',
                                args=(gaussian_process, evaluated_loss, maximize, number_parameters))

        if best_acquisition_value is None:
            best_acquisition_value = minimize_obj.fun
        if minimize_obj.fun <= best_acquisition_value:
            best_acquisition_value = minimize_obj.fun
            best_x = minimize_obj.x
    return best_x


def expected_improvement(x, gaussian_process, evaluated_loss, maximize=False, number_parameters=1):

    x_to_predict = x.reshape(-1, number_parameters)

    mean, std_dev = gaussian_process.predict(x_to_predict, return_std=True)

    if maximize:
        loss_optimum = np.max(evaluated_loss)
    else:
        loss_optimum = np.min(evaluated_loss)

    if maximize:
        factor = 1
    else:
        factor = -1

    with np.errstate(divide='ignore'): # overcome std_dev = 0
        xi = 0.0
        Z = factor * (mean - loss_optimum - xi) / std_dev
        expected_improvement = factor * \
            (mean - loss_optimum - xi) * norm.cdf(Z) + std_dev * norm.pdf(Z)
        expected_improvement[std_dev == 0.0] == 0.0

    return -1 * expected_improvement
