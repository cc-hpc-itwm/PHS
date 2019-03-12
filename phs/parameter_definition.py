import os
import pandas as pd
import random as rd
import pickle

from phs import utils


class ParameterDefinition:
    """ """

    def __init__(self):
        utils.print_section(header='ParameterDefinition')
        self.parameter_frame = pd.DataFrame()
        self.parameter_dict = {}
        self.parameter_dict_list = []
        self.bayesian_register_dict = {}
        self.bayesian_register_dict_list = []
        self.bayesian_register_frame = pd.DataFrame()
        self.bayesian_options_bounds_low_dict = {}
        self.bayesian_options_bounds_low_dict_list = []
        self.bayesian_options_bounds_low_frame = pd.DataFrame()
        self.bayesian_options_bounds_high_dict = {}
        self.bayesian_options_bounds_high_dict_list = []
        self.bayesian_options_bounds_high_frame = pd.DataFrame()
        self.bayesian_options_round_digits_dict = {}
        self.bayesian_options_round_digits_dict_list = []
        self.bayesian_options_round_digits_frame = pd.DataFrame()
        self.expression_data_type_flag = 'expr'
        self.finalized = False

    def set_data_types_and_order(self, parameter_data_types_and_order):
        """
        Set the data types and order of the parameters which should be used in the framework.

        Parameters
        ----------
        - **parameter_data_types_and_order** (list): list of tuples, each consists of parameter name and data type.
        order of tuples represents order of parameters.

            - example:
            ```python
            [('x', float), ('y', float)]
            ```
        """

        self.data_types_ordered_list = parameter_data_types_and_order

    def set_data_types_and_order_listed(self, parameter_list, datatype_list=[], datatype_for_all=None):
        """
        An alternative to set the data types and order via a simple list. The data types can be set with a second list
        or via a single type for all.

        Parameters
        ----------
        - **parameter_list** (list): parameter names to represent their order
        - **datatype_list** (list, Default value = []): datatype for each parameter
        - **datatype_for_all** (datatype, Default value = None): data type applied to all parameters
        """

        parameter_data_types_and_order = []
        if datatype_list:
            par_and_type = zip(parameter_list, datatype_list)
            for par, datatype in par_and_type:
                parameter_data_types_and_order.append((par, datatype))
            self.data_types_ordered_list = parameter_data_types_and_order
        if datatype_for_all is not None:
            for par in parameter_list:
                parameter_data_types_and_order.append((par, datatype_for_all))
            self.data_types_ordered_list = parameter_data_types_and_order

    def add_individual_parameter_set(self, number_of_sets=1, set={}, prevent_duplicate=True):
        """
        Add one or multiple parameter sets to your parameter definition.

        Parameters
        ----------
        - **number_of_sets** (int, Default value = 1): number of parameter sets to be generated
        - **set** (dict, Default value = {}): two nested dicts defining the generation of a parameter set. the outer
        dict keywords represent the parameter names while the respective values are the inner dicts defining how this
        parameter should be generated (see documentation for more information).
        - **prevent_duplicate** (Default value = True): If True, each generated parameter set is checked for
        equality against all parameter sets already included in the parameter definition. In case an identity is found,
        the current parameter set is redrawn again. If there is any bayesian task in the set, the check is skipped.
            - example:

                ```python
                add_individual_parameter_set(
                    number_of_sets=20,
                    set={'x': {'type': 'random', 'bounds': [-5, 5], 'distribution': 'uniform', 'round_digits': 3},
                         'y': {'type': 'random_from_list', 'lst': [1.2, 3.4, 5.4, 6.3]}},
                         prevent_duplicate=True)
                ```
        """

        for set_i in range(number_of_sets):
            bayesian_in_set = False
            for par in set:
                if set[par]['type'] == 'random':
                    value = set[par]['bounds'][0] + rd.random() * (set[par]['bounds']
                                                                   [1] - set[par]['bounds'][0])
                    if set[par]['round_digits'] is not None:
                        value = round(value, set[par]['round_digits'])
                        if set[par]['round_digits'] <= 0:
                            value = int(value)
                    self.parameter_dict[par] = value
                    self.bayesian_register_dict[par] = 0
                if set[par]['type'] == 'random_from_list':
                    value = rd.choice(set[par]['lst'])
                    self.parameter_dict[par] = value
                    self.bayesian_register_dict[par] = 0
                if set[par]['type'] == 'explicit':
                    self.parameter_dict[par] = set[par]['value']
                    self.bayesian_register_dict[par] = 0
                if set[par]['type'] == 'bayesian':
                    self.parameter_dict[par] = 0
                    self.bayesian_register_dict[par] = 1
                    self.bayesian_options_bounds_low_dict[par] = set[par]['bounds'][0]
                    self.bayesian_options_bounds_high_dict[par] = set[par]['bounds'][1]
                    self.bayesian_options_round_digits_dict[par] = set[par]['round_digits']
                    bayesian_in_set = True

            if prevent_duplicate and not bayesian_in_set:
                equal = False
                for dict_i in self.parameter_dict_list:
                    if dict_i == self.parameter_dict:
                        equal = True
                        break
                    else:
                        equal = False
                        continue
                if equal:
                    print('duplicate recognized. redrawing parameter set.')
                    self.add_individual_parameter_set(
                        number_of_sets=1, set=set, prevent_duplicate=prevent_duplicate)
                else:
                    self.register_parameter_set()
            else:
                self.register_parameter_set()

    def add_listed_parameter_set(self, number_of_sets, parameter_list, options, prevent_duplicate=True):
        """
        An alternative to define parameter sets via a list.

        Parameters
        ----------
        - **number_of_sets** (int): number of parameter sets to be generated
        - **parameter_list** (list): a list containing all parameter names
        - **options** (dict): options are applied to all parameters. the mandatory keyword which has to be filled with
        a value is ```'type_for_all'```. There are four types available. Depending on the choice the some other
        keywords become compulsary.
            - ```'random'```

                -> ```'bounds_for_all'``` (list): borders of the random draw [low, high]

                -> ```'round_digits_for_all'``` (int): round value to given number of digits

            - ```'random_from_list'```

                -> ```'lst_for_all'``` (list): list from which one element is randomly picked

            - ```'explicit'```

                -> ```'value_for_all'``` (): value provided here is assigned to all parameters

            - ```'bayesian'```

                -> ```'bounds_for_all'``` (list): borders of the bayesian optimization [low, high]

                -> ```'round_digits_for_all'``` (int): round value to given number of digits

        - **prevent_duplicate** (Default value = True): If True, each generated parameter set is checked for
        equality against all parameter sets already included in the parameter definition. In case an identity is found,
        the current parameter set is redrawn again. If there is any bayesian task in the set, the check is skipped.
            - example:

                ```python
                add_listed_parameter_set(
                    number_of_sets=10,
                    parameter_list=['x1', 'x2', 'x3'],
                    options={'type_for_all': 'random', 'bounds_for_all': [1, 34], 'round_digits_for_all': 2},
                    prevent_duplicate=True)
                ```
        """

        for set_i in range(number_of_sets):
            bayesian_in_set = False
            if options['type_for_all'] == 'random':
                for par in parameter_list:
                    value = options['bounds_for_all'][0] + rd.random() * (options['bounds_for_all']
                                                                          [1] - options['bounds_for_all'][0])
                    if options['round_digits_for_all'] is not None:
                        value = round(value, options['round_digits_for_all'])
                        if options['round_digits_for_all'] <= 0:
                            value = int(value)
                    self.parameter_dict[par] = value
                    self.bayesian_register_dict[par] = 0
            if options['type_for_all'] == 'random_from_list':
                for par in parameter_list:
                    value = rd.choice(options['lst_for_all'])
                    self.parameter_dict[par] = value
                    self.bayesian_register_dict[par] = 0

            if options['type_for_all'] == 'explicit':
                for par in parameter_list:
                    self.parameter_dict[par] = options['value_for_all']
                    self.bayesian_register_dict[par] = 0

            if options['type_for_all'] == 'bayesian':
                for par in parameter_list:
                    self.parameter_dict[par] = 0
                    self.bayesian_register_dict[par] = 1
                    self.bayesian_options_bounds_low_dict[par] = options['bounds_for_all'][0]
                    self.bayesian_options_bounds_high_dict[par] = options['bounds_for_all'][1]
                    self.bayesian_options_round_digits_dict[par] = options['round_digits_for_all']
                    bayesian_in_set = True

            if prevent_duplicate and not bayesian_in_set:
                equal = False
                for dict_i in self.parameter_dict_list:
                    if dict_i == self.parameter_dict:
                        equal = True
                        break
                    else:
                        equal = False
                        continue
                if equal:
                    print('duplicate recognized. redrawing parameter set.')
                    self.add_listed_parameter_set(
                        number_of_sets=1,
                        parameter_list=parameter_list,
                        options=options,
                        prevent_duplicate=prevent_duplicate)
                else:
                    self.register_parameter_set()
            else:
                self.register_parameter_set()

    def register_parameter_set(self):
        """ """
        self.parameter_dict_list.append(self.parameter_dict)
        self.bayesian_register_dict_list.append(self.bayesian_register_dict)
        self.bayesian_options_bounds_low_dict_list.append(self.bayesian_options_bounds_low_dict)
        self.bayesian_options_bounds_high_dict_list.append(self.bayesian_options_bounds_high_dict)
        self.bayesian_options_round_digits_dict_list.append(self.bayesian_options_round_digits_dict)

        self.parameter_dict = {}
        self.bayesian_register_dict = {}
        self.bayesian_options_bounds_low_dict = {}
        self.bayesian_options_bounds_high_dict = {}
        self.bayesian_options_round_digits_dict = {}

    def finalize_parameter_definitions(self):
        """ """
        parameter_names_ordered_list = []
        for tuple_i in self.data_types_ordered_list:
            parameter_names_ordered_list.append(tuple_i[0])
        self.parameter_frame = pd.DataFrame(
            self.parameter_dict_list, columns=parameter_names_ordered_list)
        self.bayesian_register_frame = pd.DataFrame(
            self.bayesian_register_dict_list, columns=parameter_names_ordered_list)
        self.bayesian_options_bounds_low_frame = pd.DataFrame(
            self.bayesian_options_bounds_low_dict_list, columns=parameter_names_ordered_list)
        self.bayesian_options_bounds_high_frame = pd.DataFrame(
            self.bayesian_options_bounds_high_dict_list, columns=parameter_names_ordered_list)
        self.bayesian_options_round_digits_frame = pd.DataFrame(
            self.bayesian_options_round_digits_dict_list, columns=parameter_names_ordered_list)

        for tuple_i in self.data_types_ordered_list:
            if tuple_i[1] != self.expression_data_type_flag:
                par = tuple_i[0]
                self.parameter_frame[par] = self.parameter_frame[par].astype(tuple_i[1])
            else:
                self.parameter_frame[par] = self.parameter_frame[par].astype(str)

        self.finalized = True

    def export_parameter_definitions(self, export_path):
        """
        Save the complete parameter definition of the class instance to hard disc. It contains several human readable
        files and meet the requirements to be reused in the parallel_hyperparameter_search class.

        Parameters
        ----------
        - **export_path** (string): absolute path to a parent folder in which the parameter definitions are saved
        """

        self.export_path = export_path
        if os.path.exists(self.export_path) and os.path.isdir(self.export_path):
            raise ValueError('directory ' + self.export_path +
                             ' already exists. Please choose a different experiment name.')
        else:
            os.mkdir(self.export_path)

        if not self.finalized:
            self.finalize_parameter_definitions()
        self.path_to_parameter_frame = self.export_path + '/parameter_frame'
        self.path_to_bayesian_register_frame = self.export_path + '/bayesian_register_frame'
        self.path_to_bayesian_options_bounds_low_frame = self.export_path + '/bayesian_options_bounds_low_frame'
        self.path_to_bayesian_options_bounds_high_frame = self.export_path + '/bayesian_options_bounds_high_frame'
        self.path_to_bayesian_options_round_digits_frame = self.export_path + \
            '/bayesian_options_round_digits_frame'
        self.path_to_data_types_ordered_list = self.export_path + '/data_types_ordered_list'

        self.parameter_frame.to_pickle(self.path_to_parameter_frame + '.pkl')
        with open(self.path_to_parameter_frame + '.txt', 'w') as f:
            f.write(self.parameter_frame.to_string())
        self.parameter_frame.to_csv(self.path_to_parameter_frame +
                                    '.csv', sep='\t', index=True, header=True)

        self.bayesian_register_frame.to_pickle(self.path_to_bayesian_register_frame + '.pkl')
        with open(self.path_to_bayesian_register_frame + '.txt', 'w') as f:
            f.write(self.bayesian_register_frame.to_string())
        self.bayesian_options_bounds_low_frame.to_pickle(
            self.path_to_bayesian_options_bounds_low_frame + '.pkl')
        with open(self.path_to_bayesian_options_bounds_low_frame + '.txt', 'w') as f:
            f.write(self.bayesian_options_bounds_low_frame.to_string())
        self.bayesian_options_bounds_high_frame.to_pickle(
            self.path_to_bayesian_options_bounds_high_frame + '.pkl')
        with open(self.path_to_bayesian_options_bounds_high_frame + '.txt', 'w') as f:
            f.write(self.bayesian_options_bounds_high_frame.to_string())
        self.bayesian_options_round_digits_frame.to_pickle(
            self.path_to_bayesian_options_round_digits_frame + '.pkl')
        with open(self.path_to_bayesian_options_round_digits_frame + '.txt', 'w') as f:
            f.write(self.bayesian_options_round_digits_frame.to_string())
        with open(self.path_to_data_types_ordered_list + '.pkl', 'wb') as f:
            pickle.dump(self.data_types_ordered_list, f)
        with open(self.path_to_data_types_ordered_list + '.txt', 'w') as f:
            f.write(str(self.data_types_ordered_list))

        rows, columns = self.parameter_frame.shape
        print('', end='\n')
        print('\t{0:30}{1:}' .format('number of parameters:', columns))
        print('\t{0:30}{1:}' .format('number of parameter sets:', rows))
        print('\t{0:30}{1:}' .format('exported to:', self.export_path), end='\n\n')

    def _return_parameter_definitions(self):
        """ """
        if not self.finalized:
            self.finalize_parameter_definitions()
        return {'parameter_frame': self.parameter_frame,
                'bayesian_register_frame': self.bayesian_register_frame,
                'bayesian_options_bounds_low_frame': self.bayesian_options_bounds_low_frame,
                'bayesian_options_bounds_high_frame': self.bayesian_options_bounds_high_frame,
                'bayesian_options_round_digits_frame': self.bayesian_options_round_digits_frame,
                'data_types_ordered_list': self.data_types_ordered_list}
