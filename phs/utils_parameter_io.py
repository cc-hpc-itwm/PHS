import pickle
import pandas as pd
import phs.global_names


def save_parameter_definitions(export_path,
                               parameter_frame,
                               bayesian_register_frame,
                               bayesian_options_bounds_low_frame,
                               bayesian_options_bounds_high_frame,
                               data_types_ordered_list):

    glob = phs.global_names.GlobalNames()
    path_to_parameter_frame = export_path + glob.get_name_par_frame()
    path_to_bayesian_register_frame = export_path + glob.get_name_bay_reg()
    path_to_bayesian_options_bounds_low_frame = export_path + glob.get_name_bay_opt_low()
    path_to_bayesian_options_bounds_high_frame = export_path + glob.get_name_bay_opt_high()
    path_to_data_types_ordered_list = export_path + glob.get_name_data_types_ord()

    parameter_frame.to_pickle(path_to_parameter_frame + '.pkl')
    with open(path_to_parameter_frame + '.txt', 'w') as f:
        f.write(parameter_frame.to_string())
    parameter_frame.to_csv(path_to_parameter_frame +
                           '.csv', sep='\t', index=True, header=True)

    bayesian_register_frame.to_pickle(path_to_bayesian_register_frame + '.pkl')
    with open(path_to_bayesian_register_frame + '.txt', 'w') as f:
        f.write(bayesian_register_frame.to_string())
    bayesian_options_bounds_low_frame.to_pickle(
        path_to_bayesian_options_bounds_low_frame + '.pkl')
    with open(path_to_bayesian_options_bounds_low_frame + '.txt', 'w') as f:
        f.write(bayesian_options_bounds_low_frame.to_string())
    bayesian_options_bounds_high_frame.to_pickle(
        path_to_bayesian_options_bounds_high_frame + '.pkl')
    with open(path_to_bayesian_options_bounds_high_frame + '.txt', 'w') as f:
        f.write(bayesian_options_bounds_high_frame.to_string())
    with open(path_to_data_types_ordered_list + '.pkl', 'wb') as f:
        pickle.dump(data_types_ordered_list, f)
    with open(path_to_data_types_ordered_list + '.txt', 'w') as f:
        f.write(str(data_types_ordered_list))


def load_parameter_definitions(import_path):
    glob = phs.global_names.GlobalNames()
    path_in_to_parameter_frame = import_path + glob.get_name_par_frame()
    path_in_to_bayesian_register_frame = import_path + glob.get_name_bay_reg()
    path_in_to_bayesian_options_bounds_low_frame = import_path + glob.get_name_bay_opt_low()
    path_in_to_bayesian_options_bounds_high_frame = import_path + glob.get_name_bay_opt_high()
    path_in_to_data_types_ordered_list = import_path + glob.get_name_data_types_ord()

    parameter_frame = pd.read_pickle(path_in_to_parameter_frame + '.pkl')
    bayesian_register_frame = pd.read_pickle(path_in_to_bayesian_register_frame + '.pkl')
    bayesian_options_bounds_low_frame = pd.read_pickle(
        path_in_to_bayesian_options_bounds_low_frame + '.pkl')
    bayesian_options_bounds_high_frame = pd.read_pickle(
        path_in_to_bayesian_options_bounds_high_frame + '.pkl')
    with open(path_in_to_data_types_ordered_list + '.pkl', 'rb') as f:
        data_types_ordered_list = pickle.load(f)

    return (parameter_frame,
            bayesian_register_frame,
            bayesian_options_bounds_low_frame,
            bayesian_options_bounds_high_frame,
            data_types_ordered_list)
