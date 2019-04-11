'''# self.model_preview_path = self.experiment_dir + '/model_preview'


def show_parameter_set_dtypes(self):
    """ """
    print(self.parameter_frame.dtypes)


def show_parameter_set(self):
    """ """
    print(self.parameter_frame)


def show_bayesian_options_bounds_low_frame(self):
    """ """
    print('bayesian_options_bounds_low_frame')
    print(self.bayesian_options_bounds_low_frame)


def show_bayesian_options_bounds_high_frame(self):
    """ """
    print('bayesian_options_bounds_high_frame')
    print(self.bayesian_options_bounds_high_frame)


def create_parameter_string_list(self):
    """ """
    self.parameter_string_list = []
    list_of_dicts = self.parameter_frame.to_dict(orient='records')
    for dict_i in list_of_dicts:
        for key in dict_i:
            dict_i[key] = dict_i[key].item()
        string = js.dumps(dict_i, separators=['\n', '='])
        string = string.replace('"', "")
        string = string.strip('{}')
        self.parameter_string_list.append(string)
    return self.parameter_string_list


def show_model_preview(self, preview_function_name):
    """

    Parameters
    ----------
    preview_function_name :


    Returns
    -------

    """
    os.mkdir(self.model_preview_path)
    with open(self.model_preview_path + '/model_preview.txt', 'w') as f:
        with redirect_stdout(f):
            self.model_preview_out(preview_function_name)
    self.model_preview_out(preview_function_name)


def model_preview_out(self, preview_function_name):
    """

    Parameters
    ----------
    preview_function_name :


    Returns
    -------

    """
    self.preview_function_name = preview_function_name
    self.loaded_preview_function = getattr(self.target_module, self.preview_function_name)

    parameter_string_list_preview = self.create_parameter_string_list()
    parameter_index_list_preview = self.parameter_frame.index.values.tolist()
    list_of_parameter_dicts_preview = self.parameter_frame.astype(
        object).to_dict(orient='records')
    for i in parameter_index_list_preview:
        parameter_dict_i = list_of_parameter_dicts_preview[i]
        string = js.dumps(parameter_dict_i, separators=['\n', '='])
        # string = string.strip('{}')
        string = string[1:-1]
        for key in parameter_dict_i:
            string = string.replace("\"" + key + "\"", key)
        print('\nparameter set ' + str(i) + ':')
        self.loaded_preview_function(string)
'''
