import numpy as np
import pandas as pd
import math as ma

import sklearn.gaussian_process as gp
from scipy.stats import norm
from scipy.optimize import minimize

import utils

def compute_bayesian_suggestion(at_index, bayesian_placeholder_phrase, paths, data_types):
    
    current_folder = utils.find_current_folder(paths['swap_path'])
    current_log_frame = pd.read_pickle(current_folder + '/log_frame.pkl')
    
    bayesian_options_bounds_low_frame = pd.read_pickle(paths['path_to_bayesian_options_bounds_low_frame'] + '.pkl')
    bayesian_options_bounds_high_frame = pd.read_pickle(paths['path_to_bayesian_options_bounds_high_frame'] + '.pkl')
    bayesian_options_round_digits_frame = pd.read_pickle(paths['path_to_bayesian_options_round_digits_frame'] + '.pkl')

    samples_array_x = []
    num_bayesian_placeholder = 0
    col_name_list = []
    bounds_list = []
    for col_i in range(len(current_log_frame.columns)):
        if current_log_frame.iloc[at_index,col_i] == bayesian_placeholder_phrase:
            col_name = current_log_frame.columns[col_i]
            col_name_list.append(col_name)
            bounds_i = [bayesian_options_bounds_low_frame.loc[at_index,col_name], bayesian_options_bounds_high_frame.loc[at_index,col_name]]
            bounds_list.append(bounds_i)
            num_bayesian_placeholder = num_bayesian_placeholder + 1
            samples_x = []
            for row in range(at_index):
                value = current_log_frame.loc[row,'result']
                if not ma.isnan(value):
                    samples_x.append(current_log_frame.iloc[row,col_i])
            samples_array_x.append(samples_x)
    samples_array_x_np = np.asarray(samples_array_x).reshape(num_bayesian_placeholder,-1)
    samples_array_x_np = np.transpose(samples_array_x_np)

    bounds = np.asarray(bounds_list).reshape(-1,2)
    
    samples_y = []
    for row in range(at_index):
        value = current_log_frame.loc[row,'result']
        if not ma.isnan(value):
            samples_y.append(value)
    samples_array_y_np = np.asarray(samples_y).reshape(-1)

    xp = samples_array_x_np
    yp = samples_array_y_np
    kernel = gp.kernels.Matern()
    alpha = 1e-5
    epsilon = 1e-7
    model = gp.GaussianProcessRegressor(kernel=kernel,alpha=alpha,n_restarts_optimizer=10,normalize_y=True)
    model.fit(xp, yp)
    next_sample = sample_next_hyperparameter(expected_improvement, model, yp, greater_is_better=False, bounds=bounds, n_restarts=100)
    if np.any(np.abs(next_sample - xp) <= epsilon):
        next_sample = np.random.uniform(bounds[:, 0], bounds[:, 1], bounds.shape[0])
    bayesian_replacement_dict = {}
    for i, col in enumerate(col_name_list):
        if not ma.isnan(bayesian_options_round_digits_frame.loc[at_index,col_name_list[i]]):
            next_sample[i] = round(next_sample[i],int(bayesian_options_round_digits_frame.loc[at_index,col_name_list[i]]))
        bayesian_replacement_dict[col_name_list[i]] = next_sample[i].astype(data_types[col_name_list[i]]).item()
    return bayesian_replacement_dict

def sample_next_hyperparameter(acquisition_func, gaussian_process, evaluated_loss, greater_is_better, bounds=(0, 10), n_restarts=25):
    best_x = None
    best_acquisition_value = None
    n_params = bounds.shape[0]

    for starting_point in np.random.uniform(bounds[:, 0], bounds[:, 1], size=(n_restarts, n_params)):

        minimize_obj = minimize(fun=acquisition_func, x0=starting_point.reshape(1, -1), bounds=bounds, method='L-BFGS-B',
                       args=(gaussian_process, evaluated_loss, greater_is_better, n_params))

        if best_acquisition_value == None:
            best_acquisition_value = minimize_obj.fun
        if minimize_obj.fun <= best_acquisition_value:
            best_acquisition_value = minimize_obj.fun
            best_x = minimize_obj.x
    return best_x

def expected_improvement(x, gaussian_process, evaluated_loss, greater_is_better=False, n_params=1):

    x_to_predict = x.reshape(-1, n_params)

    mu, sigma = gaussian_process.predict(x_to_predict, return_std=True)

    if greater_is_better:
        loss_optimum = np.max(evaluated_loss)
    else:
        loss_optimum = np.min(evaluated_loss)

    scaling_factor = (-1) ** (not greater_is_better)

    # In case sigma equals zero
    with np.errstate(divide='ignore'):
        Z = scaling_factor * (mu - loss_optimum) / sigma
        expected_improvement = scaling_factor * (mu - loss_optimum) * norm.cdf(Z) + sigma * norm.pdf(Z)
        expected_improvement[sigma == 0.0] == 0.0

    return -1 * expected_improvement