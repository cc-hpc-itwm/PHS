class GlobalNames:
    def __init__(self):
        self.__parameter_frame_name = '/parameter_frame'
        self.__bayesian_register_frame_name = '/bayesian_register_frame'
        self.__bayesian_options_bounds_low_frame_name = '/bayesian_options_bounds_low_frame'
        self.__bayesian_options_bounds_high_frame_name = '/bayesian_options_bounds_high_frame'
        self.__data_types_ordered_list_name = '/data_types_ordered_list'
        self.__data_types_additional_information_dict_name = '/data_types_additional_information_dict'

    # names
    def get_name_par_frame(self):
        return self.__parameter_frame_name

    def get_name_bay_reg(self):
        return self.__bayesian_register_frame_name

    def get_name_bay_opt_low(self):
        return self.__bayesian_options_bounds_low_frame_name

    def get_name_bay_opt_high(self):
        return self.__bayesian_options_bounds_high_frame_name

    def get_name_data_types_ord(self):
        return self.__data_types_ordered_list_name

    def get_name_data_types_additional_inf(self):
        return self.__data_types_additional_information_dict_name

    # first level directories
    def get_lev1_res(self, experiment_path):
        return experiment_path + '/results'

    def get_lev1_par(self, experiment_path):
        return experiment_path + '/parameter_definitions'

    def get_lev1_source(self, experiment_path):
        return experiment_path + '/source_code_target'

    def get_lev1_worker(self, experiment_path):
        return experiment_path + '/worker_out'
